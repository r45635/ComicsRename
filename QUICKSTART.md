# ComicsRename Quick Start Guide

## Getting Started (July 2025)

This document provides quick instructions for running the ComicsRename application.

### Requirements

- Python 3.8+
- PySide6 (Qt6)
- Other dependencies in requirements.txt

### Setup Instructions

1. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

### Recent Improvements

- ✅ **QuickView Enhancement**: Standalone module with improved pan/zoom controls
- ✅ **UI Error Handling**: Better error messages for search results
- ✅ **Translation System**: Complete English and French localizations
- ✅ **Cross-Platform Compatibility**: Improved file operations on Windows/macOS

### Testing

Run the comprehensive integration test:
```bash
python test_integration_comprehensive.py
```

### Notes

- BDGest API requires valid credentials (username/password)
- ComicVine API requires an API key
- Configure credentials in a `.env` file (see `.env.example` if available)

### License

MIT License - See LICENSE file for details.
