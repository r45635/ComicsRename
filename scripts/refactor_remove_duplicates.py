#!/usr/bin/env python3
"""
Script de refactorisation pour supprimer les doublons dans comicsFileRenamer_v3.py
"""
import re


def remove_duplicate_classes():
    """Supprime les classes dupliquées du fichier principal"""
    
    file_path = "comicsFileRenamer_v3.py"
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Classes à supprimer (avec leurs définitions complètes)
    patterns_to_remove = [
        # MetadataProvider et providers (lignes 52-418 environ)
        r'class MetadataProvider:.*?PROVIDERS = \{\s*\'ComicVine\': ComicVineProvider\(\),\s*\'BDGest\': BDGestProvider\(\),\s*\}',
        
        # SearchWorker (lignes 419-555 environ)  
        r'class SearchWorker\(QThread\):.*?(?=# ---------- Metadata Providers ----------|class DroppableLineEdit)',
        
        # DroppableLineEdit et EditableFolderLineEdit (lignes 556-687 environ)
        r'class DroppableLineEdit\(QLineEdit\):.*?class EditableFolderLineEdit\(QLineEdit\):.*?(?=class FileTable\(QTableWidget\):)',
        
        # FileTable (lignes 688-991 environ)
        r'class FileTable\(QTableWidget\):.*?(?=class AlbumTable\(QTableWidget\):)',
        
        # AlbumTable (lignes 992-1056 environ)
        r'class AlbumTable\(QTableWidget\):.*?(?=# ---------- Settings Dialog ----------)',
        
        # SettingsDialog (lignes 1057-1156 environ)
        r'class SettingsDialog\(QDialog\):.*?(?=class ComicRenamer\(QWidget\):)',
        
        # Lignes de commentaires orphelines
        r'# ---------- Metadata Providers ----------\s*\n',
        r'# ---------- Worker Thread for Search Operations ----------\s*\n',
        r'# ---------- Settings Dialog ----------\s*\n',
    ]
    
    # Appliquer les suppressions une par une
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Nettoyer les lignes vides multiples
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Sauvegarder le fichier modifié
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Doublons supprimés avec succès!")


if __name__ == "__main__":
    remove_duplicate_classes()
