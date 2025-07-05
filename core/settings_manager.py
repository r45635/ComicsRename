"""
Settings Manager for ComicsRename application.

Provides centralized, type-safe access to application settings with validation.
"""

from PySide6.QtCore import QSettings
import os
import pathlib


class SettingsManager:
    """Centralized settings management with type safety and validation."""
    
    def __init__(self, app_name="ComicsRename", org_name="App"):
        """Initialize settings manager.
        
        Args:
            app_name (str): Application name for settings
            org_name (str): Organization name for settings
        """
        self.settings = QSettings(app_name, org_name)
        self.debug = self.get_debug_mode()
    
    # Boolean settings with type safety
    def get_debug_mode(self) -> bool:
        """Get debug mode setting."""
        return str(self.settings.value('debug', 'false')).lower() == 'true'
    
    def get_verbose_mode(self) -> bool:
        """Get verbose mode setting."""
        return str(self.settings.value('verbose', 'false')).lower() == 'true'
    
    def get_safe_rename_enabled(self) -> bool:
        """Get SafeRename enabled setting."""
        return str(self.settings.value('safe_rename', 'false')).lower() == 'true'
    
    def get_skip_problematic_pdfs(self) -> bool:
        """Get skip problematic PDFs setting."""
        return str(self.settings.value('skip_problematic_pdfs', 'false')).lower() == 'true'
    
    def get_series_name_mode(self) -> bool:
        """Get series name mode setting."""
        return str(self.settings.value('series_name_mode', 'false')).lower() == 'true'
    
    # String settings with validation
    def get_default_provider(self) -> str:
        """Get default provider with validation."""
        provider = str(self.settings.value("default_provider", "BDGest"))
        valid_providers = ["BDGest", "ComicVine"]
        
        if provider not in valid_providers:
            if self.debug:
                print(f"[DEBUG] Invalid provider '{provider}', using default 'BDGest'")
            provider = "BDGest"
            self.set_default_provider(provider)
        
        return provider
    
    def get_last_folder(self) -> str:
        """Get last used folder path."""
        return str(self.settings.value("last_folder", ""))
    
    def get_current_language(self) -> str:
        """Get current language setting."""
        return str(self.settings.value("language", "en"))
    
    # Numeric settings with validation
    def get_safe_rename_threshold(self) -> float:
        """Get SafeRename SSIM threshold."""
        try:
            threshold = float(str(self.settings.value("safe_rename_threshold", 0.7)))
            # Validate range
            if not (0.0 <= threshold <= 1.0):
                if self.debug:
                    print(f"[DEBUG] Invalid threshold '{threshold}', using default 0.7")
                threshold = 0.7
                self.set_safe_rename_threshold(threshold)
            return threshold
        except (ValueError, TypeError):
            if self.debug:
                print(f"[DEBUG] Invalid threshold format, using default 0.7")
            self.set_safe_rename_threshold(0.7)
            return 0.7
    
    def get_image_cache_size(self) -> int:
        """Get image cache size in MB."""
        try:
            size = int(str(self.settings.value("image_cache_size", 100)))
            # Validate range (1MB to 1GB)
            if not (1 <= size <= 1024):
                if self.debug:
                    print(f"[DEBUG] Invalid cache size '{size}', using default 100MB")
                size = 100
                self.set_image_cache_size(size)
            return size
        except (ValueError, TypeError):
            if self.debug:
                print(f"[DEBUG] Invalid cache size format, using default 100MB")
            self.set_image_cache_size(100)
            return 100
    
    # Setters with validation
    def set_debug_mode(self, enabled: bool):
        """Set debug mode."""
        self.settings.setValue('debug', 'true' if enabled else 'false')
        self.debug = enabled
    
    def set_verbose_mode(self, enabled: bool):
        """Set verbose mode."""
        self.settings.setValue('verbose', 'true' if enabled else 'false')
    
    def set_safe_rename_enabled(self, enabled: bool):
        """Set SafeRename enabled."""
        self.settings.setValue('safe_rename', 'true' if enabled else 'false')
    
    def set_skip_problematic_pdfs(self, enabled: bool):
        """Set skip problematic PDFs."""
        self.settings.setValue('skip_problematic_pdfs', 'true' if enabled else 'false')
    
    def set_series_name_mode(self, enabled: bool):
        """Set series name mode."""
        self.settings.setValue('series_name_mode', 'true' if enabled else 'false')
    
    def set_default_provider(self, provider: str):
        """Set default provider with validation."""
        valid_providers = ["BDGest", "ComicVine"]
        if provider not in valid_providers:
            raise ValueError(f"Invalid provider '{provider}'. Must be one of: {valid_providers}")
        self.settings.setValue("default_provider", provider)
    
    def set_last_folder(self, path: str):
        """Set last used folder with validation."""
        if path and not os.path.exists(path):
            if self.debug:
                print(f"[DEBUG] Warning: Setting last_folder to non-existent path: {path}")
        self.settings.setValue("last_folder", path)
    
    def set_current_language(self, language: str):
        """Set current language."""
        # Could add validation for supported languages here
        self.settings.setValue("language", language)
    
    def set_safe_rename_threshold(self, threshold: float):
        """Set SafeRename threshold with validation."""
        if not (0.0 <= threshold <= 1.0):
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")
        self.settings.setValue("safe_rename_threshold", threshold)
    
    def set_image_cache_size(self, size: int):
        """Set image cache size with validation."""
        if not (1 <= size <= 1024):
            raise ValueError(f"Cache size must be between 1 and 1024 MB, got {size}")
        self.settings.setValue("image_cache_size", size)
    
    # Utility methods
    def get_fallback_folder_path(self, stored_path: str) -> str:
        """Get fallback folder path when stored path doesn't exist."""
        if not stored_path:
            return str(pathlib.Path.home())
        
        path = pathlib.Path(stored_path)
        
        # Try parent directories until we find one that exists
        while path.parent != path:  # Stop at root
            if path.parent.exists():
                if self.debug:
                    print(f"[DEBUG] Fallback folder: {path.parent}")
                return str(path.parent)
            path = path.parent
        
        # If all else fails, use home directory
        if self.debug:
            print(f"[DEBUG] All fallback attempts failed, using home directory")
        return str(pathlib.Path.home())
    
    def sync(self):
        """Sync settings to persistent storage."""
        self.settings.sync()
    
    def get_all_settings(self) -> dict:
        """Get all settings as a dictionary for debugging."""
        result = {}
        for key in self.settings.allKeys():
            result[key] = self.settings.value(key)
        return result
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        if self.debug:
            print("[DEBUG] Resetting all settings to defaults")
        
        self.settings.clear()
        
        # Set explicit defaults
        self.set_debug_mode(False)
        self.set_verbose_mode(False)
        self.set_safe_rename_enabled(False)
        self.set_skip_problematic_pdfs(False)
        self.set_series_name_mode(False)
        self.set_default_provider("BDGest")
        self.set_current_language("en")
        self.set_safe_rename_threshold(0.7)
        self.set_image_cache_size(100)
        
        self.sync()
