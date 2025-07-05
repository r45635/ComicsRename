"""
Filename Generator for ComicsRename application.

Handles filename generation with metadata extraction, formatting, and validation.
"""

import re
import pathlib
from typing import Dict, Any, Optional, List


class FilenameGenerator:
    """Handles filename generation with consistent formatting and validation."""
    
    def __init__(self, debug: bool = False):
        """Initialize filename generator.
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        
        # Common year patterns
        self.year_patterns = [
            r'(\d{4})',  # Simple 4-digit year
            r'(\d{4})-\d{2}-\d{2}',  # ISO date format
            r'(\d{4})/\d{2}/\d{2}',  # US date format
            r'(\d{2})/\d{2}/(\d{4})',  # EU date format (captures second group)
        ]
        
        # Unicode character replacements for filename safety
        self.unicode_replacements = {
            '\u2019': "'",  # Right single quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '-',  # Em dash
            '\u00e9': 'e',  # é
            '\u00e8': 'e',  # è
            '\u00ea': 'e',  # ê
            '\u00eb': 'e',  # ë
            '\u00e0': 'a',  # à
            '\u00e1': 'a',  # á
            '\u00e2': 'a',  # â
            '\u00e4': 'a',  # ä
            '\u00e7': 'c',  # ç
            '\u00f1': 'n',  # ñ
            '\u00fc': 'u',  # ü
            '\u00f6': 'o',  # ö
        }
    
    def generate_filename(self, meta: Dict[str, Any], file_info: Dict[str, Any]) -> str:
        """Generate a formatted filename from metadata.
        
        Args:
            meta: Album metadata dictionary
            file_info: File information dictionary with 'ext' key
            
        Returns:
            str: Generated filename
        """
        if self.debug:
            print(f"[DEBUG] FilenameGenerator: Generating filename from meta: {list(meta.keys())}")
        
        # Extract components
        series = self._extract_series(meta)
        number = self._extract_number(meta)
        title = self._extract_title(meta)
        year = self._extract_year(meta)
        
        if self.debug:
            print(f"[DEBUG] FilenameGenerator: series='{series}', number='{number}', title='{title}', year='{year}'")
        
        # Build filename components
        components = []
        
        # Series name (required)
        if series:
            components.append(self.clean_string(series))
        
        # Album number (formatted)
        if number:
            components.append(self.format_number(number))
        
        # Album title (required)
        if title:
            components.append(self.clean_string(title))
        
        # Join components with separators
        base_name = ' - '.join(components)
        
        # Add year if available
        if year:
            base_name += f' ({year})'
        
        # Add file extension
        ext = file_info.get('ext', '').lstrip('.')
        if ext:
            filename = f"{base_name}.{ext}"
        else:
            filename = base_name
        
        if self.debug:
            print(f"[DEBUG] FilenameGenerator: Generated filename: '{filename}'")
        
        return filename
    
    def _extract_series(self, meta: Dict[str, Any]) -> str:
        """Extract series name from metadata."""
        # Try multiple possible fields
        series_fields = [
            'serie_name',    # BDGest
            'series',        # General
            'series_name',   # Alternative
            'volume',        # ComicVine volume
        ]
        
        for field in series_fields:
            value = meta.get(field)
            if value:
                # Handle nested volume structure
                if isinstance(value, dict) and 'name' in value:
                    return str(value['name'])
                elif isinstance(value, str):
                    return value
        
        return ''
    
    def _extract_number(self, meta: Dict[str, Any]) -> str:
        """Extract album/issue number from metadata."""
        # Try multiple possible fields
        number_fields = [
            'album_number',  # BDGest
            'num',           # General
            'issue_number',  # ComicVine
            'number',        # Alternative
        ]
        
        for field in number_fields:
            value = meta.get(field)
            if value:
                return str(value)
        
        return ''
    
    def _extract_title(self, meta: Dict[str, Any]) -> str:
        """Extract album/issue title from metadata."""
        # Try multiple possible fields
        title_fields = [
            'album_name',    # BDGest
            'title',         # General
            'name',          # Alternative
            'issue_title',   # ComicVine
        ]
        
        for field in title_fields:
            value = meta.get(field)
            if value:
                return str(value)
        
        return ''
    
    def _extract_year(self, meta: Dict[str, Any]) -> str:
        """Extract year from various date fields."""
        # Try multiple possible date fields
        date_fields = [
            'date',          # General
            'parution',      # BDGest
            'cover_date',    # ComicVine
            'year',          # Direct year field
            'date_parution', # Alternative BDGest
            'publication_date', # Alternative
        ]
        
        for field in date_fields:
            date_str = meta.get(field)
            if date_str:
                year = self._parse_year_from_string(str(date_str))
                if year:
                    return year
        
        return ''
    
    def _parse_year_from_string(self, date_str: str) -> Optional[str]:
        """Parse year from date string using various patterns."""
        if not date_str:
            return None
        
        for pattern in self.year_patterns:
            match = re.search(pattern, date_str)
            if match:
                # For patterns with multiple groups, use the appropriate one
                if len(match.groups()) > 1:
                    # For EU date format, use the second group (year)
                    year = match.group(2)
                else:
                    year = match.group(1)
                
                # Validate year (should be between 1800 and current year + 5)
                try:
                    year_int = int(year)
                    if 1800 <= year_int <= 2030:
                        return year
                except ValueError:
                    continue
        
        return None
    
    def format_number(self, number: str) -> str:
        """Format album/issue number with consistent padding."""
        if not number:
            return ''
        
        # Remove common prefixes
        number = number.strip()
        number = re.sub(r'^(#|No\.?|Issue\s*)', '', number, flags=re.IGNORECASE)
        
        # Try to parse as integer for padding
        try:
            num_int = int(number)
            # Pad with zeros to 2 digits for numbers 1-99
            if 1 <= num_int <= 99:
                return f"{num_int:02d}"
            else:
                return str(num_int)
        except ValueError:
            # Handle special cases like "1.5", "1a", etc.
            if re.match(r'^\d+[a-zA-Z]$', number):
                # Number with letter suffix (e.g., "1a")
                return number
            elif re.match(r'^\d+\.\d+$', number):
                # Decimal number (e.g., "1.5")
                return number
            else:
                # Return as-is for complex formats
                return number
    
    def clean_string(self, text: str) -> str:
        """Clean string for filename use while preserving readability."""
        if not text:
            return ''
        
        if self.debug:
            print(f"[DEBUG] FilenameGenerator: Cleaning string: '{text}'")
        
        # Convert to string if not already
        text = str(text)
        
        # Replace Unicode characters with ASCII equivalents
        for unicode_char, ascii_char in self.unicode_replacements.items():
            text = text.replace(unicode_char, ascii_char)
        
        # Remove or replace problematic characters for filenames
        # Keep: letters, numbers, spaces, hyphens, underscores, parentheses, apostrophes
        # Remove: other punctuation and special characters
        cleaned = re.sub(r"[^\w\s'\u2019\-\_()]", '', text, flags=re.UNICODE)
        
        # Replace multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        
        if self.debug:
            print(f"[DEBUG] FilenameGenerator: Cleaned string: '{cleaned}'")
        
        return cleaned
    
    def validate_filename(self, filename: str, max_length: int = 255) -> Dict[str, Any]:
        """Validate filename for filesystem compatibility.
        
        Args:
            filename: Filename to validate
            max_length: Maximum filename length (default 255)
            
        Returns:
            dict: {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'suggested_fix': str
            }
        """
        errors = []
        warnings = []
        
        # Check length
        if len(filename) > max_length:
            errors.append(f"Filename too long ({len(filename)} > {max_length} characters)")
        
        # Check for problematic characters
        problematic_chars = r'[<>:"/\\|?*]'
        if re.search(problematic_chars, filename):
            errors.append("Contains invalid characters: < > : \" / \\ | ? *")
        
        # Check for reserved names (Windows)
        reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + \
                        [f'COM{i}' for i in range(1, 10)] + \
                        [f'LPT{i}' for i in range(1, 10)]
        
        name_without_ext = pathlib.Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            errors.append(f"'{name_without_ext}' is a reserved filename")
        
        # Check for trailing periods or spaces
        if filename.endswith('.') or filename.endswith(' '):
            errors.append("Filename cannot end with period or space")
        
        # Warnings
        if len(filename) > 200:
            warnings.append("Filename is very long and may cause issues on some systems")
        
        # Generate suggested fix if there are errors
        suggested_fix = filename
        if errors:
            # Fix problematic characters
            suggested_fix = re.sub(r'[<>:"/\\|?*]', '_', suggested_fix)
            # Remove trailing periods/spaces
            suggested_fix = suggested_fix.rstrip('. ')
            # Truncate if too long
            if len(suggested_fix) > max_length:
                ext = pathlib.Path(suggested_fix).suffix
                max_base_len = max_length - len(ext)
                base = pathlib.Path(suggested_fix).stem[:max_base_len]
                suggested_fix = base + ext
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'suggested_fix': suggested_fix
        }
    
    def generate_safe_filename(self, meta: Dict[str, Any], file_info: Dict[str, Any]) -> str:
        """Generate a safe filename with automatic validation and fixing.
        
        Args:
            meta: Album metadata dictionary
            file_info: File information dictionary
            
        Returns:
            str: Safe filename
        """
        # Generate initial filename
        filename = self.generate_filename(meta, file_info)
        
        # Validate and fix if necessary
        validation = self.validate_filename(filename)
        
        if not validation['valid']:
            if self.debug:
                print(f"[DEBUG] FilenameGenerator: Filename validation failed: {validation['errors']}")
                print(f"[DEBUG] FilenameGenerator: Using suggested fix: '{validation['suggested_fix']}'")
            filename = validation['suggested_fix']
        
        return filename
    
    def extract_metadata_summary(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a summary of metadata fields for debugging.
        
        Args:
            meta: Metadata dictionary
            
        Returns:
            dict: Summary of extracted fields
        """
        return {
            'series': self._extract_series(meta),
            'number': self._extract_number(meta),
            'title': self._extract_title(meta),
            'year': self._extract_year(meta),
            'available_fields': list(meta.keys())
        }
