"""
Metadata providers for comic information fetching.
"""
from .base import MetadataProvider
from .bdgest import BDGestProvider
from .comicvine import ComicVineProvider

# Provider registry
PROVIDERS = {
    'ComicVine': ComicVineProvider(),
    'BDGest': BDGestProvider(),
}

__all__ = [
    'MetadataProvider',
    'BDGestProvider', 
    'ComicVineProvider',
    'PROVIDERS'
]
