"""
Enhanced PDF Cover Comparator with improved image similarity detection.

This module provides advanced functionality to compare PDF covers with reference images
using multiple metrics and adaptive thresholding to handle quality differences.
"""

import cv2
import os
import tempfile
import requests
import numpy as np
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse
from PIL import Image

# Qt imports for PDF rendering
try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtCore import Qt
    QT_PDF_AVAILABLE = True
except ImportError:
    QT_PDF_AVAILABLE = False


class EnhancedPDFCoverComparator:
    """
    Enhanced PDF cover comparator with improved similarity detection.
    
    Features:
    - Multiple similarity metrics (SSIM, MSE, Histogram comparison)
    - Adaptive thresholding based on image quality
    - Noise filtering to handle compression artifacts
    - Quality-aware comparison
    """
    
    def __init__(self, ssim_threshold=0.65, use_adaptive_threshold=True, debug=False):
        """
        Initialize the enhanced PDF cover comparator.
        
        Args:
            ssim_threshold (float): Base SSIM threshold (will be adjusted adaptively)
            use_adaptive_threshold (bool): Enable adaptive thresholding
            debug (bool): Enable debug output
        """
        self.base_threshold = ssim_threshold
        self.use_adaptive_threshold = use_adaptive_threshold
        self.debug = debug
        
        if not QT_PDF_AVAILABLE:
            raise ImportError("Qt PDF modules not available. Please install PySide6 with PDF support.")
        
        # Cache for extracted PDF pages
        self._pdf_page_cache = {}
        
        # Quality assessment parameters
        self.quality_thresholds = {
            'low': 0.4,      # Very compressed/low quality
            'medium': 0.6,   # Moderate quality
            'high': 0.8      # High quality
        }
        
        # Adaptive thresholds based on detected quality
        self.adaptive_thresholds = {
            'low': 0.55,     # More lenient for low quality images
            'medium': 0.65,  # Standard threshold
            'high': 0.75     # Stricter for high quality images
        }

    def _debug_print(self, message):
        """Print debug message if debug mode is enabled."""
        if self.debug:
            print(f"[DEBUG] Enhanced Comparator: {message}")

    def _assess_image_quality(self, image_path):
        """
        Assess the quality of an image based on various metrics.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Quality assessment results
        """
        try:
            # Load image
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return {'quality': 'unknown', 'score': 0.0}
            
            # Calculate Laplacian variance (sharpness)
            laplacian_var = cv2.Laplacian(img, cv2.CV_64F).var()
            
            # Calculate gradient magnitude (edge strength)
            grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2).mean()
            
            # Normalize and combine metrics
            quality_score = (laplacian_var / 1000.0 + gradient_magnitude / 100.0) / 2.0
            quality_score = min(quality_score, 1.0)  # Cap at 1.0
            
            # Classify quality
            if quality_score < self.quality_thresholds['low']:
                quality_level = 'low'
            elif quality_score < self.quality_thresholds['medium']:
                quality_level = 'medium'
            else:
                quality_level = 'high'
            
            self._debug_print(f"Image quality assessment: {quality_level} (score: {quality_score:.3f})")
            
            return {
                'quality': quality_level,
                'score': quality_score,
                'laplacian_var': laplacian_var,
                'gradient_magnitude': gradient_magnitude
            }
            
        except Exception as e:
            self._debug_print(f"Quality assessment failed: {e}")
            return {'quality': 'unknown', 'score': 0.0}

    def _preprocess_image(self, image_path, target_size=(256, 256)):
        """
        Preprocess image with noise reduction and normalization.
        
        Args:
            image_path (str): Path to the image file
            target_size (tuple): Target size for resizing
            
        Returns:
            numpy.ndarray: Preprocessed image
        """
        try:
            # Load image
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise Exception(f"Could not load image: {image_path}")
            
            # Apply noise reduction
            img_denoised = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
            
            # Resize
            img_resized = cv2.resize(img_denoised, target_size)
            
            # Normalize histogram
            img_normalized = cv2.equalizeHist(img_resized)
            
            self._debug_print(f"Preprocessed image: {image_path}")
            
            return img_normalized
            
        except Exception as e:
            # Fallback to simple preprocessing
            self._debug_print(f"Advanced preprocessing failed, using basic: {e}")
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise Exception(f"Could not load image: {image_path}")
            return cv2.resize(img, target_size)

    def _calculate_histogram_similarity(self, img1, img2):
        """
        Calculate histogram similarity between two images.
        
        Args:
            img1, img2 (numpy.ndarray): Images to compare
            
        Returns:
            float: Histogram correlation (0.0 to 1.0)
        """
        try:
            # Calculate histograms
            hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
            
            # Calculate correlation
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Ensure result is in [0, 1] range
            correlation = max(0.0, min(1.0, correlation))
            
            self._debug_print(f"Histogram correlation: {correlation:.3f}")
            
            return correlation
            
        except Exception as e:
            self._debug_print(f"Histogram calculation failed: {e}")
            return 0.0

    def _calculate_feature_similarity(self, img1, img2):
        """
        Calculate feature-based similarity using corner detection.
        
        Args:
            img1, img2 (numpy.ndarray): Images to compare
            
        Returns:
            float: Feature similarity score (0.0 to 1.0)
        """
        try:
            # Use Harris corner detection as a simpler alternative
            corners1 = cv2.goodFeaturesToTrack(img1, maxCorners=100, qualityLevel=0.01, minDistance=10)
            corners2 = cv2.goodFeaturesToTrack(img2, maxCorners=100, qualityLevel=0.01, minDistance=10)
            
            if corners1 is None or corners2 is None:
                self._debug_print("No corners found in one or both images")
                return 0.0
            
            # Simple feature count comparison
            count1 = len(corners1)
            count2 = len(corners2)
            
            if count1 == 0 or count2 == 0:
                return 0.0
            
            # Calculate similarity based on feature count ratio
            similarity = min(count1, count2) / max(count1, count2)
            
            self._debug_print(f"Feature similarity: {similarity:.3f} (corners: {count1} vs {count2})")
            
            return similarity
            
        except Exception as e:
            self._debug_print(f"Feature matching failed: {e}")
            return 0.0

    def _get_adaptive_threshold(self, pdf_quality, cover_quality):
        """
        Calculate adaptive threshold based on image qualities.
        
        Args:
            pdf_quality (dict): PDF image quality assessment
            cover_quality (dict): Cover image quality assessment
            
        Returns:
            float: Adaptive threshold value
        """
        if not self.use_adaptive_threshold:
            return self.base_threshold
        
        # Use the lower quality level for threshold selection
        pdf_level = pdf_quality.get('quality', 'medium')
        cover_level = cover_quality.get('quality', 'medium')
        
        # Use the more lenient threshold if either image is low quality
        if pdf_level == 'low' or cover_level == 'low':
            threshold = self.adaptive_thresholds['low']
        elif pdf_level == 'high' and cover_level == 'high':
            threshold = self.adaptive_thresholds['high']
        else:
            threshold = self.adaptive_thresholds['medium']
        
        self._debug_print(f"Adaptive threshold: {threshold:.3f} (PDF: {pdf_level}, Cover: {cover_level})")
        
        return threshold

    def _download_image(self, url):
        """Download an image from a URL to a temporary file."""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"Failed to download image: {url} (Status: {response.status_code})")
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(response.content)
            temp_file.close()
            return temp_file.name
        except requests.RequestException as e:
            raise Exception(f"Network error downloading image: {url} - {e}")

    def _extract_first_page_qt(self, pdf_path):
        """Extract the first page of a PDF as an image using Qt's native PDF rendering."""
        try:
            # Check if file exists and is readable
            if not os.path.exists(pdf_path):
                raise Exception(f"PDF file does not exist: {pdf_path}")
            
            if not os.path.isfile(pdf_path):
                raise Exception(f"Path is not a file: {pdf_path}")
            
            if not os.access(pdf_path, os.R_OK):
                raise Exception(f"PDF file is not readable: {pdf_path}")
            
            # Check file size
            file_size = os.path.getsize(pdf_path)
            if file_size == 0:
                raise Exception(f"PDF file is empty: {pdf_path}")
            
            # Create PDF document
            pdf_doc = QPdfDocument()
            
            # Load the PDF
            load_err = pdf_doc.load(pdf_path)
            if load_err != QPdfDocument.Error.None_:
                error_messages = {
                    QPdfDocument.Error.FileNotFound: "PDF file not found",
                    QPdfDocument.Error.InvalidFileFormat: "Invalid PDF file format",
                    QPdfDocument.Error.IncorrectPassword: "PDF requires password",
                    QPdfDocument.Error.UnsupportedSecurityScheme: "Unsupported PDF security scheme",
                }
                error_msg = error_messages.get(load_err, f"PDF error: {load_err}")
                raise Exception(f"Failed to load PDF: {pdf_path} - {error_msg}")
            
            if pdf_doc.pageCount() == 0:
                raise Exception("PDF has no pages")
            
            # Get first page size
            page_size = pdf_doc.pagePointSize(0)
            
            # Check if page size is valid
            if page_size.width() <= 0 or page_size.height() <= 0:
                raise Exception(f"Invalid page size: {page_size.width()}x{page_size.height()}")
            
            # Scale factor for good quality (150 DPI equivalent)
            scale_factor = 150.0 / 72.0
            
            # Create image size
            image_size = page_size * scale_factor
            image_size_qt = QSize(int(image_size.width()), int(image_size.height()))
            
            # Ensure minimum size
            if image_size_qt.width() < 10 or image_size_qt.height() < 10:
                raise Exception(f"Rendered image size too small: {image_size_qt.width()}x{image_size_qt.height()}")
            
            # Ensure maximum size (prevent memory issues)
            max_size = 4000
            if image_size_qt.width() > max_size or image_size_qt.height() > max_size:
                if image_size_qt.width() > image_size_qt.height():
                    scale_down = max_size / image_size_qt.width()
                else:
                    scale_down = max_size / image_size_qt.height()
                image_size_qt = QSize(int(image_size_qt.width() * scale_down), 
                                     int(image_size_qt.height() * scale_down))
            
            # Render the first page
            try:
                from PySide6.QtPdf import QPdfDocumentRenderOptions
                render_options = QPdfDocumentRenderOptions()
                rendered_image = pdf_doc.render(0, image_size_qt, render_options)
            except ImportError:
                # Fallback without render options
                rendered_image = pdf_doc.render(0, image_size_qt)
            
            if rendered_image.isNull():
                raise Exception("Failed to render PDF page")
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            temp_file.close()
            
            if not rendered_image.save(temp_file.name):
                raise Exception("Failed to save rendered page")
            
            return temp_file.name
            
        except Exception as e:
            raise Exception(f"Failed to extract first page from PDF: {e}")

    def compare(self, pdf_path, cover_path_or_url, local_cover_path=None):
        """
        Enhanced comparison with multiple metrics and adaptive thresholding.
        
        Args:
            pdf_path (str): Path to the PDF file
            cover_path_or_url (str): Path to cover image file or URL
            local_cover_path (str, optional): Path to locally cached cover image
            
        Returns:
            dict: Enhanced comparison results with multiple metrics
        """
        temp_files = []
        try:
            # Extract the first page from the PDF
            extracted_cover = self._extract_first_page_qt(pdf_path)
            temp_files.append(extracted_cover)

            # Use local cached cover if available, otherwise download/use provided path
            if local_cover_path and os.path.exists(local_cover_path):
                cover_path = local_cover_path
                self._debug_print(f"Using cached cover image: {local_cover_path}")
            elif cover_path_or_url.startswith("http://") or cover_path_or_url.startswith("https://"):
                self._debug_print(f"Downloading cover image from: {cover_path_or_url}")
                cover_path = self._download_image(cover_path_or_url)
                temp_files.append(cover_path)
            else:
                cover_path = cover_path_or_url

            # Assess image qualities
            pdf_quality = self._assess_image_quality(extracted_cover)
            cover_quality = self._assess_image_quality(cover_path)
            
            # Get adaptive threshold
            adaptive_threshold = self._get_adaptive_threshold(pdf_quality, cover_quality)

            # Preprocess images
            img_pdf = self._preprocess_image(extracted_cover)
            img_cover = self._preprocess_image(cover_path)

            # Calculate multiple similarity metrics
            ssim_score = ssim(img_pdf, img_cover)
            if isinstance(ssim_score, tuple):
                ssim_score = ssim_score[0]
            
            mse_score = mse(img_pdf, img_cover)
            mse_similarity = 1.0 / (1.0 + mse_score / 10000.0)  # Convert MSE to similarity
            
            histogram_similarity = self._calculate_histogram_similarity(img_pdf, img_cover)
            feature_similarity = self._calculate_feature_similarity(img_pdf, img_cover)
            
            # Calculate combined score with weighted average
            weights = {
                'ssim': 0.4,
                'mse': 0.2,
                'histogram': 0.2,
                'features': 0.2
            }
            
            combined_score = (
                weights['ssim'] * ssim_score +
                weights['mse'] * mse_similarity +
                weights['histogram'] * histogram_similarity +
                weights['features'] * feature_similarity
            )
            
            # Determine if images match using adaptive threshold
            ssim_match = ssim_score > adaptive_threshold
            combined_match = combined_score > adaptive_threshold
            
            # Use combined score for final decision, but provide both
            final_match = combined_match or (ssim_match and combined_score > (adaptive_threshold * 0.9))
            
            self._debug_print(f"Similarity metrics - SSIM: {ssim_score:.3f}, MSE: {mse_similarity:.3f}, "
                            f"Histogram: {histogram_similarity:.3f}, Features: {feature_similarity:.3f}")
            self._debug_print(f"Combined score: {combined_score:.3f}, Threshold: {adaptive_threshold:.3f}, Match: {final_match}")
            
            return {
                "ssim_score": ssim_score,
                "mse_similarity": mse_similarity,
                "histogram_similarity": histogram_similarity,
                "feature_similarity": feature_similarity,
                "combined_score": combined_score,
                "adaptive_threshold": adaptive_threshold,
                "match": final_match,
                "ssim_match": ssim_match,
                "combined_match": combined_match,
                "pdf_quality": pdf_quality,
                "cover_quality": cover_quality,
                "pdf_image_path": extracted_cover,
                "cover_image_path": cover_path,
                "temp_files": temp_files
            }

        except Exception as e:
            # Clean up on error
            for f in temp_files:
                try:
                    os.remove(f)
                except Exception:
                    pass
            raise e

    def cleanup_temp_files(self, temp_files):
        """Clean up temporary files created during comparison."""
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass
