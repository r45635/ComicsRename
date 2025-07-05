"""
SafeRename Manager for ComicsRename application.

Handles PDF/cover comparison logic with integrated caching and error handling.
"""

import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from .error_handler import ErrorHandler
from .image_manager import ImageManager


class SafeRenameManager:
    """Manages SafeRename operations with PDF/cover comparison."""
    
    def __init__(self, settings_manager, error_handler: ErrorHandler, image_manager: ImageManager, debug: bool = False):
        """Initialize SafeRename manager.
        
        Args:
            settings_manager: Settings manager instance
            error_handler: Error handler instance
            image_manager: Image manager instance
            debug: Enable debug logging
        """
        self.settings_manager = settings_manager
        self.error_handler = error_handler
        self.image_manager = image_manager
        self.debug = debug
        
        # Cache for comparators
        self._comparator_cache = {}
        
        # Supported comparator types
        self.comparator_types = ['qt-native', 'poppler-based']
    
    def check_rename_safety(self, file_info: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Check if rename is safe by comparing PDF cover with album cover.
        
        Args:
            file_info: File information dictionary
            meta: Album metadata dictionary
            
        Returns:
            dict: {
                'proceed': bool,  # True if rename should proceed
                'reason': str,    # Reason for the result
                'user_cancelled': bool,  # True if user explicitly cancelled
                'comparison_score': float,  # SSIM score if available
                'used_cache': bool  # True if used cached images
            }
        """
        if self.debug:
            print(f"[DEBUG] SafeRename: Starting safety check for {file_info.get('path', 'unknown')}")
        
        # Check if SafeRename is enabled
        if not self.settings_manager.get_safe_rename_enabled():
            return {
                'proceed': True,
                'reason': 'SafeRename disabled',
                'user_cancelled': False,
                'comparison_score': 0.0,
                'used_cache': False
            }
        
        # Check if file is PDF
        if not self._is_pdf_file(file_info):
            return {
                'proceed': True,
                'reason': 'Not a PDF file',
                'user_cancelled': False,
                'comparison_score': 0.0,
                'used_cache': False
            }
        
        try:
            # Get comparator
            comparator = self._get_comparator()
            if not comparator:
                return self._handle_no_comparator()
            
            # Get cover information
            cover_info = self._get_cover_info(meta)
            if not cover_info['available']:
                return {
                    'proceed': True,
                    'reason': 'No cover available for comparison',
                    'user_cancelled': False,
                    'comparison_score': 0.0,
                    'used_cache': False
                }
            
            # Perform comparison
            comparison_result = self._perform_comparison(
                file_info, cover_info, comparator
            )
            
            if comparison_result['error']:
                return self._handle_comparison_error(comparison_result['error'], file_info)
            
            # Process comparison result
            return self._process_comparison_result(
                comparison_result, file_info, meta
            )
            
        except Exception as e:
            self.error_handler.log_error(f"SafeRename check failed for {file_info.get('path', 'unknown')}", e)
            return self._handle_unexpected_error(e, file_info)
    
    def _is_pdf_file(self, file_info: Dict[str, Any]) -> bool:
        """Check if file is a PDF."""
        file_path = file_info.get('path', '')
        ext = file_info.get('ext', '')
        
        return (
            file_path.lower().endswith('.pdf') or
            ext.lower() in ['pdf', '.pdf']
        )
    
    def _get_comparator(self):
        """Get PDF comparator instance with caching."""
        threshold = self.settings_manager.get_safe_rename_threshold()
        
        # Check cache first
        cache_key = f"comparator_{threshold}"
        if cache_key in self._comparator_cache:
            return self._comparator_cache[cache_key]
        
        # Try Qt-native version first
        try:
            from pdf_cover_comparator_qt import PDFCoverComparator
            comparator = PDFCoverComparator(ssim_threshold=threshold)
            self._comparator_cache[cache_key] = comparator
            if self.debug:
                print(f"[DEBUG] SafeRename: Using Qt-native comparator")
            return comparator
        except ImportError as e:
            if self.debug:
                print(f"[DEBUG] SafeRename: Qt-native import failed: {e}")
        
        # Fallback to Poppler-based version
        try:
            from pdf_cover_comparator import PDFCoverComparator
            comparator = PDFCoverComparator(ssim_threshold=threshold)
            self._comparator_cache[cache_key] = comparator
            if self.debug:
                print(f"[DEBUG] SafeRename: Using Poppler-based comparator")
            return comparator
        except ImportError as e:
            if self.debug:
                print(f"[DEBUG] SafeRename: Poppler-based import failed: {e}")
        
        return None
    
    def _get_cover_info(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Get cover information from metadata."""
        # Check for cached cover first
        cached_path = meta.get('cover_local_path')
        if cached_path and os.path.exists(cached_path):
            return {
                'available': True,
                'url': meta.get('cover_url', ''),
                'local_path': cached_path,
                'cached': True
            }
        
        # Get cover URL
        cover_url = meta.get('cover_url', '')
        if not cover_url:
            # Try alternative fields
            cover_url = meta.get('image_url', '')
            if not cover_url and meta.get('image'):
                cover_url = meta.get('image', {}).get('original_url', '')
        
        if not cover_url:
            return {'available': False}
        
        # Normalize URL
        normalized_url = self.image_manager.normalize_url(cover_url)
        
        # Check if already cached
        cached_path = self.image_manager.get_cached_image_path(normalized_url)
        
        return {
            'available': True,
            'url': normalized_url,
            'local_path': cached_path,
            'cached': cached_path is not None
        }
    
    def _perform_comparison(self, file_info: Dict[str, Any], cover_info: Dict[str, Any], comparator) -> Dict[str, Any]:
        """Perform the actual PDF/cover comparison."""
        try:
            if self.debug:
                print(f"[DEBUG] SafeRename: Comparing {file_info['path']} with cover")
                if cover_info['cached']:
                    print(f"[DEBUG] SafeRename: Using cached cover: {cover_info['local_path']}")
                else:
                    print(f"[DEBUG] SafeRename: Will download cover: {cover_info['url']}")
            
            # Perform comparison
            result = comparator.compare(
                str(file_info['path']),
                cover_info['url'],
                cover_info.get('local_path')
            )
            
            return {
                'error': None,
                'match': result.get('match', False),
                'score': result.get('ssim_score', 0.0),
                'pdf_image_path': result.get('pdf_image_path'),
                'cover_image_path': result.get('cover_image_path'),
                'temp_files': result.get('temp_files', []),
                'used_cache': cover_info['cached']
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'match': False,
                'score': 0.0,
                'used_cache': cover_info.get('cached', False)
            }
    
    def _process_comparison_result(self, comparison_result: Dict[str, Any], file_info: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Process the comparison result and determine action."""
        if comparison_result['match']:
            # Covers match - proceed with rename
            if self.debug:
                print(f"[DEBUG] SafeRename: Cover match (score: {comparison_result['score']:.3f})")
            
            # Clean up temp files
            self._cleanup_temp_files(comparison_result.get('temp_files', []))
            
            return {
                'proceed': True,
                'reason': f'Cover match (score: {comparison_result["score"]:.3f})',
                'user_cancelled': False,
                'comparison_score': comparison_result['score'],
                'used_cache': comparison_result['used_cache']
            }
        else:
            # Covers don't match - show dialog
            if self.debug:
                print(f"[DEBUG] SafeRename: Cover mismatch (score: {comparison_result['score']:.3f})")
            
            user_choice = self._show_comparison_dialog(
                comparison_result, file_info, meta
            )
            
            # Clean up temp files
            self._cleanup_temp_files(comparison_result.get('temp_files', []))
            
            proceed = user_choice == 'proceed'
            return {
                'proceed': proceed,
                'reason': f'User {"approved" if proceed else "rejected"} mismatch (score: {comparison_result["score"]:.3f})',
                'user_cancelled': not proceed,
                'comparison_score': comparison_result['score'],
                'used_cache': comparison_result['used_cache']
            }
    
    def _show_comparison_dialog(self, comparison_result: Dict[str, Any], file_info: Dict[str, Any], meta: Dict[str, Any]) -> str:
        """Show comparison dialog to user."""
        try:
            from cover_comparison_dialog import CoverComparisonDialog
            
            # Get dialog parameters
            file_name = os.path.basename(file_info.get('path', 'Unknown File'))
            album_name = meta.get('album_name') or meta.get('name') or 'Unknown Album'
            threshold = self.settings_manager.get_safe_rename_threshold()
            
            # Create and show dialog
            dialog = CoverComparisonDialog(
                parent=None,  # Will be set by caller if needed
                pdf_image_path=comparison_result.get('pdf_image_path'),
                cover_image_path=comparison_result.get('cover_image_path'),
                ssim_score=comparison_result['score'],
                threshold=threshold,
                file_name=file_name,
                album_name=album_name
            )
            
            dialog.exec()
            user_choice = dialog.get_user_choice()
            return user_choice if user_choice is not None else 'cancel'
            
        except Exception as e:
            self.error_handler.log_error("Failed to show comparison dialog", e)
            # Default to not proceed if dialog fails
            return 'cancel'
    
    def _handle_no_comparator(self) -> Dict[str, Any]:
        """Handle case where no comparator is available."""
        message = (
            "SafeRename feature requires additional dependencies.\n"
            "Please install: pip install opencv-python scikit-image"
        )
        
        self.error_handler.show_warning("SafeRename Unavailable", message)
        
        return {
            'proceed': True,
            'reason': 'Dependencies missing',
            'user_cancelled': False,
            'comparison_score': 0.0,
            'used_cache': False
        }
    
    def _handle_comparison_error(self, error: str, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comparison errors."""
        if self.debug:
            print(f"[DEBUG] SafeRename: Comparison error: {error}")
        
        # Check if user wants to skip problematic PDFs
        if self.settings_manager.get_skip_problematic_pdfs():
            if self.debug:
                print(f"[DEBUG] SafeRename: Skipping problematic PDF (user setting)")
            return {
                'proceed': True,
                'reason': 'Skipped problematic PDF',
                'user_cancelled': False,
                'comparison_score': 0.0,
                'used_cache': False
            }
        
        # Show error dialog
        should_proceed = self.error_handler.handle_pdf_error(Exception(error), file_info.get('path', 'Unknown'))
        
        return {
            'proceed': should_proceed,
            'reason': f'PDF error: {error}',
            'user_cancelled': not should_proceed,
            'comparison_score': 0.0,
            'used_cache': False
        }
    
    def _handle_unexpected_error(self, error: Exception, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle unexpected errors."""
        if self.debug:
            print(f"[DEBUG] SafeRename: Unexpected error: {error}")
        
        # Log error
        self.error_handler.log_error(f"Unexpected SafeRename error", error)
        
        # Ask user what to do
        should_proceed = self.error_handler.handle_file_error(
            error,
            file_info.get('path', 'Unknown'),
            "SafeRename check"
        )
        
        return {
            'proceed': should_proceed,
            'reason': f'Unexpected error: {error}',
            'user_cancelled': not should_proceed,
            'comparison_score': 0.0,
            'used_cache': False
        }
    
    def _cleanup_temp_files(self, temp_files: list):
        """Clean up temporary files."""
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    if self.debug:
                        print(f"[DEBUG] SafeRename: Cleaned up temp file: {temp_file}")
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] SafeRename: Failed to clean up {temp_file}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get SafeRename usage statistics."""
        return {
            'comparator_cache_size': len(self._comparator_cache),
            'supported_comparators': self.comparator_types,
            'current_threshold': self.settings_manager.get_safe_rename_threshold(),
            'skip_problematic_enabled': self.settings_manager.get_skip_problematic_pdfs()
        }
    
    def clear_cache(self):
        """Clear comparator cache."""
        self._comparator_cache.clear()
        if self.debug:
            print("[DEBUG] SafeRename: Comparator cache cleared")
    
    def set_parent_widget(self, parent_widget):
        """Set parent widget for dialogs."""
        # This will be called from the main application
        # to set the parent for dialog display
        pass
