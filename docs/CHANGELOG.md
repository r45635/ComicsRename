# Changelog

All notable changes to the ComicsRename project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.2] - 2025-06-28

### 🐛 Bug Fixes

#### **Folder Renaming**
- Fixed missing brackets around style names in folder renaming functionality
- Enhanced style extraction logic to intelligently extract style from existing folder names when metadata doesn't provide it
- Added support for extracting style from both `[Style] Series` and `Style Series` folder name patterns
- Improved folder rename function to preserve and properly format style information with brackets

#### **User Interface**
- Fixed double confirmation dialog issue when editing folder names directly
- Added `editing_finished` flag to prevent multiple processing of folder rename events
- Preserved brackets `[]` in folder names during direct editing (double-click rename)
- Updated clean function to allow brackets in folder names while filtering other invalid characters

#### **Metadata Display**
- Reordered BDGest metadata display to show key fields first: serie_name, style, album_name, album_number, ISBN, date
- Restructured "Détails complets" section to show album_url and cover_url before nested details
- Enhanced URL display formatting with cleaner, clickable links
- Fixed duplicate section headers in metadata display

#### **Amazon Search Integration**
- Implemented Amazon search feature accessible via cover image click or context menu
- Added proper Amazon domain selection based on provider (BDGest → amazon.fr, ComicVine → amazon.com)
- Integrated partner ID (`bdma-21`) for affiliate tracking
- Added translation keys for Amazon search functionality in both English and French

### 🔧 Technical Improvements
- Enhanced debug logging for folder rename operations with comprehensive metadata inspection
- Improved style field detection across multiple possible field names (Style, Genre, Style/Genre, etc.)
- Added intelligent folder name pattern matching for style extraction
- Optimized metadata display logic with provider-specific field ordering

---

## [3.2.1] - 2025-06-27

### 🐛 Bug Fixes

#### **Folder Management**
- Fixed fallback logic for "Last used folder" to always try the exact stored path first
- Prevented automatic updating of `last_folder` setting after folder renames to maintain fallback functionality
- Enhanced folder search logic with exhaustive search in common locations (/Volumes, Desktop, Documents, Downloads)
- Improved handling of renamed folders while preserving original path references

#### **HTML Entity Decoding**
- Fixed HTML entities in BDGest search results (e.g., `&amp;` now displays as `&`)
- Added `_decode_html_entities()` function to properly decode HTML entities in series and album names
- Applied HTML decoding to all text content from BDGest including series names, album names, and metadata

#### **User Interface**
- Restored double-click editing functionality for folder names in the folder display
- Added `_confirm_and_rename_folder()` method for direct folder renaming from the UI
- Enhanced `EditableFolderLineEdit` with proper editing states and keyboard shortcuts (Enter to save, Escape to cancel)

### 🔧 Technical Improvements
- Improved error handling and user feedback for folder operations
- Enhanced folder path resolution with better debugging information
- Strengthened HTML parsing and entity decoding throughout the BDGest scraper
- Added comprehensive testing for folder management and HTML decoding features

---

## [3.0.1] - 2025-06-22

### 🐛 Bug Fixes

#### **macOS Compatibility**
- Fixed launcher script compatibility with macOS BSD grep (replaced `grep -P` with `awk` solution)
- Corrected main.py to import the correct class name (`ComicRenamer` instead of `ComicsFileRenamer`)
- Updated validation script to check for the correct class name
- Enhanced cross-platform compatibility for launcher scripts

#### **Application Entry Point**
- Fixed import error in main.py that prevented application startup
- Validated application can now start correctly on all platforms
- Improved error handling in the entry point

### 🔧 Technical Improvements
- Enhanced validation script with class existence checking
- Better error reporting for import issues
- Improved launcher script robustness

---

## [3.0.0] - 2024-12-XX

### 🚀 Major Features Added

#### **ComicVine Integration Enhancement**
- Enhanced ComicVine provider to fetch and display richer album/issue metadata
- Added `get_comicvine_issue_details()` function for detailed issue information
- ComicVine albums now display publication year, description, creative team, characters, and cover images
- Improved UI parity between BDGest and ComicVine modes

#### **BDGest Series Albums Feature**
- Added Series Name mode for BDGest with dropdown series selection
- Implemented `fetch_albums_by_series_id()` and `get_bdgest_albums_by_series_id()` functions
- Auto-population of albums when series are found
- Parallel processing for album detail fetching with configurable thread count
- Series cover images and metadata display

#### **Session Management Optimization**
- Persistent session management for BDGest provider
- Automatic authentication with session reuse
- Significant performance improvement for multiple searches
- Smart session invalidation and re-authentication

### 🔒 Security Improvements

#### **Credential Security**
- **BREAKING**: Removed all hardcoded credentials and API keys from source code
- Migrated to environment variables and `.env` file configuration
- Added secure credential storage using QSettings encryption
- Created `setup_credentials.py` script for secure credential setup
- Added `.env.example` template file

