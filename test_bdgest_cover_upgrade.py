#!/usr/bin/env python3
"""
Test de l'amélioration des URLs de couverture BDGest
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bdgest_cover_upgrade():
    """Test la fonction d'amélioration des URLs de couverture BDGest"""
    
    print("🔍 Test d'amélioration des URLs de couverture BDGest")
    print("=" * 60)
    
    from bdgest_scraper_api import _upgrade_bdgest_cover_url
    
    # Test cases
    test_cases = [
        {
            'input': 'https://www.bedetheque.com/cache/thb_couv/Castaka1_20032007.jpg',
            'expected': 'https://www.bedetheque.com/media/Couvertures/Castaka1_20032007.jpg',
            'description': 'URL de miniature BDGest standard'
        },
        {
            'input': 'https://www.bedetheque.com/cache/thb_couv/SomethingElse_12345.jpg',
            'expected': 'https://www.bedetheque.com/media/Couvertures/SomethingElse_12345.jpg',
            'description': 'Autre URL de miniature BDGest'
        },
        {
            'input': 'https://comicvine.gamespot.com/a/uploads/scale_large/1/image.jpg',
            'expected': 'https://comicvine.gamespot.com/a/uploads/scale_large/1/image.jpg',
            'description': 'URL ComicVine (ne doit pas changer)'
        },
        {
            'input': 'https://www.bedetheque.com/media/Couvertures/AlreadyHQ_67890.jpg',
            'expected': 'https://www.bedetheque.com/media/Couvertures/AlreadyHQ_67890.jpg',
            'description': 'URL déjà haute qualité (ne doit pas changer)'
        },
        {
            'input': '',
            'expected': '',
            'description': 'URL vide'
        },
        {
            'input': None,
            'expected': None,
            'description': 'URL None'
        }
    ]
    
    all_tests_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test['description']}")
        print(f"   Entrée: {test['input']}")
        
        # Tester sans session (transformation directe)
        result = _upgrade_bdgest_cover_url(test['input'], session=None, debug=False)
        print(f"   Résultat: {result}")
        print(f"   Attendu: {test['expected']}")
        
        if result == test['expected']:
            print(f"   ✅ SUCCÈS")
        else:
            print(f"   ❌ ÉCHEC")
            all_tests_passed = False
    
    # Test avec debug activé pour voir les messages
    print(f"\n🔍 Test avec debug activé:")
    test_url = 'https://www.bedetheque.com/cache/thb_couv/DebugTest_99999.jpg'
    print(f"   URL test: {test_url}")
    result = _upgrade_bdgest_cover_url(test_url, session=None, debug=True)
    print(f"   Résultat: {result}")
    
    # Résultat final
    print(f"\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("   ✅ Les URLs de miniatures BDGest sont correctement améliorées")
        print("   ✅ Les URLs non-BDGest sont conservées")
        print("   ✅ Les cas limites sont gérés")
        return True
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("   Vérifiez la fonction _upgrade_bdgest_cover_url")
        return False

if __name__ == "__main__":
    success = test_bdgest_cover_upgrade()
    if success:
        print("\n✅ Amélioration des URLs BDGest prête à l'emploi!")
    else:
        print("\n❌ Des corrections sont nécessaires.")
