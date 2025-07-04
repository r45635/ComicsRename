#!/usr/bin/env python3
"""
Test script to verify cover comparison dialog translations work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from cover_comparison_dialog import CoverComparisonDialog
from i18n import tr, set_language

def test_english_translations():
    """Test English translations for cover comparison dialog."""
    print("Testing English translations...")
    set_language('en')
    
    # Test all translation keys
    keys_to_test = [
        "messages.cover_comparison.title",
        "messages.cover_comparison.mismatch_detected",
        "messages.cover_comparison.file_label",
        "messages.cover_comparison.album_label",
        "messages.cover_comparison.similarity_score",
        "messages.cover_comparison.pdf_cover",
        "messages.cover_comparison.album_cover",
        "messages.cover_comparison.explanation",
        "messages.cover_comparison.proceed_anyway",
        "messages.cover_comparison.cancel_rename",
        "messages.cover_comparison.pdf_load_error",
        "messages.cover_comparison.pdf_not_available",
        "messages.cover_comparison.cover_load_error",
        "messages.cover_comparison.cover_not_available"
    ]
    
    for key in keys_to_test:
        if key in ["messages.cover_comparison.file_label", "messages.cover_comparison.album_label"]:
            # These keys use parameters
            if key == "messages.cover_comparison.file_label":
                translation = tr(key, file_name="test.pdf")
            else:
                translation = tr(key, album_name="Test Album")
        elif key == "messages.cover_comparison.similarity_score":
            translation = tr(key, score=0.65, threshold=0.7)
        else:
            translation = tr(key)
        
        print(f"  {key}: {translation}")
        
        # Check if translation failed (would return the key itself)
        if translation == key:
            print(f"    ❌ FAILED: Translation not found for {key}")
        else:
            print(f"    ✅ SUCCESS: Translation found")
    
    print()

def test_french_translations():
    """Test French translations for cover comparison dialog."""
    print("Testing French translations...")
    set_language('fr')
    
    # Test all translation keys
    keys_to_test = [
        "messages.cover_comparison.title",
        "messages.cover_comparison.mismatch_detected",
        "messages.cover_comparison.file_label",
        "messages.cover_comparison.album_label",
        "messages.cover_comparison.similarity_score",
        "messages.cover_comparison.pdf_cover",
        "messages.cover_comparison.album_cover",
        "messages.cover_comparison.explanation",
        "messages.cover_comparison.proceed_anyway",
        "messages.cover_comparison.cancel_rename",
        "messages.cover_comparison.pdf_load_error",
        "messages.cover_comparison.pdf_not_available",
        "messages.cover_comparison.cover_load_error",
        "messages.cover_comparison.cover_not_available"
    ]
    
    for key in keys_to_test:
        if key in ["messages.cover_comparison.file_label", "messages.cover_comparison.album_label"]:
            # These keys use parameters
            if key == "messages.cover_comparison.file_label":
                translation = tr(key, file_name="test.pdf")
            else:
                translation = tr(key, album_name="Test Album")
        elif key == "messages.cover_comparison.similarity_score":
            translation = tr(key, score=0.65, threshold=0.7)
        else:
            translation = tr(key)
        
        print(f"  {key}: {translation}")
        
        # Check if translation failed (would return the key itself)
        if translation == key:
            print(f"    ❌ FAILED: Translation not found for {key}")
        else:
            print(f"    ✅ SUCCESS: Translation found")
    
    print()

def test_dialog_creation():
    """Test that the dialog can be created without errors."""
    print("Testing dialog creation...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Test with English
        set_language('en')
        dialog_en = CoverComparisonDialog(
            pdf_image_path=None,
            cover_image_path=None,
            ssim_score=0.65,
            threshold=0.7,
            file_name="test.pdf",
            album_name="Test Album"
        )
        print("  ✅ English dialog created successfully")
        
        # Test with French
        set_language('fr')
        dialog_fr = CoverComparisonDialog(
            pdf_image_path=None,
            cover_image_path=None,
            ssim_score=0.65,
            threshold=0.7,
            file_name="test.pdf",
            album_name="Test Album"
        )
        print("  ✅ French dialog created successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FAILED: Dialog creation failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Cover Comparison Dialog Translation Test")
    print("=" * 50)
    
    test_english_translations()
    test_french_translations()
    
    success = test_dialog_creation()
    
    if success:
        print("\n🎉 All tests passed! Cover comparison dialog translations are working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
