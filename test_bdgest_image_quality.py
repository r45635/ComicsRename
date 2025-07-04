#!/usr/bin/env python3
"""
Test BDGest high quality image URL logic
"""

import requests

def test_bdgest_image_quality_improvement():
    """Test the BDGest image quality improvement logic"""
    
    print("🔍 Testing BDGest High Quality Image URL Logic")
    print("=" * 60)
    
    # Test URLs (example from your request)
    test_cases = [
        {
            'original': 'https://www.bedetheque.com/cache/thb_couv/Castaka1_20032007.jpg',
            'expected_hq': 'https://www.bedetheque.com/media/Couvertures/Castaka1_20032007.jpg'
        },
        {
            'original': 'https://www.bedetheque.com/cache/thb_couv/SomeOtherComic_12345.jpg',
            'expected_hq': 'https://www.bedetheque.com/media/Couvertures/SomeOtherComic_12345.jpg'
        }
    ]
    
    print("\n📋 Testing URL conversion logic...")
    
    for i, test_case in enumerate(test_cases, 1):
        original_url = test_case['original']
        expected_hq_url = test_case['expected_hq']
        
        print(f"\n--- Test Case {i} ---")
        print(f"Original URL: {original_url}")
        
        # Apply the conversion logic
        if 'bedetheque.com' in original_url and '/cache/thb_couv/' in original_url:
            converted_url = original_url.replace('/cache/thb_couv/', '/media/Couvertures/')
            print(f"Converted URL: {converted_url}")
            
            if converted_url == expected_hq_url:
                print("✅ URL conversion correct")
            else:
                print(f"❌ URL conversion incorrect. Expected: {expected_hq_url}")
            
            # Test if the high quality image actually exists
            print("🌐 Testing if high quality image exists...")
            try:
                response = requests.head(converted_url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ High quality image EXISTS (HTTP {response.status_code})")
                    final_url = converted_url
                else:
                    print(f"❌ High quality image NOT FOUND (HTTP {response.status_code})")
                    final_url = original_url
            except Exception as e:
                print(f"❌ Failed to check high quality image: {e}")
                final_url = original_url
            
            print(f"🎯 Final URL to use: {final_url}")
        else:
            print("ℹ️  Not a BDGest cache URL, no conversion needed")
    
    # Test with a real example
    print(f"\n🧪 Testing with your specific example...")
    castaka_original = 'https://www.bedetheque.com/cache/thb_couv/Castaka1_20032007.jpg'
    castaka_hq = 'https://www.bedetheque.com/media/Couvertures/Castaka1_20032007.jpg'
    
    print(f"Testing: {castaka_hq}")
    try:
        response = requests.head(castaka_hq, timeout=5)
        print(f"Response: HTTP {response.status_code}")
        if response.status_code == 200:
            print("✅ Castaka high quality image is available!")
        else:
            print("❌ Castaka high quality image not found")
    except Exception as e:
        print(f"❌ Error checking Castaka image: {e}")

if __name__ == "__main__":
    test_bdgest_image_quality_improvement()
