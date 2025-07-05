"""
Core components for ComicsRename application.
"""
from .providers import PROVIDERS, MetadataProvider, BDGestProvider, ComicVineProvider
from .workers import SearchWorker
from .folder_renamer import FolderRenamer
from .details_formatter import DetailsFormatter
from .album_populator import AlbumPopulator

__all__ = [
    'PROVIDERS',
    'MetadataProvider',
    'BDGestProvider', 
    'ComicVineProvider',
    'SearchWorker',
    'FolderRenamer',
    'DetailsFormatter',
    'AlbumPopulator'
]
