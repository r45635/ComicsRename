#!/usr/bin/env python3
"""
ComicsRename Launcher

This launcher ensures ComicsRename runs with the correct virtual environment
and all dependencies (including Safe Rename) are available.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main launcher function"""
    print("🚀 ComicsRename Launcher")
    print("=" * 40)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    venv_dir = script_dir / ".venv"
    
    # Check if virtual environment exists
    if not venv_dir.exists():
        print("❌ Virtual environment not found!")
        print(f"Expected location: {venv_dir}")
        print("\nTo create virtual environment:")
        print("1. cd to project directory")
        print("2. python3 -m venv .venv")
        print("3. source .venv/bin/activate")
        print("4. pip install -r requirements.txt")
        return 1
    
    # Determine Python executable in virtual environment
    if sys.platform == "win32":
        python_exe = venv_dir / "Scripts" / "python.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
    
    if not python_exe.exists():
        print(f"❌ Python executable not found in virtual environment: {python_exe}")
        return 1
    
    print(f"✅ Found virtual environment: {venv_dir}")
    print(f"🐍 Using Python: {python_exe}")
    print()
    
    # Check dependencies
    print("🔍 Checking Safe Rename dependencies...")
    try:
        result = subprocess.run([
            str(python_exe), "-c", 
            """
import sys
sys.path.insert(0, '.')

try:
    import cv2
    print('✅ OpenCV available')
except ImportError:
    print('❌ OpenCV not available - Safe Rename will be disabled')

try:
    from skimage.metrics import structural_similarity as ssim
    print('✅ scikit-image available')
except ImportError:
    print('❌ scikit-image not available - Safe Rename will be disabled')

try:
    from pdf_cover_comparator_qt import PDFCoverComparator
    print('✅ Safe Rename feature available')
except ImportError:
    print('❌ Safe Rename feature not available')
"""
        ], cwd=script_dir, capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
    
    except subprocess.TimeoutExpired:
        print("⚠️  Dependency check timed out, continuing anyway...")
    except Exception as e:
        print(f"⚠️  Could not check dependencies: {e}")
    
    print()
    print("🎉 Starting ComicsRename...")
    print("💡 Close the application window to exit")
    print()
    
    # Run the main application
    try:
        # Set up environment for Qt plugins
        env = os.environ.copy()
        qt_plugin_path = venv_dir / "lib" / "python3.9" / "site-packages" / "PySide6" / "Qt" / "plugins"
        if qt_plugin_path.exists():
            env["QT_PLUGIN_PATH"] = str(qt_plugin_path)
        
        result = subprocess.run([
            str(python_exe), "main.py"
        ], cwd=script_dir, env=env)
        
        print(f"\n👋 ComicsRename exited with code: {result.returncode}")
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error running ComicsRename: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
