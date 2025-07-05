"""
Error Handler for ComicsRename application.

Provides centralized error handling with consistent logging and user feedback.
"""

import os
import traceback
from typing import Optional, Dict, Any
from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtWidgets import QMessageBox as QMsgBox


class ErrorHandler:
    """Centralized error handling with logging and user feedback."""
    
    def __init__(self, parent_widget: Optional[QWidget] = None, debug: bool = False):
        """Initialize error handler.
        
        Args:
            parent_widget: Parent widget for message boxes
            debug: Enable debug logging
        """
        self.parent = parent_widget
        self.debug = debug
        self.error_counts = {}
    
    def log_debug(self, message: str, category: str = "DEBUG"):
        """Log debug message if debug mode is enabled.
        
        Args:
            message: Debug message to log
            category: Category for the message (DEBUG, INFO, WARNING, ERROR)
        """
        if self.debug:
            print(f"[{category}] {message}")
    
    def log_error(self, message: str, error: Optional[Exception] = None):
        """Log error message with optional exception details.
        
        Args:
            message: Error message to log
            error: Optional exception object
        """
        error_msg = f"[ERROR] {message}"
        if error:
            error_msg += f": {str(error)}"
        
        print(error_msg)
        
        if self.debug and error:
            print(f"[DEBUG] Exception traceback:")
            traceback.print_exc()
    
    def handle_file_error(self, error: Exception, file_path: str, operation: str = "processing") -> bool:
        """Handle file-related errors.
        
        Args:
            error: Exception that occurred
            file_path: Path to the file that caused the error
            operation: Operation being performed (e.g., "renaming", "reading")
            
        Returns:
            bool: True if user wants to continue, False to abort
        """
        error_type = type(error).__name__
        file_name = os.path.basename(file_path)
        
        self.log_error(f"File {operation} failed for {file_name}", error)
        
        # Track error frequency
        key = f"{error_type}_{operation}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Common file errors
        if isinstance(error, FileNotFoundError):
            title = "File Not Found"
            message = f"The file '{file_name}' could not be found.\n\nIt may have been moved, deleted, or renamed."
        elif isinstance(error, PermissionError):
            title = "Permission Denied"
            message = f"Cannot access '{file_name}' due to insufficient permissions.\n\nPlease check file permissions or try running as administrator."
        elif isinstance(error, OSError):
            title = "File System Error"
            message = f"A file system error occurred while {operation} '{file_name}':\n\n{str(error)}"
        else:
            title = "File Error"
            message = f"An error occurred while {operation} '{file_name}':\n\n{str(error)}"
        
        if self.parent:
            reply = QMessageBox.critical(
                self.parent,
                title,
                message + "\n\nDo you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            return reply == QMessageBox.StandardButton.Yes
        else:
            print(f"[ERROR] {title}: {message}")
            return False
    
    def handle_network_error(self, error: Exception, url: str, operation: str = "download") -> bool:
        """Handle network-related errors.
        
        Args:
            error: Exception that occurred
            url: URL that caused the error
            operation: Operation being performed (e.g., "downloading", "fetching")
            
        Returns:
            bool: True if user wants to retry, False to skip
        """
        error_type = type(error).__name__
        
        self.log_error(f"Network {operation} failed for {url}", error)
        
        # Track error frequency
        key = f"{error_type}_{operation}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Common network errors
        if "timeout" in str(error).lower():
            title = "Network Timeout"
            message = f"The request timed out while {operation} from:\n{url}\n\nThis might be due to a slow internet connection or server issues."
        elif "connection" in str(error).lower():
            title = "Connection Error"
            message = f"Could not connect to server while {operation} from:\n{url}\n\nPlease check your internet connection."
        elif "404" in str(error) or "not found" in str(error).lower():
            title = "Resource Not Found"
            message = f"The requested resource was not found:\n{url}\n\nThe URL may be incorrect or the resource may have been moved."
        elif "403" in str(error) or "forbidden" in str(error).lower():
            title = "Access Denied"
            message = f"Access was denied while {operation} from:\n{url}\n\nThe server may require authentication or the resource may be restricted."
        else:
            title = "Network Error"
            message = f"A network error occurred while {operation} from:\n{url}\n\nError: {str(error)}"
        
        if self.parent:
            reply = QMessageBox.critical(
                self.parent,
                title,
                message + "\n\nDo you want to retry?",
                QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Ignore | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Retry
            )
            return reply == QMessageBox.StandardButton.Retry
        else:
            print(f"[ERROR] {title}: {message}")
            return False
    
    def handle_pdf_error(self, error: Exception, pdf_path: str, operation: str = "processing") -> Dict[str, Any]:
        """Handle PDF-related errors.
        
        Args:
            error: Exception that occurred
            pdf_path: Path to the PDF file
            operation: Operation being performed
            
        Returns:
            dict: {
                'skip': bool,           # True if user wants to skip
                'retry': bool,          # True if user wants to retry
                'abort': bool,          # True if user wants to abort
                'disable_feature': bool # True if user wants to disable the feature
            }
        """
        error_type = type(error).__name__
        file_name = os.path.basename(pdf_path)
        
        self.log_error(f"PDF {operation} failed for {file_name}", error)
        
        # Track error frequency
        key = f"{error_type}_pdf_{operation}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Determine error category
        error_str = str(error).lower()
        if "password" in error_str or "encrypted" in error_str:
            title = "Password Protected PDF"
            message = (f"The PDF '{file_name}' is password protected or encrypted.\n\n"
                      f"ComicsRename cannot process password-protected files.")
            category = "password"
        elif "corrupted" in error_str or "invalid" in error_str or "damaged" in error_str:
            title = "Corrupted PDF"
            message = (f"The PDF '{file_name}' appears to be corrupted or damaged.\n\n"
                      f"The file may be incomplete or have structural issues.")
            category = "corrupted"
        elif "unsupported" in error_str or "format" in error_str:
            title = "Unsupported PDF Format"
            message = (f"The PDF '{file_name}' uses an unsupported format or version.\n\n"
                      f"Some PDFs use advanced features that are not supported.")
            category = "unsupported"
        elif "no pages" in error_str or "empty" in error_str:
            title = "Empty PDF"
            message = (f"The PDF '{file_name}' appears to be empty or contains no readable pages.\n\n"
                      f"This might indicate a problem with the file.")
            category = "empty"
        else:
            title = "PDF Processing Error"
            message = (f"An error occurred while processing '{file_name}':\n\n"
                      f"{str(error)}")
            category = "unknown"
        
        if self.parent:
            # Create detailed dialog with multiple options
            msg_box = QMessageBox(self.parent)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            
            if category in ["password", "corrupted", "unsupported"]:
                msg_box.setInformativeText(
                    "This can happen with:\n"
                    "• Password-protected PDFs\n"
                    "• Corrupted PDF files\n"
                    "• Unsupported PDF formats\n"
                    "• Files with special security features\n\n"
                    "💡 You can disable SafeRename for problematic PDFs in Settings"
                )
            
            skip_btn = msg_box.addButton("Skip This File", QMessageBox.ButtonRole.AcceptRole)
            retry_btn = msg_box.addButton("Retry", QMessageBox.ButtonRole.ActionRole)
            disable_btn = msg_box.addButton("Disable SafeRename", QMessageBox.ButtonRole.ActionRole)
            abort_btn = msg_box.addButton("Cancel Operation", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.setDefaultButton(skip_btn)
            msg_box.exec()
            
            clicked = msg_box.clickedButton()
            
            return {
                'skip': clicked == skip_btn,
                'retry': clicked == retry_btn,
                'abort': clicked == abort_btn,
                'disable_feature': clicked == disable_btn
            }
        else:
            print(f"[ERROR] {title}: {message}")
            return {
                'skip': True,
                'retry': False,
                'abort': False,
                'disable_feature': False
            }
    
    def handle_metadata_error(self, error: Exception, source: str, query: str) -> bool:
        """Handle metadata retrieval errors.
        
        Args:
            error: Exception that occurred
            source: Data source (e.g., "BDGest", "ComicVine")
            query: Search query that failed
            
        Returns:
            bool: True if user wants to continue, False to abort
        """
        error_type = type(error).__name__
        
        self.log_error(f"Metadata retrieval failed for {source} query '{query}'", error)
        
        # Track error frequency
        key = f"{error_type}_metadata_{source.lower()}"
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        title = f"{source} Search Error"
        message = f"Failed to retrieve metadata from {source} for query '{query}'.\n\nError: {str(error)}"
        
        if self.parent:
            reply = QMessageBox.warning(
                self.parent,
                title,
                message + "\n\nDo you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            return reply == QMessageBox.StandardButton.Yes
        else:
            print(f"[ERROR] {title}: {message}")
            return False
    
    def show_info(self, title: str, message: str):
        """Show information message to user.
        
        Args:
            title: Dialog title
            message: Message to display
        """
        self.log_debug(f"Info: {title} - {message}", "INFO")
        
        if self.parent:
            QMessageBox.information(self.parent, title, message)
        else:
            print(f"[INFO] {title}: {message}")
    
    def show_warning(self, title: str, message: str) -> bool:
        """Show warning message to user.
        
        Args:
            title: Dialog title
            message: Message to display
            
        Returns:
            bool: True if user wants to continue, False otherwise
        """
        self.log_debug(f"Warning: {title} - {message}", "WARNING")
        
        if self.parent:
            reply = QMessageBox.warning(
                self.parent,
                title,
                message + "\n\nDo you want to continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            return reply == QMessageBox.StandardButton.Yes
        else:
            print(f"[WARNING] {title}: {message}")
            return False
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of errors that occurred.
        
        Returns:
            dict: Error type counts
        """
        return self.error_counts.copy()
    
    def reset_error_counts(self):
        """Reset error counters."""
        self.error_counts.clear()
        self.log_debug("Error counters reset")
