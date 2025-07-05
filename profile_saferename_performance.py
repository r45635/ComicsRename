#!/usr/bin/env python3
"""
Script de profilage pour identifier les goulots d'étranglement de SafeRename
"""

import os
import sys
import time
import tempfile
import requests
from pathlib import Path

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_pdf():
    """Create a simple test PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.close()
        
        c = canvas.Canvas(temp_file.name, pagesize=letter)
        c.drawString(100, 750, "Test PDF for Performance Analysis")
        c.setFillColorRGB(0.2, 0.4, 0.8)
        c.rect(100, 500, 200, 300, fill=True)
        c.setFillColorRGB(1, 1, 1)
        c.drawString(150, 650, "TEST")
        c.save()
        
        return temp_file.name
    except ImportError:
        print("⚠️  ReportLab not available. Using existing PDF if available.")
        return None

def find_existing_pdf():
    """Find an existing PDF file for testing"""
    pdf_dirs = [
        "/Users/vincentcruvellier/OneDrive/Ebooks/TEMP-GATEWAY",
        "/Users/vincentcruvellier/Documents",
        "/Users/vincentcruvellier/Downloads"
    ]
    
    for pdf_dir in pdf_dirs:
        if os.path.exists(pdf_dir):
            for file in os.listdir(pdf_dir):
                if file.lower().endswith('.pdf'):
                    pdf_path = os.path.join(pdf_dir, file)
                    if os.path.getsize(pdf_path) > 100000:  # At least 100KB
                        return pdf_path
    return None

def profile_saferename_operations():
    """Profile each operation in SafeRename to identify bottlenecks"""
    
    print("=== Profilage des opérations SafeRename ===")
    
    # Get a test PDF
    pdf_path = create_test_pdf()
    if not pdf_path:
        pdf_path = find_existing_pdf()
    
    if not pdf_path:
        print("❌ Aucun PDF disponible pour les tests")
        return False
    
    print(f"✅ PDF de test: {os.path.basename(pdf_path)}")
    
    # Test cover URL
    cover_url = "https://www.bedetheque.com/media/Couvertures/Couv_51823.jpg"
    
    try:
        from pdf_cover_comparator_qt import PDFCoverComparator
        comparator = PDFCoverComparator(ssim_threshold=0.7)
        
        print(f"\n1. Test de téléchargement d'image...")
        start_time = time.time()
        cover_path = comparator._download_image(cover_url)
        download_time = time.time() - start_time
        print(f"   Temps de téléchargement: {download_time:.3f}s")
        
        print(f"\n2. Test d'extraction de page PDF...")
        start_time = time.time()
        pdf_image_path = comparator._extract_first_page_qt(pdf_path)
        extraction_time = time.time() - start_time
        print(f"   Temps d'extraction PDF: {extraction_time:.3f}s")
        
        print(f"\n3. Test de préprocessing des images...")
        start_time = time.time()
        img_pdf = comparator._load_and_resize(pdf_image_path)
        img_cover = comparator._load_and_resize(cover_path)
        preprocess_time = time.time() - start_time
        print(f"   Temps de préprocessing: {preprocess_time:.3f}s")
        
        print(f"\n4. Test de comparaison SSIM...")
        start_time = time.time()
        from skimage.metrics import structural_similarity as ssim
        score = ssim(img_pdf, img_cover)
        ssim_time = time.time() - start_time
        print(f"   Temps de comparaison SSIM: {ssim_time:.3f}s")
        print(f"   Score SSIM: {score:.3f}")
        
        # Calcul des proportions
        total_time = download_time + extraction_time + preprocess_time + ssim_time
        
        print(f"\n📊 Analyse des temps (total: {total_time:.3f}s):")
        print(f"   Téléchargement:  {download_time:.3f}s ({download_time/total_time*100:.1f}%)")
        print(f"   Extraction PDF:  {extraction_time:.3f}s ({extraction_time/total_time*100:.1f}%)")
        print(f"   Préprocessing:   {preprocess_time:.3f}s ({preprocess_time/total_time*100:.1f}%)")
        print(f"   Comparaison:     {ssim_time:.3f}s ({ssim_time/total_time*100:.1f}%)")
        
        # Analyse des goulots d'étranglement
        max_time = max(download_time, extraction_time, preprocess_time, ssim_time)
        if max_time == download_time:
            bottleneck = "Téléchargement d'image"
        elif max_time == extraction_time:
            bottleneck = "Extraction PDF"
        elif max_time == preprocess_time:
            bottleneck = "Préprocessing"
        else:
            bottleneck = "Comparaison SSIM"
        
        print(f"\n🎯 Goulot d'étranglement principal: {bottleneck}")
        
        # Calcul de l'amélioration théorique
        improvement_percentage = (download_time / total_time) * 100
        print(f"\n💡 Amélioration théorique avec cache: {improvement_percentage:.1f}%")
        
        if improvement_percentage < 30:
            print(f"⚠️  L'amélioration est limitée car l'extraction PDF prend {extraction_time/total_time*100:.1f}% du temps")
            print(f"   Suggestions d'optimisation:")
            print(f"   - Cache des pages PDF extraites")
            print(f"   - Résolution plus faible pour l'extraction")
            print(f"   - Préprocessing optimisé")
        
        # Nettoyage
        os.unlink(cover_path)
        os.unlink(pdf_image_path)
        if pdf_path.startswith('/tmp/'):
            os.unlink(pdf_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du profilage: {e}")
        return False

def suggest_optimizations():
    """Suggest additional optimizations"""
    
    print(f"\n=== Suggestions d'optimisations supplémentaires ===")
    
    print(f"\n1. 🚀 Cache des pages PDF extraites")
    print(f"   - Stocker les premières pages extraites des PDFs")
    print(f"   - Éviter la re-extraction pour les mêmes fichiers")
    print(f"   - Gain potentiel: 30-60% selon la taille des PDFs")
    
    print(f"\n2. ⚡ Extraction PDF optimisée")
    print(f"   - Réduire la résolution d'extraction (150 DPI → 100 DPI)")
    print(f"   - Limiter la taille max de l'image extraite")
    print(f"   - Gain potentiel: 20-40%")
    
    print(f"\n3. 🔄 Préprocessing parallèle")
    print(f"   - Traitement simultané PDF et couverture")
    print(f"   - Threading pour les opérations I/O")
    print(f"   - Gain potentiel: 15-30%")
    
    print(f"\n4. 📏 Comparaison optimisée")
    print(f"   - Images plus petites pour SSIM (128x128 au lieu de 256x256)")
    print(f"   - Algorithme de comparaison plus rapide")
    print(f"   - Gain potentiel: 10-25%")

def main():
    """Test principal de profilage"""
    
    print("SafeRename Performance Profiler")
    print("=" * 50)
    print("Analyse des goulots d'étranglement pour optimiser SafeRename")
    print()
    
    success = profile_saferename_operations()
    
    if success:
        suggest_optimizations()
    
    print("\n" + "=" * 50)
    print("Conclusion:")
    print("L'optimisation du cache d'images est un bon début, mais")
    print("l'extraction PDF reste souvent le goulot d'étranglement principal.")
    print("Des optimisations supplémentaires sont possibles.")

if __name__ == "__main__":
    main()
