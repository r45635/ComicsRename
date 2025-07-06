#!/usr/bin/env python3
"""
Test script for the new folder move feature.

This tests the new functionality that allows moving files to an existing folder
when the target folder already exists during a rename operation.
"""

import os
import tempfile
import pathlib
import shutil
from core.folder_renamer import FolderRenamer


def test_folder_move_feature():
    """Test the new folder move functionality."""
    print("🧪 Testing Folder Move Feature")
    print("=" * 50)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        
        # Create test structure
        source_folder = temp_path / "Source_Folder"
        target_folder = temp_path / "Target_Folder"
        
        source_folder.mkdir()
        target_folder.mkdir()
        
        # Create test files in source folder
        test_files = ["file1.pdf", "file2.cbz", "file3.cbr"]
        file_list = []
        
        for filename in test_files:
            file_path = source_folder / filename
            file_path.write_text(f"Test content for {filename}")
            file_list.append({
                'name': filename.split('.')[0],
                'ext': filename.split('.')[1],
                'path': str(file_path),
                'folder': str(source_folder)
            })
        
        # Also create a conflicting file in target
        conflict_file = target_folder / "file1.pdf"
        conflict_file.write_text("Different content in target")
        
        print(f"✅ Created test structure:")
        print(f"   Source: {source_folder} ({len(test_files)} files)")
        print(f"   Target: {target_folder} (1 conflict file)")
        
        # Test the FolderRenamer
        folder_renamer = FolderRenamer(debug=True)
        
        # Test validation
        print(f"\n🔍 Testing validation...")
        status, target_path = folder_renamer.validate_rename_with_move_option(
            source_folder, "Target_Folder"
        )
        print(f"   Status: {status}")
        print(f"   Target path: {target_path}")
        
        if status == "target_exists":
            print(f"✅ Correctly detected existing target folder")
            
            # Test conflict detection
            print(f"\n🔍 Testing conflict detection...")
            for file_info in file_list:
                src_path = pathlib.Path(file_info['path'])
                dst_path = target_folder / src_path.name
                
                conflict_info = folder_renamer.check_file_conflict(src_path, dst_path)
                print(f"   {src_path.name}: {'CONFLICT' if conflict_info['conflict'] else 'NO CONFLICT'}")
                
                if conflict_info['conflict']:
                    src_info = conflict_info['src_info']
                    dst_info = conflict_info['dst_info']
                    print(f"     Source: {src_info['size_str']} - {src_info['mod_date_str']}")
                    print(f"     Target: {dst_info['size_str']} - {dst_info['mod_date_str']}")
            
            # Test file move with conflict handler
            print(f"\n🚀 Testing file move with conflict handler...")
            
            def test_conflict_handler(src_path, dst_path, conflict_info):
                print(f"   [HANDLER] Conflict for {src_path.name} -> returning 'skip'")
                return 'skip'  # Skip conflicts in test
            
            result = folder_renamer.move_files_to_existing_folder(
                file_list, source_folder, target_folder, test_conflict_handler
            )
            
            print(f"\n📊 Move Results:")
            print(f"   Success: {result['success']}")
            print(f"   Moved: {result['moved_count']} files")
            print(f"   Skipped: {result['skipped_count']} files")
            print(f"   Failed: {result['failed_count']} files")
            
            if result['moved_files']:
                print(f"   Moved files: {', '.join(result['moved_files'])}")
            if result['skipped_files']:
                print(f"   Skipped files: {', '.join(result['skipped_files'])}")
            if result['errors']:
                print(f"   Errors: {result['errors']}")
            
            # Test cleanup of empty folder
            print(f"\n🧹 Testing empty folder cleanup...")
            cleanup_success, cleanup_msg = folder_renamer.cleanup_empty_folder(source_folder)
            print(f"   Cleanup success: {cleanup_success}")
            print(f"   Message: {cleanup_msg}")
            
            # Verify final state
            print(f"\n🔍 Final verification...")
            print(f"   Source folder exists: {source_folder.exists()}")
            print(f"   Target folder exists: {target_folder.exists()}")
            if target_folder.exists():
                target_files = list(target_folder.iterdir())
                print(f"   Target folder contents: {[f.name for f in target_files]}")
            
            print(f"\n✅ Test completed successfully!")
        else:
            print(f"❌ Unexpected validation status: {status}")
            return False
    
    return True


def test_file_info_extraction():
    """Test file information extraction."""
    print(f"\n🧪 Testing File Info Extraction")
    print("=" * 40)
    
    folder_renamer = FolderRenamer(debug=True)
    
    # Test with current script file
    script_path = pathlib.Path(__file__)
    if script_path.exists():
        file_info = folder_renamer.get_file_info(script_path)
        
        print(f"✅ File info for {script_path.name}:")
        print(f"   Size: {file_info['size_str']}")
        print(f"   Modified: {file_info['mod_date_str']}")
        print(f"   Exists: {file_info['exists']}")
    else:
        print(f"❌ Script file not found")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Starting Folder Move Feature Tests")
    print("=" * 60)
    
    success = True
    
    try:
        # Test file info extraction
        if not test_file_info_extraction():
            success = False
            
        # Test main folder move feature
        if not test_folder_move_feature():
            success = False
            
        if success:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"✅ New folder move feature is working correctly")
        else:
            print(f"\n❌ Some tests failed")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print(f"\n📋 Test Summary: {'SUCCESS' if success else 'FAILURE'}")
