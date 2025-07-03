# ComicsRename for macOS

## Download and Installation

### Method 1: DMG File (Recommended)
1. Download `ComicsRename-macOS.dmg` from the [releases page](https://github.com/r45635/ComicsRename/releases)
2. Open the DMG file
3. Drag `ComicsRename.app` to your Applications folder
4. Eject the DMG

### Method 2: Direct App Download
1. Download `ComicsRename.app` from the [releases page](https://github.com/r45635/ComicsRename/releases)
2. Extract the zip file
3. Move `ComicsRename.app` to your Applications folder

## Running the Application

### First Time Setup
Since this application is not signed with an Apple Developer certificate, macOS will show security warnings. Here's how to run it:

#### Option 1: System Preferences Method
1. Double-click `ComicsRename.app` 
2. macOS will show a security warning
3. Go to **System Preferences** → **Security & Privacy** → **General**
4. You'll see a message about ComicsRename being blocked
5. Click **"Open Anyway"**
6. Confirm by clicking **"Open"** in the dialog

#### Option 2: Right-Click Method
1. Right-click on `ComicsRename.app`
2. Select **"Open"** from the context menu
3. Click **"Open"** in the security dialog

#### Option 3: Terminal Method
1. Open Terminal
2. Navigate to the folder containing ComicsRename.app
3. Run: `open ComicsRename.app`

### Using the Helper Script
We provide a helper script to automatically fix common permissions issues:

1. Download `macos-helper.sh` from the repository
2. Place it in the same folder as `ComicsRename.app`
3. Open Terminal and navigate to that folder
4. Run: `chmod +x macos-helper.sh && ./macos-helper.sh`
5. Follow the on-screen instructions

## Troubleshooting

### "ComicsRename.app is damaged and can't be opened"
This happens when macOS quarantines the application. To fix:
```bash
xattr -cr ComicsRename.app
```

### "Permission denied" errors
Make sure the application is executable:
```bash
chmod +x ComicsRename.app/Contents/MacOS/ComicsRename
```

### Application won't start
Try running from Terminal to see error messages:
```bash
./ComicsRename.app/Contents/MacOS/ComicsRename
```

### Still having issues?
1. Make sure you're running macOS 10.14 or later
2. Check if you have enough disk space
3. Try restarting your Mac
4. Download the app again (the file might be corrupted)

## System Requirements
- macOS 10.14 (Mojave) or later
- Intel or Apple Silicon (M1/M2/M3) processor
- 200MB free disk space
- Internet connection for metadata lookup

## Security Notice
This application is not signed with an Apple Developer certificate because:
- It's an open-source project
- Apple Developer certificates cost $99/year
- The app is safe to use (you can review the source code)

macOS security warnings are normal and expected for unsigned applications.

## Support
- [GitHub Issues](https://github.com/r45635/ComicsRename/issues)
- [Documentation](https://github.com/r45635/ComicsRename/docs)
- [Source Code](https://github.com/r45635/ComicsRename)

## Building from Source
If you prefer to build the application yourself:
```bash
git clone https://github.com/r45635/ComicsRename
cd ComicsRename
pip install -r requirements.txt
python -m PyInstaller ComicsRename.spec
```

The built application will be in the `dist/` folder.
