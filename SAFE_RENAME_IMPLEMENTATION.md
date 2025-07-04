# Safe Rename Feature Implementation (Qt-Native)

## Overview

The Safe Rename feature has been successfully implemented in ComicsRename using **Qt's native PDF rendering**, maintaining consistency with the existing QuickView functionality. When enabled, this feature compares the first page of PDF files with the selected album cover before renaming, helping prevent incorrect file associations.

**✅ NEW: Qt-Native Implementation**  
The Safe Rename feature now uses the same PDF rendering approach as QuickView (`QPdfDocument.render()`), eliminating the need for external dependencies like Poppler.

**✅ Drag-and-Drop Support**  
The Safe Rename feature works with both the "Rename" button and drag-and-drop operations from the albums table to files.

## New Files Created

### 1. `pdf_cover_comparator_qt.py` (NEW - Qt-Native)
- Core functionality for PDF cover comparison using Qt's native PDF rendering
- Uses `QPdfDocument.render()` - same as QuickView
- No Poppler dependency required
- Uses SSIM (Structural Similarity Index) to compare images
- Handles both local files and remote URLs
- Automatic cleanup of temporary files
- Configurable similarity threshold (default: 0.7)

### 2. `pdf_cover_comparator.py` (LEGACY - Poppler-based)
- Original implementation using pdf2image/Poppler
- Kept for fallback compatibility
- Will be phased out in favor of Qt-native version

### 3. `cover_comparison_dialog.py` 
- GUI dialog for manual verification when covers don't match
- Shows PDF first page and album cover side-by-side
- Displays similarity score and threshold
- Allows user to proceed or cancel the rename operation
- Fully internationalized (English/French)

### 4. `test_safe_rename_qt.py` (NEW)
- Test script specifically for Qt-native implementation
- Shows implementation comparison
- Emphasizes consistency with QuickView
- Can test with actual PDF files and cover URLs

### 5. `test_safe_rename.py` (LEGACY)
- Original test script for Poppler-based implementation
- Still functional for testing fallback version

### 6. `debug_drag_drop.py`
- Debug script specifically for drag-and-drop functionality
- Tests metadata serialization/deserialization
- Validates Safe Rename logic conditions

## Modified Files

### 1. `requirements.txt`
**SIMPLIFIED DEPENDENCIES:**
```
PySide6>=6.4.0          # Already required - includes PDF support
requests>=2.28.0        # Already required
beautifulsoup4>=4.11.0  # Already required  
lxml>=4.9.0            # Already required
python-dotenv>=1.0.0   # Already required
pyinstaller>=5.7.0     # Already required
pillow>=9.0.0          # Already required
opencv-python>=4.5.0   # For image processing
scikit-image>=0.19.0   # For SSIM comparison
```
**REMOVED:**
- ~~pdf2image~~ (no longer needed)
- ~~poppler dependency~~ (no longer needed)

### 2. `comicsFileRenamer_v3.py`
- Added "Safe Rename" checkbox to SettingsDialog
- Modified `_rename_selected()` method to include cover comparison
- Enhanced `_perform_safe_rename_check()` method with Qt-native priority:
  - **First**: Try Qt-native implementation (`pdf_cover_comparator_qt`)
  - **Fallback**: Use Poppler-based implementation (`pdf_cover_comparator`)
- **Enhanced drag-and-drop system** to support Safe Rename:
  - Modified `mouseMoveEvent()` to include full metadata in drag data
  - Modified `dropEvent()` to check for Safe Rename before renaming
  - Added metadata serialization/deserialization for drag-and-drop
- Graceful handling of missing dependencies

### 3. `main.py`
- Updated version number to 3.4.3

### 4. Translation Files
- `translations/en.json`: Added English translations for new UI elements
- `translations/fr.json`: Added French translations for new UI elements

## How It Works

### Qt-Native PDF Rendering (Primary Method)
```python
# Same approach as QuickView
pdf_doc = QPdfDocument()
pdf_doc.load(pdf_path)
page_size = pdf_doc.pagePointSize(0)
image_size_qt = QSize(int(width), int(height))
rendered_image = pdf_doc.render(0, image_size_qt)
```

### Button Rename
1. **Settings**: User enables "Safe Rename" in the Settings dialog
2. **File Selection**: When renaming a PDF file with Safe Rename enabled:
   - Extract first page using Qt's native PDF rendering
   - Get album cover from metadata
   - Compare images using SSIM algorithm
3. **Good Match**: If similarity score > threshold (0.7), rename proceeds automatically
4. **Poor Match**: If similarity score < threshold, show comparison dialog

