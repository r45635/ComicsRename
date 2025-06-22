#!/usr/bin/env python3
"""
String Extraction Tool for ComicsRename

This script extracts all translatable strings from the ComicsRename codebase
and generates a comprehensive list for translation purposes.
"""

import os
import re
import json
import ast
from typing import Set, List, Dict, Tuple

class StringExtractor:
    def __init__(self):
        self.found_strings = set()
        self.string_contexts = {}  # Maps strings to their file/line contexts
        
    def extract_from_file(self, file_path: str) -> Set[str]:
        """Extract strings from a Python file"""
        print(f"Extracting from: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract strings from various patterns
            strings = set()
            
            # 1. QMessageBox strings
            strings.update(self._extract_qmessagebox_strings(content, file_path))
            
            # 2. setText, setWindowTitle, setToolTip, etc.
            strings.update(self._extract_qt_setter_strings(content, file_path))
            
            # 3. String literals in UI context
            strings.update(self._extract_ui_strings(content, file_path))
            
            # 4. addItem strings
            strings.update(self._extract_additem_strings(content, file_path))
            
            # 5. Print statements with user messages
            strings.update(self._extract_user_messages(content, file_path))
            
            return strings
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return set()
    
    def _extract_qmessagebox_strings(self, content: str, file_path: str) -> Set[str]:
        """Extract strings from QMessageBox calls"""
        strings = set()
        
        patterns = [
            r'QMessageBox\.(?:information|warning|critical|question)\([^,]+,\s*["\']([^"\']+)["\']',
            r'QMessageBox\.(?:information|warning|critical|question)\([^,]+,\s*["\']([^"\']+)["\'][^,]*,\s*["\']([^"\']+)["\']',
            r'\.setText\(\s*["\']([^"\']+)["\']',
            r'\.setWindowTitle\(\s*["\']([^"\']+)["\']',
            r'\.addButton\(\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                for group in match.groups():
                    if group and self._is_translatable_string(group):
                        strings.add(group)
                        self._add_context(group, file_path, self._get_line_number(content, match.start()))
        
        return strings
    
    def _extract_qt_setter_strings(self, content: str, file_path: str) -> Set[str]:
        """Extract strings from Qt setter methods"""
        strings = set()
        
        patterns = [
            r'\.setText\(\s*["\']([^"\']+)["\']',
            r'\.setWindowTitle\(\s*["\']([^"\']+)["\']',
            r'\.setToolTip\(\s*["\']([^"\']+)["\']',
            r'\.setStatusTip\(\s*["\']([^"\']+)["\']',
            r'\.setPlaceholderText\(\s*["\']([^"\']+)["\']',
            r'\.setHeaderLabels\(\s*\[["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                string_val = match.group(1)
                if self._is_translatable_string(string_val):
                    strings.add(string_val)
                    self._add_context(string_val, file_path, self._get_line_number(content, match.start()))
        
        return strings
    
    def _extract_ui_strings(self, content: str, file_path: str) -> Set[str]:
        """Extract UI-related string literals"""
        strings = set()
        
        # Look for string literals that appear to be UI text
        string_literals = re.finditer(r'["\']([^"\']+)["\']', content)
        
        for match in string_literals:
            string_val = match.group(1)
            line_num = self._get_line_number(content, match.start())
            line_content = content.split('\n')[line_num - 1].strip()
            
            # Check if this string appears to be UI-related
            if self._is_ui_context(line_content) and self._is_translatable_string(string_val):
                strings.add(string_val)
                self._add_context(string_val, file_path, line_num)
        
        return strings
    
    def _extract_additem_strings(self, content: str, file_path: str) -> Set[str]:
        """Extract strings from addItem calls"""
        strings = set()
        
        pattern = r'\.addItem\(\s*["\']([^"\']+)["\']'
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            string_val = match.group(1)
            if self._is_translatable_string(string_val):
                strings.add(string_val)
                self._add_context(string_val, file_path, self._get_line_number(content, match.start()))
        
        return strings
    
    def _extract_user_messages(self, content: str, file_path: str) -> Set[str]:
        """Extract user-facing messages from print statements and similar"""
        strings = set()
        
        # Look for print statements that contain user messages (not debug)
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'print(' in line and not any(debug_marker in line.lower() for debug_marker in ['[debug]', '[error]', '[warn]', '[info]']):
                # Extract string from print statement
                match = re.search(r'print\([^"\']*["\']([^"\']+)["\']', line)
                if match:
                    string_val = match.group(1)
                    if self._is_translatable_string(string_val) and len(string_val) > 3:
                        strings.add(string_val)
                        self._add_context(string_val, file_path, i + 1)
        
        return strings
    
    def _is_translatable_string(self, string_val: str) -> bool:
        """Check if a string should be translated"""
        if not string_val or len(string_val.strip()) < 2:
            return False
        
        # Skip technical strings
        skip_patterns = [
            r'^[A-Z_]+$',  # Constants
            r'^https?://',  # URLs
            r'^/[/\w-]+',  # File paths
            r'^\w+\.\w+',  # File extensions or module names
            r'^[0-9.]+$',  # Numbers
            r'^[a-z_]+$',  # Variable names
            r'^\[[A-Z]+\]',  # Debug markers like [DEBUG]
            r'^ComicsRename$',  # App name
            r'^App$',  # Simple identifiers
            r'^\w+_\w+$',  # Snake case identifiers
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, string_val.strip()):
                return False
        
        # Skip strings that are just formatting
        if string_val.strip() in ['', ' ', '\n', '\t']:
            return False
            
        return True
    
    def _is_ui_context(self, line_content: str) -> bool:
        """Check if a line appears to be in a UI context"""
        ui_indicators = [
            'QMessageBox', 'setText', 'setWindowTitle', 'setToolTip',
            'addItem', 'setPlaceholderText', 'setStatusTip',
            'QLabel', 'QPushButton', 'setHeaderLabels'
        ]
        
        return any(indicator in line_content for indicator in ui_indicators)
    
    def _get_line_number(self, content: str, position: int) -> int:
        """Get line number for a position in the content"""
        return content[:position].count('\n') + 1
    
    def _add_context(self, string_val: str, file_path: str, line_num: int):
        """Add context information for a string"""
        if string_val not in self.string_contexts:
            self.string_contexts[string_val] = []
        self.string_contexts[string_val].append({
            'file': os.path.basename(file_path),
            'line': line_num
        })
    
    def extract_all_strings(self, directory: str) -> Dict:
        """Extract all strings from Python files in directory"""
        python_files = []
        
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        all_strings = set()
        
        for file_path in python_files:
            strings = self.extract_from_file(file_path)
            all_strings.update(strings)
            self.found_strings.update(strings)
        
        return {
            'strings': sorted(list(all_strings)),
            'contexts': self.string_contexts,
            'files_processed': len(python_files),
            'total_strings': len(all_strings)
        }
    
    def generate_translation_template(self, output_file: str):
        """Generate a template for translators"""
        template = {
            "extraction_info": {
                "total_strings": len(self.found_strings),
                "files_processed": len(set(ctx['file'] for contexts in self.string_contexts.values() for ctx in contexts))
            },
            "strings_to_translate": []
        }
        
        for string_val in sorted(self.found_strings):
            contexts = self.string_contexts.get(string_val, [])
            template["strings_to_translate"].append({
                "original": string_val,
                "english": string_val,  # Template for English
                "french": "",  # To be filled by translator
                "contexts": contexts,
                "notes": self._generate_translation_notes(string_val, contexts)
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"Translation template saved to: {output_file}")

    def _generate_translation_notes(self, string_val: str, contexts: List[Dict]) -> str:
        """Generate helpful notes for translators"""
        notes = []
        
        # Context-based notes
        for ctx in contexts:
            if 'QMessageBox' in str(ctx):
                notes.append("Used in dialog/message box")
            elif 'setWindowTitle' in str(ctx):
                notes.append("Used as window title")
            elif 'setToolTip' in str(ctx):
                notes.append("Used as tooltip text")
        
        # Content-based notes
        if '{' in string_val and '}' in string_val:
            notes.append("Contains variables for substitution")
        
        if '\\n' in string_val:
            notes.append("Contains line breaks")
        
        return "; ".join(notes) if notes else ""

def main():
    """Main function to run the string extraction"""
    print("ComicsRename String Extraction Tool")
    print("=" * 40)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Initialize extractor
    extractor = StringExtractor()
    
    # Extract strings
    print(f"Scanning directory: {script_dir}")
    results = extractor.extract_all_strings(script_dir)
    
    print(f"\n📊 Extraction Results:")
    print(f"   Files processed: {results['files_processed']}")
    print(f"   Strings found: {results['total_strings']}")
    
    # Generate reports
    output_dir = os.path.join(script_dir, 'translation_work')
    os.makedirs(output_dir, exist_ok=True)
    
    # Save extraction results
    results_file = os.path.join(output_dir, 'extracted_strings.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Generate translation template
    template_file = os.path.join(output_dir, 'translation_template.json')
    extractor.generate_translation_template(template_file)
    
    # Generate simple list for quick reference
    simple_list_file = os.path.join(output_dir, 'strings_list.txt')
    with open(simple_list_file, 'w', encoding='utf-8') as f:
        f.write("ComicsRename - Extracted Strings for Translation\\n")
        f.write("=" * 50 + "\\n\\n")
        for i, string_val in enumerate(sorted(results['strings']), 1):
            f.write(f"{i:3d}. {string_val}\\n")
    
    print(f"\n📁 Output files created in: {output_dir}")
    print(f"   • extracted_strings.json    - Complete extraction data")
    print(f"   • translation_template.json - Template for translators")
    print(f"   • strings_list.txt         - Simple list for reference")
    
    print(f"\n🎯 Top 10 strings to translate:")
    for i, string_val in enumerate(sorted(results['strings'])[:10], 1):
        print(f"   {i:2d}. {string_val}")
    
    if len(results['strings']) > 10:
        print(f"   ... and {len(results['strings']) - 10} more")

if __name__ == "__main__":
    main()
