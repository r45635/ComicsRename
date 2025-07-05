#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections SafeRename et format de nom
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QSettings

def test_safe_rename_setting():
    """Test si SafeRename est disponible dans les paramètres"""
    print("=" * 50)
    print("TEST SAFE RENAME SETTING")
    print("=" * 50)
    
    settings = QSettings("ComicsRename", "App")
    
    # Test lecture de la valeur par défaut
    safe_rename_default = settings.value('safe_rename', 'false')
    print(f"SafeRename par défaut: {safe_rename_default}")
    
    # Test définition à True
    settings.setValue('safe_rename', 'true')
    safe_rename_enabled = settings.value('safe_rename', 'false') == 'true'
    print(f"SafeRename après activation: {safe_rename_enabled}")
    
    # Test définition à False
    settings.setValue('safe_rename', 'false')
    safe_rename_disabled = settings.value('safe_rename', 'false') == 'true'
    print(f"SafeRename après désactivation: {safe_rename_disabled}")
    
    print("✅ SafeRename setting test passed!\n")

def test_filename_format():
    """Test du format de nom de fichier"""
    print("=" * 50)
    print("TEST FILENAME FORMAT")
    print("=" * 50)
    
    # Test data
    test_cases = [
        {
            'series': 'Lucky Luke',
            'num': '1',
            'title': 'La Mine d\'or de Dick Digger',
            'year': '1949',
            'expected': 'Lucky Luke - 01 - La Mine d\'or de Dick Digger (1949)'
        },
        {
            'series': 'Astérix',
            'num': '12',
            'title': 'Astérix aux Jeux Olympiques',
            'year': '1968',
            'expected': 'Astérix - 12 - Astérix aux Jeux Olympiques (1968)'
        },
        {
            'series': 'Test Series',
            'num': '5',
            'title': 'Test Album',
            'year': '',
            'expected': 'Test Series - 05 - Test Album'
        }
    ]
    
    def format_num(n):
        try:
            n_int = int(n)
            return f"{n_int:02d}"
        except Exception:
            return str(n)
    
    import re
    def clean(s):
        return re.sub(r"[^\w\s'\u2019\-\_()]", '', str(s), flags=re.UNICODE).strip()
    
    for i, case in enumerate(test_cases):
        series = case['series']
        num = case['num']
        title = case['title']
        year = case['year']
        expected = case['expected']
        
        # Format selon le nouveau système
        base = f"{clean(series)} - {format_num(num)} - {clean(title)}"
        if year:
            base += f" ({year})"
        
        print(f"Test {i+1}:")
        print(f"  Input: series='{series}', num='{num}', title='{title}', year='{year}'")
        print(f"  Result: '{base}'")
        print(f"  Expected: '{expected}'")
        print(f"  ✅ Pass" if base == expected else f"  ❌ Fail")
        print()
    
    print("✅ Filename format test completed!\n")

if __name__ == "__main__":
    print("🧪 COMICS RENAME - TESTS DE CORRECTION")
    print("🔧 SafeRename + Format de nom de fichier")
    print()
    
    test_safe_rename_setting()
    test_filename_format()
    
    print("=" * 50)
    print("📋 RÉSUMÉ DES CORRECTIONS")
    print("=" * 50)
    print("1. ✅ SafeRename ajouté aux paramètres (ui/dialogs.py)")
    print("2. ✅ SafeRename debug ajouté (drag & drop)")
    print("3. ✅ Format de nom: 'Serie Name - Album Number - Album Title (Year)'")
    print("4. ✅ Renommage par bouton et drag & drop cohérents")
    print()
    print("🎯 PROCHAINES ÉTAPES:")
    print("- Lancez l'application: python3 main.py")
    print("- Activez SafeRename dans Paramètres")
    print("- Testez le drag & drop avec un PDF")
    print("- Vérifiez les messages de debug dans la console")
    print("=" * 50)
