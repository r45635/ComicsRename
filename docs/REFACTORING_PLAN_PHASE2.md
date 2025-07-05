"""
ComicsRename - Code Refactoring Plan (Phase 2)

Following the SafeRename optimization work, this document outlines the next phase
of refactoring to improve code maintainability, modularity, and future extensibility.

## Current State Analysis

### Strengths
✅ Core business logic successfully modularized (FolderRenamer, DetailsFormatter, etc.)
✅ SafeRename optimization implemented with cover image caching
✅ Unified rename logic eliminates code duplication
✅ Provider abstraction layer established
✅ UI components properly separated

### Areas for Further Refactoring

#### 1. Image Management Module
The `_load_cover_image` method (75+ lines) handles multiple responsibilities:
- URL normalization for different providers
- HTTP requests with headers
- QPixmap creation and validation
- Local caching (temp file management)
- UI updates and scaling
- Error handling

**Proposed Solution:** Create `core/image_manager.py`
- `ImageManager` class with methods:
  - `load_and_cache_cover(url, meta)` - Main entry point
  - `normalize_url(url, provider)` - Provider-specific URL handling
  - `download_image(url)` - HTTP request handling
  - `cache_image(data, meta)` - Local storage management
  - `create_pixmap(data)` - QPixmap creation with validation

#### 2. SafeRename Module
The `_perform_safe_rename_check` method (80+ lines) is complex:
- Comparator selection (Qt vs Poppler)
- URL/path validation
- Result interpretation
- Dialog management
- Error handling with user interaction

**Proposed Solution:** Create `core/safe_rename_manager.py`
- `SafeRenameManager` class with methods:
  - `check_rename_safety(file_info, meta)` - Main entry point
  - `get_comparator()` - Comparator selection logic
  - `validate_inputs(file_info, meta)` - Input validation
  - `handle_comparison_result(result)` - Result processing
  - `handle_errors(error, file_info)` - Error handling

#### 3. Filename Generation Module
The filename generation logic in `_unified_rename_file` handles:
- Metadata extraction from different sources
- Year extraction from various date formats
- Number formatting
- String cleaning with Unicode support
- Path construction

**Proposed Solution:** Create `core/filename_generator.py`
- `FilenameGenerator` class with methods:
  - `generate_filename(meta, file_info)` - Main entry point
  - `extract_metadata(meta)` - Metadata extraction
  - `format_number(num)` - Number formatting
  - `clean_string(text)` - String sanitization
  - `extract_year(date_fields)` - Year extraction

#### 4. Settings Manager
Settings are accessed directly throughout the code:
- `self.settings.value()` called in multiple places
- No centralized defaults
- Type conversion scattered
- No validation

**Proposed Solution:** Create `core/settings_manager.py`
- `SettingsManager` class with methods:
  - `get_safe_rename_enabled()` - Type-safe boolean
  - `get_debug_mode()` - Type-safe boolean
  - `get_default_provider()` - String with validation
  - `get_skip_problematic_pdfs()` - Type-safe boolean
  - `set_last_folder(path)` - Path validation

#### 5. Error Handling Module
Error handling is inconsistent:
- Some errors show dialogs, others just print
- Mix of debug prints and logging
- No centralized error categorization

**Proposed Solution:** Create `core/error_handler.py`
- `ErrorHandler` class with methods:
  - `handle_file_error(error, file_path)` - File-specific errors
  - `handle_network_error(error, url)` - Network-specific errors
  - `handle_pdf_error(error, pdf_path)` - PDF-specific errors
  - `log_debug(message)` - Centralized debug logging

## Implementation Priority

### Phase 1: Core Utilities (Week 1)
1. `core/settings_manager.py` - Foundation for other modules
2. `core/error_handler.py` - Centralized error handling
3. `core/filename_generator.py` - Isolated, testable logic

### Phase 2: Complex Modules (Week 2)
1. `core/image_manager.py` - Image handling abstraction
2. `core/safe_rename_manager.py` - SafeRename logic extraction

### Phase 3: Integration & Testing (Week 3)
1. Update main file to use new modules
2. Add unit tests for each module
3. Integration testing
4. Performance validation

## Benefits Expected

### Code Quality
- Reduced cyclomatic complexity
- Better separation of concerns
- Easier unit testing
- Cleaner main file

### Maintainability
- Isolated changes to specific modules
- Easier debugging
- Better error messages
- Consistent settings handling

### Future Extensibility
- Easy to add new providers
- Pluggable image formats
- Configurable rename strategies
- Modular error handling

## Testing Strategy

### Unit Tests
Each new module should have comprehensive unit tests:
- `test_image_manager.py` - Mock HTTP requests, temp file handling
- `test_filename_generator.py` - Various metadata scenarios
- `test_settings_manager.py` - Settings validation
- `test_safe_rename_manager.py` - Mock comparator results

### Integration Tests
- End-to-end rename operations
- SafeRename with various PDF types
- Settings persistence
- Error recovery scenarios

## Migration Notes

### Backward Compatibility
- All existing functionality preserved
- No API changes for users
- Settings format unchanged
- File operations identical

### Performance
- No performance regressions expected
- Potential improvements through better caching
- Reduced code duplication
- More efficient error handling

## Success Metrics

### Code Quality Metrics
- Cyclomatic complexity < 10 per method
- Method length < 30 lines
- Class responsibility single-focused
- Test coverage > 80%

### Performance Metrics
- SafeRename performance maintained
- Memory usage stable
- UI responsiveness preserved
- Error recovery time improved

This refactoring plan builds on the successful SafeRename optimization and
continues the modularity improvements for long-term maintainability.
"""
