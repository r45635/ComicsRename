# Building ComicsRename Windows Executable

This guide explains how to create a standalone Windows executable (.exe) for ComicsRename that can be distributed without requiring Python installation.

## Prerequisites

### For Windows Build (Recommended)
- Windows 10/11
- Python 3.8+ installed
- Git (optional, for cloning)

### For Cross-Platform Build
- Python 3.8+ on any platform
- PyInstaller will create platform-specific executables

## Quick Start (Windows)

1. **Clone/Download the project**
   ```cmd
   git clone <repository-url>
   cd ComicsRename
   ```

2. **Run the build script**
   ```cmd
   build_windows.bat
   ```

3. **Find your executable**
   - Location: `dist\ComicsRename.exe`
   - This file can be distributed standalone

## Manual Build Process

### Step 1: Setup Environment
```cmd
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Build Executable
```cmd
# Clean previous builds
rmdir /s /q build dist __pycache__

# Build with PyInstaller
python -m PyInstaller ComicsRename.spec
```

### Step 3: Test the Executable
```cmd
# Run the built executable
dist\ComicsRename.exe
```

## Build Configuration

The build is configured through `ComicsRename.spec`:

- **Single File**: All dependencies packed into one .exe
- **No Console**: GUI-only application (no command prompt window)
- **Optimized**: UPX compression enabled for smaller file size
- **Includes**: All translations and data files
- **Version Info**: Professional executable metadata

## File Structure After Build

```
ComicsRename/
├── dist/
│   └── ComicsRename.exe          # Standalone executable (~150-200MB)
├── build/                        # Temporary build files
├── ComicsRename.spec            # PyInstaller configuration
├── version_info.txt             # Windows version metadata
└── build_windows.bat            # Build script
```

## Distribution

The `ComicsRename.exe` file in the `dist` folder is completely standalone:

✅ **Includes everything needed:**
- Python runtime
- All Python packages (PySide6, requests, etc.)
- Application code
- Translation files
- Configuration files

✅ **Requirements for end users:**
- Windows 10/11 (64-bit recommended)
- No Python installation needed
- No additional dependencies

## Customization

### Adding an Icon
1. Place an `icon.ico` file in the project root
2. The build script will automatically include it

### Modifying Build Settings
Edit `ComicsRename.spec` to customize:
- Add/remove files to include
- Change executable name
- Modify compression settings
- Add additional hidden imports

### Version Information
Edit `version_info.txt` to update:
- Version numbers
- Company information
- File descriptions

## Troubleshooting

### Common Issues

**Missing modules error:**
- Add missing modules to `hiddenimports` in `ComicsRename.spec`

**Large file size:**
- The executable includes the entire Python runtime (~150-200MB is normal)
- Enable UPX compression (already enabled in spec)

**Antivirus warnings:**
- Some antivirus software flags PyInstaller executables
- This is a false positive - submit to antivirus vendor if needed

**Application won't start:**
- Test in the same environment where you built it
- Check Windows Event Viewer for error details
- Try building with `console=True` for debugging

### Build Logs
Check these files for detailed build information:
- `build/ComicsRename/warn-ComicsRename.txt` - Warnings
- Console output during build

## Cross-Platform Notes

### Building on macOS/Linux for Windows
This requires additional setup and is not recommended. For best results:
1. Use a Windows machine or Windows VM
2. Use GitHub Actions for automated builds
3. Use Docker with Windows containers

### Building for Other Platforms
Use `build_executable.sh` on macOS/Linux:
```bash
chmod +x build_executable.sh
./build_executable.sh
```

## Automation with GitHub Actions

For automated builds, see the GitHub Actions workflow that can build executables for multiple platforms automatically on each release.

---

**Need Help?**
- Check the console output during build for specific error messages
- Ensure all dependencies are properly installed
- Test the application with `python main.py` before building
