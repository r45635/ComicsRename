# ComicsRename - Development Guide

## 📁 Project Structure

```
ComicsRename/
├── main.py                      # Application entry point
├── comicsFileRenamer_v3.py     # Main GUI application class
├── bdgest_scraper_api.py       # BDGest API scraper
├── comicVine_scraper_api.py    # ComicVine API scraper  
├── utils.py                    # Utility functions
├── i18n.py                     # Internationalization system
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
├── ComicsRename.spec          # PyInstaller build spec
├── ui/                        # UI components
│   ├── __init__.py
│   ├── dialogs.py            # Dialog windows
│   ├── quick_view.py         # PDF quick view component
│   └── tables.py             # Custom table widgets
├── translations/              # Internationalization files
│   ├── en.json              # English translations
│   └── fr.json              # French translations
├── icons/                     # Application icons
├── docs/                      # Documentation
├── tests/                     # Test files
├── dev-tools/                 # Development utilities
├── screenshots/               # Application screenshots
└── src/                      # Future code organization
```

## 🚀 Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

3. **Run tests:**
   ```bash
   python -m pytest tests/
   ```

## 🛠️ Development

### Core Files
- `main.py` - Entry point, handles application initialization
- `comicsFileRenamer_v3.py` - Main application logic and GUI
- `*_scraper_api.py` - Web scraping modules for metadata
- `utils.py` - Shared utility functions
- `i18n.py` - Translation and localization system

### UI Components
- `ui/tables.py` - Custom table widgets with drag & drop
- `ui/dialogs.py` - Settings and configuration dialogs
- `ui/quick_view.py` - PDF preview functionality

### Building
```bash
# Build executable with PyInstaller
pyinstaller ComicsRename.spec
```

## 📝 Code Style

- Follow PEP 8 Python style guide
- Use descriptive variable and function names
- Add docstrings for all public functions
- Keep functions focused and small
- Use type hints where helpful

## 🧪 Testing

Test files are organized in the `tests/` directory:
- Unit tests for individual components
- Integration tests for full workflows
- UI tests for interface components

## 📚 Documentation

Documentation is in the `docs/` directory:
- Technical implementation details
- Feature specifications
- Release notes and changelogs
- Development guides
