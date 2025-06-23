# ComicsRename - Standalone Windows Executable

## 🎯 Quick Summary

ComicsRename is now available as a **standalone Windows executable** that requires no Python installation or dependencies. Just download and run!

## 📦 What's Included

The Windows executable (`ComicsRename.exe`) includes:

✅ **Complete Application**
- Full GUI interface built with PySide6
- BDGest and ComicVine scraper APIs
- Bilingual support (English/French)
- All comic book organizing and renaming features

✅ **All Dependencies Bundled**
- Python 3.11 runtime
- PySide6 (Qt GUI framework)
- requests, beautifulsoup4, lxml
- All translation files and assets

✅ **Zero Installation Required**
- No Python needed on target system
- No additional downloads required
- Runs on Windows 10/11 (64-bit)

## 🚀 Building the Executable

### Option 1: Automated Build (Windows)
```cmd
# Clone the repository
git clone <your-repo-url>
cd ComicsRename

# Run the build script
build_windows.bat
```

### Option 2: Manual Build
```cmd
# Setup environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Build executable
python -m PyInstaller ComicsRename.spec
```

### Option 3: GitHub Actions (Recommended for Releases)
- Tag a release: `git tag v1.0.0 && git push origin v1.0.0`
- GitHub automatically builds executables for Windows, macOS, and Linux
- Download from the Releases page

## 📁 Build Output

After building, you'll find:
```
dist/
└── ComicsRename.exe    # Standalone executable (~150-200MB)
```

## 🎨 Features Included in Executable

- **Comic File Organization**: Rename and organize comic files using metadata
- **Dual Source Support**: BDGest and ComicVine APIs
- **Bilingual Interface**: English and French translations
- **Batch Processing**: Handle multiple files at once
- **Metadata Extraction**: Automatic series, album, and issue detection
- **User-Friendly GUI**: Intuitive interface for all operations

## 🔧 Technical Details

**Build Configuration:**
- Single file executable (all-in-one)
- UPX compression for smaller size
- Windows version information embedded
- No console window (GUI-only)
- Professional application metadata

**System Requirements:**
- Windows 10 or Windows 11
- 64-bit architecture (recommended)
- ~500MB free disk space (for extraction)
- Internet connection (for metadata fetching)

## 📋 Distribution Checklist

For distributing the executable:

- [ ] Test on clean Windows system (no Python)
- [ ] Verify all features work correctly
- [ ] Check translation files are included
- [ ] Test with various comic file formats
- [ ] Include user documentation
- [ ] Consider code signing (for enterprise distribution)

## 🛡️ Security Notes

**Antivirus Warnings:**
- Some antivirus software may flag PyInstaller executables
- This is a common false positive
- Submit to antivirus vendors if needed for whitelisting

**Code Signing (Optional):**
- For enterprise distribution, consider code signing
- Reduces security warnings on end-user systems
- Requires a code signing certificate

## 📖 User Instructions

Share these instructions with end users:

1. **Download** `ComicsRename.exe` 
2. **Run** the executable (no installation needed)
3. **Configure** your comic directories
4. **Organize** your comic collection!

No Python, no dependencies, no hassle! 🎉

---

**File Size:** ~150-200MB (includes complete Python runtime)  
**Startup Time:** 3-5 seconds (first run may be slower)  
**Memory Usage:** ~100-150MB (typical GUI application)

For questions or issues, see the main README.md or open an issue on GitHub.
