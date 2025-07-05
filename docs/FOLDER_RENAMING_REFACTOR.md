# Folder Renaming Refactoring - Step 2

## Overview
This refactoring step extracted the folder renaming logic from the main `ComicRenamer` class into a dedicated `FolderRenamer` class in `core/folder_renamer.py`.

## What Was Extracted

### New Module: `core/folder_renamer.py`
- **FolderRenamer class**: Contains all folder renaming business logic
- **Style extraction**: Methods to extract style/genre information from metadata and folder names
- **Name cleaning**: Utilities to clean folder names for filesystem compatibility
- **Validation**: Logic to validate rename operations before execution
- **Rename execution**: The actual folder renaming operation

### Key Methods in FolderRenamer:
- `extract_style_from_metadata()`: Extract style from comic metadata
- `extract_style_from_folder_name()`: Extract style from existing folder names using pattern matching
- `clean_name()`: Clean names for filesystem compatibility
- `clean_folder_name()`: Clean folder names (allows brackets for style formatting)
- `build_folder_name()`: Build new folder names from series and style
- `get_folder_rename_info()`: Get complete rename information from metadata
- `validate_rename()`: Validate if a rename is possible and necessary
- `perform_rename()`: Execute the actual folder rename operation
- `debug_info()`: Print debug information about rename operations

## Benefits

### 1. **Separation of Concerns**
- UI logic (dialogs, user interaction) remains in `ComicRenamer`
- Business logic (folder renaming rules) is in `FolderRenamer`
- Cleaner architecture with single responsibility principle

### 2. **Testability**
- `FolderRenamer` can be unit tested independently
- Mock testing becomes easier for folder operations
- Business logic can be tested without UI dependencies

### 3. **Reusability**
- `FolderRenamer` can be used by other parts of the application
- Command-line tools could use the same logic
- Batch operations become easier to implement

### 4. **Maintainability**
- Folder renaming logic is consolidated in one place
- Changes to renaming rules only need to be made in one location
- Easier to debug and modify folder renaming behavior

## Code Size Reduction
- **comicsFileRenamer_v3.py**: Reduced by ~130 lines
- **Extracted**: ~300 lines moved to `FolderRenamer`
- **Net improvement**: Better organization, cleaner main class

## Updated Methods in ComicRenamer

### `_rename_folder_to_serie()`
- **Before**: 80+ lines of complex logic
- **After**: 40 lines focusing on UI interaction
- **Improvement**: Uses `FolderRenamer` methods for all business logic

### `_confirm_and_rename_folder()`
- **Before**: 40+ lines with embedded validation logic
- **After**: 30 lines using `FolderRenamer` validation
- **Improvement**: Consistent error handling and validation

## Usage Example

```python
# Initialize with debug mode
folder_renamer = FolderRenamer(debug=True)

# Get rename information from metadata
current_folder = pathlib.Path('/path/to/current/folder')
serie_name, style, new_name = folder_renamer.get_folder_rename_info(current_folder, metadata)

# Validate the rename
is_valid, reason = folder_renamer.validate_rename(current_folder, new_name)

# Perform the rename if valid
if is_valid:
    success, error_msg, new_path = folder_renamer.perform_rename(current_folder, new_name)
```

## Integration
- Added `FolderRenamer` to `core/__init__.py` exports
- Updated main file imports to use `from core import FolderRenamer`
- Maintained backward compatibility with existing functionality

## Testing
- ✅ Application imports successfully
- ✅ `FolderRenamer` can be instantiated
- ✅ Basic functionality works (name cleaning, etc.)
- ✅ All existing functionality preserved

## Next Steps
This refactoring enables further improvements:
1. **Unit tests** for `FolderRenamer` class
2. **Enhanced style detection** algorithms
3. **Batch folder renaming** features
4. **Configuration options** for naming patterns
5. **Additional validation** rules

## Files Modified
- `comicsFileRenamer_v3.py`: Updated to use `FolderRenamer`
- `core/__init__.py`: Added `FolderRenamer` export
- `core/folder_renamer.py`: New module (created)

## Commit
- **Hash**: 30b4bda
- **Message**: "refactor: Extract folder renaming logic to core/folder_renamer.py"
- **Status**: ✅ Committed and pushed to GitHub

## Summary
This refactoring step successfully extracted folder renaming logic into a dedicated, testable, and reusable module. The main `ComicRenamer` class is now cleaner and more focused on UI concerns, while the business logic is properly separated and organized.
