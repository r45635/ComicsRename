# ComicsRename 📚

<div align="center">
  <img src="icons/comicsrename_256x256.png" alt="ComicsRename Logo" width="128" height="128">
  
  **A powerful Python GUI application for organizing and renaming comic book files**
  
  ![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
  ![PySide6](https://img.shields.io/badge/PySide6-6.4+-green.svg)
  ![License](https://img.shields.io/badge/license-MIT-blue.svg)
  ![Version](https://img.shields.io/badge/version-3.3.0-brightgreen.svg)
</div>

---

## 💭 Why ComicsRename?

Are you **too lazy** to rename manually all your comic files in your storage? **Too lazy** to search manually for the correct series name, the proper title, and all those details? That's exactly why I created and use **ComicsRename**! 

I was tired of spending hours organizing my comic collection, hunting down metadata, and fixing inconsistent file names. So I built this tool to automate the entire process. Now I'm happy to share it with you - and I'd love to hear from you if it helps you too! 🎉

**ComicsRename** transforms the tedious task of organizing comic book files into a breeze, using metadata from **BDGest** and **ComicVine** databases.

## 📸 Screenshots

<div align="center">
  
### Main Interface
*The clean, intuitive interface showing file management and metadata search*

<img src="screenshots/Screenshot1.png" alt="ComicsRename Main Interface" width="600">

### Metadata Search & Display - File Organization
*Rich metadata display with cover images and detailed information*
*Drag & drop file management with smart organization features*

<img src="docs/screenshots/Screenshot2.png" alt="ComicsRename Main Interface and Quick View" width="600">

</div>

## 🌟 Features

<div align="center">
  <img src="icons/comicsrename_48x48.png" alt="Features" width="32" height="32">
</div>

<table>
<tr>
<td width="50%">

### 🔍 **Dual Metadata Sources**
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **BDGest Integration**: French comic database
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **ComicVine Integration**: International comics database

### 📖 **Smart Search Modes**
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Series Name Mode**: Browse albums within series
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Album Search**: Direct album/issue search
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Auto-population**: Automatically load albums

### 🎨 **Rich Metadata Display**
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Cover Images**: High-quality cover art
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Detailed Information**: Dates, descriptions, teams
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Album Details**: ISBN, publisher, page count

</td>
<td width="50%">

### 🗂️ **File Management**
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Drag & Drop**: Intuitive file organization
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Folder Renaming**: With validation and confirmation
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Bulk Operations**: Handle multiple files efficiently
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Smart Scanning**: CBZ, CBR, PDF, etc.

### 🔒 **Security & Credentials**
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Secure Storage**: Encrypted credential storage
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Environment Variables**: Support for .env files
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **No Hardcoded Keys**: All API keys stored securely

### ⚡ **Performance Optimizations**
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Session Management**: Persistent authentication
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Parallel Processing**: Multi-threaded fetching
- <img src="icons/comicsrename_16x16.png" width="16" height="16"> **Caching**: Efficient data caching and reuse

</td>
</tr>
</table>

## 🚀 Getting Started

<div align="center">
  <img src="icons/comicsrename_64x64.png" alt="Installation" width="48" height="48">
</div>

### Prerequisites

- **Python 3.8+** (recommended: Python 3.9 or higher)
- **Operating System**: Windows, macOS, or Linux

### 📦 Installation Options

#### Option 1: Package Installation (Recommended)
```bash
# Install from the latest release package
pip install comicsrename-3.3.0-py3-none-any.whl

# Or from source distribution
pip install comicsrename-3.3.0.tar.gz
```

#### Option 2: Development Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/r45635/ComicsRename.git
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
### 🚀 Running the Application

<div align="center">
  <img src="icons/comicsrename_32x32.png" alt="Run App" width="24" height="24">
</div>

```bash
python main.py
```

## 📖 Usage Guide

<div align="center">
  <img src="icons/comicsrename_64x64.png" alt="Usage Guide" width="48" height="48">
</div>

### 🎯 Quick Start Workflow

<table>
<tr>
<td width="50%">

#### 1. **Initial Setup** <img src="icons/comicsrename_16x16.png" width="16" height="16">
- Launch the application using `python main.py`
- Configure credentials (if using BDGest)
- Set ComicVine API key (if using ComicVine)

#### 2. **Basic Workflow** <img src="icons/comicsrename_16x16.png" width="16" height="16">
- **Select a folder** containing comic files
- **Choose metadata source** (BDGest or ComicVine)
- **Search for series or albums**
- **Review metadata** and cover images

</td>
<td width="50%">

#### 3. **File Organization** <img src="icons/comicsrename_16x16.png" width="16" height="16">
- **Organize files** using drag & drop
- **Rename folders** by double-clicking folder names
- **Validate changes** with built-in confirmation

#### 4. **Advanced Features** <img src="icons/comicsrename_16x16.png" width="16" height="16">
- **Batch Processing**: Handle multiple folders
- **Metadata Comparison**: Compare sources
- **Session Persistence**: Auto authentication

</td>
</tr>
</table>

### 🔧 Configuration Options

| Feature | Description | Icon |
|---------|-------------|------|
| **BDGest Setup** | Configure French comic database access | <img src="icons/comicsrename_16x16.png" width="16" height="16"> |
| **ComicVine API** | Set up international database access | <img src="icons/comicsrename_16x16.png" width="16" height="16"> |
| **Environment Variables** | Use `.env` file for secure configuration | <img src="icons/comicsrename_16x16.png" width="16" height="16"> |

## 🎨 Visual Identity

<div align="center">
  
### Application Icon
  
<img src="icons/comicsrename_128x128.png" alt="ComicsRename Icon" width="128" height="128">

**ComicsRename** features a custom-designed icon representing comic book organization and file management. The icon is available in multiple formats:

| Format | Size | Usage |
|--------|------|-------|
| <img src="icons/comicsrename_16x16.png" width="16" height="16"> | 16x16 | System tray, small icons |
| <img src="icons/comicsrename_32x32.png" width="32" height="32"> | 32x32 | Interface elements |
| <img src="icons/comicsrename_64x64.png" width="64" height="64"> | 64x64 | Application windows |
| <img src="icons/comicsrename_128x128.png" width="64" height="64"> | 128x128 | High-resolution displays |
| <img src="icons/comicsrename_256x256.png" width="64" height="64"> | 256x256 | Documentation, README |

The icon design incorporates:
- 📚 **Comic book elements** representing the core functionality
- 🗂️ **File organization symbols** showing the management aspect
- 🎨 **Modern design** with clean lines and vibrant colors

</div>

## 🤝 Contributing

<div align="center">
  <img src="icons/comicsrename_48x48.png" alt="Contributing" width="32" height="32">
</div>

We welcome contributions! Here's how you can help:

- 🐛 **Report bugs** and issues
- 💡 **Suggest new features** 
- 🔧 **Submit pull requests**
- 📖 **Improve documentation**
- 🌍 **Add translations**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

<div align="center">
  <img src="icons/comicsrename_32x32.png" alt="Thanks" width="24" height="24">
</div>

- **BDGest**: For providing comprehensive French comic book metadata
- **ComicVine**: For the extensive international comics database
- **PySide6 Team**: For the excellent Qt-based GUI framework
- **Python Community**: For the amazing tools and libraries

---

<div align="center">
  
<img src="icons/comicsrename_64x64.png" alt="ComicsRename" width="48" height="48">

**Made with ❤️ for comic book enthusiasts**

**ComicsRename v3.3.0** | [Repository](https://github.com/r45635/ComicsRename) | [Issues](https://github.com/r45635/ComicsRename/issues) | [Releases](https://github.com/r45635/ComicsRename/releases)

*Transform your comic collection organization from tedious to effortless!*

</div>
