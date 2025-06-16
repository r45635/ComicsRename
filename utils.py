import os
import pathlib
import unicodedata

def list_comic_files(folder, extensions=None):
    """Retourne la liste des fichiers comics dans un dossier."""
    if extensions is None:
        extensions = ('.cbz', '.cbr', '.pdf', '.epub')
    return [f for f in os.listdir(folder) if f.lower().endswith(extensions)]

def scan_comic_files(folder, recursive=False):
    """Scans a folder for comic files and returns their metadata."""
    supported_ext = {'.pdf', '.epub', '.cbz', '.cbr'}
    files = []
    iterator = pathlib.Path(folder).rglob('*') if recursive else pathlib.Path(folder).glob('*')
    for p in sorted(iterator):
        if p.suffix.lower() in supported_ext:
            try:
                # Normalize path to NFC (macOS standard)
                p_norm = pathlib.Path(unicodedata.normalize('NFC', str(p)))
                size_mb = round(p_norm.stat().st_size / (1024*1024), 2)
            except FileNotFoundError:
                # Optionally log: print(f"[WARN] File not found: {p}")
                continue
            files.append({
                'path': p,
                'name': p.stem,
                'ext': p.suffix.lower()[1:],
                'size': f"{size_mb} MB",
                'folder': str(p.parent)
            })
    return files

def load_bdgest_credentials():
    # TODO: Securely load credentials
    BDGEST_USER = "r45635"
    BDGEST_PASS = "G9BxNeZcoU"
    return BDGEST_USER, BDGEST_PASS

def extract_year(date_str):
    """Extracts the year from a date string like '08/2022' or '2022'."""
    if not date_str:
        return ''
    if '/' in date_str:
        return date_str.split('/')[-1]
    return date_str[:4]
