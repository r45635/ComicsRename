#!/usr/bin/env python3
"""
Icon Generator for ComicsRename
Creates application icons in multiple formats and sizes
"""

import os
from pathlib import Path

def create_icon_svg():
    """Create SVG icon for ComicsRename"""
    
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Gradient for comic book -->
    <linearGradient id="comicGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FF6B6B;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#4ECDC4;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#45B7D1;stop-opacity:1" />
    </linearGradient>
    
    <!-- Shadow filter -->
    <filter id="dropshadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="4" dy="4" stdDeviation="8" flood-color="#000000" flood-opacity="0.3"/>
    </filter>
  </defs>
  
  <!-- Background circle -->
  <circle cx="256" cy="256" r="240" fill="#F8F9FA" stroke="#E9ECEF" stroke-width="8"/>
  
  <!-- Main comic book -->
  <rect x="140" y="120" width="180" height="240" rx="12" ry="12" 
        fill="url(#comicGrad)" 
        filter="url(#dropshadow)"
        stroke="#2C3E50" stroke-width="3"/>
  
  <!-- Comic book spine -->
  <rect x="140" y="120" width="20" height="240" rx="12" ry="12" 
        fill="#2C3E50" opacity="0.8"/>
  
  <!-- Comic book pages effect -->
  <rect x="160" y="130" width="150" height="220" rx="8" ry="8" 
        fill="#FFFFFF" opacity="0.9"/>
  <rect x="170" y="140" width="130" height="200" rx="6" ry="6" 
        fill="#F1F3F4" stroke="#BDC3C7" stroke-width="1"/>
  
  <!-- Comic panels/frames -->
  <rect x="180" y="160" width="50" height="40" rx="3" ry="3" 
        fill="#FFE66D" stroke="#FF6B6B" stroke-width="2"/>
  <rect x="240" y="160" width="50" height="40" rx="3" ry="3" 
        fill="#A8E6CF" stroke="#4ECDC4" stroke-width="2"/>
  <rect x="180" y="210" width="110" height="30" rx="3" ry="3" 
        fill="#FFB3B3" stroke="#FF6B6B" stroke-width="2"/>
  <rect x="180" y="250" width="110" height="40" rx="3" ry="3" 
        fill="#B3D9FF" stroke="#45B7D1" stroke-width="2"/>
  
  <!-- Speech bubble -->
  <ellipse cx="220" cy="180" rx="15" ry="10" fill="#FFFFFF" stroke="#2C3E50" stroke-width="2"/>
  <polygon points="212,186 218,194 208,190" fill="#FFFFFF" stroke="#2C3E50" stroke-width="2"/>
  
  <!-- Rename/Edit tag -->
  <rect x="320" y="200" width="80" height="40" rx="20" ry="20" 
        fill="#28A745" 
        filter="url(#dropshadow)"
        stroke="#1E7E34" stroke-width="2"/>
  
  <!-- Pencil/edit icon in tag -->
  <path d="M340 210 L360 210 L355 230 L345 230 Z" 
        fill="#FFFFFF" stroke="#1E7E34" stroke-width="1"/>
  <circle cx="365" cy="215" r="6" fill="#FFFFFF" stroke="#1E7E34" stroke-width="1"/>
  
  <!-- Text in tag -->
  <text x="350" y="226" font-family="Arial, sans-serif" font-size="10" fill="#FFFFFF" text-anchor="middle">ABC</text>
  
  <!-- Folder base (subtle) -->
  <path d="M100 320 L120 300 L200 300 L220 320 L420 320 L420 400 L100 400 Z" 
        fill="#FFC107" opacity="0.6" 
        stroke="#F57C00" stroke-width="2"/>
  
  <!-- Files organization indicator -->
  <rect x="120" y="340" width="60" height="8" rx="4" ry="4" fill="#6C757D" opacity="0.5"/>
  <rect x="120" y="355" width="80" height="8" rx="4" ry="4" fill="#6C757D" opacity="0.5"/>
  <rect x="120" y="370" width="40" height="8" rx="4" ry="4" fill="#6C757D" opacity="0.5"/>
  
  <!-- Arrow indicating transformation -->
  <path d="M360 280 Q380 260 400 280" stroke="#28A745" stroke-width="4" fill="none" marker-end="url(#arrowhead)"/>
  
  <!-- Arrow marker -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" 
            refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#28A745"/>
    </marker>
  </defs>
