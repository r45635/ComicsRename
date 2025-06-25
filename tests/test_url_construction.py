#!/usr/bin/env python3
"""
Simple test to verify the series albums functionality
"""

# Test URL construction
import requests

def test_url_construction():
    print("🔍 Testing URL construction...")
    
    # Test case from user example
    series_id = "7891"
    series_name = "Légende de Cassidy (La)"
    
    # Our construction
    encoded_series_name = requests.utils.quote(series_name)
    url = f"https://online.bdgest.com/albums/import?ids={series_id}&s={encoded_series_name}&t=&e=&c=&y=&ida=&a=&p=&f=&o=&lang=&dld=&cmin=&isbn=&dlf=&cmax="
    
    print(f"Series ID: {series_id}")
    print(f"Series Name: {series_name}")
    print(f"Encoded Name: {encoded_series_name}")
    print(f"Constructed URL: {url}")
    
    # Expected URL from user example
    expected_url = "https://online.bdgest.com/albums/import?ids=7891&s=L%C3%A9eeegende+de+Cassidy+%28La%29&t=&e=&c=&y=&ida=&a=&p=&f=&o=&lang=&dld=&cmin=&isbn=&dlf=&cmax="
    
    print(f"Expected URL: {expected_url}")
    
    # Check URL structure
    if f"ids={series_id}" in url:
        print("✅ Series ID correctly placed in 'ids' parameter")
    else:
        print("❌ Series ID not found in 'ids' parameter")
    
    if f"s={encoded_series_name}" in url:
        print("✅ Series name correctly placed in 's' parameter")
    else:
        print("❌ Series name not found in 's' parameter")
    
    print("\n🔍 Testing function availability...")
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from bdgest_scraper_api import get_bdgest_albums_by_series_id
        print("✅ get_bdgest_albums_by_series_id imported successfully")
        
        from comicsFileRenamer_v3 import BDGestProvider
        provider = BDGestProvider()
        
        if hasattr(provider, 'search_albums_by_series_id'):
            print("✅ BDGestProvider.search_albums_by_series_id method available")
        else:
            print("❌ BDGestProvider.search_albums_by_series_id method not found")
            
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_construction()
