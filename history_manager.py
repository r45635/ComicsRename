"""
History manager for tracking file and directory rename operations.
Supports undoing up to a fixed number of past renames.
"""
import os
import json
import pathlib
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any


class HistoryManager:
    """Manages a history of file/folder rename operations with undo capability."""
    
    def __init__(self, max_size: int = 5):
        """
        Initialize the history manager.
        
        Args:
            max_size: Maximum number of operations to keep in history
        """
        self.max_size = max_size
        self._history: List[Dict[str, Any]] = []
        self._history_file = pathlib.Path.home() / '.comicsrename_history.json'
        self._load_history()
    
    def record_file_rename(self, old_path: str, new_path: str) -> None:
        """
        Record a file rename operation.
        
        Args:
            old_path: Original file path
            new_path: New file path after rename
        """
        operation = {
            'type': 'file',
            'old_path': str(old_path),
            'new_path': str(new_path),
            'timestamp': datetime.now().isoformat(),
            'original_name': pathlib.Path(old_path).name,
            'new_name': pathlib.Path(new_path).name
        }
        self._add_operation(operation)
    
    def record_folder_rename(self, old_path: str, new_path: str) -> None:
        """
        Record a folder rename operation.
        
        Args:
            old_path: Original folder path
            new_path: New folder path after rename
        """
        operation = {
            'type': 'folder',
            'old_path': str(old_path),
            'new_path': str(new_path),
            'timestamp': datetime.now().isoformat(),
            'original_name': pathlib.Path(old_path).name,
            'new_name': pathlib.Path(new_path).name
        }
        self._add_operation(operation)
    
    def _add_operation(self, operation: Dict[str, Any]) -> None:
        """Add an operation to history and maintain size limit."""
        self._history.append(operation)
        
        # Trim history to max size
        if len(self._history) > self.max_size:
            self._history.pop(0)
        
        self._save_history()
    
    def undo_last(self) -> Tuple[bool, str]:
        """
        Undo the last recorded operation.
        
        Returns:
            Tuple of (success, message)
        """
        if not self._history:
            return False, "Aucune opération à annuler"
        
        operation = self._history.pop()
        
        try:
            old_path = operation['old_path']
            new_path = operation['new_path']
            
            # Check if the current (new) path exists
            if not os.path.exists(new_path):
                self._history.append(operation)  # Put it back
                return False, f"Le fichier/dossier '{pathlib.Path(new_path).name}' n'existe plus"
            
            # Check if the target (old) path would conflict
            if os.path.exists(old_path):
                self._history.append(operation)  # Put it back
                return False, f"Impossible d'annuler: '{pathlib.Path(old_path).name}' existe déjà"
            
            # Perform the undo rename
            os.rename(new_path, old_path)
            
            self._save_history()
            
            op_type = "dossier" if operation['type'] == 'folder' else "fichier"
            return True, f"Annulation réussie: {op_type} '{operation['new_name']}' → '{operation['original_name']}'"
            
        except Exception as e:
            # Put the operation back in history if undo failed
            self._history.append(operation)
            self._save_history()
            return False, f"Erreur lors de l'annulation: {str(e)}"
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the current history of operations."""
        return self._history.copy()
    
    def can_undo(self) -> bool:
        """Check if there are operations that can be undone."""
        return len(self._history) > 0
    
    def get_last_operation_summary(self) -> Optional[str]:
        """Get a summary of the last operation for display."""
        if not self._history:
            return None
        
        op = self._history[-1]
        op_type = "Dossier" if op['type'] == 'folder' else "Fichier"
        return f"{op_type}: '{op['original_name']}' → '{op['new_name']}'"
    
    def clear_history(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._save_history()
    
    def _load_history(self) -> None:
        """Load history from disk."""
        try:
            if self._history_file.exists():
                with open(self._history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = data.get('operations', [])
                    
                    # Trim to max size in case it was changed
                    if len(self._history) > self.max_size:
                        self._history = self._history[-self.max_size:]
        except Exception as e:
            print(f"Erreur lors du chargement de l'historique: {e}")
            self._history = []
    
    def _save_history(self) -> None:
        """Save history to disk."""
        try:
            data = {
                'version': '1.0',
                'max_size': self.max_size,
                'operations': self._history
            }
            
            with open(self._history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de l'historique: {e}")
