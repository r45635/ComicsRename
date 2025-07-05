#!/usr/bin/env python3
"""
Script de debug ultra-détaillé pour identifier pourquoi SafeRename ne fonctionne pas en drag & drop
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QSettings

def debug_settings():
    """Debug des paramètres SafeRename"""
    print("🔍 DEBUG PARAMÈTRES SAFE RENAME")
    print("=" * 40)
    
    settings = QSettings("ComicsRename", "App")
    
    # Vérifier tous les paramètres liés à SafeRename
    keys = settings.allKeys()
    print("Toutes les clés de paramètres:")
    for key in sorted(keys):
        value = settings.value(key)
        print(f"  {key}: {value} (type: {type(value)})")
    
    print()
    
    # Test spécifique SafeRename
    safe_rename_raw = settings.value('safe_rename')
    safe_rename_bool = settings.value('safe_rename', 'false') == 'true'
    
    print(f"safe_rename (raw): {safe_rename_raw} (type: {type(safe_rename_raw)})")
    print(f"safe_rename (bool): {safe_rename_bool}")
    
    # Forcer l'activation si nécessaire
    if not safe_rename_bool:
        print("⚠️  SafeRename désactivé, activation...")
        settings.setValue('safe_rename', 'true')
        safe_rename_bool = settings.value('safe_rename', 'false') == 'true'
        print(f"SafeRename après activation: {safe_rename_bool}")
    
    return safe_rename_bool

def debug_file_structure():
    """Debug de la structure des fichiers comme dans scan_comic_files"""
    print("\n🔍 DEBUG STRUCTURE FICHIER")
    print("=" * 30)
    
    # Simuler exactement le fichier de votre log
    test_file = {
        'path': '/Users/vincentcruvellier/OneDrive/Ebooks/TEMP-GATEWAY/Kiff_-_01_-_Pulpeuses_amp_amp_g_233_n_233_reuses.pdf',
        'name': 'Kiff_-_01_-_Pulpeuses_amp_amp_g_233_n_233_reuses',
        'ext': 'pdf',  # SANS le point selon scan_comic_files
        'size': '10.5 MB',
        'folder': '/Users/vincentcruvellier/OneDrive/Ebooks/TEMP-GATEWAY'
    }
    
    print(f"Fichier test (votre cas exact):")
    print(f"  path: {test_file['path']}")
    print(f"  ext: '{test_file['ext']}'")
    
    # Test de détection PDF avec toutes les variantes
    test_variants = [
        ("f['ext'].lower() == 'pdf'", test_file['ext'].lower() == 'pdf'),
        ("f['ext'].lower() == '.pdf'", test_file['ext'].lower() == '.pdf'),
        ("f['path'].lower().endswith('.pdf')", test_file['path'].lower().endswith('.pdf')),
        ("'pdf' in f['ext'].lower()", 'pdf' in test_file['ext'].lower()),
    ]
    
    print("\nTests de détection PDF:")
    for test_desc, result in test_variants:
        print(f"  {test_desc}: {result}")
    
    # Test final (notre code corrigé)
    is_pdf = test_file['ext'].lower() == 'pdf' or test_file['path'].lower().endswith('.pdf')
    print(f"\nDétection finale (code corrigé): {is_pdf}")
    
    return test_file, is_pdf

def debug_metadata():
    """Debug des métadonnées Blacksad comme dans votre log"""
    print("\n🔍 DEBUG MÉTADONNÉES")
    print("=" * 20)
    
    # Métadonnées exactes de votre log
    meta = {
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
    
    print("Métadonnées Blacksad:")
    for key, value in meta.items():
        print(f"  {key}: {value}")
    
    # Test extraction avec code corrigé
    series = meta.get('serie_name', meta.get('series', ''))
    num = meta.get('album_number', meta.get('issue_number', meta.get('num', '')))
    title = meta.get('album_name', meta.get('title', ''))
    
    # Extract year from date field
    y = ''
    date_str = meta.get('date', meta.get('parution', meta.get('year', '')))
    if date_str:
        import re
        year_match = re.search(r'(\d{4})', str(date_str))
        if year_match:
            y = year_match.group(1)
    
    print(f"\nExtraction corrigée:")
    print(f"  series: '{series}'")
    print(f"  num: '{num}'")
    print(f"  title: '{title}'")
    print(f"  year: '{y}'")
    
    # Test cover URL pour SafeRename
    cover_url = meta.get('cover_url', meta.get('image_url', ''))
    print(f"  cover_url: {cover_url}")
    
    has_cover = bool(cover_url)
    print(f"\nCouverture disponible pour SafeRename: {has_cover}")
    
    return meta, has_cover

def create_debug_patch():
    """Crée un patch pour ajouter encore plus de debug au dropEvent"""
    print("\n🔧 CRÉATION PATCH DEBUG ULTRA-DÉTAILLÉ")
    print("=" * 45)
    
    debug_code = '''
    def dropEvent(self, event):
        print(f"[ULTRA-DEBUG] ========== DRAG & DROP STARTED ==========")
        print(f"[ULTRA-DEBUG] Event type: {type(event)}")
        
        # Internal drag & drop (DnD rename)
        if event.mimeData().hasFormat('application/x-comic-meta'):
            print(f"[ULTRA-DEBUG] Has comic meta format: TRUE")
            
            pos = event.position().toPoint() if hasattr(event, "position") else event.pos()
            row = self.rowAt(pos.y())
            print(f"[ULTRA-DEBUG] Target row: {row}")
            
            if row < 0:
                print(f"[ULTRA-DEBUG] Invalid row, returning")
                return
            
            payload = event.mimeData().data('application/x-comic-meta').data().decode()
            print(f"[ULTRA-DEBUG] Payload received, length: {len(payload)}")
            
            # Try to parse as JSON (complete metadata)
            try:
                import json
                meta = json.loads(payload)
                print(f"[ULTRA-DEBUG] JSON parsed successfully")
                print(f"[ULTRA-DEBUG] Meta type: {type(meta)}")
                print(f"[ULTRA-DEBUG] Meta keys: {list(meta.keys()) if isinstance(meta, dict) else 'Not a dict'}")
                
                # ... rest of your corrected extraction code ...
                
                # CRITIQUE: Vérification des conditions SafeRename
                f = self.main.files[row]
                print(f"[ULTRA-DEBUG] File object: {f}")
                
                is_pdf = f['ext'].lower() == 'pdf' or f['path'].lower().endswith('.pdf')
                safe_rename_enabled = self.main.settings.value('safe_rename', 'false') == 'true'
                
                print(f"[ULTRA-DEBUG] File extension raw: {repr(f['ext'])}")
                print(f"[ULTRA-DEBUG] File path: {f['path']}")
                print(f"[ULTRA-DEBUG] is_pdf calculation: {is_pdf}")
                print(f"[ULTRA-DEBUG] safe_rename_enabled: {safe_rename_enabled}")
                print(f"[ULTRA-DEBUG] Condition (safe_rename_enabled and is_pdf): {safe_rename_enabled and is_pdf}")
                
                if safe_rename_enabled and is_pdf:
                    print(f"[ULTRA-DEBUG] *** ENTERING SAFE RENAME CHECK ***")
                    # ... SafeRename code ...
                else:
                    print(f"[ULTRA-DEBUG] *** SKIPPING SAFE RENAME CHECK ***")
                    if not safe_rename_enabled:
                        print(f"[ULTRA-DEBUG] Reason: SafeRename disabled")
                    if not is_pdf:
                        print(f"[ULTRA-DEBUG] Reason: Not a PDF file")
    '''
    
    print("Code de debug ultra-détaillé créé.")
    print("Vous devez l'intégrer manuellement dans ui/tables.py")
    
    return True

if __name__ == "__main__":
    print("🚨 DEBUG ULTRA-DÉTAILLÉ SAFE RENAME DRAG & DROP")
    print("=" * 60)
    
    # 1. Debug paramètres
    settings_ok = debug_settings()
    
    # 2. Debug structure fichier
    test_file, pdf_detected = debug_file_structure()
    
    # 3. Debug métadonnées
    meta, cover_available = debug_metadata()
    
    # 4. Patch debug
    patch_created = create_debug_patch()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC COMPLET")
    print("=" * 60)
    print(f"SafeRename activé: {'✅' if settings_ok else '❌'}")
    print(f"PDF détecté: {'✅' if pdf_detected else '❌'}")
    print(f"Couverture disponible: {'✅' if cover_available else '❌'}")
    print(f"Debug patch créé: {'✅' if patch_created else '❌'}")
    
    print(f"\nCondition SafeRename (settings_ok AND pdf_detected): {'✅' if (settings_ok and pdf_detected) else '❌'}")
    
    if settings_ok and pdf_detected and cover_available:
        print("\n✅ TOUTES LES CONDITIONS SONT REMPLIES")
        print("SafeRename DEVRAIT s'activer en drag & drop")
        print("\n🎯 PROCHAINES ÉTAPES:")
        print("1. Lancez l'application avec debug ultra-détaillé")
        print("2. Testez le drag & drop")
        print("3. Vérifiez les logs [ULTRA-DEBUG]")
    else:
        print("\n❌ CONDITIONS NON REMPLIES - DIAGNOSTIC NÉCESSAIRE")
    
    print("=" * 60)
