#!/usr/bin/env python3
"""
Test script for the file deletion functionality
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import delete_file_cross_platform


class TestDeleteFile(unittest.TestCase):
    """Test cases for the delete_file_cross_platform function"""

    def setUp(self):
        """Create a temporary file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"Test content")
        self.temp_file.close()

    def test_delete_existing_file(self):
        """Test deleting an existing file"""
        # Verify file exists
        self.assertTrue(os.path.exists(self.temp_file.name))
        
        # Delete the file
        result = delete_file_cross_platform(self.temp_file.name)
        
        # Check result
        self.assertEqual(result, True)
        
        # Verify file no longer exists
        self.assertFalse(os.path.exists(self.temp_file.name))

    def test_delete_nonexistent_file(self):
        """Test attempting to delete a non-existent file"""
        non_existent_path = "/path/to/nonexistent/file.txt"
        
        # Delete the file
        result = delete_file_cross_platform(non_existent_path)
        
        # Check result is a tuple with error message
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0], False)
        self.assertIn("not found", result[1])

    def tearDown(self):
        """Clean up any remaining test files"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)


if __name__ == "__main__":
    print("🧪 Running delete file tests...")
    unittest.main()
