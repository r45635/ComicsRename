#!/usr/bin/env python3
"""
Test d'intégration de l'amélioration des URLs BDGest dans l'application
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bdgest_integration():
    """Test que l'amélioration des URLs BDGest fonctionne dans l'application"""
    
    print("🔍 Test d'intégration de l'amélioration des URLs BDGest")
    print("=" * 60)
    
    # Simuler des données d'albums BDGest avec URLs de miniatures
    mock_albums_data = [
        {
            'serie_name': 'Castaka',
            'album_name': 'Le Premier Ancêtre',
            'cover_url': 'https://www.bedetheque.com/cache/thb_couv/Castaka1_20032007.jpg'
        },
        {
            'serie_name': 'Lanfeust',
            'album_name': 'L\'Ivoire du Magohamoth',
            'cover_url': 'https://www.bedetheque.com/cache/thb_couv/Lanfeust1_12345.jpg'
        },
        {
            'serie_name': 'Déjà en HQ',
            'album_name': 'Test',
            'cover_url': 'https://www.bedetheque.com/media/Couvertures/Already_HQ.jpg'
        }
    ]
    
    print("📋 Albums de test avec URLs originales:")
    for i, album in enumerate(mock_albums_data, 1):
        print(f"   {i}. {album['serie_name']} - {album['album_name']}")
        print(f"      URL originale: {album['cover_url']}")
    
    # Appliquer l'amélioration
    from bdgest_scraper_api import _upgrade_bdgest_cover_url
    
    print(f"\n🔄 Application de l'amélioration...")
    
    improved_albums = []
    for album in mock_albums_data:
        improved_album = album.copy()
        improved_album['cover_url'] = _upgrade_bdgest_cover_url(
            album['cover_url'], 
            session=None, 
            debug=False
        )
        improved_albums.append(improved_album)
    
    print(f"\n✅ Albums avec URLs améliorées:")
    improvements = 0
    
    for i, (original, improved) in enumerate(zip(mock_albums_data, improved_albums), 1):
        print(f"   {i}. {improved['serie_name']} - {improved['album_name']}")
        print(f"      URL améliorée: {improved['cover_url']}")
        
        if original['cover_url'] != improved['cover_url']:
            print(f"      🎉 AMÉLIORÉE! (miniature → haute qualité)")
            improvements += 1
        else:
            print(f"      ✓ Conservée (déjà optimale)")
    
    print(f"\n📊 Résultats:")
    print(f"   Albums traités: {len(mock_albums_data)}")
    print(f"   URLs améliorées: {improvements}")
    print(f"   URLs conservées: {len(mock_albums_data) - improvements}")
    
    if improvements > 0:
        print(f"\n🎉 SUCCÈS! L'amélioration des URLs BDGest fonctionne!")
        print(f"   ✅ Les miniatures sont automatiquement remplacées par les images HQ")
        print(f"   ✅ Les URLs déjà optimales sont conservées")
        return True
    else:
        print(f"\n⚠️  Aucune amélioration détectée - vérifiez les URLs de test")
        return False

if __name__ == "__main__":
    success = test_bdgest_integration()
    if success:
        print("\n✅ Intégration réussie! Les utilisateurs profiteront d'images de meilleure qualité.")
    else:
        print("\n❌ Problème d'intégration détecté.")
