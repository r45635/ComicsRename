#!/usr/bin/env python3
"""
Test script for Safe Rename feature (Qt-native version)

This script tests the PDF cover comparison functionality using Qt's native
PDF rendering instead of Poppler, matching the QuickView implementation.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dependencies():
    """Test if all required dependencies are available"""
    print("Testing Safe Rename dependencies (Qt-native version)...")
    
    try:
        import cv2
        print("✓ opencv-python is available")
    except ImportError:
        print("✗ opencv-python is missing - install with: pip install opencv-python")
        return False
    
    try:
        from skimage.metrics import structural_similarity as ssim
        print("✓ scikit-image is available")
    except ImportError:
        print("✗ scikit-image is missing - install with: pip install scikit-image")
        return False
    
    try:
        from PySide6.QtPdf import QPdfDocument
        print("✓ Qt PDF modules are available")
    except ImportError:
        print("✗ Qt PDF modules are missing - ensure PySide6 with PDF support is installed")
        return False
    
    try:
        from pdf_cover_comparator_qt import PDFCoverComparator
        print("✓ PDFCoverComparator (Qt-native) is available")
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
    print("💡 This version uses Qt's native PDF rendering (same as QuickView)")
    print("💡 No Poppler dependency required!")
    return True

def test_comparator(pdf_path=None, cover_url=None):
    """Test the PDF cover comparator with sample files"""
    if not test_dependencies():
        return False
    
    from pdf_cover_comparator_qt import PDFCoverComparator
    
    if not pdf_path:
        print("No PDF file provided for testing")
        return True
    
    if not cover_url:
        print("No cover URL provided for testing")
        return True
    
    try:
        print(f"\nTesting Qt-native comparison...")
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
        print("✓ Qt-native comparison test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Qt-native comparison test failed: {e}")
        return False

def compare_implementations():
    """Compare the Qt-native vs Poppler implementations"""
    print("\n" + "="*50)
    print("IMPLEMENTATION COMPARISON")
    print("="*50)
    
    print("\n🚀 Qt-Native Version (NEW):")
    print("  ✓ Uses Qt's QPdfDocument.render() - same as QuickView")
    print("  ✓ No external dependencies (Poppler not needed)")
    print("  ✓ Consistent with existing codebase")
    print("  ✓ Cross-platform compatibility")
    print("  ✓ High-quality rendering")
    
    print("\n📦 Poppler Version (OLD):")
    print("  ➖ Uses pdf2image library")
    print("  ➖ Requires Poppler installation")
    print("  ➖ Additional system dependency")
    print("  ➖ Inconsistent with QuickView approach")
    
    print("\n💡 Recommendation: Use Qt-native version for consistency!")

def main():
    """Main debug function"""
    print("Safe Rename Qt-Native Debug Script")
    print("=" * 50)
    
    success = True
    
    # Test dependencies
    if not test_dependencies():
        success = False
    
    # Show implementation comparison
    compare_implementations()
    
    if success:
        print("\n✓ Qt-native Safe Rename implementation is ready!")
    else:
        print("\n✗ Some issues found. Check the implementation.")
    
    print("\nQuickView Consistency Notes:")
    print("1. Both QuickView and Safe Rename now use Qt's native PDF rendering")
    print("2. No external PDF libraries required (Poppler, pdf2image)")
    print("3. Consistent rendering quality and behavior")
    print("4. Simplified dependency management")
    
    if len(sys.argv) > 2:
        print(f"\nTesting with provided files...")
        test_comparator(sys.argv[1], sys.argv[2])
    else:
        print("\nTo test with actual files, run:")
        print("python test_safe_rename_qt.py <pdf_file> <cover_url>")

if __name__ == "__main__":
    main()
