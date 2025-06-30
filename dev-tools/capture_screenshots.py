#!/usr/bin/env python3
"""
Screenshot Generator for ComicsRename README

This script can be used to automatically capture screenshots of the
ComicsRename application for documentation purposes.
"""

import os
import sys
from pathlib import Path

def create_screenshot_placeholders():
    """Create placeholder images for README screenshots"""
    
    print("📸 ComicsRename Screenshot Generator")
    print("=" * 40)
    
    # Create screenshots directory
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # Define screenshot specifications
    screenshots = [
        {
            "name": "main_interface.png",
            "description": "Main interface showing file management and metadata search",
            "size": "800x500"
        },
        {
            "name": "metadata_search.png", 
            "description": "Rich metadata display with cover images",
            "size": "800x500"
        },
        {
            "name": "file_organization.png",
            "description": "Drag & drop file management interface",
            "size": "800x500"
        },
        {
            "name": "settings_dialog.png",
            "description": "Settings and configuration dialog",
            "size": "600x400"
        },
        {
            "name": "folder_renaming.png",
            "description": "Folder renaming with validation",
            "size": "500x300"
        }
    ]
    
    print("📋 Screenshot specifications:")
    for screenshot in screenshots:
        print(f"   • {screenshot['name']} ({screenshot['size']})")
        print(f"     {screenshot['description']}")
    
    print(f"\n📁 Screenshots will be saved to: {screenshots_dir.absolute()}")
    
    # Instructions for manual screenshot capture
    print(f"\n💡 To capture screenshots:")
    print(f"   1. Launch ComicsRename: python main.py")
    print(f"   2. Navigate to different interfaces")
    print(f"   3. Take screenshots and save them in {screenshots_dir}/")
    print(f"   4. Update README.md with actual screenshot paths")
    
    # Create placeholder instructions file
    instructions_file = screenshots_dir / "README.md"
    with open(instructions_file, 'w') as f:
        f.write("# ComicsRename Screenshots\n\n")
        f.write("This directory contains screenshots for the ComicsRename documentation.\n\n")
        f.write("## Required Screenshots:\n\n")
        
        for screenshot in screenshots:
            f.write(f"### {screenshot['name']}\n")
            f.write(f"- **Size**: {screenshot['size']}\n")
            f.write(f"- **Description**: {screenshot['description']}\n")
            f.write(f"- **Status**: ⏳ Pending\n\n")
        
        f.write("## Guidelines:\n\n")
        f.write("- Use high-quality PNG format\n")
        f.write("- Ensure good contrast and readability\n")
        f.write("- Show realistic comic file examples\n")
        f.write("- Include various UI states (loading, results, etc.)\n")
        f.write("- Keep file sizes reasonable for web display\n")
    
    print(f"✅ Created instructions: {instructions_file}")
    
    # Update .gitignore to include screenshots
    gitignore_content = """
# Screenshots for documentation
screenshots/*.png
screenshots/*.jpg
screenshots/*.jpeg
!screenshots/README.md
"""
    
    with open(".gitignore", "a") as f:
        f.write(gitignore_content)
    
    print("✅ Updated .gitignore for screenshots")
    
    return screenshots_dir

def update_readme_with_screenshots():
    """Update README.md to use local screenshots when available"""
    
    screenshots_dir = Path("screenshots")
    
    if not screenshots_dir.exists():
        print("⚠️  Screenshots directory not found. Run create_screenshot_placeholders() first.")
        return
    
    # Check for existing screenshots
    available_screenshots = list(screenshots_dir.glob("*.png"))
    
    if available_screenshots:
        print(f"📸 Found {len(available_screenshots)} screenshots:")
        for screenshot in available_screenshots:
            print(f"   • {screenshot.name}")
        
        print("\n💡 To use these screenshots in README:")
        print("   1. Replace placeholder URLs with local paths")
        print("   2. Example: screenshots/main_interface.png")
        print("   3. Commit screenshots to repository if desired")
    else:
        print("⏳ No screenshots found. Please capture screenshots first.")

def main():
    """Main function"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        update_readme_with_screenshots()
    else:
        screenshots_dir = create_screenshot_placeholders()
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Launch ComicsRename and capture screenshots")
        print(f"   2. Save them in {screenshots_dir}/")
        print(f"   3. Run: python {__file__} --update")
        print(f"   4. Update README.md with local screenshot paths")

if __name__ == "__main__":
    main()
