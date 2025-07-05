"""
Base provider for metadata fetching.
"""
from abc import ABC, abstractmethod


class MetadataProvider(ABC):
    """Abstract base class for metadata providers."""
    
    @abstractmethod
    def search_series(self, query):
        """Search for series by query."""
        raise NotImplementedError
    
    @abstractmethod
    def search_albums(self, series_id_or_name):
        """Search for albums by series ID or name."""
        raise NotImplementedError
