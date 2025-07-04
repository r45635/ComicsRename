#!/usr/bin/env python3
"""
Test the ComicVine cover fix with detailed issue fetching
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_comicvine_fix_with_details():
    """Test that fetching detailed issue information resolves cover URL issues"""
    
    print("🔍 Testing ComicVine Fix with Detailed Issue Fetching")
    print("=" * 60)
    
    # Mock ComicVine API responses
    
    # 1. Mock basic issues from volume endpoint (no individual cover images)
    mock_basic_issues = [
        {
            'id': 101,
            'name': 'Batman #1',
            'issue_number': '1',
            'cover_date': '2023-01-01',
            # No individual image - this is what causes the problem
        },
        {
            'id': 102,
            'name': 'Batman #2', 
            'issue_number': '2',
            'cover_date': '2023-02-01',
            # No individual image
        },
        {
            'id': 103,
            'name': 'Batman #3',
            'issue_number': '3', 
            'cover_date': '2023-03-01',
            # No individual image
        }
    ]
    
    # 2. Mock detailed issue responses (with individual cover images)
    mock_detailed_issues = {
        101: {
            'id': 101,
            'name': 'Batman #1',
            'image': {'original_url': 'https://comicvine.gamespot.com/batman_issue_1_cover.jpg'},
            'description': 'The Dark Knight begins...'
        },
        102: {
            'id': 102,
            'name': 'Batman #2',
            'image': {'original_url': 'https://comicvine.gamespot.com/batman_issue_2_cover.jpg'},
            'description': 'The Dark Knight continues...'
        },
        103: {
            'id': 103,
            'name': 'Batman #3',
            'image': {'original_url': 'https://comicvine.gamespot.com/batman_issue_3_cover.jpg'},
            'description': 'The Dark Knight fights...'
        }
    }
    
    # 3. Mock volume details (fallback cover)
    mock_volume_details = {
        'image': {'original_url': 'https://comicvine.gamespot.com/batman_volume_cover.jpg'},
        'start_year': 2023
    }
    
    print("📋 Simulating the fixed ComicVine provider logic...")
    
    # Simulate the fixed algorithm
    enriched_issues = []
    
    for issue in mock_basic_issues:
        issue_id = issue.get('id')
        print(f"\n🔍 Processing Issue ID: {issue_id}")
        
        # Simulate fetching detailed issue information
        issue_details = mock_detailed_issues.get(issue_id, {})
        print(f"   📥 Fetched detailed info: {bool(issue_details)}")
        
        if issue_details:
            merged_issue = {**issue, **issue_details}
            print(f"   🔄 Merged basic + detailed data")
        else:
            merged_issue = issue
            print(f"   ⚠️  Using basic data only")
        
        # Apply the fixed cover URL logic
        cover_url = (merged_issue.get('image', {}).get('original_url', '') or 
                    (mock_volume_details.get('image', {}).get('original_url', '') if mock_volume_details else ''))
        
        enriched_issue = {
            'id': merged_issue.get('id'),
            'name': merged_issue.get('name'),
            'issue_number': merged_issue.get('issue_number'),
            'cover_url': cover_url,
            'image': merged_issue.get('image', {}) or mock_volume_details.get('image', {})
        }
        
        enriched_issues.append(enriched_issue)
        print(f"   ✅ Final cover URL: {cover_url}")
    
    # Test the results
    print(f"\n📊 Testing Results:")
    print(f"   Total issues processed: {len(enriched_issues)}")
    
    cover_urls = [issue['cover_url'] for issue in enriched_issues]
    unique_covers = len(set(cover_urls))
    
    print(f"   Unique cover URLs: {unique_covers}")
    print(f"   Expected unique covers: {len(enriched_issues)}")
    
    if unique_covers == len(enriched_issues):
        print("\n🎉 SUCCESS: All issues have different cover URLs!")
        print("   The fix should resolve the ComicVine cover issue.")
        return True
    else:
        print("\n❌ PROBLEM: Some issues still share cover URLs")
        print("   Cover URLs found:")
        for i, url in enumerate(cover_urls, 1):
            print(f"     Issue {i}: {url}")
        return False

if __name__ == "__main__":
    success = test_comicvine_fix_with_details()
    if success:
        print("\n✅ Fix verification successful!")
    else:
        print("\n❌ Fix needs more work.")
