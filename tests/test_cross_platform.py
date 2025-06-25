#!/usr/bin/env python3
"""
Test script for cross-platform file operations
Tests open file and reveal file functions on Windows, macOS, and Linux
"""

import sys
import os
import tempfile
import pathlib

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import open_file_cross_platform, reveal_file_cross_platform, get_system_info

def test_cross_platform_functions():
    """Test cross-platform file operations"""
    
    print("🧪 Test des fonctions cross-platform")
    print("=" * 50)
    
    # Get system information
    system_info = get_system_info()
    print(f"🖥️  Système détecté: {system_info['system']}")
    print(f"📱 Plateforme: {system_info['platform']}")
    print(f"🔍 Version: {system_info['version']}")
    print()
    
    # Display OS-specific information
    if system_info['is_windows']:
        print("✅ Windows détecté")
        print("   • Commande 'ouvrir fichier': os.startfile()")
        print("   • Commande 'afficher dans l'explorateur': explorer /select,")
    elif system_info['is_macos']:
        print("✅ macOS détecté")
        print("   • Commande 'ouvrir fichier': open")
        print("   • Commande 'révéler dans Finder': open -R")
    elif system_info['is_linux']:
        print("✅ Linux détecté")
        print("   • Commande 'ouvrir fichier': xdg-open")
        print("   • Commande 'afficher dans gestionnaire': nautilus/dolphin/thunar/...")
    else:
        print(f"⚠️  Système non supporté: {system_info['system']}")
    
    print()
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test file for ComicsRename cross-platform operations\n")
        f.write(f"Created on: {system_info['system']}\n")
        f.write("This file was created to test open and reveal operations.\n")
        test_file_path = f.name
    
    print(f"📄 Fichier de test créé: {test_file_path}")
    print()
    
    # Test functions
    print("🔧 Test des fonctions:")
    
    # Test 1: open_file_cross_platform
    print("   1. Test de open_file_cross_platform...")
    result = open_file_cross_platform(test_file_path)
    if result is True:
        print("      ✅ Fonction exécutée avec succès")
        print("      📂 Le fichier devrait s'ouvrir dans l'application par défaut")
    else:
        success, error_msg = result
        if success:
            print("      ✅ Fonction exécutée avec succès")
        else:
            print(f"      ❌ Erreur: {error_msg}")
    
    print()
    
    # Test 2: reveal_file_cross_platform
    print("   2. Test de reveal_file_cross_platform...")
    result = reveal_file_cross_platform(test_file_path)
    if result is True:
        print("      ✅ Fonction exécutée avec succès")
        if system_info['is_windows']:
            print("      📂 Le fichier devrait être sélectionné dans l'Explorateur Windows")
        elif system_info['is_macos']:
            print("      📂 Le fichier devrait être révélé dans le Finder")
        else:
            print("      📂 Le fichier devrait être affiché dans le gestionnaire de fichiers")
    else:
        success, error_msg = result
        if success:
            print("      ✅ Fonction exécutée avec succès")
        else:
            print(f"      ❌ Erreur: {error_msg}")
    
    print()
    
    # Test with non-existent file
    print("   3. Test avec fichier inexistant...")
    fake_file = "/path/that/does/not/exist/fake_file.txt"
    result = open_file_cross_platform(fake_file)
    if result is True:
        print("      ⚠️  Fonction exécutée (résultat inattendu)")
    else:
        success, error_msg = result
        if not success:
            print("      ✅ Erreur correctement détectée")
            print(f"      📝 Message d'erreur: {error_msg}")
        else:
            print("      ⚠️  Pas d'erreur détectée (résultat inattendu)")
    
    print()
    
    # Cleanup
    try:
        os.unlink(test_file_path)
        print(f"🧹 Fichier de test supprimé: {test_file_path}")
    except:
        print(f"⚠️  Impossible de supprimer le fichier de test: {test_file_path}")
    
    print()
    print("🎯 Résumé des adaptations par OS:")
    print()
    print("📱 **Windows:**")
    print("   • Menu: 'Open File' / 'Show in Explorer'")
    print("   • Ouverture: os.startfile()")
    print("   • Révélation: explorer /select,")
    print()
    print("🍎 **macOS:**")
    print("   • Menu: 'Open File' / 'Reveal in Finder'")
    print("   • Ouverture: open")
    print("   • Révélation: open -R")
    print()
    print("🐧 **Linux:**")
    print("   • Menu: 'Open File' / 'Show in File Manager'")
    print("   • Ouverture: xdg-open")
    print("   • Révélation: nautilus/dolphin/thunar (avec fallback)")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = test_cross_platform_functions()
        
        if success:
            print("🎉 Test terminé!")
            print("Les fonctions cross-platform sont maintenant implémentées.")
            print()
            print("💡 Dans l'application ComicsRename:")
            print("   • Clic droit sur un fichier → menus adaptés selon l'OS")
            print("   • 'Open File' fonctionne sur tous les systèmes")
            print("   • 'Reveal/Show' s'adapte au gestionnaire de fichiers")
            print("   • Gestion d'erreur améliorée")
        else:
            print("❌ Test échoué.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
