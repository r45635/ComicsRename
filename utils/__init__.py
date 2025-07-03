# Utils package initialization
# Import all functions from core module for compatibility

from .core import (
    scan_comic_files, 
    load_bdgest_credentials, 
    extract_year, 
    open_file_cross_platform, 
    reveal_file_cross_platform, 
    get_system_info,
    delete_file_cross_platform
)

from .icons import get_app_icon, get_icon_path

# Re-export for package access
__all__ = [
    'scan_comic_files',
    'load_bdgest_credentials', 
    'extract_year',
    'open_file_cross_platform',
    'reveal_file_cross_platform',
    'get_system_info',
    'delete_file_cross_platform',
    'get_app_icon',
    'get_icon_path'
]
