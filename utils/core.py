import os
import pathlib
import unicodedata
import platform
import subprocess

def list_comic_files(folder, extensions=None):
    """Retourne la liste des fichiers comics dans un dossier."""
    if extensions is None:
        extensions = ('.cbz', '.cbr', '.pdf', '.epub')
    return [f for f in os.listdir(folder) if f.lower().endswith(extensions)]

def scan_comic_files(folder, recursive=False):
    """
    Scans a folder for comic files and returns their metadata.
    
    Args:
        folder (str): Path to the folder to scan
        recursive (bool): If True, recursively scans all subfolders and their 
                         subdirectories. If False, only scans the current folder.
    
    Returns:
        list: List of dictionaries containing file metadata:
              - path: pathlib.Path object
              - name: filename without extension
              - ext: file extension (without dot)
              - size: file size in MB as string
              - folder: parent folder path as string
    
    Note:
        This is NOT a search function but a folder scanning function.
        When recursive=True, it will traverse the entire directory tree
        starting from the given folder, finding all comic files in all
        subdirectories at any depth.
    """
    supported_ext = {'.pdf', '.epub', '.cbz', '.cbr'}
    files = []
    # Use rglob for recursive scanning (all subdirectories) or glob for current folder only
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
    """Load BDGest credentials from environment variables or settings"""
    import os
    from PySide6.QtCore import QSettings
    
    # Try environment variables first (for security)
    user = os.environ.get('BDGEST_USER')
    password = os.environ.get('BDGEST_PASS')
    
    if user and password:
        return user, password
    
    # Fallback to QSettings (stored by user in UI)
    settings = QSettings("ComicsRename", "App")
    user = settings.value('bdgest_user', '')
    password = settings.value('bdgest_pass', '')
    
    return user, password

def extract_year(date_str):
    """Extracts the year from a date string like '08/2022' or '2022'."""
    if not date_str:
        return ''
    if '/' in date_str:
        return date_str.split('/')[-1]
    return date_str[:4]

def open_file_cross_platform(file_path):
    """Opens a file using the default system application, cross-platform compatible."""
    try:
        # Check if file exists first
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
            
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.Popen(['open', file_path])
        elif system == "Windows":  # Windows
            os.startfile(file_path)
        elif system == "Linux":  # Linux
            subprocess.Popen(['xdg-open', file_path])
        else:
            raise OSError(f"Unsupported operating system: {system}")
        return True
    except Exception as e:
        return False, str(e)

def reveal_file_cross_platform(file_path):
    """Reveals/shows a file in the system file manager, cross-platform compatible."""
    try:
        # Check if file exists first
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
            
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.Popen(['open', '-R', file_path])
        elif system == "Windows":  # Windows
            subprocess.Popen(['explorer', '/select,', file_path])
        elif system == "Linux":  # Linux
            # Try different file managers (most common ones)
            file_managers = [
                ['nautilus', '--select', file_path],  # GNOME
                ['dolphin', '--select', file_path],   # KDE
                ['thunar', file_path],                # XFCE
                ['pcmanfm', file_path],               # LXDE
                ['nemo', file_path],                  # Cinnamon
            ]
            
            folder_path = os.path.dirname(file_path)
            for fm_cmd in file_managers:
                try:
                    subprocess.Popen(fm_cmd)
                    break
                except FileNotFoundError:
                    continue
            else:
                # Fallback: just open the folder
                subprocess.Popen(['xdg-open', folder_path])
        else:
            raise OSError(f"Unsupported operating system: {system}")
        return True
    except Exception as e:
        return False, str(e)

def get_system_info():
    """Returns information about the current operating system."""
    system = platform.system()
    return {
        'system': system,
        'is_windows': system == "Windows",
        'is_macos': system == "Darwin", 
        'is_linux': system == "Linux",
        'version': platform.version(),
        'platform': platform.platform(),
    }

def delete_file_cross_platform(file_path):
    """
    Delete a file with cross-platform support.
    
    Args:
        file_path (str): The path to the file to delete
        
    Returns:
        bool or tuple: True if successful, or a tuple (False, error_message) if failed
    """
    import os
    import sys
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        else:
            return (False, f"File not found: {file_path}")
    except Exception as e:
        return (False, str(e))
