"""
PDF Cover Comparator (Qt Native Version)

This module provides functionality to compare PDF covers with reference images
using structural similarity (SSIM) for the ComicsRename application.

This version uses Qt's native PDF rendering instead of pdf2image/Poppler,
maintaining consistency with the QuickView functionality.
"""

import cv2
import os
import tempfile
import requests
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
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


class PDFCoverComparator:
    """
    A class for comparing PDF first pages with reference cover images.
    
    Uses Qt's native PDF rendering (no Poppler dependency required) and
    structural similarity (SSIM) to determine if a PDF's first page
    matches a given cover image, helping to verify correct comic renaming.
    """
    
    def __init__(self, ssim_threshold=0.7):
        """
        Initialize the PDF cover comparator.
        
        Args:
            ssim_threshold (float): Minimum SSIM score to consider images matching.
                                  Values range from 0.0 to 1.0, where 1.0 is identical.
        """
        self.threshold = ssim_threshold
        
        if not QT_PDF_AVAILABLE:
            raise ImportError("Qt PDF modules not available. Please install PySide6 with PDF support.")
        
        # Cache for extracted PDF pages to avoid re-extraction
        self._pdf_page_cache = {}

    def _get_pdf_cache_key(self, pdf_path):
        """
        Generate a cache key for a PDF file based on its path and modification time.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            str: Cache key for the PDF file.
        """
        try:
            stat = os.stat(pdf_path)
            return f"{pdf_path}_{stat.st_mtime}_{stat.st_size}"
        except Exception:
            # Fallback to just the path if stat fails
            return pdf_path

    def _download_image(self, url):
        """
        Download an image from a URL to a temporary file.
        
        Args:
            url (str): The URL to download the image from.
            
        Returns:
            str: Path to the temporary file containing the downloaded image.
            
        Raises:
            Exception: If the download fails or returns non-200 status.
        """
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
        """
        Extract the first page of a PDF as an image using Qt's native PDF rendering.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            str: Path to the temporary image file containing the first page.
            
        Raises:
            Exception: If PDF extraction fails.
        """
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
            
            # Load the PDF using the same approach as QuickView
            load_err = pdf_doc.load(pdf_path)
            if load_err != QPdfDocument.Error.None_:
                # Provide more detailed error information
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
            page_size = pdf_doc.pagePointSize(0)  # Page 0 = first page
            
            # Check if page size is valid
            if page_size.width() <= 0 or page_size.height() <= 0:
                raise Exception(f"Invalid page size: {page_size.width()}x{page_size.height()}")
            
            # Scale factor for good quality (150 DPI equivalent)
            scale_factor = 150.0 / 72.0  # PDF points are 72 DPI
            
            # Create image size
            image_size = page_size * scale_factor
            image_size_qt = QSize(int(image_size.width()), int(image_size.height()))
            
            # Ensure minimum size
            if image_size_qt.width() < 10 or image_size_qt.height() < 10:
                raise Exception(f"Rendered image size too small: {image_size_qt.width()}x{image_size_qt.height()}")
            
            # Ensure maximum size (prevent memory issues)
            max_size = 4000
            if image_size_qt.width() > max_size or image_size_qt.height() > max_size:
                # Scale down while maintaining aspect ratio
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

    def _load_and_resize(self, path, size=(256, 256)):
        """
        Load an image, convert to grayscale, and resize it.
        
        Args:
            path (str): Path to the image file.
            size (tuple): Target size as (width, height).
            
        Returns:
            numpy.ndarray: Processed image array.
            
        Raises:
            Exception: If image loading or processing fails.
        """
        try:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise Exception(f"Could not load image: {path}")
            return cv2.resize(img, size)
        except Exception as e:
            raise Exception(f"Failed to process image {path}: {e}")

    def compare(self, pdf_path, cover_path_or_url, local_cover_path=None):
        """
        Compare a PDF's first page with a reference cover image.
        
        Args:
            pdf_path (str): Path to the PDF file.
            cover_path_or_url (str): Path to cover image file or URL.
            local_cover_path (str, optional): Path to locally cached cover image.
                                            If provided, this will be used instead of downloading.
            
        Returns:
            dict: Contains 'ssim_score' (float), 'match' (bool), 
                 'pdf_image_path' (str), and 'cover_image_path' (str).
                 The image paths are temporary files that should be cleaned up.
                 
        Raises:
            Exception: If comparison fails due to file access or processing errors.
        """
        temp_files = []
        try:
            # Extract the first page from the PDF using Qt
            extracted_cover = self._extract_first_page_qt(pdf_path)
            temp_files.append(extracted_cover)

            # Use local cached cover if available, otherwise download/use provided path
            if local_cover_path and os.path.exists(local_cover_path):
                cover_path = local_cover_path
                print(f"[DEBUG] Using cached cover image: {local_cover_path}")
            elif cover_path_or_url.startswith("http://") or cover_path_or_url.startswith("https://"):
                print(f"[DEBUG] Downloading cover image from: {cover_path_or_url}")
                cover_path = self._download_image(cover_path_or_url)
                temp_files.append(cover_path)
            else:
                cover_path = cover_path_or_url

            # Preprocess and compare
            img_pdf = self._load_and_resize(extracted_cover)
            img_cover = self._load_and_resize(cover_path)
            score = ssim(img_pdf, img_cover)
            # If ssim returns a tuple (score, diff), extract the score
            if isinstance(score, tuple):
                score_value = score[0]
            else:
                score_value = score

            return {
                "ssim_score": score_value,
                "match": score_value > self.threshold,
                "pdf_image_path": extracted_cover,
                "cover_image_path": cover_path,
                "temp_files": temp_files  # For cleanup by caller
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
        """
        Clean up temporary files created during comparison.
        
        Args:
            temp_files (list): List of temporary file paths to remove.
        """
        for f in temp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass  # Ignore cleanup errors
