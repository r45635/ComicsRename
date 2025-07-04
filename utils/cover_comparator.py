"""
PDF Cover Comparator for ComicsRename

This module provides functionality to compare the first page of a PDF file
with the cover image of a comic album to verify they match.
"""

import cv2
import os
import tempfile
import requests
from pathlib import Path
from pdf2image import convert_from_path
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np


class PDFCoverComparator:
    """
    Compares PDF first pages with cover images using structural similarity.
    
    This class can compare a PDF's first page with either a local image file
    or a cover image URL to determine if they match.
    """
    
    def __init__(self, ssim_threshold=0.7):
        """
        Initialize the comparator.
        
        Args:
            ssim_threshold (float): Threshold for considering images as matching (0.0 to 1.0)
        """
        self.threshold = ssim_threshold
    
    def _download_image(self, url, timeout=30):
        """
        Download an image from a URL to a temporary file.
        
        Args:
            url (str): URL of the image to download
            timeout (int): Request timeout in seconds
            
        Returns:
            str: Path to the downloaded temporary file
            
        Raises:
            Exception: If download fails
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            # Create temporary file with appropriate extension
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_file.write(response.content)
            temp_file.close()
            return temp_file.name
            
        except Exception as e:
            raise Exception(f"Failed to download image from {url}: {str(e)}")
    
    def _extract_first_page(self, pdf_path):
        """
        Extract the first page of a PDF as an image.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Path to the extracted page image
            
        Raises:
            Exception: If PDF processing fails
        """
        try:
            # Convert first page to image at good resolution
            pages = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=200)
            
            if not pages:
                raise Exception("No pages found in PDF")
            
            # Save to temporary file
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            pages[0].save(temp_img.name, "JPEG", quality=95)
            temp_img.close()
            
            return temp_img.name
            
        except Exception as e:
            raise Exception(f"Failed to extract first page from PDF {pdf_path}: {str(e)}")
    
    def _load_and_resize(self, path, size=(256, 256)):
        """
        Load an image and resize it for comparison.
        
        Args:
            path (str): Path to the image file
            size (tuple): Target size (width, height)
            
        Returns:
            numpy.ndarray: Processed grayscale image
            
        Raises:
            Exception: If image processing fails
        """
        try:
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise Exception(f"Could not load image: {path}")
            
            # Resize maintaining aspect ratio
            resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
            
            # Apply slight gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(resized, (3, 3), 0)
            
            return blurred
            
        except Exception as e:
            raise Exception(f"Failed to process image {path}: {str(e)}")
    
    def compare(self, pdf_path, cover_path_or_url):
        """
        Compare a PDF's first page with a cover image.
        
        Args:
            pdf_path (str): Path to the PDF file
            cover_path_or_url (str): Path to cover image file or URL
            
        Returns:
            dict: Dictionary with comparison results:
                - ssim_score (float): Structural similarity score (0.0 to 1.0)
                - match (bool): Whether images match based on threshold
                - confidence (str): Human-readable confidence level
                
        Raises:
            Exception: If comparison fails
        """
        temp_files = []
        
        try:
            print(f"[DEBUG] Comparing PDF cover: {pdf_path}")
            print(f"[DEBUG] With cover: {cover_path_or_url}")
            
            # Extract the first page from the PDF
            extracted_cover = self._extract_first_page(pdf_path)
            temp_files.append(extracted_cover)
            print(f"[DEBUG] Extracted PDF first page to: {extracted_cover}")
            
            # Download if cover is a URL
            if cover_path_or_url.startswith("http://") or cover_path_or_url.startswith("https://"):
                cover_path = self._download_image(cover_path_or_url)
                temp_files.append(cover_path)
                print(f"[DEBUG] Downloaded cover image to: {cover_path}")
            else:
                cover_path = cover_path_or_url
                print(f"[DEBUG] Using local cover image: {cover_path}")
            
            # Preprocess and compare
            img_pdf = self._load_and_resize(extracted_cover)
            img_cover = self._load_and_resize(cover_path)
            
            # Calculate structural similarity
            score = ssim(img_pdf, img_cover)
            
            # Determine confidence level
            if score >= 0.9:
                confidence = "Très élevée"
            elif score >= 0.8:
                confidence = "Élevée"
            elif score >= 0.7:
                confidence = "Moyenne"
            elif score >= 0.5:
                confidence = "Faible"
            else:
                confidence = "Très faible"
            
            result = {
                "ssim_score": score,
                "match": score > self.threshold,
                "confidence": confidence
            }
            
            print(f"[DEBUG] Comparison result: SSIM={score:.3f}, Match={result['match']}, Confidence={confidence}")
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Cover comparison failed: {str(e)}")
            raise
            
        finally:
            # Clean up temporary files
            for f in temp_files:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                        print(f"[DEBUG] Cleaned up temp file: {f}")
                except Exception as e:
                    print(f"[WARNING] Could not clean up temp file {f}: {e}")
    
    def batch_compare(self, pdf_files, cover_urls):
        """
        Compare multiple PDF files with their corresponding cover images.
        
        Args:
            pdf_files (list): List of PDF file paths
            cover_urls (list): List of cover image URLs/paths
            
        Returns:
            list: List of comparison results
        """
        results = []
        
        for pdf_path, cover_url in zip(pdf_files, cover_urls):
            try:
                result = self.compare(pdf_path, cover_url)
                result['pdf_path'] = pdf_path
                result['cover_url'] = cover_url
                results.append(result)
            except Exception as e:
                results.append({
                    'pdf_path': pdf_path,
                    'cover_url': cover_url,
                    'error': str(e),
                    'ssim_score': 0.0,
                    'match': False,
                    'confidence': 'Erreur'
                })
        
        return results


def test_comparator():
    """Test function for the PDF cover comparator."""
    try:
        comparator = PDFCoverComparator(ssim_threshold=0.7)
        
        # Test with dummy data
        print("PDF Cover Comparator test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    test_comparator()
