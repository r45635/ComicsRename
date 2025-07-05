#!/usr/bin/env python3
"""
Script pour activer SafeRename automatiquement et tester le drag & drop
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QSettings

def enable_safe_rename():
    """Active SafeRename dans les paramètres"""
    print("🔧 Activation de SafeRename...")
    
    settings = QSettings("ComicsRename", "App")
    settings.setValue('safe_rename', 'true')
    
    # Vérification
    safe_rename_enabled = settings.value('safe_rename', 'false') == 'true'
    
    if safe_rename_enabled:
        print("✅ SafeRename activé avec succès!")
    else:
        print("❌ Échec de l'activation de SafeRename")
    
    return safe_rename_enabled

def test_metadata_extraction():
    """Test l'extraction des métadonnées BDGest"""
    print("\n🧪 Test d'extraction des métadonnées BDGest...")
    
    # Exemple de métadonnées BDGest (comme dans vos logs)
    sample_meta = {
        'album_id': '15161',
        'album_name': 'Quelque part entre les ombres',
        'album_number': '1',
        'album_url': 'https://www.bedetheque.com/BD-Blacksad-Tome-1-Quelque-part-entre-les-ombres-15161.html',
        'collection': 'Sombre',
        'cover_url': 'https://www.bedetheque.com/media/Couvertures/Couv_15161.jpg',
        'date': '03/2000',
        'details': '...',
        'editor': 'Dargaud',
        'isbn': '2205050273',
        'pages': '56',
        'serie_name': 'Blacksad'
    }
    
    # Test de l'extraction avec la logique corrigée
    series = sample_meta.get('serie_name', sample_meta.get('series', ''))
    num = sample_meta.get('album_number', sample_meta.get('issue_number', sample_meta.get('num', '')))
    title = sample_meta.get('album_name', sample_meta.get('title', ''))
    
    # Extract year from date field
    y = ''
    date_str = sample_meta.get('date', sample_meta.get('parution', sample_meta.get('year', '')))
    if date_str:
        import re
        year_match = re.search(r'(\d{4})', str(date_str))
        if year_match:
            y = year_match.group(1)
    
    print(f"📋 Métadonnées extraites:")
    print(f"   Series: '{series}'")
    print(f"   Number: '{num}'")
    print(f"   Title: '{title}'")
    print(f"   Year: '{y}'")
    
    # Test du format de nom de fichier
    def format_num(n):
        try:
            n_int = int(n)
            return f"{n_int:02d}"
        except Exception:
            return str(n)
    
    import re
    def clean(s):
        return re.sub(r"[^\w\s'\u2019\-\_()]", '', str(s), flags=re.UNICODE).strip()
    
    base = f"{clean(series)} - {format_num(num)} - {clean(title)}"
    if y:
        base += f" ({y})"
    
    print(f"📄 Nom de fichier généré: '{base}.pdf'")
    
    expected = "Blacksad - 01 - Quelque part entre les ombres (2000)"
    if base == expected:
        print("✅ Format de nom correct!")
    else:
        print(f"❌ Format incorrect. Attendu: '{expected}'")
    
    return base == expected

if __name__ == "__main__":
    print("🚀 CONFIGURATION ET TEST COMICS RENAME")
    print("=" * 50)
    
    # 1. Activer SafeRename
    safe_rename_ok = enable_safe_rename()
    
    # 2. Tester l'extraction des métadonnées
    metadata_ok = test_metadata_extraction()
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")
    print("=" * 50)
    print(f"SafeRename activé: {'✅' if safe_rename_ok else '❌'}")
    print(f"Extraction métadonnées: {'✅' if metadata_ok else '❌'}")
    
    if safe_rename_ok and metadata_ok:
        print("\n🎯 PRÊT POUR LE TEST!")
        print("1. Lancez l'application: python3 main.py")
        print("2. Faites un drag & drop d'un album vers un PDF")
        print("3. Vous devriez voir SafeRename s'activer automatiquement")
    else:
        print("\n⚠️  Corrections nécessaires avant le test")
    
    print("=" * 50)
