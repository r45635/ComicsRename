#!/usr/bin/env python3
"""
Internationalization (i18n) system for ComicsRename

This module provides translation support for English and French languages.
Language selection is saved in user settings for future use.
"""

import json
import os
from typing import Dict, Any
from PySide6.QtCore import QSettings

class I18n:
    """Internationalization manager for ComicsRename"""
    
    def __init__(self):
        self.settings = QSettings("ComicsRename", "App")
        self.current_language = self.settings.value('language', 'en')  # Default to English
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load translation files for all supported languages"""
        try:
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            translations_dir = os.path.join(script_dir, 'translations')
            
            # Load English (default)
            en_path = os.path.join(translations_dir, 'en.json')
            if os.path.exists(en_path):
                with open(en_path, 'r', encoding='utf-8') as f:
                    self.translations['en'] = json.load(f)
            else:
                # Fallback to embedded English translations
                self.translations['en'] = self._get_default_english_translations()
            
            # Load French
            fr_path = os.path.join(translations_dir, 'fr.json')
            if os.path.exists(fr_path):
                with open(fr_path, 'r', encoding='utf-8') as f:
                    self.translations['fr'] = json.load(f)
            else:
                # Fallback to embedded French translations
                self.translations['fr'] = self._get_default_french_translations()
                
        except Exception as e:
            print(f"[ERROR] Failed to load translations: {e}")
            # Use embedded translations as fallback
            self.translations['en'] = self._get_default_english_translations()
            self.translations['fr'] = self._get_default_french_translations()
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return {
            'en': 'English',
            'fr': 'Français'
        }
    
    def set_language(self, language_code: str):
        """Set the current language and save to settings"""
        if language_code in self.translations:
            self.current_language = language_code
            self.settings.setValue('language', language_code)
        else:
            print(f"[WARNING] Language '{language_code}' not supported. Using English as fallback.")
            self.current_language = 'en'
            self.settings.setValue('language', 'en')
    
    def get_current_language(self) -> str:
        """Get the current language code"""
        return self.current_language
    
    def tr(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current language
        
        Args:
            key: Translation key (can use dot notation like 'ui.buttons.browse')
            **kwargs: Variables to substitute in the translation string
            
        Returns:
            Translated string with variable substitution
        """
        try:
            # Get the translation for the current language
            translation = self._get_nested_value(
                self.translations.get(self.current_language, {}), 
                key
            )
            
            # If not found, fallback to English
            if translation is None:
                translation = self._get_nested_value(
                    self.translations.get('en', {}), 
                    key
                )
            
            # If still not found, return the key itself
            if translation is None:
                print(f"[WARNING] Translation not found for key: {key}")
                return key
            
            # Substitute variables if provided
            if kwargs:
                try:
                    return translation.format(**kwargs)
                except (KeyError, ValueError) as e:
                    print(f"[WARNING] Failed to substitute variables in translation '{key}': {e}")
                    return translation
            
            return translation
            
        except Exception as e:
            print(f"[ERROR] Translation error for key '{key}': {e}")
            return key
    
    def _get_nested_value(self, data: Dict, key: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    def _get_default_english_translations(self) -> Dict:
        """Get default English translations (embedded fallback)"""
        return {
            "app": {
                "title": "Comic Renamer - Multi-Source",
                "settings": "Settings"
            },
            "ui": {
                "buttons": {
                    "browse": "Browse",
                    "search": "Search",
                    "settings": "Settings",
                    "rename": "Rename",
                    "rename_folder": "Rename Folder",
                    "refresh": "Refresh",
                    "ok": "OK",
                    "cancel": "Cancel",
                    "yes": "Yes",
                    "no": "No"
                },
                "labels": {
                    "folder": "Folder",
                    "search_term": "Search term",
                    "series_name_mode": "Series Name Mode",
                    "provider": "Provider",
                    "language": "Language"
                },
                "tooltips": {
                    "series_name_mode": "Search only in series names (BDGest only)",
                    "settings": "Application Settings",
                    "rename_folder": "Rename folder with selected series name"
                },
                "placeholders": {
                    "search": "Enter search term..."
                }
            },
            "dialogs": {
                "folder_selection": {
                    "title": "Folder Selection",
                    "message": "Where would you like to start browsing?",
                    "external_drives": "External drives (/Volumes)",
                    "last_folder": "Last used folder",
                    "home_folder": "Home folder"
                },
                "rename_confirmation": {
                    "title": "Rename Confirmation",
                    "file_message": "Rename '{old_name}' to '{new_name}'?",
                    "folder_message": "Rename folder '{old_name}' to '{new_name}'?"
                },
                "add_files": {
                    "title": "Add Files",
                    "message": "Add {count} file(s) to the current folder?"
                },
                "settings": {
                    "title": "Settings",
                    "language_label": "Language:",
                    "bdgest_credentials": "BDGest Credentials",
                    "username": "Username:",
                    "password": "Password:",
                    "comicvine_settings": "ComicVine Settings",
                    "api_key": "API Key:"
                }
            },
            "messages": {
                "errors": {
                    "no_results": "No albums found for this search.",
                    "no_series_found": "No series found for this search on BDGest.",
                    "no_albums_found": "No albums found for this search on BDGest.",
                    "file_not_exists": "Source file does not exist:\\n{path}",
                    "file_already_exists": "A file named '{name}' already exists in this folder.",
                    "folder_already_exists": "A folder named '{name}' already exists in this directory.",
                    "no_files_in_folder": "No files in the folder.",
                    "no_album_selected": "Please select an album from the list.",
                    "album_metadata_missing": "Album metadata missing.",
                    "cannot_determine_series": "Cannot determine series name.",
                    "rename_error": "Rename Error",
                    "error": "Error",
                    "no_active_folder": "No active folder for import.",
                    "unsupported_format": "Only PDF, EPUB, CBZ or CBR files are accepted.",
                    "could_not_open_file": "Could not open file:\\n{error}",
                    "could_not_reveal_file": "Could not reveal file:\\n{error}"
                },
                "warnings": {
                    "file_overwrite": "A file named '{name}' already exists.\\nOverwrite?"
                },
                "info": {
                    "folder_same_name": "Folder already has this name.",
                    "series_found": "{count} series found",
                    "albums_found": "{count} albums found"
                },
                "success": {
                    "rename_complete": "Rename completed successfully"
                }
            },
            "debug": {
                "image_load_failed": "Image load failed",
                "fetch_albums_failed": "Failed to fetch albums for series {series}",
                "clean_input": "clean() input",
                "clean_output": "clean() output"
            }
        }
    
    def _get_default_french_translations(self) -> Dict:
        """Get default French translations (embedded fallback)"""
        return {
            "app": {
                "title": "Comic Renamer - Multi-Source",
                "settings": "Paramètres"
            },
            "ui": {
                "buttons": {
                    "browse": "Parcourir",
                    "search": "Rechercher",
                    "settings": "Paramètres",
                    "rename": "Renommer",
                    "rename_folder": "Renommer le dossier",
                    "refresh": "Actualiser",
                    "ok": "OK",
                    "cancel": "Annuler",
                    "yes": "Oui",
                    "no": "Non"
                },
                "labels": {
                    "folder": "Dossier",
                    "search_term": "Terme de recherche",
                    "series_name_mode": "Mode nom de série",
                    "provider": "Fournisseur",
                    "language": "Langue"
                },
                "tooltips": {
                    "series_name_mode": "Rechercher uniquement dans les noms de séries (BDGest uniquement)",
                    "settings": "Paramètres de l'application",
                    "rename_folder": "Renommer le dossier avec le nom de la série sélectionnée"
                },
                "placeholders": {
                    "search": "Entrez un terme de recherche..."
                }
            },
            "dialogs": {
                "folder_selection": {
                    "title": "Sélection du dossier",
                    "message": "Où souhaitez-vous commencer la navigation ?",
                    "external_drives": "Disques externes (/Volumes)",
                    "last_folder": "Dernier dossier utilisé",
                    "home_folder": "Dossier personnel"
                },
                "rename_confirmation": {
                    "title": "Confirmation de renommage",
                    "file_message": "Renommer '{old_name}' en '{new_name}' ?",
                    "folder_message": "Renommer le dossier '{old_name}' en '{new_name}' ?"
                },
                "add_files": {
                    "title": "Ajouter des fichiers",
                    "message": "Ajouter {count} fichier(s) au dossier actuel ?"
                },
                "settings": {
                    "title": "Paramètres",
                    "language_label": "Langue :",
                    "bdgest_credentials": "Identifiants BDGest",
                    "username": "Nom d'utilisateur :",
                    "password": "Mot de passe :",
                    "comicvine_settings": "Paramètres ComicVine",
                    "api_key": "Clé API :"
                }
            },
            "messages": {
                "errors": {
                    "no_results": "Aucun album trouvé pour cette recherche.",
                    "no_series_found": "Aucune série trouvée pour cette recherche sur BDGest.",
                    "no_albums_found": "Aucun album trouvé pour cette recherche sur BDGest.",
                    "file_not_exists": "Le fichier source n'existe pas :\\n{path}",
                    "file_already_exists": "Un fichier nommé '{name}' existe déjà dans ce dossier.",
                    "folder_already_exists": "Un dossier nommé '{name}' existe déjà dans ce répertoire.",
                    "no_files_in_folder": "Aucun fichier dans le dossier.",
                    "no_album_selected": "Veuillez sélectionner un album dans la liste.",
                    "album_metadata_missing": "Métadonnées de l'album manquantes.",
                    "cannot_determine_series": "Impossible de déterminer le nom de la série.",
                    "rename_error": "Erreur de renommage",
                    "error": "Erreur",
                    "no_active_folder": "Aucun dossier actif pour l'import.",
                    "unsupported_format": "Seuls les fichiers PDF, EPUB, CBZ ou CBR sont acceptés.",
                    "could_not_open_file": "Impossible d'ouvrir le fichier :\\n{error}",
                    "could_not_reveal_file": "Impossible de révéler le fichier :\\n{error}"
                },
                "warnings": {
                    "file_overwrite": "Un fichier nommé '{name}' existe déjà.\\nÉcraser ?"
                },
                "info": {
                    "folder_same_name": "Le dossier porte déjà ce nom.",
                    "series_found": "{count} série(s) trouvée(s)",
                    "albums_found": "{count} album(s) trouvé(s)"
                },
                "success": {
                    "rename_complete": "Renommage terminé avec succès"
                }
            },
            "debug": {
                "image_load_failed": "Échec du chargement de l'image",
                "fetch_albums_failed": "Échec de la récupération des albums pour la série {series}",
                "clean_input": "entrée clean()",
                "clean_output": "sortie clean()"
            }
        }

# Global instance for easy access
_i18n = I18n()

def tr(key: str, **kwargs) -> str:
    """Global translation function for convenience"""
    return _i18n.tr(key, **kwargs)

def set_language(language_code: str):
    """Global function to set language"""
    _i18n.set_language(language_code)

def get_current_language() -> str:
    """Global function to get current language"""
    return _i18n.get_current_language()

def get_supported_languages() -> Dict[str, str]:
    """Global function to get supported languages"""
    return _i18n.get_supported_languages()

def get_i18n_instance():
    """Get the global i18n instance"""
    return _i18n
