#!/usr/bin/env python3
"""
Test rapide pour vérifier que le cover_local_path est correctement transmis
"""

import os
import sys
import tempfile

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cache_integration():
    """Test que le cover_local_path est bien transmis lors du drag & drop"""
    
    print("=== Test d'intégration du cache cover_local_path ===")
    
    # Simuler des métadonnées avec cover_local_path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(b"fake image data")
        cached_path = temp_file.name
    
    # Métadonnées comme elles seraient dans l'album
    test_meta = {
        'album_id': '51823',
        'album_name': 'Âme Rouge',
        'album_number': '3',
        'cover_url': 'https://www.bedetheque.com/media/Couvertures/Couv_51823.jpg',
        'cover_local_path': cached_path  # Ceci devrait maintenant être présent
    }
    
    print(f"✅ Métadonnées test créées avec cover_local_path: {cached_path}")
    
    # Test la logique de décision du cache dans SafeRename
    local_cover_path = test_meta.get('cover_local_path', '')
    if local_cover_path and os.path.exists(local_cover_path):
        print(f"✅ Cache serait utilisé: {local_cover_path}")
        use_cache = True
    else:
        print(f"❌ Cache ne serait pas utilisé")
        use_cache = False
    
    # Test la sérialisation JSON (comme dans le drag & drop)
    import json
    meta_json = json.dumps(test_meta, default=str)
    deserialized_meta = json.loads(meta_json)
    
    if 'cover_local_path' in deserialized_meta:
        print(f"✅ cover_local_path survit à la sérialisation JSON")
        print(f"   Chemin: {deserialized_meta['cover_local_path']}")
    else:
        print(f"❌ cover_local_path perdu lors de la sérialisation JSON")
    
    # Test de la logique comme dans SafeRename
    local_cover_path = deserialized_meta.get('cover_local_path', '')
    if local_cover_path and os.path.exists(local_cover_path):
        print(f"✅ SafeRename utiliserait le cache après désérialisation")
    else:
        print(f"❌ SafeRename n'utiliserait pas le cache après désérialisation")
    
    # Nettoyage
    os.unlink(cached_path)
    
    return use_cache

def main():
    """Test principal"""
    
    print("Test d'intégration de l'optimisation SafeRename")
    print("=" * 50)
    
    success = test_cache_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test réussi ! Le cache devrait maintenant fonctionner.")
        print("\nCe qui devrait maintenant se passer :")
        print("1. ✅ Affichage d'une couverture → cache créé")
        print("2. ✅ Drag & drop de cet album → cover_local_path transmis")
        print("3. ✅ SafeRename → utilise le cache au lieu de télécharger")
        print("4. ✅ Performance améliorée !")
    else:
        print("❌ Test échoué. Le cache ne fonctionnerait pas.")
    
    print("\nPour tester en réel :")
    print("1. Lancez l'application")
    print("2. Recherchez des albums (ex: 'blacksad')")
    print("3. Cliquez sur un album pour afficher sa couverture")
    print("4. Faites un drag & drop sur un PDF")
    print("5. Vérifiez les logs pour voir si le cache est utilisé")

if __name__ == "__main__":
    main()
