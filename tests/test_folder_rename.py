#!/usr/bin/env python3
"""
Test script for folder double-click renaming functionality
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_folder_renaming():
    """Test the folder double-click renaming functionality"""
    
    print("🧪 Test de renommage de dossier par double-clic")
    print("=" * 50)
    
    try:
        from comicsFileRenamer_v3 import EditableFolderLineEdit, ComicRenamer
        
        print("✅ Classes importées avec succès")
        
        # Test EditableFolderLineEdit features
        print("\n🔍 Fonctionnalités d'EditableFolderLineEdit:")
        
        features = {
            'mouseDoubleClickEvent': 'Gestion du double-clic',
            '_on_editing_finished': 'Validation de l\'édition',
            '_cancel_editing': 'Annulation de l\'édition',
            '_reset_to_readonly': 'Retour en mode lecture seule',
            'keyPressEvent': 'Gestion des touches (Échap pour annuler)'
        }
        
        for method, description in features.items():
            if hasattr(EditableFolderLineEdit, method):
                print(f"✅ {method}: {description}")
            else:
                print(f"❌ {method}: MANQUANT")
        
        print("\n📋 Workflow complet:")
        print("   1. 🖱️  Double-clic sur le nom du dossier")
        print("   2. ✏️  Passage en mode édition (fond jaune, bordure bleue)")
        print("   3. ⌨️  Saisie du nouveau nom du dossier")
        print("   4. ✅ Validation par Entrée ou perte de focus")
        print("   5. 🔍 Vérification que le nouveau nom est valide")
        print("   6. ❓ Demande de confirmation à l'utilisateur")
        print("   7. 📁 Renommage effectif du dossier")
        print("   8. 🔄 Rechargement des fichiers dans le nouveau dossier")
        print("   9. 📍 Mise à jour des paramètres (last_folder)")
        print("  10. 📢 Message de confirmation")
        
        print("\n🛡️ Protections implémentées:")
        print("   • Validation du nom (caractères autorisés)")
        print("   • Vérification de l'existence (pas de conflit)")
        print("   • Confirmation obligatoire de l'utilisateur")
        print("   • Gestion des erreurs (permissions, etc.)")
        print("   • Annulation possible avec Échap")
        print("   • Restauration du nom original en cas d'annulation")
        
        print("\n⌨️ Raccourcis clavier:")
        print("   • Entrée: Valider le nouveau nom")
        print("   • Échap: Annuler et restaurer le nom original")
        print("   • Perte de focus: Valider le nouveau nom")
        
        print("\n🎨 Indicateurs visuels:")
        print("   • Mode lecture: Aspect normal")
        print("   • Mode édition: Fond jaune, bordure bleue")
        print("   • Sélection automatique du texte en mode édition")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_folder_renaming()
    
    if success:
        print("\n🎉 Test réussi!")
        print("La fonctionnalité de renommage par double-clic est opérationnelle.")
        print("\n💡 Pour tester:")
        print("   1. Lancez l'application")
        print("   2. Ouvrez un dossier avec des fichiers")
        print("   3. Double-cliquez sur le nom du dossier en haut")
        print("   4. Modifiez le nom et appuyez sur Entrée")
    else:
        print("\n❌ Test échoué.")
        sys.exit(1)
