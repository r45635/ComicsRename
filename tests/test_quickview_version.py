#!/usr/bin/env python3
"""
Test pour vérifier visuellement la version QuickView utilisée
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class QuickViewTester(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test QuickView - Vérification Version")
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("Cliquez pour tester QuickView et vérifier la version utilisée")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Test button
        test_btn = QPushButton("🔍 Tester QuickView avec PDF")
        test_btn.clicked.connect(self.test_quickview)
        layout.addWidget(test_btn)
        
        # Results label
        self.result_label = QLabel("Résultat du test s'affichera ici...")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("QLabel { padding: 10px; background-color: #f0f0f0; }")
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
        
    def test_quickview(self):
        try:
            from ui.quick_view import QuickViewDialog
            
            # Chercher un fichier PDF
            test_pdf = 'test_quick_view.pdf'
            if not os.path.exists(test_pdf):
                self.result_label.setText("❌ Fichier test_quick_view.pdf non trouvé. Créez-le d'abord.")
                return
                
            # Créer et afficher QuickView  
            dialog = QuickViewDialog(self, test_pdf)
            if dialog.file_path:
                dialog.show()
                
                # Analyser les fonctionnalités
                features = []
                if hasattr(dialog, 'first_btn'):
                    features.append("✅ Navigation: First/Prev/Next/Last")
                if hasattr(dialog, 'zoom_in_btn'):
                    features.append("✅ Zoom: Boutons manuels")
                if hasattr(dialog, 'export_btn'):
                    features.append("✅ Export: PNG haute qualité")
                if hasattr(dialog, 'pdf_view_wrapper') and hasattr(dialog.pdf_view_wrapper, 'panning'):
                    features.append("✅ Pan: Clic-gauche + glisser")
                
                result_text = f"🎉 NOUVELLE VERSION ACTIVE!\n\n" + "\n".join(features)
                result_text += f"\n\n📋 Instructions d'utilisation:\n"
                result_text += f"• Zoom: Boutons 🔍+ / 🔍- ou Ctrl + molette\n"
                result_text += f"• Pan: Clic-gauche + glisser (quand zoomé)\n"
                result_text += f"• Navigation: ⏮ ◀ ▶ ⏭\n"
                result_text += f"• Export: 💾 Export PNG\n"
                
                self.result_label.setText(result_text)
            else:
                self.result_label.setText("❌ Erreur création QuickView dialog")
                
        except Exception as e:
            self.result_label.setText(f"❌ Erreur: {e}")

def main():
    app = QApplication(sys.argv)
    
    # Créer le testeur
    tester = QuickViewTester()
    tester.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
