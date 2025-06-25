# Development Environment Setup for ComicsRename

This guide helps you set up a development environment for ComicsRename.

## Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, or similar)

## Setup Instructions

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-username/ComicsRename.git
cd ComicsRename

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -e ".[dev]"
```

### 2. Environment Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env file with your credentials
# Add your ComicVine API key and BDGest credentials
```

### 3. Test the Installation

```bash
# Run the application
python main.py

# Run tests
python test_bdgest_series.py
python test_session_management.py
```

## Development Workflow

### Code Style

The project uses Black for code formatting:

```bash
# Format code
black .

# Check formatting
black --check .
```

### Type Checking

The project supports mypy for type checking:

```bash
# Run type checker
mypy .
```

### Testing

Run individual test files:

```bash
python test_bdgest_series.py      # Test BDGest functionality
python test_session_management.py # Test session management
python test_folder_rename.py      # Test folder operations
python test_album_details.py      # Test album metadata
```

### Project Structure for Development

```
ComicsRename/
├── main.py                      # Application entry point
├── comicsFileRenamer_v3.py      # Main GUI application
├── bdgest_scraper_api.py        # BDGest API integration
├── comicVine_scraper_api.py     # ComicVine API integration
├── utils.py                     # Utility functions
├── setup_credentials.py        # Credential setup
├── requirements.txt             # Dependencies
├── pyproject.toml              # Project configuration
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── SECURITY.md                 # Security guidelines
├── DEVELOPMENT.md              # This file
├── IMPLEMENTATION_SUMMARY.md    # Technical details
└── test_*.py                   # Test files
```

## Key Development Areas

### 1. GUI Development (comicsFileRenamer_v3.py)
- PySide6-based Qt application
- Responsive design with splitters and layouts
- Drag & drop functionality
- Custom widgets for editable labels

### 2. API Integration
- **BDGest API** (bdgest_scraper_api.py): French comic database
- **ComicVine API** (comicVine_scraper_api.py): International comic database
- Session management and authentication
- Parallel processing for performance

### 3. Metadata Processing
- Album/issue metadata parsing
- Cover image handling and caching
- Data enrichment and validation

### 4. File Management
- Comic file detection and scanning
- Folder organization and renaming
- Drag & drop operations

## Contributing Guidelines

### Before Contributing

1. Check existing issues and pull requests
2. Create an issue for major changes
3. Follow the existing code style
4. Add tests for new functionality
5. Update documentation as needed

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages
6. Push to your fork
7. Create a pull request

### Code Quality

- Use meaningful variable and function names
- Add docstrings for public functions
- Handle errors gracefully
- Follow PEP 8 style guidelines
- Add type hints where appropriate

## Debugging

### Debug Mode

Set environment variable to enable debug output:

```bash
export DEBUG=1
python main.py
```

### Common Development Issues

**Import Errors**: Make sure virtual environment is activated and dependencies are installed

**Qt/PySide6 Issues**: Ensure Qt dependencies are properly installed for your platform

**API Connection Issues**: Check credentials and network connectivity

**Performance Issues**: Enable debug mode to see timing information

## Architecture Notes

### Provider Pattern
The application uses a provider pattern for metadata sources:
- `MetadataProvider`: Abstract base class
- `BDGestProvider`: BDGest implementation
- `ComicVineProvider`: ComicVine implementation

### Session Management
Persistent session management for better performance:
- Automatic authentication
- Session reuse
- Error recovery

### GUI Architecture
- Main window with splitter layout
- Separate panels for folders, albums, and details
- Custom widgets for enhanced functionality
- Responsive design with proper scaling

## Performance Considerations

- **Threading**: Long-running operations use background threads
- **Caching**: Metadata and images are cached for reuse
- **Parallel Processing**: Multiple API calls handled concurrently
- **Session Persistence**: Avoid re-authentication overhead

## Security Notes

- No hardcoded credentials in source code
- Environment variables for sensitive data
- Secure credential storage using QSettings
- Input validation and sanitization

For more detailed security information, see [SECURITY.md](SECURITY.md).