</svg>'''
    
    return svg_content

def create_icon_files():
    """Create icon files for the application"""
    
    print("🎨 Génération des icônes pour ComicsRename")
    print("=" * 50)
    
    # Create icons directory
    icons_dir = Path("icons")
    icons_dir.mkdir(exist_ok=True)
    
    # Create SVG icon
    svg_content = create_icon_svg()
    svg_file = icons_dir / "comicsrename_icon.svg"
    
    with open(svg_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✅ Icône SVG créée: {svg_file}")
    
    # Try to create other formats if libraries are available
    try:
        import cairosvg
        
        # Create PNG versions
        sizes = [16, 32, 48, 64, 128, 256, 512]
        for size in sizes:
            png_file = icons_dir / f"comicsrename_icon_{size}x{size}.png"
            cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=str(png_file),
                output_width=size,
                output_height=size
            )
            print(f"✅ PNG {size}x{size} créé: {png_file}")
        
        # Create ICO file for Windows
        ico_file = icons_dir / "comicsrename_icon.ico"
        cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            write_to=str(ico_file),
            output_width=256,
            output_height=256
        )
        print(f"✅ ICO créé: {ico_file}")
        
    except ImportError:
        print("⚠️  cairosvg non installé - seul le SVG a été créé")
        print("   Pour créer les PNG/ICO: pip install cairosvg")
    
    # Create a simple HTML preview
    html_preview = f'''<!DOCTYPE html>
