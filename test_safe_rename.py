#!/usr/bin/env python3
"""
Test script for Safe Rename feature

This script tests the PDF cover comparison functionality without requiring
a full GUI application setup.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dependencies():
    """Test if all required dependencies are available"""
    print("Testing Safe Rename dependencies...")
    
    try:
        import cv2
        print("✓ opencv-python is available")
    except ImportError:
        print("✗ opencv-python is missing - install with: pip install opencv-python")
        return False
    
    try:
        from pdf2image import convert_from_path
        print("✓ pdf2image is available")
    except ImportError:
        print("✗ pdf2image is missing - install with: pip install pdf2image")
        return False
    
    try:
        from skimage.metrics import structural_similarity as ssim
        print("✓ scikit-image is available")
    except ImportError:
        print("✗ scikit-image is missing - install with: pip install scikit-image")
        return False
    
    try:
        from pdf_cover_comparator import PDFCoverComparator
        print("✓ PDFCoverComparator is available")
    except ImportError as e:
        print(f"✗ PDFCoverComparator import failed: {e}")
        return False
    
    try:
        from cover_comparison_dialog import CoverComparisonDialog
        print("✓ CoverComparisonDialog is available")
    except ImportError as e:
        print(f"✗ CoverComparisonDialog import failed: {e}")
        return False
    
    print("\nAll dependencies are available! ✓")
    return True

def test_comparator(pdf_path=None, cover_url=None):
    """Test the PDF cover comparator with sample files"""
    if not test_dependencies():
        return False
    
    from pdf_cover_comparator import PDFCoverComparator
    
    if not pdf_path:
        print("No PDF file provided for testing")
        return True
    
    if not cover_url:
        print("No cover URL provided for testing")
        return True
    
    try:
        print(f"\nTesting comparison...")
        print(f"PDF: {pdf_path}")
        print(f"Cover: {cover_url}")
        
        comparator = PDFCoverComparator(ssim_threshold=0.7)
        result = comparator.compare(pdf_path, cover_url)
        
        print(f"SSIM Score: {result['ssim_score']:.3f}")
        print(f"Match: {result['match']}")
        print(f"PDF Image: {result.get('pdf_image_path', 'N/A')}")
        print(f"Cover Image: {result.get('cover_image_path', 'N/A')}")
        
        # Clean up
        comparator.cleanup_temp_files(result.get('temp_files', []))
        print("✓ Comparison test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Comparison test failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        test_comparator(sys.argv[1], sys.argv[2])
    else:
        test_dependencies()
        print("\nTo test with actual files, run:")
        print("python test_safe_rename.py <pdf_file> <cover_url>")
