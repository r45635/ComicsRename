#!/bin/bash

# macOS Helper Script for ComicsRename
# This script helps resolve common macOS security issues with unsigned applications

echo "🍎 ComicsRename macOS Helper Script"
echo "=================================="
echo ""

# Check if ComicsRename.app exists
if [ ! -d "ComicsRename.app" ]; then
    echo "❌ ComicsRename.app not found in current directory"
    echo "Please ensure you're running this script from the same directory as ComicsRename.app"
    exit 1
fi

echo "✅ Found ComicsRename.app"

# Remove quarantine attribute
echo "🔧 Removing quarantine attribute..."
xattr -cr ComicsRename.app
if [ $? -eq 0 ]; then
    echo "✅ Quarantine attribute removed"
else
    echo "⚠️  Could not remove quarantine attribute (this is normal if it wasn't quarantined)"
fi

# Make executable
echo "🔧 Making executable..."
chmod +x ComicsRename.app/Contents/MacOS/ComicsRename
if [ $? -eq 0 ]; then
    echo "✅ Made executable"
else
    echo "❌ Could not make executable"
    exit 1
fi

# Check if app can run
echo "🔧 Testing application..."
if ./ComicsRename.app/Contents/MacOS/ComicsRename --version &>/dev/null; then
    echo "✅ Application appears to be working"
else
    echo "⚠️  Application may have issues, but this is normal for GUI apps"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "How to run ComicsRename:"
echo "1. Double-click ComicsRename.app"
echo "2. If macOS shows a security warning:"
echo "   - Go to System Preferences → Security & Privacy → General"
echo "   - Click 'Open Anyway' next to the ComicsRename message"
echo "   - Or right-click the app and select 'Open'"
echo ""
echo "If you still have issues:"
echo "- Try running: open ComicsRename.app"
echo "- Or: ./ComicsRename.app/Contents/MacOS/ComicsRename"
echo ""
echo "For more help, visit: https://github.com/r45635/ComicsRename/issues"
