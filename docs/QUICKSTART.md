# 🚀 ComicsRename Quick Start Guide

Welcome to ComicsRename! This guide will get you up and running in just a few minutes.

## ⚡ Super Quick Start (2 minutes)

1. **Download and Install**
   ```bash
   git clone https://github.com/your-username/ComicsRename.git
   cd ComicsRename
   pip install -r requirements.txt
   ```

2. **Launch the App**
   ```bash
   python main.py
   ```

3. **Start Organizing**
   - Select a folder with comic files
   - Search for series or albums
   - Drag and drop to organize!

---

## 📋 Detailed Setup (5 minutes)

### Step 1: Prerequisites
- **Python 3.8+** ([Download here](https://python.org/downloads/))
- **Git** (optional, for cloning)

### Step 2: Installation

#### Option A: Using Git (Recommended)
```bash
git clone https://github.com/your-username/ComicsRename.git
cd ComicsRename
pip install -r requirements.txt
```

#### Option B: Manual Download
1. Download the ZIP file from GitHub
2. Extract to a folder
3. Open terminal/command prompt in that folder
4. Run: `pip install -r requirements.txt`

### Step 3: Validation
Check that everything is working:
```bash
python validate_install.py
```

You should see: **🎉 All checks passed!**

### Step 4: Launch
```bash
python main.py
```

Or use the launcher scripts:
- **macOS/Linux**: `./launch.sh`
- **Windows**: Double-click `launch.bat`

---

## 🎮 Basic Usage

### 1. **Select Comic Files**
- Click **"Browse"** to select a folder containing comic files
- Supported formats: CBZ, CBR, PDF, and more

### 2. **Choose Your Database**
- **BDGest**: French comics database (requires account)
- **ComicVine**: International database (requires free API key)

### 3. **Search for Comics**
- **Series Mode**: Search by series name, then browse albums
- **Album Mode**: Search directly for specific albums/issues

### 4. **Organize Your Files**
- View album details and cover art
- Drag and drop files to organize
- Double-click folder names to rename them

---

## ⚙️ Configuration (Optional)

### For BDGest Access
1. Create a free account at [BDGest.com](https://www.bdgest.com/)
2. Run the setup script:
   ```bash
   python setup_credentials.py
   ```

### For ComicVine Access
1. Get a free API key from [ComicVine](https://comicvine.gamespot.com/api/)
2. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and add your API key:
   ```
   COMICVINE_API_KEY=your_api_key_here
   ```

---

## 🔧 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**GUI doesn't start**
- Make sure you have Python 3.8+
- On Linux: `sudo apt-get install python3-tk`

**No search results**
- Check your internet connection
- Verify credentials/API keys
- Try different search terms

### Get Help
- Check the [README.md](README.md) for detailed documentation
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Enable debug mode: Set `DEBUG=1` environment variable

---

## 🎯 Pro Tips

### Efficient Workflow
1. **Use Series Mode** for browsing complete series
2. **Enable auto-population** to see results immediately
3. **Use drag & drop** for quick file organization
4. **Double-click folders** to rename them instantly

### Power Features
- **Parallel processing**: Fetches multiple album details simultaneously
- **Session persistence**: Stays logged in across searches
- **Responsive UI**: Cover images scale with window size
- **Smart validation**: Prevents invalid folder names

### Keyboard Shortcuts
- **Ctrl+R**: Refresh folder contents
- **F5**: Refresh album search
- **Escape**: Cancel current operation
- **Enter**: Confirm folder rename

---

## 🌟 What's Next?

Once you're comfortable with the basics:

1. **Explore Advanced Features**
   - Custom renaming patterns
   - Bulk operations
   - Metadata comparison

2. **Customize Your Setup**
   - Configure search preferences
   - Set up multiple databases
   - Create custom workflows

3. **Join the Community**
   - Report bugs or request features
   - Share your workflows
   - Contribute improvements

---

## 📚 Learning Resources

- **[README.md](README.md)**: Complete documentation
- **[DEVELOPMENT.md](DEVELOPMENT.md)**: For developers
- **[SECURITY.md](SECURITY.md)**: Security guidelines
- **[CHANGELOG.md](CHANGELOG.md)**: What's new

---

**Happy comic organizing! 📚✨**

*Need help? Open an issue on GitHub or check the documentation.*