### Drag-and-Drop Rename
1. **Drag Start**: When dragging an album from the albums table:
   - Include both text payload (for display) and full metadata (for Safe Rename)
   - Metadata is JSON-serialized and included in drag data
2. **Drop**: When dropping on a file:
   - Deserialize metadata from drag data
   - Check if Safe Rename is enabled and file is PDF
   - If yes, perform cover comparison before rename
   - Show comparison dialog if covers don't match
3. **Fallback**: If metadata can't be deserialized, drag-and-drop works as before (without Safe Rename)

## Technical Advantages

### Consistency with QuickView
- **Same PDF Library**: Both use Qt's `QPdfDocument`
- **Same Rendering Method**: Both use `.render()` with similar parameters
- **Same Quality**: Consistent image quality and rendering behavior
- **Same Dependencies**: No additional system dependencies required

### Simplified Architecture
- **Fewer Dependencies**: Eliminated pdf2image and Poppler requirements
- **Native Integration**: Uses Qt APIs already available in the application
- **Cross-Platform**: Qt's PDF rendering works consistently across platforms
- **Maintenance**: Easier to maintain with fewer external dependencies

### Performance Benefits
- **Faster Startup**: No need to locate Poppler binaries
- **Better Error Handling**: Qt provides clearer error messages
- **Memory Efficiency**: Direct image rendering without intermediate files

## Installation Requirements

**SIMPLIFIED - Only 2 additional packages needed:**
```bash
pip install opencv-python scikit-image
```

**NO LONGER NEEDED:**
- ~~pdf2image~~ 
- ~~poppler-utils~~ (macOS: ~~brew install poppler~~)
- ~~poppler~~ (Linux: ~~apt-get install poppler-utils~~)

## Implementation Priority

The system now uses this priority order:

1. **Qt-Native** (`pdf_cover_comparator_qt.py`) - **PRIMARY**
   - Uses Qt's native PDF rendering
   - Consistent with QuickView
   - No external dependencies

2. **Poppler-based** (`pdf_cover_comparator.py`) - **FALLBACK** 
   - Uses pdf2image library
   - Only if Qt-native fails
   - Will be deprecated

## Configuration

- **Threshold**: Currently hardcoded to 0.7 (can be made configurable later)
- **Image Size**: Comparison images resized to 256x256 for processing
- **Display Size**: Dialog images scaled to ~350x450 with scroll bars
- **Timeout**: Network requests have 30-second timeout
- **Rendering Quality**: 150 DPI equivalent (same as QuickView export)

## Error Handling

The implementation gracefully handles various error scenarios:
- Missing Qt PDF modules (shows warning, falls back to Poppler)
- Missing opencv/scikit-image (shows warning, allows bypass)
- Network failures (shows error, asks to proceed)
- Invalid PDF files (shows error, asks to proceed)
- Missing cover URLs (skips comparison, proceeds normally)
- Metadata serialization errors (falls back to normal drag-and-drop)

## Testing

### Test Qt-Native Implementation
```bash
python test_safe_rename_qt.py
```

### Test with Actual Files
```bash
python test_safe_rename_qt.py /path/to/comic.pdf https://example.com/cover.jpg
```

### Test Original Implementation (Fallback)
```bash
python test_safe_rename.py
```

### Debug Drag-and-Drop
```bash
python debug_drag_drop.py
```

## Debugging

To debug Safe Rename issues:
1. Enable debug mode in application settings
2. Check console output for debug messages:
   - `[DEBUG] Safe Rename (Qt-native):` - Using Qt implementation
   - `[DEBUG] Safe Rename (Poppler-based):` - Using fallback
3. Use the Qt-native test script to verify functionality
4. Verify that albums have cover URLs in their metadata

## Future Enhancements

Potential improvements for future versions:
1. Configurable similarity threshold in settings
2. Support for other comic formats (CBR/CBZ) using same Qt approach
3. Batch processing with automatic decisions
4. Machine learning-based comparison
5. Cover quality assessment
6. User feedback integration for threshold tuning
7. Performance optimizations for large files

## Migration Notes

### For Existing Users
- No action required - Qt-native version is used automatically
- If Qt PDF modules unavailable, system falls back to Poppler version
- Existing Poppler installations continue to work as fallback

### For Developers
- Primary implementation moved to `pdf_cover_comparator_qt.py`
- Original implementation in `pdf_cover_comparator.py` kept for compatibility
- QuickView and Safe Rename now share consistent PDF handling approach

## Translation Keys

All translation keys remain the same:
- `ui.labels.safe_rename`
- `ui.tooltips.safe_rename` 
- `dialogs.cover_comparison.*` (multiple keys for the comparison dialog)

All keys are available in both English and French.
