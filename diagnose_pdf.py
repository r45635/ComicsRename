#!/usr/bin/env python3
"""
PDF Diagnostic Script

This script helps diagnose PDF loading issues for the Safe Rename feature.
"""

import sys
import os
from pathlib import Path

def diagnose_pdf(pdf_path):
    """Diagnose PDF file for potential issues"""
    print(f"🔍 Diagnosing PDF: {pdf_path}")
    print("=" * 60)
    
    # Basic file checks
    if not os.path.exists(pdf_path):
        print("❌ File does not exist")
        return False
    
    if not os.path.isfile(pdf_path):
        print("❌ Path is not a file")
        return False
    
    if not os.access(pdf_path, os.R_OK):
        print("❌ File is not readable")
        return False
    
    file_size = os.path.getsize(pdf_path)
    print(f"✅ File exists and is readable")
    print(f"📁 File size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
    
    if file_size == 0:
        print("❌ File is empty")
        return False
    
    # Check file extension
    ext = Path(pdf_path).suffix.lower()
    print(f"📄 File extension: {ext}")
    
    # Basic PDF header check
    try:
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            if header.startswith(b'%PDF-'):
                version = header[5:8].decode('ascii', errors='ignore')
                print(f"✅ Valid PDF header found (version: {version})")
            else:
                print(f"❌ Invalid PDF header: {header}")
                return False
    except Exception as e:
        print(f"❌ Error reading file header: {e}")
        return False
    
    # Test Qt PDF loading
    try:
        from PySide6.QtPdf import QPdfDocument
        from PySide6.QtCore import QSize
        
        print("\n🔍 Testing Qt PDF loading...")
        
        pdf_doc = QPdfDocument()
        load_err = pdf_doc.load(pdf_path)
        
        if load_err == QPdfDocument.Error.None_:
            print("✅ Qt PDF loading successful")
            print(f"📄 Page count: {pdf_doc.pageCount()}")
            
            if pdf_doc.pageCount() > 0:
                page_size = pdf_doc.pagePointSize(0)
                print(f"📏 First page size: {page_size.width():.1f} x {page_size.height():.1f} points")
                
                # Test rendering
                try:
                    image_size = QSize(200, 200)  # Small test size
                    rendered_image = pdf_doc.render(0, image_size)
                    
                    if not rendered_image.isNull():
                        print("✅ PDF rendering successful")
                        print(f"🖼️ Rendered image size: {rendered_image.width()} x {rendered_image.height()}")
                        return True
                    else:
                        print("❌ PDF rendering failed (null image)")
                        return False
                        
                except Exception as e:
                    print(f"❌ PDF rendering error: {e}")
                    return False
            else:
                print("❌ PDF has no pages")
                return False
                
        else:
            print(f"❌ Qt PDF loading failed with error: {load_err}")
            
            # Try to get error details
            error_messages = {
                QPdfDocument.Error.FileNotFound: "File not found",
                QPdfDocument.Error.InvalidFileFormat: "Invalid PDF file format",
                QPdfDocument.Error.IncorrectPassword: "PDF requires password",
                QPdfDocument.Error.UnsupportedSecurityScheme: "Unsupported PDF security scheme",
            }
            error_msg = error_messages.get(load_err, f"Unknown error: {load_err}")
            print(f"❌ PDF error: {error_msg}")
            
            return False
            
    except ImportError as e:
        print(f"❌ Qt PDF modules not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main diagnostic function"""
    if len(sys.argv) != 2:
        print("Usage: python3 diagnose_pdf.py <pdf_file_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    print("🔧 PDF Diagnostic Tool for Safe Rename")
    print("=" * 60)
    
    success = diagnose_pdf(pdf_path)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ PDF should work with Safe Rename feature")
        print("💡 If Safe Rename still fails, there may be other issues")
    else:
        print("❌ PDF has issues that prevent Safe Rename from working")
        print("💡 Consider:")
        print("   - Check if the PDF is password-protected")
        print("   - Try opening the PDF in another application")
        print("   - Check if the file is corrupted")
        print("   - Verify the PDF format is supported")

if __name__ == "__main__":
    main()
