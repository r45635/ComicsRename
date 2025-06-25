#!/usr/bin/env python3
"""
Simple Icon Creator for ComicsRename
Creates application icons using Pillow (no Cairo dependency)
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_simple_icon(size=512):
    """Create a simple icon using Pillow"""
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Scale factor for drawing
    s = size / 512
    
    # Background circle
    circle_radius = int(240 * s)
    circle_center = (size // 2, size // 2)
    draw.ellipse([
        circle_center[0] - circle_radius, circle_center[1] - circle_radius,
        circle_center[0] + circle_radius, circle_center[1] + circle_radius
    ], fill=(248, 249, 250, 255), outline=(233, 236, 239, 255), width=int(4 * s))
    
    # Main comic book
    comic_x, comic_y = int(140 * s), int(120 * s)
    comic_w, comic_h = int(180 * s), int(240 * s)
    draw.rounded_rectangle([
        comic_x, comic_y, comic_x + comic_w, comic_y + comic_h
    ], radius=int(12 * s), fill=(255, 107, 107, 255), outline=(44, 62, 80, 255), width=int(3 * s))
    
    # Comic spine
    draw.rounded_rectangle([
        comic_x, comic_y, comic_x + int(20 * s), comic_y + comic_h
    ], radius=int(12 * s), fill=(44, 62, 80, 200))
    
    # Comic pages
    page_x, page_y = comic_x + int(20 * s), comic_y + int(10 * s)
    page_w, page_h = int(150 * s), int(220 * s)
    draw.rounded_rectangle([
        page_x, page_y, page_x + page_w, page_y + page_h
    ], radius=int(8 * s), fill=(255, 255, 255, 230))
    
    # Inner page
    inner_x, inner_y = page_x + int(10 * s), page_y + int(10 * s)
    inner_w, inner_h = int(130 * s), int(200 * s)
    draw.rounded_rectangle([
        inner_x, inner_y, inner_x + inner_w, inner_y + inner_h
    ], radius=int(6 * s), fill=(241, 243, 244, 255), outline=(189, 195, 199, 255), width=int(1 * s))
    
    # Comic panels
    panel_x, panel_y = inner_x + int(10 * s), inner_y + int(20 * s)
    
    # Panel 1
    draw.rounded_rectangle([
        panel_x, panel_y, panel_x + int(50 * s), panel_y + int(40 * s)
    ], radius=int(3 * s), fill=(255, 230, 109, 255), outline=(255, 107, 107, 255), width=int(2 * s))
    
    # Panel 2
    draw.rounded_rectangle([
        panel_x + int(60 * s), panel_y, panel_x + int(110 * s), panel_y + int(40 * s)
    ], radius=int(3 * s), fill=(168, 230, 207, 255), outline=(78, 205, 196, 255), width=int(2 * s))
    
    # Panel 3
    draw.rounded_rectangle([
        panel_x, panel_y + int(50 * s), panel_x + int(110 * s), panel_y + int(80 * s)
    ], radius=int(3 * s), fill=(255, 179, 179, 255), outline=(255, 107, 107, 255), width=int(2 * s))
    
    # Panel 4
    draw.rounded_rectangle([
        panel_x, panel_y + int(90 * s), panel_x + int(110 * s), panel_y + int(130 * s)
    ], radius=int(3 * s), fill=(179, 217, 255, 255), outline=(69, 183, 209, 255), width=int(2 * s))
    
    # Rename tag
    tag_x, tag_y = int(320 * s), int(200 * s)
    tag_w, tag_h = int(80 * s), int(40 * s)
    draw.rounded_rectangle([
        tag_x, tag_y, tag_x + tag_w, tag_y + tag_h
    ], radius=int(20 * s), fill=(40, 167, 69, 255), outline=(30, 126, 52, 255), width=int(2 * s))
    
    # Simple edit symbol in tag
    edit_x, edit_y = tag_x + int(20 * s), tag_y + int(10 * s)
    draw.polygon([
        (edit_x, edit_y + int(10 * s)),
        (edit_x + int(15 * s), edit_y + int(10 * s)),
        (edit_x + int(12 * s), edit_y + int(20 * s)),
        (edit_x + int(3 * s), edit_y + int(20 * s))
    ], fill=(255, 255, 255, 255))
    
    draw.ellipse([
        edit_x + int(18 * s), edit_y + int(5 * s),
        edit_x + int(30 * s), edit_y + int(17 * s)
    ], fill=(255, 255, 255, 255))
    
    # Folder base
    folder_y = int(320 * s)
    folder_points = [
        (int(100 * s), folder_y + int(80 * s)),
        (int(120 * s), folder_y),
        (int(200 * s), folder_y),
        (int(220 * s), folder_y + int(20 * s)),
        (int(420 * s), folder_y + int(20 * s)),
        (int(420 * s), folder_y + int(80 * s))
    ]
    draw.polygon(folder_points, fill=(255, 193, 7, 150), outline=(245, 124, 0, 255), width=int(2 * s))
    
    return img

def create_all_icon_sizes():
    """Create icons in all needed sizes"""
    
    print("🎨 Création des icônes ComicsRename (Pillow)")
    print("=" * 50)
    
    # Create icons directory
    icons_dir = Path("icons")
    icons_dir.mkdir(exist_ok=True)
    
    # Icon sizes needed
    sizes = [16, 32, 48, 64, 128, 256, 512]
    
    icons_created = []
    
    for size in sizes:
        print(f"📐 Création icône {size}x{size}...")
        
        # Create icon
        icon = create_simple_icon(size)
        
        # Save PNG
        png_file = icons_dir / f"comicsrename_{size}x{size}.png"
        icon.save(png_file, "PNG")
        icons_created.append(png_file)
        print(f"   ✅ PNG sauvé: {png_file}")
    
    # Create ICO file (Windows)
    print("🪟 Création du fichier ICO pour Windows...")
    ico_sizes = [16, 32, 48, 256]  # Common ICO sizes
    ico_images = []
    
    for size in ico_sizes:
        ico_images.append(create_simple_icon(size))
    
    ico_file = icons_dir / "comicsrename.ico"
    ico_images[0].save(ico_file, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
    print(f"   ✅ ICO sauvé: {ico_file}")
    
    # Create a high-res version for app stores
    print("📱 Création version haute résolution...")
    hires = create_simple_icon(1024)
    hires_file = icons_dir / "comicsrename_1024x1024.png"
    hires.save(hires_file, "PNG")
    print(f"   ✅ Haute résolution: {hires_file}")
    
    # Copy main icon for PyInstaller
    main_icon = icons_dir / "icon.ico"
    ico_images[0].save(main_icon, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
    print(f"   ✅ Icône principale: {main_icon}")
    
    return icons_dir, icons_created

def create_html_preview(icons_dir, icons_created):
    """Create HTML preview of all icons"""
    
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>ComicsRename - Icônes Générées</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; 
               padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
               color: white; min-height: 100vh; margin: 0; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 3em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; opacity: 0.9; margin: 10px 0; }
        .icon-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                     gap: 20px; margin: 40px 0; }
        .icon-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); 
                     border-radius: 15px; padding: 20px; text-align: center; 
                     border: 1px solid rgba(255,255,255,0.2); }
        .icon-card img { max-width: 100%; height: auto; margin: 10px 0; 
                         background: white; border-radius: 8px; padding: 10px; }
        .icon-title { font-weight: bold; margin: 10px 0; }
        .icon-info { font-size: 0.9em; opacity: 0.8; }
        .usage-section { background: rgba(255,255,255,0.1); border-radius: 15px; 
                        padding: 30px; margin: 40px 0; }
        .usage-section h2 { margin-top: 0; }
        .usage-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                     gap: 20px; margin: 20px 0; }
        .usage-item { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 20px; }
        .usage-item h3 { margin-top: 0; color: #FFE66D; }
        .code { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; 
                font-family: Monaco, monospace; font-size: 0.9em; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                   gap: 15px; margin: 20px 0; }
        .feature { background: rgba(255,255,255,0.05); border-radius: 10px; padding: 15px; }
        .feature h4 { margin: 0 0 10px 0; color: #A8E6CF; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 ComicsRename</h1>
            <p>Icônes de l'Application</p>
            <p><em>Générées avec Pillow - Prêtes pour toutes les plateformes</em></p>
        </div>

        <div class="icon-grid">'''
    
    # Add icon cards
    sizes_info = {
        16: "Barre des tâches Windows",
        32: "Icône système, listes",
        48: "Icône bureau Windows",
        64: "Icône détaillée",
        128: "Dock macOS, aperçus",
        256: "Haute résolution",
        512: "Très haute résolution",
        1024: "App Store, distribution"
    }
    
    for icon_file in sorted(icons_created, key=lambda x: int(x.stem.split('_')[1].split('x')[0])):
        size = int(icon_file.stem.split('_')[1].split('x')[0])
        usage = sizes_info.get(size, "Usage général")
        
        html_content += f'''
            <div class="icon-card">
                <img src="{icon_file.name}" alt="Icône {size}x{size}">
                <div class="icon-title">{size}×{size} pixels</div>
                <div class="icon-info">{usage}</div>
            </div>'''
    
    html_content += '''
        </div>

        <div class="usage-section">
            <h2>🚀 Utilisation des Icônes</h2>
            
            <div class="usage-grid">
                <div class="usage-item">
                    <h3>🪟 Windows (PyInstaller)</h3>
                    <p>Utilisez le fichier <strong>icon.ico</strong> dans votre spec :</p>
                    <div class="code">icon='icon.ico'</div>
                </div>
                
                <div class="usage-item">
                    <h3>🍎 macOS (Bundle)</h3>
                    <p>Utilisez les PNG haute résolution :</p>
                    <div class="code">comicsrename_512x512.png<br>comicsrename_1024x1024.png</div>
                </div>
                
                <div class="usage-item">
                    <h3>🐧 Linux (Desktop)</h3>
                    <p>Fichiers PNG pour .desktop :</p>
                    <div class="code">Icon=comicsrename_256x256.png</div>
                </div>
                
                <div class="usage-item">
                    <h3>📦 Distribution</h3>
                    <p>GitHub, documentation, sites web :</p>
                    <div class="code">comicsrename_128x128.png<br>comicsrename_256x256.png</div>
                </div>
            </div>
        </div>

        <div class="usage-section">
            <h2>🎯 Caractéristiques du Design</h2>
            
            <div class="features">
                <div class="feature">
                    <h4>📚 Livre de BD</h4>
                    <p>Représente les comics avec des panels colorés et une couverture attrayante</p>
                </div>
                
                <div class="feature">
                    <h4>🏷️ Tag de Renommage</h4>
                    <p>Symbole vert avec icône d'édition pour indiquer la fonction de renommage</p>
                </div>
                
                <div class="feature">
                    <h4>📁 Organisation</h4>
                    <p>Base de dossier suggérant l'organisation et la structure des fichiers</p>
                </div>
                
                <div class="feature">
                    <h4>🎨 Couleurs Vibrantes</h4>
                    <p>Palette moderne avec rouge, bleu, vert et jaune pour un look dynamique</p>
                </div>
                
                <div class="feature">
                    <h4>📐 Scalabilité</h4>
                    <p>Design vectoriel adapté de 16×16 à 1024×1024 pixels</p>
                </div>
                
                <div class="feature">
                    <h4>🔍 Visibilité</h4>
                    <p>Contrastes élevés et éléments distincts pour une reconnaissance facile</p>
                </div>
            </div>
        </div>

        <div class="usage-section">
            <h2>📋 Étapes Suivantes</h2>
            <ol>
                <li><strong>Testez</strong> les icônes dans votre application</li>
                <li><strong>Copiez</strong> icon.ico vers la racine du projet pour PyInstaller</li>
                <li><strong>Utilisez</strong> les PNG appropriés selon la plateforme</li>
                <li><strong>Distribuez</strong> avec votre application</li>
            </ol>
        </div>
    </div>
</body>
</html>'''
    
    preview_file = icons_dir / "preview.html"
    with open(preview_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return preview_file

if __name__ == "__main__":
    try:
        # Create all icons
        icons_dir, icons_created = create_all_icon_sizes()
        
        # Create preview
        preview_file = create_html_preview(icons_dir, icons_created)
        
        print(f"\n🎉 Génération terminée!")
        print(f"📁 Dossier: {icons_dir}")
        print(f"🌐 Aperçu: {preview_file}")
        print(f"📊 {len(icons_created)} icônes PNG créées")
        print(f"🪟 Fichier ICO pour Windows: comicsrename.ico")
        print(f"🎯 Icône principale: icon.ico")
        
        print(f"\n💡 Prochaines étapes:")
        print(f"   1. Ouvrez {preview_file} dans un navigateur")
        print(f"   2. Copiez icon.ico vers la racine du projet")
        print(f"   3. Testez l'icône dans votre application")
        print(f"   4. Utilisez les PNG selon vos besoins")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
