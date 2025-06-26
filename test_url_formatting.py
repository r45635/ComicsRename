#!/usr/bin/env python3
"""
Quick test script to verify URL formatting in ComicsRename
"""

import re

def make_links_clickable(text):
    """Convert URLs in text to clickable HTML links"""
    # URL pattern to match http/https URLs
    url_pattern = r'(https?://[^\s<>"]{2,})'
    # Replace URLs with HTML links
    def replace_url(match):
        url = match.group(1)
        # Truncate very long URLs for display
        display_url = url if len(url) <= 50 else url[:47] + '...'
        return f'<a href="{url}">{display_url}</a>'
    
    return re.sub(url_pattern, replace_url, str(text))

# Test cases
test_cases = [
    "Visit https://comicvine.gamespot.com/api/issue/123456/",
    "Check out https://www.bedetheque.com/serie-12345.html for more info",
    "This is a very long URL: https://comicvine.gamespot.com/api/issue/4000-123456/?api_key=YOUR_API_KEY&format=json&field_list=all_fields",
    "Multiple URLs: https://example.com and https://another-site.org/path/to/page"
]

print("URL Formatting Test Results:")
print("=" * 50)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}:")
    print(f"Input:  {test}")
    result = make_links_clickable(test)
    print(f"Output: {result}")
    
    # Check for redundant title attributes (should not exist)
    if 'title=' in result:
        print("⚠️  WARNING: Found 'title=' attribute in output!")
    else:
        print("✅ Clean URL formatting (no redundant title attributes)")