<html>
<head>
    <title>ComicsRename Icon Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        .icon-container {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .icon {{ margin: 10px; display: inline-block; text-align: center; }}
        .icon img {{ border: 1px solid #ddd; border-radius: 4px; }}
        .icon-title {{ margin-top: 8px; font-weight: bold; color: #333; }}
    </style>
</head>
<body>
    <h1>🎨 ComicsRename - Aperçu des Icônes</h1>
    
    <div class="icon-container">
        <h2>Icône Principale (SVG)</h2>
        <div class="icon">
            <img src="comicsrename_icon.svg" width="128" height="128" alt="ComicsRename Icon">
            <div class="icon-title">128x128</div>
        </div>
        <div class="icon">
            <img src="comicsrename_icon.svg" width="64" height="64" alt="ComicsRename Icon">
            <div class="icon-title">64x64</div>
        </div>
        <div class="icon">
            <img src="comicsrename_icon.svg" width="32" height="32" alt="ComicsRename Icon">
            <div class="icon-title">32x32</div>
        </div>
        <div class="icon">
            <img src="comicsrename_icon.svg" width="16" height="16" alt="ComicsRename Icon">
            <div class="icon-title">16x16</div>
        </div>
    </div>
    
    <div class="icon-container">
        <h2>Concept Design</h2>
        <p><strong>Éléments visuels:</strong></p>
        <ul>
            <li>📚 <strong>Livre de BD</strong> - Représente les comics avec des panels colorés</li>
            <li>🏷️ <strong>Tag de renommage</strong> - Indique la fonction de renommage</li>
            <li>📁 <strong>Base dossier</strong> - Organisation des fichiers</li>
            <li>➡️ <strong>Flèche</strong> - Transformation/organisation</li>
        </ul>
        
        <p><strong>Couleurs:</strong></p>
        <ul>
            <li>🔴 Rouge/Rose - Énergie des comics</li>
            <li>🔵 Bleu - Technologie et organisation</li>
            <li>🟢 Vert - Action de renommage/succès</li>
            <li>🟡 Jaune - Dossiers et mise en évidence</li>
        </ul>
    </div>
</body>
</html>'''
    
    preview_file = icons_dir / "preview.html"
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write(html_preview)
    
    print(f"✅ Aperçu HTML créé: {preview_file}")
    print()
    print("🎯 Utilisation:")
    print(f"   • Ouvrez {preview_file} dans un navigateur pour voir l'icône")
    print(f"   • Utilisez {svg_file} pour l'application")
    print(f"   • Copiez vers icon.ico pour l'exécutable Windows")
    
    return icons_dir

def create_additional_concepts():
    """Create additional icon concept variations"""
    
    concepts = {
        "concept_minimal": '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <!-- Minimal concept: Simple comic + rename symbol -->
  <circle cx="256" cy="256" r="240" fill="#FFFFFF" stroke="#E3F2FD" stroke-width="8"/>
  
  <!-- Comic book simplified -->
  <rect x="180" y="150" width="120" height="160" rx="8" ry="8" 
        fill="#FF5722" stroke="#D84315" stroke-width="3"/>
  <rect x="190" y="160" width="100" height="140" rx="4" ry="4" 
        fill="#FFFFFF"/>
  
  <!-- Comic panels -->
  <rect x="200" y="180" width="35" height="25" fill="#FFEB3B"/>
  <rect x="245" y="180" width="35" height="25" fill="#4CAF50"/>
  <rect x="200" y="215" width="80" height="20" fill="#2196F3"/>
  <rect x="200" y="245" width="80" height="35" fill="#FF9800"/>
  
  <!-- Rename symbol -->
  <circle cx="350" cy="220" r="40" fill="#4CAF50" stroke="#2E7D32" stroke-width="3"/>
  <text x="350" y="230" font-family="Arial" font-size="24" fill="white" text-anchor="middle">✏️</text>
</svg>''',
        
        "concept_folder": '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <!-- Folder-based concept -->
  <circle cx="256" cy="256" r="240" fill="#F5F5F5" stroke="#BDBDBD" stroke-width="4"/>
  
  <!-- Folder -->
  <path d="M120 200 L140 180 L200 180 L220 200 L380 200 L380 340 L120 340 Z" 
        fill="#FFC107" stroke="#FF8F00" stroke-width="3"/>
  
  <!-- Comics coming out of folder -->
  <rect x="140" y="160" width="40" height="60" rx="4" fill="#E91E63" transform="rotate(-10 160 190)"/>
  <rect x="180" y="150" width="40" height="60" rx="4" fill="#3F51B5" transform="rotate(5 200 180)"/>
  <rect x="220" y="155" width="40" height="60" rx="4" fill="#4CAF50" transform="rotate(15 240 185)"/>
  
  <!-- Organization arrows -->
  <path d="M300 240 L340 240" stroke="#FF5722" stroke-width="6" marker-end="url(#arrow)"/>
  <path d="M300 260 L340 260" stroke="#FF5722" stroke-width="6" marker-end="url(#arrow)"/>
  <path d="M300 280 L340 280" stroke="#FF5722" stroke-width="6" marker-end="url(#arrow)"/>
  
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="3" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#FF5722"/>
    </marker>
  </defs>
</svg>''',
        
        "concept_modern": '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <!-- Modern flat design concept -->
  <rect width="512" height="512" rx="80" ry="80" fill="url(#modernGrad)"/>
  
  <defs>
    <linearGradient id="modernGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea"/>
      <stop offset="100%" style="stop-color:#764ba2"/>
    </linearGradient>
  </defs>
  
  <!-- Comic stack -->
  <rect x="140" y="120" width="100" height="140" rx="8" fill="#FFFFFF" opacity="0.9"/>
  <rect x="160" y="100" width="100" height="140" rx="8" fill="#FFE082"/>
  <rect x="180" y="80" width="100" height="140" rx="8" fill="#81C784"/>
  
  <!-- Edit symbol -->
  <circle cx="360" cy="180" r="50" fill="#FFFFFF"/>
  <path d="M340 160 L360 160 L350 200 Z" fill="#667eea"/>
  <circle cx="365" cy="155" r="8" fill="#667eea"/>
  
  <!-- Connection line -->
  <path d="M280 150 Q320 130 340 160" stroke="#FFFFFF" stroke-width="4" fill="none"/>
</svg>'''
    }
    
    icons_dir = Path("icons")
    
    for name, svg_content in concepts.items():
        concept_file = icons_dir / f"{name}.svg"
        with open(concept_file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"✅ Concept créé: {concept_file}")

if __name__ == "__main__":
    try:
        # Create main icons
        icons_dir = create_icon_files()
        
        print("\n🎨 Création de concepts supplémentaires...")
        create_additional_concepts()
        
        print("\n🎉 Génération terminée!")
        print(f"📁 Tous les fichiers sont dans le dossier: {icons_dir}")
        print("\n💡 Étapes suivantes:")
        print("   1. Ouvrez icons/preview.html pour voir l'icône principale")
        print("   2. Choisissez votre concept préféré")
        print("   3. Copiez l'icône vers icon.ico pour l'exécutable Windows")
        print("   4. Utilisez le SVG pour les autres plateformes")
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()
