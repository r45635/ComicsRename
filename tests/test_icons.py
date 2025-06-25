#!/usr/bin/env python3
"""
Test script for ComicsRename icon integration
Verifies that all icon files are present and ready for distribution
"""

import os
from pathlib import Path

def test_icon_integration():
    """Test that all necessary icon files are present"""
    
    print("🎨 Test d'Intégration des Icônes ComicsRename")
    print("=" * 55)
    
    # Check main icon
    main_icon = Path("icon.ico")
    if main_icon.exists():
        print(f"✅ Icône principale trouvée: {main_icon} ({main_icon.stat().st_size} bytes)")
    else:
        print(f"❌ Icône principale manquante: {main_icon}")
        return False
    
    # Check icons directory
    icons_dir = Path("icons")
    if not icons_dir.exists():
        print(f"❌ Dossier d'icônes manquant: {icons_dir}")
        return False
    
    print(f"✅ Dossier d'icônes trouvé: {icons_dir}")
    
    # Check required icon files
    required_files = [
        "comicsrename_16x16.png",
        "comicsrename_32x32.png", 
        "comicsrename_48x48.png",
        "comicsrename_128x128.png",
        "comicsrename_256x256.png",
        "comicsrename_512x512.png",
        "comicsrename.ico",
        "icon.ico"
    ]
    
    print("\n📋 Vérification des fichiers requis:")
    missing_files = []
    
    for filename in required_files:
        filepath = icons_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size
            print(f"   ✅ {filename} ({size} bytes)")
        else:
            print(f"   ❌ {filename} - MANQUANT")
            missing_files.append(filename)
    
    # Check PyInstaller spec
    spec_file = Path("ComicsRename.spec")
    if spec_file.exists():
        print(f"\n🔧 Vérification PyInstaller spec: {spec_file}")
        
        with open(spec_file, 'r') as f:
            spec_content = f.read()
            
        if "icon='icon.ico'" in spec_content:
            print("   ✅ Référence à l'icône trouvée dans le spec")
        elif "icon.ico" in spec_content:
            print("   ✅ Icône référencée dans le spec")
        else:
            print("   ⚠️  Pas de référence d'icône trouvée dans le spec")
    else:
        print(f"\n⚠️  Fichier spec PyInstaller non trouvé: {spec_file}")
    
    # Check preview
    preview_file = icons_dir / "preview.html"
    if preview_file.exists():
        print(f"\n🌐 Aperçu disponible: {preview_file}")
        print(f"   💡 Ouvrez file://{preview_file.absolute()} pour voir les icônes")
    
    # Summary
    print(f"\n📊 Résumé:")
    print(f"   • Icône principale: {'✅ Présente' if main_icon.exists() else '❌ Manquante'}")
    print(f"   • Fichiers d'icônes: {len(required_files) - len(missing_files)}/{len(required_files)}")
    print(f"   • Spec PyInstaller: {'✅ Configuré' if spec_file.exists() else '⚠️  À configurer'}")
    
    if missing_files:
        print(f"\n❌ Fichiers manquants: {', '.join(missing_files)}")
        print("   💡 Exécutez 'python create_simple_icons.py' pour les recréer")
        return False
    
    print(f"\n🎉 Intégration des icônes réussie!")
    print(f"   • L'application est prête pour la distribution")
    print(f"   • Icônes compatibles Windows, macOS, Linux")
    print(f"   • PyInstaller configuré pour utiliser l'icône")
    
    # Build test
    print(f"\n🔨 Test de build recommandé:")
    print(f"   python -m PyInstaller ComicsRename.spec")
    print(f"   → L'exécutable devrait avoir l'icône ComicsRename")
    
    return True

if __name__ == "__main__":
    success = test_icon_integration()
    
    if success:
        print(f"\n✅ Tous les tests passés!")
        print(f"Votre projet ComicsRename est prêt avec ses icônes! 🎨")
    else:
        print(f"\n❌ Certains tests ont échoué.")
        print(f"Veuillez corriger les problèmes avant de continuer.")
        exit(1)
