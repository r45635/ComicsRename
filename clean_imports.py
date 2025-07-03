#!/usr/bin/env python3
"""
Script de nettoyage automatique pour supprimer les imports redondants
"""
import re

def clean_redundant_imports():
    """Supprime les imports redondants de requests dans comicsFileRenamer_v3.py"""
    
    file_path = 'comicsFileRenamer_v3.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    cleaned_lines = []
    
    # Garde track des imports déjà vus
    global_import_seen = False
    
    for i, line in enumerate(lines):
        # Si c'est l'import global (ligne 19), on le garde
        if line.strip() == 'import requests' and not global_import_seen:
            global_import_seen = True
            cleaned_lines.append(line)
        # Si c'est un import local redondant, on le supprime
        elif line.strip() == 'import requests' and global_import_seen:
            print(f"Suppression de l'import redondant à la ligne {i+1}")
            continue
        else:
            cleaned_lines.append(line)
    
    # Écrit le fichier nettoyé
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    print("✅ Nettoyage des imports terminé")

if __name__ == "__main__":
    clean_redundant_imports()
