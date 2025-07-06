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

    def validate_rename_with_move_option(self, current_folder: pathlib.Path, new_folder_name: str) -> Tuple[str, Optional[pathlib.Path]]:
        """
        Validate if a folder rename is possible and return the status with target path.
        
        Args:
            current_folder (pathlib.Path): Current folder path
            new_folder_name (str): Proposed new folder name
            
        Returns:
            Tuple[str, Optional[pathlib.Path]]: (status, target_path)
            Status can be: "valid", "same_name", "target_exists", "invalid"
        """
        if not new_folder_name:
            return "invalid", None
        
        if current_folder.name == new_folder_name:
            return "same_name", None
        
        new_folder_path = current_folder.parent / new_folder_name
        if new_folder_path.exists():
            return "target_exists", new_folder_path
        
        return "valid", new_folder_path
    
    def get_file_info(self, file_path: pathlib.Path) -> Dict[str, Any]:
        """
        Get file information including size and modification date.
        
        Args:
            file_path (pathlib.Path): Path to the file
            
        Returns:
            Dict[str, Any]: File information
        """
        try:
            stat = file_path.stat()
            import datetime
            
            # Format file size
            size_bytes = stat.st_size
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024**2:
                size_str = f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3:
                size_str = f"{size_bytes/(1024**2):.1f} MB"
            else:
                size_str = f"{size_bytes/(1024**3):.1f} GB"
            
            # Format modification date
            mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
            mod_date_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                'size_bytes': size_bytes,
                'size_str': size_str,
                'mod_time': mod_time,
                'mod_date_str': mod_date_str,
                'exists': True
            }
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error getting file info for {file_path}: {e}")
            return {
                'size_bytes': 0,
                'size_str': "Unknown",
                'mod_time': None,
                'mod_date_str': "Unknown",
                'exists': False,
                'error': str(e)
            }
    
    def check_file_conflict(self, src_path: pathlib.Path, dst_path: pathlib.Path) -> Dict[str, Any]:
        """
        Check if there's a file conflict and return detailed information.
        
        Args:
            src_path (pathlib.Path): Source file path
            dst_path (pathlib.Path): Destination file path
            
        Returns:
            Dict[str, Any]: Conflict information
        """
        if not dst_path.exists():
            return {
                'conflict': False,
                'action': 'move'
            }
        
        # Get info for both files
        src_info = self.get_file_info(src_path)
        dst_info = self.get_file_info(dst_path)
        
        return {
            'conflict': True,
            'src_info': src_info,
            'dst_info': dst_info,
            'action': 'conflict_resolution_needed'
        }
    
    def move_files_to_existing_folder(self, files_list: list, current_folder: pathlib.Path, 
                                     target_folder: pathlib.Path, conflict_handler=None) -> Dict[str, Any]:
        """
        Move selected files to an existing target folder with conflict resolution.
        
        Args:
            files_list (list): List of file dictionaries from the main app
            current_folder (pathlib.Path): Current folder path
            target_folder (pathlib.Path): Target folder path (must exist)
            conflict_handler (callable): Function to handle conflicts, should return 'overwrite', 'skip', or 'abort'
            
        Returns:
            Dict[str, Any]: Operation result with statistics
        """
        if not target_folder.exists():
            return {
                'success': False,
                'error': f"Target folder does not exist: {target_folder}",
                'moved_count': 0,
                'skipped_count': 0,
                'failed_count': 0
            }
        
        results = {
            'success': True,
            'moved_count': 0,
            'skipped_count': 0,
            'failed_count': 0,
            'errors': [],
            'moved_files': [],
            'skipped_files': [],
            'failed_files': []
        }
        
        for file_info in files_list:
            try:
                src_path = pathlib.Path(file_info['path'])
                dst_path = target_folder / src_path.name
                
                if self.debug:
                    print(f"[DEBUG] Processing file: {src_path.name}")
                
                # Check for conflicts
                conflict_info = self.check_file_conflict(src_path, dst_path)
                
                if conflict_info['conflict']:
                    if self.debug:
                        print(f"[DEBUG] Conflict detected for: {src_path.name}")
                    
                    if conflict_handler:
                        action = conflict_handler(src_path, dst_path, conflict_info)
                        if action == 'abort':
                            results['success'] = False
                            results['errors'].append(f"Operation aborted by user for file: {src_path.name}")
                            break
                        elif action == 'skip':
                            results['skipped_count'] += 1
                            results['skipped_files'].append(src_path.name)
                            if self.debug:
                                print(f"[DEBUG] Skipped: {src_path.name}")
                            continue
                        elif action != 'overwrite':
                            results['failed_count'] += 1
                            results['failed_files'].append(src_path.name)
                            results['errors'].append(f"Unknown action '{action}' for file: {src_path.name}")
                            continue
                    else:
                        # Default behavior: skip conflicts
                        results['skipped_count'] += 1
                        results['skipped_files'].append(src_path.name)
                        continue
                
                # Perform the move
                if self.debug:
                    print(f"[DEBUG] Moving {src_path} -> {dst_path}")
                
                import shutil
                shutil.move(str(src_path), str(dst_path))
                
                results['moved_count'] += 1
                results['moved_files'].append(src_path.name)
                
                if self.debug:
                    print(f"[DEBUG] Successfully moved: {src_path.name}")
                
            except Exception as e:
                results['failed_count'] += 1
                results['failed_files'].append(file_info.get('name', 'Unknown'))
                results['errors'].append(f"Error moving {file_info.get('name', 'Unknown')}: {str(e)}")
                results['success'] = False
                
                if self.debug:
                    print(f"[DEBUG] Error moving {file_info.get('name', 'Unknown')}: {e}")
        
        return results
    
    def cleanup_empty_folder(self, folder_path: pathlib.Path) -> Tuple[bool, str]:
        """
        Remove a folder if it's empty.
        
        Args:
            folder_path (pathlib.Path): Path to the folder to clean up
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not folder_path.exists():
                return True, "Folder does not exist"
            
            if not folder_path.is_dir():
                return False, "Path is not a directory"
            
            # Check if folder is empty
            try:
                # List all items (including hidden files)
                items = list(folder_path.iterdir())
                if items:
                    return False, f"Folder is not empty ({len(items)} items remaining)"
            except PermissionError:
                return False, "Permission denied to access folder contents"
            
            # Remove the empty folder
            folder_path.rmdir()
            
            if self.debug:
                print(f"[DEBUG] Successfully removed empty folder: {folder_path}")
            
            return True, "Empty folder removed successfully"
            
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Error removing folder {folder_path}: {e}")
            return False, f"Error removing folder: {str(e)}"
    
    def create_new_folder_with_move(self, files, current_folder, target_location, series_name, cleanup_empty=True):
        """
        Create a new folder at the specified location and move files there.
        
        Args:
            files (list): List of file dictionaries
            current_folder (pathlib.Path): Current folder path
            target_location (pathlib.Path): Parent directory for the new folder
            series_name (str): Name of the new folder
            cleanup_empty (bool): Whether to clean up empty source folder
            
        Returns:
            dict: Operation result with success status and details
        """
        if self.debug:
            print(f"[DEBUG] Creating new folder and moving files")
            print(f"  Current folder: {current_folder}")
            print(f"  Target location: {target_location}")
            print(f"  Series name: {series_name}")
        
        # Create target path
        target_path = target_location / series_name
        
        # Check if target already exists
        if target_path.exists():
            if self.debug:
                print(f"[DEBUG] Target folder already exists: {target_path}")
            # Move files to existing folder
            return self.move_files_to_existing_folder(files, current_folder, target_path)
        
        # Create new folder
        try:
            target_path.mkdir(parents=True, exist_ok=True)
            if self.debug:
                print(f"[DEBUG] Created new folder: {target_path}")
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to create folder: {str(e)}",
                'target_path': None
            }
        
        # Move files to new folder
        result = self.move_files_to_existing_folder(files, current_folder, target_path)
        
        # Clean up empty source folder if requested and operation was successful
        if cleanup_empty and result['success'] and result['moved_count'] > 0:
            cleanup_success, cleanup_message = self.cleanup_empty_folder(current_folder)
            result['cleanup_performed'] = cleanup_success
            result['cleanup_message'] = cleanup_message
        
        return result
    
    def handle_folder_rename_options(self, files, current_folder, options):
        """
        Handle folder rename operation based on user-selected options.
        
        Args:
            files (list): List of file dictionaries
            current_folder (pathlib.Path): Current folder path
            options (dict): Options dictionary from folder rename dialog
            
        Returns:
            dict: Operation result with success status and details
        """
        if self.debug:
            print(f"[DEBUG] Handling folder rename options")
            print(f"  Option: {options['option']}")
            print(f"  Create new folder: {options['create_new_folder']}")
            print(f"  Target location: {options['target_location']}")
            print(f"  Series name: {options['series_name']}")
        
        series_name = options['series_name']
        target_location = options['target_location']
        cleanup_empty = options['cleanup_empty']
        
        if options['option'] == 'rename_current':
            # Standard rename operation
            success, error_msg, new_folder_path = self.perform_rename(current_folder, series_name)
            
            if success:
                return {
                    'success': True,
                    'operation': 'rename',
                    'new_path': new_folder_path,
                    'message': f"Folder renamed to '{series_name}'"
                }
            else:
                return {
                    'success': False,
                    'operation': 'rename',
                    'error': error_msg
                }
        
        elif options['create_new_folder']:
            # Create new folder and move files
            return self.create_new_folder_with_move(
                files, current_folder, target_location, series_name, cleanup_empty
            )
        
        else:
            return {
                'success': False,
                'error': "Unknown operation option"
            }
