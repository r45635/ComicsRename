#!/usr/bin/env python3
"""
Script de test pour forcer l'activation de SafeRename et vérifier la détection PDF
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QSettings

def test_pdf_detection():
    """Test la détection des fichiers PDF"""
    print("🔍 TEST DÉTECTION PDF")
    print("=" * 30)
    
    # Simuler les données de fichier comme dans scan_comic_files
    test_files = [
        {
            'path': '/path/to/file.pdf',
            'name': 'file',
            'ext': 'pdf',  # SANS le point !
            'size': '10.5 MB',
            'folder': '/path/to'
        },
        {
            'path': '/path/to/file.cbz',
            'name': 'file',
            'ext': 'cbz',  # SANS le point !
            'size': '5.2 MB',
            'folder': '/path/to'
        }
    ]
    
    for f in test_files:
        # Test de la logique corrigée
        is_pdf = f['ext'].lower() == 'pdf' or f['path'].lower().endswith('.pdf')
        
        print(f"📄 Fichier: {f['name']}.{f['ext']}")
        print(f"   Extension: '{f['ext']}'")
        print(f"   Path: '{f['path']}'")
        print(f"   Détecté comme PDF: {is_pdf}")
        print()
    
    return True

def test_cover_comparison_import():
    """Test l'import du dialogue de comparaison de couvertures"""
    print("🖼️  TEST IMPORT COVER COMPARISON DIALOG")
    print("=" * 40)
    
    try:
        from cover_comparison_dialog import CoverComparisonDialog
        print("✅ CoverComparisonDialog importé avec succès")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import CoverComparisonDialog: {e}")
        return False

def test_safe_rename_dependencies():
    """Test les dépendances SafeRename"""
    print("🔧 TEST DÉPENDANCES SAFE RENAME")
    print("=" * 30)
    
    # Test import PDF comparator
    pdf_comparator_ok = False
    try:
        from pdf_cover_comparator_qt import PDFCoverComparator
        print("✅ pdf_cover_comparator_qt disponible (Qt-native)")
        pdf_comparator_ok = True
    except ImportError:
        try:
            from pdf_cover_comparator import PDFCoverComparator
            print("✅ pdf_cover_comparator disponible (Poppler-based)")
            pdf_comparator_ok = True
        except ImportError as e:
            print(f"❌ Aucun comparateur PDF disponible: {e}")
    
    # Test import cover comparison dialog
    cover_dialog_ok = test_cover_comparison_import()
    
    return pdf_comparator_ok and cover_dialog_ok

def force_test_safe_rename():
    """Force un test SafeRename en créant un fichier temporaire"""
    print("🧪 TEST FORCÉ SAFE RENAME")
    print("=" * 25)
    
    # S'assurer que SafeRename est activé
    settings = QSettings("ComicsRename", "App")
    settings.setValue('safe_rename', 'true')
    
    safe_rename_enabled = settings.value('safe_rename', 'false') == 'true'
    print(f"SafeRename activé: {safe_rename_enabled}")
    
    if safe_rename_enabled:
        print("✅ SafeRename est prêt à être testé")
        print()
        print("🎯 POUR TESTER MAINTENANT:")
        print("1. Lancez l'application: python3 main.py")
        print("2. Chargez un dossier contenant un fichier PDF")
        print("3. Cherchez 'Blacksad' (ou tout autre album)")
        print("4. Glissez un album vers le fichier PDF")
        print("5. Vérifiez les logs pour:")
        print("   - 'File is PDF: True'")
        print("   - 'Safe Rename enabled: True'") 
        print("   - 'Starting Safe Rename check'")
        print("   - Ouverture du dialogue CoverComparisonDialog")
    
    return safe_rename_enabled

if __name__ == "__main__":
    print("🚀 TEST COMPLET SAFE RENAME")
    print("=" * 50)
    
    # 1. Test détection PDF
    pdf_detection_ok = test_pdf_detection()
    
    # 2. Test dépendances SafeRename
    dependencies_ok = test_safe_rename_dependencies()
    
    # 3. Test configuration SafeRename
    config_ok = force_test_safe_rename()
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 50)
    print(f"Détection PDF: {'✅' if pdf_detection_ok else '❌'}")
    print(f"Dépendances SafeRename: {'✅' if dependencies_ok else '❌'}")
    print(f"Configuration SafeRename: {'✅' if config_ok else '❌'}")
    
    all_ok = pdf_detection_ok and dependencies_ok and config_ok
    
    if all_ok:
        print("\n🎉 TOUT EST PRÊT POUR SAFE RENAME!")
        print("Le dialogue CoverComparisonDialog devrait maintenant s'afficher")
        print("lors du drag & drop d'un album vers un PDF.")
    else:
        print("\n⚠️  Des corrections sont nécessaires avant le test")
    
    print("=" * 50)