#### **Security Documentation**
- Added comprehensive `SECURITY.md` with security guidelines
- Updated `.gitignore` to protect sensitive files
- Added security audit recommendations

### 🎨 UI/UX Improvements

#### **Enhanced File Management**
- **Double-click to edit**: Folder names are now editable with validation and confirmation
- **Fixed drag-and-drop**: Folder renaming only triggers on intentional drag operations
- **Responsive cover images**: Cover art maintains aspect ratio and scales with panel resizing
- **Context menu fix**: Moved "Rafraîchir les dossiers" to the correct context menu (file table)

#### **Visual Enhancements**
- Improved album cover display with proper centering and scaling
- Better visual feedback during operations
- Enhanced dropdown behavior (closes immediately on selection)
- Removed unnecessary popup interruptions

### 📦 Project Infrastructure

#### **Package Management**
- Added `requirements.txt` with proper dependency specifications
- Created `pyproject.toml` for modern Python packaging
- Added `LICENSE` file (MIT License)

#### **Documentation**
- **Comprehensive README.md**: Complete project documentation with usage guide
- **DEVELOPMENT.md**: Detailed development environment setup guide
- **IMPLEMENTATION_SUMMARY.md**: Technical implementation details
- **CHANGELOG.md**: This changelog for tracking changes

#### **Development Tools**
- **Updated main.py**: Proper application entry point with error handling
- **validate_install.py**: Installation validation script
- **launch.sh/launch.bat**: Cross-platform launcher scripts
- **VS Code tasks**: Integrated development tasks

#### **Enhanced Testing**
- Multiple test scripts for different components:
  - `test_bdgest_series.py`: BDGest series functionality
  - `test_session_management.py`: Session management
  - `test_folder_rename.py`: Folder operations
  - `test_album_details.py`: Album metadata
  - `test_series_albums.py`: Series album fetching
  - `test_url_construction.py`: URL construction validation

### 🔧 Technical Improvements

#### **Performance Optimizations**
- Parallel metadata fetching with `ThreadPoolExecutor`
- Configurable concurrency with `max_workers` parameter
- Efficient session reuse and caching
- Optimized GUI responsiveness

#### **Code Quality**
- Enhanced error handling and validation
- Improved logging and debug output
- Better separation of concerns with provider pattern
- Type hints and documentation improvements

#### **Configuration Management**
- Environment variable support with `python-dotenv`
- Secure settings storage with QSettings
- Configuration validation and setup tools

### 🐛 Bug Fixes

#### **GUI Fixes**
- Fixed folder drag-and-drop triggering on hover
- Resolved dropdown staying open during album fetch
- Fixed unnecessary API calls in SeriesName mode
- Corrected context menu placement

#### **API Fixes**
- Fixed ComicVine API key loading and environment variable parsing
- Resolved `.env` file parsing issues (removed literal `\n` problems)
- Improved error handling for network requests
- Fixed session persistence across operations

#### **Stability Improvements**
- Better exception handling throughout the application
- Graceful degradation when services are unavailable
- Improved validation for user inputs
- Enhanced error messages and user feedback

### 📋 Dependencies

#### **Added**
- `python-dotenv>=1.0.0` for environment variable management

#### **Updated Requirements**
- `PySide6>=6.4.0` (GUI framework)
- `requests>=2.28.0` (HTTP requests)
- `beautifulsoup4>=4.11.0` (HTML parsing)
- `lxml>=4.9.0` (XML/HTML parser)

### 🚧 Migration Notes

#### **Breaking Changes**
- **Credentials**: Hardcoded credentials removed. Users must set up environment variables or use the credential setup script.
- **Configuration**: Settings now use environment variables. Existing installations may need credential reconfiguration.

#### **Migration Steps**
1. Run `python setup_credentials.py` to configure credentials securely
2. Or create a `.env` file based on `.env.example`
3. Install any missing dependencies: `pip install -r requirements.txt`
4. Run `python validate_install.py` to verify installation

### 🎯 Future Enhancements

#### **Planned Features**
- Additional metadata providers
- Bulk file renaming operations
- Advanced filtering and search options
- Plugin system for custom providers
- Automated comic file organization
- Metadata export/import functionality

#### **Technical Debt**
- Consider migrating to async/await for better performance
- Implement comprehensive unit test suite
- Add CI/CD pipeline
- Consider packaging as standalone executable

---

### 📊 Statistics

- **Files Added**: 15+ new files including documentation, scripts, and configuration
- **Files Modified**: Major updates to core application files
- **Security Issues Fixed**: All hardcoded credentials removed
- **Performance Improvements**: 3+ major optimizations implemented
- **New Features**: 5+ major features added
- **Bug Fixes**: 10+ issues resolved

---

**Full Changelog**: Compare changes from previous versions at the project repository.

## Previous Versions

### [2.0.0] - Previous Release
- Basic BDGest integration
- Simple GUI with file management
- Basic ComicVine support

### [1.0.0] - Initial Release
- Initial comic file renaming functionality
- Basic GUI implementation
