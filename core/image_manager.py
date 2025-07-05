"""
Image Manager for ComicsRename application.

Handles image downloading, caching, and processing for cover images.
"""

import os
import tempfile
import requests
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ImageManager:
    """Handles image downloading, caching, and processing."""
    
    def __init__(self, debug: bool = False, cache_dir: Optional[str] = None):
        """Initialize image manager.
        
        Args:
            debug: Enable debug logging
            cache_dir: Directory for image cache (default: system temp)
        """
        self.debug = debug
        self.cache_dir = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "ComicsRename_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # HTTP session for reuse
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ComicsRename/3.3',
            'Accept': 'image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # Cache of loaded pixmaps
        self.pixmap_cache = {}
        
        # URL normalization rules
        self.url_normalizers = {
            'bdgest': self._normalize_bdgest_url,
            'comicvine': self._normalize_comicvine_url,
        }
    
    def load_and_cache_cover(self, url: str, meta: Dict[str, Any], provider: str = 'auto') -> Tuple[Optional[QPixmap], Optional[str]]:
        """Load cover image and cache it locally.
        
        Args:
            url: Image URL
            meta: Album metadata (will be updated with cache path)
            provider: Provider name for URL normalization
            
        Returns:
            tuple: (QPixmap or None, cached_file_path or None)
        """
        if self.debug:
            print(f"[DEBUG] ImageManager: Loading cover from: {url}")
        
        # Normalize URL based on provider
        normalized_url = self.normalize_url(url, provider)
        
        # Check if already cached
        cache_path = self._get_cache_path(normalized_url)
        
        if cache_path.exists():
            if self.debug:
                print(f"[DEBUG] ImageManager: Using cached image: {cache_path}")
            
            # Load from cache
            pixmap = self._load_pixmap_from_file(str(cache_path))
            if pixmap and not pixmap.isNull():
                meta['cover_local_path'] = str(cache_path)
                return pixmap, str(cache_path)
        
        # Download image
        try:
            image_data = self._download_image(normalized_url)
            if not image_data:
                return None, None
            
            # Create pixmap
            pixmap = QPixmap()
            if not pixmap.loadFromData(image_data):
                if self.debug:
                    print(f"[DEBUG] ImageManager: Failed to create QPixmap from data")
                return None, None
            
            # Cache the image
            cached_path = self._cache_image_data(image_data, normalized_url)
            if cached_path:
                meta['cover_local_path'] = cached_path
                if self.debug:
                    print(f"[DEBUG] ImageManager: Image cached at: {cached_path}")
            
            return pixmap, cached_path
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] ImageManager: Error loading image: {e}")
            return None, None
    
    def normalize_url(self, url: str, provider: str = 'auto') -> str:
        """Normalize URL based on provider.
        
        Args:
            url: Original URL
            provider: Provider name or 'auto' for auto-detection
            
        Returns:
            str: Normalized URL
        """
        if not url:
            return url
        
        # Auto-detect provider if not specified
        if provider == 'auto':
            if 'bedetheque.com' in url:
                provider = 'bdgest'
            elif 'comicvine.com' in url:
                provider = 'comicvine'
        
        # Apply provider-specific normalization
        normalizer = self.url_normalizers.get(provider.lower())
        if normalizer:
            return normalizer(url)
        
        return url
    
    def _normalize_bdgest_url(self, url: str) -> str:
        """Normalize BDGest URL."""
        if url.startswith('/'):
            return 'https://www.bedetheque.com' + url
        return url
    
    def _normalize_comicvine_url(self, url: str) -> str:
        """Normalize ComicVine URL."""
        # ComicVine URLs are typically complete
        return url
    
    def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL.
        
        Args:
            url: Image URL
            
        Returns:
            bytes: Image data or None if failed
        """
        try:
            if self.debug:
                print(f"[DEBUG] ImageManager: Downloading image from: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if not content_type.startswith('image/'):
                if self.debug:
                    print(f"[DEBUG] ImageManager: Unexpected content type: {content_type}")
                # Continue anyway as some servers don't set correct content type
            
            return response.content
            
        except requests.RequestException as e:
            if self.debug:
                print(f"[DEBUG] ImageManager: Download failed: {e}")
            return None
    
    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for URL.
        
        Args:
            url: Image URL
            
        Returns:
            Path: Cache file path
        """
        # Create hash of URL for filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Try to get file extension from URL
        parsed = urlparse(url)
        ext = Path(parsed.path).suffix
        if not ext or ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'  # Default extension
        
        return self.cache_dir / f"{url_hash}{ext}"
    
    def _cache_image_data(self, data: bytes, url: str) -> Optional[str]:
        """Cache image data to file.
        
        Args:
            data: Image data
            url: Original URL (for cache filename)
            
        Returns:
            str: Cache file path or None if failed
        """
        try:
            cache_path = self._get_cache_path(url)
            
            # Write to temporary file first, then move (atomic operation)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp_file:
                tmp_file.write(data)
                tmp_file.flush()
                
                # Move to final location
                shutil.move(tmp_file.name, cache_path)
                
                if self.debug:
                    print(f"[DEBUG] ImageManager: Cached image to: {cache_path}")
                
                return str(cache_path)
                
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] ImageManager: Failed to cache image: {e}")
            return None
    
    def _load_pixmap_from_file(self, file_path: str) -> Optional[QPixmap]:
        """Load QPixmap from file with caching.
        
        Args:
            file_path: Path to image file
            
        Returns:
            QPixmap or None if failed
        """
        # Check in-memory cache first
        if file_path in self.pixmap_cache:
            return self.pixmap_cache[file_path]
        
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Cache in memory (limit cache size)
                if len(self.pixmap_cache) > 20:  # Limit cache size
                    # Remove oldest entry
                    self.pixmap_cache.pop(next(iter(self.pixmap_cache)))
                
                self.pixmap_cache[file_path] = pixmap
                return pixmap
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] ImageManager: Failed to load pixmap from {file_path}: {e}")
        
        return None
    
    def scale_image_to_fit(self, pixmap: QPixmap, max_width: int = 200, max_height: int = 300) -> QPixmap:
        """Scale image to fit within bounds while maintaining aspect ratio.
        
        Args:
            pixmap: Original QPixmap
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            QPixmap: Scaled image
        """
        if pixmap.isNull():
            return pixmap
        
        # Calculate scaling to fit within bounds
        width_ratio = max_width / pixmap.width()
        height_ratio = max_height / pixmap.height()
        scale_ratio = min(width_ratio, height_ratio)
        
        if scale_ratio >= 1.0:
            # No scaling needed
            return pixmap
        
        # Scale with smooth transformation
        new_width = int(pixmap.width() * scale_ratio)
        new_height = int(pixmap.height() * scale_ratio)
        
        return pixmap.scaled(
            new_width, new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    
    def get_image_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about an image file.
        
        Args:
            file_path: Path to image file
            
        Returns:
            dict: Image information
        """
        try:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                return {'valid': False, 'error': 'Cannot load image'}
            
            file_size = os.path.getsize(file_path)
            
            return {
                'valid': True,
                'width': pixmap.width(),
                'height': pixmap.height(),
                'file_size': file_size,
                'file_path': file_path,
                'format': Path(file_path).suffix.lower().lstrip('.')
            }
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def cleanup_cache(self, max_age_days: int = 7, max_size_mb: int = 100):
        """Clean up old cache files.
        
        Args:
            max_age_days: Maximum age of cache files in days
            max_size_mb: Maximum total cache size in MB
        """
        if self.debug:
            print(f"[DEBUG] ImageManager: Cleaning up cache directory: {self.cache_dir}")
        
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        files_to_remove = []
        total_size = 0
        
        try:
            for file_path in self.cache_dir.glob('*'):
                if file_path.is_file():
                    stat = file_path.stat()
                    age = current_time - stat.st_mtime
                    size = stat.st_size
                    
                    # Mark old files for removal
                    if age > max_age_seconds:
                        files_to_remove.append((file_path, age, size))
                    
                    total_size += size
            
            # Remove old files
            for file_path, age, size in files_to_remove:
                try:
                    file_path.unlink()
                    total_size -= size
                    if self.debug:
                        print(f"[DEBUG] ImageManager: Removed old cache file: {file_path}")
                except Exception as e:
                    if self.debug:
                        print(f"[DEBUG] ImageManager: Failed to remove {file_path}: {e}")
            
            # If still over size limit, remove more files (oldest first)
            if total_size > max_size_mb * 1024 * 1024:
                remaining_files = []
                for file_path in self.cache_dir.glob('*'):
                    if file_path.is_file():
                        stat = file_path.stat()
                        remaining_files.append((file_path, stat.st_mtime, stat.st_size))
                
                # Sort by age (oldest first)
                remaining_files.sort(key=lambda x: x[1])
                
                for file_path, mtime, size in remaining_files:
                    if total_size <= max_size_mb * 1024 * 1024:
                        break
                    
                    try:
                        file_path.unlink()
                        total_size -= size
                        if self.debug:
                            print(f"[DEBUG] ImageManager: Removed cache file for size limit: {file_path}")
                    except Exception as e:
                        if self.debug:
                            print(f"[DEBUG] ImageManager: Failed to remove {file_path}: {e}")
            
            if self.debug:
                print(f"[DEBUG] ImageManager: Cache cleanup complete. Total size: {total_size / (1024*1024):.1f} MB")
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] ImageManager: Cache cleanup failed: {e}")
    
    def get_cached_image_path(self, url: str) -> Optional[str]:
        """Get cached image path for URL if it exists.
        
        Args:
            url: Image URL
            
        Returns:
            str: Cached file path or None if not cached
        """
        normalized_url = self.normalize_url(url)
        cache_path = self._get_cache_path(normalized_url)
        
        if cache_path.exists():
            return str(cache_path)
        
        return None
    
    def clear_cache(self):
        """Clear all cached images."""
        try:
            for file_path in self.cache_dir.glob('*'):
                if file_path.is_file():
                    file_path.unlink()
            
            # Clear in-memory cache
            self.pixmap_cache.clear()
            
            if self.debug:
                print(f"[DEBUG] ImageManager: Cache cleared")
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] ImageManager: Failed to clear cache: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, 'session'):
            self.session.close()
