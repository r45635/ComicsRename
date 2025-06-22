# ComicsRename 📚

A powerful Python GUI application for organizing and renaming comic book files using metadata from **BDGest** and **ComicVine** databases.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.4+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

### 🔍 **Dual Metadata Sources**
- **BDGest Integration**: Search and fetch detailed metadata from the French BDGest database
- **ComicVine Integration**: Access the comprehensive ComicVine database for international comics

### 📖 **Smart Search Modes**
- **Series Name Mode**: Search by series name, browse albums within each series
- **Album Search**: Direct album/issue search across both databases
- **Auto-population**: Automatically load albums when series are found

### 🎨 **Rich Metadata Display**
- **Cover Images**: High-quality cover art with responsive scaling
- **Detailed Information**: Publication dates, descriptions, creative teams, characters
- **Album Details**: Complete metadata including ISBN, publisher, page count

### 🗂️ **File Management**
- **Drag & Drop**: Intuitive file organization
- **Folder Renaming**: Edit folder names with validation and confirmation
- **Bulk Operations**: Handle multiple files and folders efficiently
- **Smart Scanning**: Detect comic files in various formats (CBZ, CBR, PDF, etc.)

### 🔒 **Security & Credentials**
- **Secure Storage**: Encrypted credential storage using QSettings
- **Environment Variables**: Support for .env files
- **No Hardcoded Keys**: All API keys and passwords stored securely

### ⚡ **Performance Optimizations**
- **Session Management**: Persistent authentication sessions
- **Parallel Processing**: Multi-threaded metadata fetching
- **Caching**: Efficient data caching and reuse

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+** (recommended: Python 3.9 or higher)
- **Operating System**: Windows, macOS, or Linux

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ComicsRename.git
   cd ComicsRename
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up credentials** (optional, for BDGest access):
   ```bash
   python setup_credentials.py
   ```

### Running the Application

```bash
python main.py
```

## 📖 Usage Guide

### Initial Setup

1. **Launch the application** using `python main.py`
2. **Configure credentials** (if using BDGest):
   - Go to Settings → Configure BDGest credentials
   - Enter your BDGest username and password
3. **Set ComicVine API key** (if using ComicVine):
   - Create a `.env` file or use environment variables
   - Add your ComicVine API key

### Basic Workflow

1. **Select a folder** containing comic files
2. **Choose your metadata source** (BDGest or ComicVine)
3. **Search for series or albums**:
   - Use **Series Name mode** to browse by series
   - Use **Album search** for direct lookup
4. **Review metadata** and cover images
5. **Organize files** using drag & drop
6. **Rename folders** by double-clicking folder names

### Advanced Features

- **Batch Processing**: Handle multiple folders and files
- **Metadata Comparison**: Compare information from different sources
- **Custom Renaming**: Manual folder name editing with validation
- **Session Persistence**: Automatic authentication management

## 🛠️ Development

### Project Structure

```
ComicsRename/
├── main.py                     # Application entry point
├── comicsFileRenamer_v3.py     # Main GUI application
├── bdgest_scraper_api.py       # BDGest API integration
├── comicVine_scraper_api.py    # ComicVine API integration
├── utils.py                    # Utility functions
├── setup_credentials.py       # Credential setup script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── SECURITY.md                # Security guidelines
├── IMPLEMENTATION_SUMMARY.md   # Technical documentation
└── test_*.py                  # Test scripts
```

### Running Tests

```bash
# Test BDGest series functionality
python test_bdgest_series.py

# Test session management
python test_session_management.py

# Test folder renaming
python test_folder_rename.py

# Test album details
python test_album_details.py
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
COMICVINE_API_KEY=your_comicvine_api_key_here
BDGEST_USERNAME=your_bdgest_username
BDGEST_PASSWORD=your_bdgest_password
```

### Application Settings

The application stores settings using QSettings:
- **Credentials**: Securely stored BDGest credentials
- **Window State**: Size, position, and layout preferences
- **Search History**: Recent searches and preferences

## 🔒 Security

- **No Hardcoded Credentials**: All sensitive information uses environment variables
- **Encrypted Storage**: Local credentials are encrypted using QSettings
- **Secure Transmission**: HTTPS for all API communications
- **Input Validation**: Comprehensive validation for all user inputs

See [SECURITY.md](SECURITY.md) for detailed security information.

## 📝 Dependencies

- **PySide6**: Modern Qt-based GUI framework
- **requests**: HTTP library for API communications
- **beautifulsoup4**: HTML parsing for web scraping
- **lxml**: XML/HTML parser
- **python-dotenv**: Environment variable management

## 🐛 Troubleshooting

### Common Issues

**Import Error**: Missing dependencies
```bash
pip install -r requirements.txt
```

**Authentication Failed**: Incorrect BDGest credentials
```bash
python setup_credentials.py
```

**ComicVine API Error**: Invalid or missing API key
- Check your `.env` file
- Verify API key validity on ComicVine

### Debug Mode

Enable debug output by setting environment variable:
```bash
export DEBUG=1
python main.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **BDGest**: French comic book database
- **ComicVine**: Comprehensive comic book database  
- **Qt/PySide6**: Cross-platform GUI framework
- **Python Community**: Excellent libraries and tools

## 🔗 Links

- [BDGest Website](https://www.bdgest.com/)
- [ComicVine API](https://comicvine.gamespot.com/api/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)

---

**Made with ❤️ for comic book enthusiasts**
