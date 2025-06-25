#!/usr/bin/env python3
"""
Test script to verify optimized Comic Vine loading.
"""
import sys
import os
import warnings
import time

# Suppress SSL warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_optimized_loading():
    """Test the optimized Comic Vine loading"""
    print("Testing Optimized Comic Vine Loading")
    print("=" * 50)
    
    # Import ComicVine provider
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from comicsFileRenamer_v3 import ComicVineProvider
    
    provider = ComicVineProvider()
    
    # Test search for series
    query = "blacksad"
    print(f"Step 1: Searching for series '{query}'")
    print("-" * 30)
    
    start_time = time.time()
    series_results = provider.search_series(query)
    search_time = time.time() - start_time
    
    print(f"✅ Found {len(series_results)} series in {search_time:.2f} seconds")
    
    if series_results:
        # Test album loading for first series
        first_series = series_results[0]
        series_name = first_series.get('name', 'Unknown')
        volume_id = str(first_series.get('id', ''))
        
        print(f"\nStep 2: Loading albums for '{series_name}' (optimized)")
        print("-" * 30)
        
        start_time = time.time()
        albums = provider.search_albums(volume_id, debug=True)
        album_time = time.time() - start_time
        
        print(f"✅ Loaded {len(albums)} albums in {album_time:.2f} seconds")
        
        if albums:
            print("\nFirst few albums:")
            for i, album in enumerate(albums[:3], 1):
                name = album.get('name', 'Unknown')
                issue_num = album.get('issue_number', 'N/A')
                cover_date = album.get('cover_date', 'Unknown')[:10]  # Just the date part
                cover_url = album.get('cover_url', '')
                has_cover = "✅" if cover_url else "❌"
                print(f"  {i}. #{issue_num} - {name} ({cover_date}) Cover: {has_cover}")
        
        total_time = search_time + album_time
        print(f"\n📊 Performance Summary:")
        print(f"   Series search: {search_time:.2f}s")
        print(f"   Album loading: {album_time:.2f}s")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Optimization: Using basic issue data (no individual API calls)")
        
    else:
        print("No series found")

if __name__ == "__main__":
    test_optimized_loading()
