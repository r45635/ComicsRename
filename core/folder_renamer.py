"""
Folder renaming utilities for ComicsRename.

This module provides functionality to rename folders based on comic metadata,
including style extraction and name cleaning.
"""

import os
import pathlib
import re
from typing import Dict, Any, Optional, Tuple


class FolderRenamer:
    """Handles folder renaming operations based on comic metadata."""
    
    def __init__(self, debug: bool = False):
        """
        Initialize the FolderRenamer.
        
        Args:
            debug (bool): Enable debug output
        """
        self.debug = debug
    
    def extract_style_from_metadata(self, meta: Dict[str, Any]) -> str:
        """
        Extract style information from comic metadata.
        
        Args:
            meta (Dict[str, Any]): Comic metadata dictionary
            
        Returns:
            str: The extracted style or empty string if not found
        """
        style = ''
        details = meta.get('details', {})
        
        # Try multiple field names and locations for style information
        style_fields = ['Style', 'Genre', 'Style/Genre', 'Styles', 'Genres']
        
        # First try top-level meta
        for field in style_fields:
            if meta.get(field):
                style = meta.get(field)
                break
        
        # Then try details dict
        if not style and isinstance(details, dict):
            for field in style_fields:
                if field in details and details[field]:
                    style = details[field]
                    break
            
            # Try nested 'Détails' structure
            if not style and 'Détails' in details and isinstance(details['Détails'], dict):
                for field in style_fields:
                    if field in details['Détails'] and details['Détails'][field]:
                        style = details['Détails'][field]
                        break
        
        # Finally try the original 'style' field
        if not style:
            style = meta.get('style', '')
        
        return style
    
    def extract_style_from_folder_name(self, folder_name: str, serie_name: str) -> str:
        """
        Extract style from current folder name using pattern matching.
        
        Args:
            folder_name (str): Current folder name
            serie_name (str): Series name to match against
            
        Returns:
            str: The extracted style or empty string if not found
        """
        if not serie_name:
            return ''
        
        # Try to extract style from patterns like "[Style] Series" or "Style Series"
        # First try bracketed style: [Style] Series
        bracket_match = re.match(r'^\[([^\]]+)\]\s*(.+)$', folder_name)
        if bracket_match:
            potential_style = bracket_match.group(1).strip()
            potential_series = bracket_match.group(2).strip()
            # Check if the series part matches our serie_name
            if potential_series.lower() == serie_name.lower():
                if self.debug:
                    print(f"[DEBUG] Extracted style from bracketed folder name: '{potential_style}'")
                return potential_style
        
        # If not bracketed, try "Style Series" pattern
        if folder_name.lower().endswith(serie_name.lower()):
            potential_style = folder_name[:-len(serie_name)].strip()
            # Only consider it a style if it's a reasonable length and not empty
            if potential_style and len(potential_style) <= 30 and not potential_style.isdigit():
                if self.debug:
                    print(f"[DEBUG] Extracted style from folder name pattern: '{potential_style}'")
                return potential_style
        
        return ''
    
    def clean_name(self, name: str) -> str:
        """
        Clean a name for filesystem compatibility.
        
        Args:
            name (str): The name to clean
            
        Returns:
            str: The cleaned name
        """
        return ''.join(c for c in str(name) if c.isalnum() or c in "-_(),' ").strip()
    
    def clean_folder_name(self, name: str) -> str:
        """
        Clean a folder name for filesystem compatibility, allowing brackets.
        
        Args:
            name (str): The name to clean
            
        Returns:
            str: The cleaned name
        """
        return ''.join(c for c in str(name) if c.isalnum() or c in "-_(),' []").strip()
    
    def build_folder_name(self, serie_name: str, style: str = '') -> str:
        """
        Build a new folder name from series name and style.
        
        Args:
            serie_name (str): The series name
            style (str): The style/genre (optional)
            
        Returns:
            str: The formatted folder name
        """
        if not serie_name:
            return ''
        
        style_clean = self.clean_name(style)
        serie_clean = self.clean_name(serie_name)
        
        return f"[{style_clean}] {serie_clean}" if style_clean else serie_clean
    
    def get_folder_rename_info(self, current_folder: pathlib.Path, meta: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Get folder rename information from metadata.
        
        Args:
            current_folder (pathlib.Path): Current folder path
            meta (Dict[str, Any]): Comic metadata
            
        Returns:
            Tuple[str, str, str]: (serie_name, style, new_folder_name)
        """
        # Extract serie_name
        serie_name = meta.get('serie_name') or (meta.get('volume') or {}).get('name', '')
        
        # Extract style from metadata
        style = self.extract_style_from_metadata(meta)
        
        # If no style found in metadata, try to extract from current folder name
        if not style:
            style = self.extract_style_from_folder_name(current_folder.name, serie_name)
        
        # Build new folder name
        new_folder_name = self.build_folder_name(serie_name, style)
        
        return serie_name, style, new_folder_name
    
    def validate_rename(self, current_folder: pathlib.Path, new_folder_name: str) -> Tuple[bool, str]:
        """
        Validate if a folder rename is possible and necessary.
        
        Args:
            current_folder (pathlib.Path): Current folder path
            new_folder_name (str): Proposed new folder name
            
        Returns:
            Tuple[bool, str]: (is_valid, reason)
        """
        if not new_folder_name:
            return False, "Cannot determine new folder name"
        
        if current_folder.name == new_folder_name:
            return False, "Folder name is already the target name"
        
        new_folder_path = current_folder.parent / new_folder_name
        if new_folder_path.exists():
            return False, f"Target folder '{new_folder_name}' already exists"
        
        return True, ""
    
    def perform_rename(self, current_folder: pathlib.Path, new_folder_name: str) -> Tuple[bool, str, Optional[pathlib.Path]]:
        """
        Perform the actual folder rename operation.
        
        Args:
            current_folder (pathlib.Path): Current folder path
            new_folder_name (str): New folder name
            
        Returns:
            Tuple[bool, str, Optional[pathlib.Path]]: (success, error_message, new_path)
        """
        try:
            new_folder_path = current_folder.parent / new_folder_name
            
            if self.debug:
                print(f"[DEBUG] Renaming {current_folder} -> {new_folder_path}")
            
            os.rename(str(current_folder), str(new_folder_path))
            return True, "", new_folder_path
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Exception during rename: {e}")
            return False, str(e), None
    
    def debug_info(self, current_folder: pathlib.Path, serie_name: str, style: str, 
                   new_folder_name: str, meta: Dict[str, Any]) -> None:
        """
        Print debug information about the rename operation.
        
        Args:
            current_folder (pathlib.Path): Current folder path
            serie_name (str): Series name
            style (str): Style/genre
            new_folder_name (str): New folder name
            meta (Dict[str, Any]): Comic metadata
        """
        if not self.debug:
            return
        
        details = meta.get('details', {})
        
        print(f"[DEBUG] current_folder: {current_folder}")
        print(f"[DEBUG] current_folder.name: {current_folder.name}")
        print(f"[DEBUG] serie_name: '{serie_name}'")
        print(f"[DEBUG] extracted style: '{style}'")
        print(f"[DEBUG] style_clean: '{self.clean_name(style)}'")
        print(f"[DEBUG] serie_clean: '{self.clean_name(serie_name)}'")
        print(f"[DEBUG] new_folder_name: {new_folder_name}")
        print(f"[DEBUG] new_folder_path: {current_folder.parent / new_folder_name}")
        print(f"[DEBUG] meta keys: {list(meta.keys())}")
        print(f"[DEBUG] details keys: {list(details.keys()) if isinstance(details, dict) else 'Not a dict'}")
        if isinstance(details, dict) and 'Détails' in details:
            print(f"[DEBUG] nested Détails keys: {list(details['Détails'].keys()) if isinstance(details['Détails'], dict) else 'Not a dict'}")
