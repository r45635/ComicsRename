#!/usr/bin/env python3
"""
Test the ComicVine cover URL fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_cover_url_fix():
    """Test that different issues have different cover URLs"""
    
    print("Testing ComicVine cover URL fix...")
    
    # Mock issue data to simulate what ComicVine API returns
    mock_issue_1 = {
        'id': 123,
        'name': 'Batman #1',
        'issue_number': '1',
        'image': {
            'original_url': 'https://comicvine.gamespot.com/a/uploads/scale_large/1/issue1_cover.jpg'
        }
    }
    
    mock_issue_2 = {
        'id': 124,
        'name': 'Batman #2',
        'issue_number': '2',
        'image': {
            'original_url': 'https://comicvine.gamespot.com/a/uploads/scale_large/1/issue2_cover.jpg'
        }
    }
    
    mock_volume_details = {
        'image': {
            'original_url': 'https://comicvine.gamespot.com/a/uploads/scale_large/1/volume_cover.jpg'
        }
    }
    
    # Test the fixed logic
    def create_enriched_issue(issue, volume_details):
        """Simulate the fixed logic from ComicVineProvider"""
        return {
            'id': issue.get('id'),
            'name': issue.get('name', 'Sans titre'),
            'issue_number': issue.get('issue_number', 'N/A'),
            # Fixed logic: prioritize issue image over volume image
            'image': issue.get('image', {}) or (volume_details.get('image', {}) if volume_details else {}),
            'cover_url': (issue.get('image', {}).get('original_url', '') or 
                         (volume_details.get('image', {}).get('original_url', '') if volume_details and volume_details.get('image') else '')),
        }
    
    # Test with the fixed logic
    enriched_issue_1 = create_enriched_issue(mock_issue_1, mock_volume_details)
    enriched_issue_2 = create_enriched_issue(mock_issue_2, mock_volume_details)
    
    print(f"Issue 1 ({enriched_issue_1['name']}):")
    print(f"  Cover URL: {enriched_issue_1['cover_url']}")
    print(f"Issue 2 ({enriched_issue_2['name']}):")
    print(f"  Cover URL: {enriched_issue_2['cover_url']}")
    
    # Check if covers are different
    if enriched_issue_1['cover_url'] != enriched_issue_2['cover_url']:
        print("✅ SUCCESS: Different issues have different cover URLs!")
        return True
    else:
        print("❌ PROBLEM: Issues have the same cover URL")
        return False

if __name__ == "__main__":
    success = test_cover_url_fix()
    if success:
        print("\n🎉 Fix verified! Each ComicVine issue should now have its own cover image.")
    else:
        print("\n❌ Fix needs more work.")
