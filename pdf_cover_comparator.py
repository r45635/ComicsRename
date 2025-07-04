"""
PDF Cover Comparator

This module provides functionality to compare PDF covers with reference images
using structural similarity (SSIM) for the ComicsRename application.
"""

import cv2
import os
import tempfile
import requests
from pathlib import Path
from pdf2image import convert_from_path
from skimage.metrics import structural_similarity as ssim
from PIL import Image


class PDFCoverComparator:
    """
    A class for comparing PDF first pages with reference cover images.
    
    Uses structural similarity (SSIM) to determine if a PDF's first page
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

    def _extract_first_page(self, pdf_path):
        """
        Extract the first page of a PDF as an image.
        
        Args:
            pdf_path (str): Path to the PDF file.
            
        Returns:
            str: Path to the temporary image file containing the first page.
            
        Raises:
            Exception: If PDF extraction fails.
        """
        try:
            pages = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
            if not pages:
                raise Exception("No pages found in PDF")
                
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            pages[0].save(temp_img.name, "JPEG", quality=85)
            return temp_img.name
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

    def compare(self, pdf_path, cover_path_or_url):
        """
        Compare a PDF's first page with a reference cover image.
        
        Args:
            pdf_path (str): Path to the PDF file.
            cover_path_or_url (str): Path to cover image file or URL.
            
        Returns:
            dict: Contains 'ssim_score' (float), 'match' (bool), 
                 'pdf_image_path' (str), and 'cover_image_path' (str).
                 The image paths are temporary files that should be cleaned up.
                 
        Raises:
            Exception: If comparison fails due to file access or processing errors.
        """
        temp_files = []
        try:
            # Extract the first page from the PDF
            extracted_cover = self._extract_first_page(pdf_path)
            temp_files.append(extracted_cover)

            # Download if cover is a URL
            if cover_path_or_url.startswith("http://") or cover_path_or_url.startswith("https://"):
                cover_path = self._download_image(cover_path_or_url)
                temp_files.append(cover_path)
            else:
                cover_path = cover_path_or_url

            # Preprocess and compare
            img_pdf = self._load_and_resize(extracted_cover)
            img_cover = self._load_and_resize(cover_path)
            score = ssim(img_pdf, img_cover)

            return {
                "ssim_score": score,
                "match": score > self.threshold,
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
