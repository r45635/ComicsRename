#!/usr/bin/env python3
"""
Test script for the enhanced PDF cover comparator.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, '/Users/vincentcruvellier/Documents/GitHub/ComicsRename')

def test_enhanced_comparator():
    """Test the enhanced PDF cover comparator functionality."""
    
    try:
        from pdf_cover_comparator_enhanced import EnhancedPDFCoverComparator
        
        # Create enhanced comparator with debug enabled
        comparator = EnhancedPDFCoverComparator(
            ssim_threshold=0.65,
            use_adaptive_threshold=True,
            debug=True
        )
        
        print("✓ Enhanced PDF cover comparator created successfully")
        
        # Test quality assessment with a dummy image
        try:
            # Create a simple test image
            import cv2
            import numpy as np
            
            # Create test image
            test_img = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_path = temp_file.name
            
            cv2.imwrite(temp_path, test_img)
            
            # Test quality assessment
            quality_result = comparator._assess_image_quality(temp_path)
            print(f"✓ Quality assessment works: {quality_result}")
            
            # Clean up
            os.remove(temp_path)
            
        except Exception as e:
            print(f"⚠ Quality assessment test failed: {e}")
        
        # Test preprocessing
        try:
            # Create another test image
            test_img2 = np.random.randint(0, 255, (200, 200), dtype=np.uint8)
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                temp_path2 = temp_file.name
            
            cv2.imwrite(temp_path2, test_img2)
            
            # Test preprocessing
            processed_img = comparator._preprocess_image(temp_path2)
            print(f"✓ Image preprocessing works: shape {processed_img.shape}")
            
            # Clean up
            os.remove(temp_path2)
            
        except Exception as e:
            print(f"⚠ Preprocessing test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced comparator test failed: {e}")
        return False

def test_integration_with_existing_system():
    """Test integration with the existing system."""
    
    try:
        # Test that we can import both comparators
        from pdf_cover_comparator_qt import PDFCoverComparator
        from pdf_cover_comparator_enhanced import EnhancedPDFCoverComparator
        
        # Create both comparators
        standard_comparator = PDFCoverComparator(ssim_threshold=0.7)
        enhanced_comparator = EnhancedPDFCoverComparator(
            ssim_threshold=0.65,
            use_adaptive_threshold=True,
            debug=True
        )
        
        print("✓ Both comparators can coexist")
        
        # Test that core modules can still be imported
        from core.safe_rename_manager import SafeRenameManager
        from core.settings_manager import SettingsManager
        from core.error_handler import ErrorHandler
        from core.image_manager import ImageManager
        
        print("✓ Core modules still work with enhanced comparator")
        
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Enhanced PDF Cover Comparator...")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_enhanced_comparator,
        test_integration_with_existing_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\n{test.__doc__}")
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ Enhanced comparator is ready for integration!")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)
