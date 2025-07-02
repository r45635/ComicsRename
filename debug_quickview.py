#!/usr/bin/env python3
"""
Debug QuickView - Intercepter les appels pour voir quelle version est utilisée
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Patch pour intercepter les imports QuickView
original_import = __builtins__.__import__

def debug_import(name, *args, **kwargs):
    if 'quick_view' in name.lower() or 'quickview' in name.lower():
        print(f"🔍 DEBUG IMPORT: {name} avec args: {args}")
    return original_import(name, *args, **kwargs)

__builtins__.__import__ = debug_import

# Patch pour intercepter la création de QuickViewDialog
original_quickview_init = None

def patch_quickview():
    """Patch QuickViewDialog pour voir quand il est créé"""
    try:
        from ui.quick_view import QuickViewDialog
        global original_quickview_init
        
        if original_quickview_init is None:
            original_quickview_init = QuickViewDialog.__init__
            
            def debug_init(self, parent=None, file_path=None):
                print(f"🎯 DEBUG QUICKVIEW CRÉÉ:")
                print(f"   - Fichier: {file_path}")
                print(f"   - Parent: {type(parent).__name__ if parent else None}")
                print(f"   - Module: {self.__module__}")
                print(f"   - Classe: {self.__class__}")
                
                # Appeler l'init original
                result = original_quickview_init(self, parent, file_path)
                
                # Vérifier les attributs après création
                print(f"   - A first_btn: {hasattr(self, 'first_btn')}")
                print(f"   - A export_btn: {hasattr(self, 'export_btn')}")
                print(f"   - A pdf_view_wrapper: {hasattr(self, 'pdf_view_wrapper')}")
                if hasattr(self, 'pdf_view_wrapper') and hasattr(self.pdf_view_wrapper, 'panning'):
                    print(f"   - Pan disponible: {hasattr(self.pdf_view_wrapper, 'panning')}")
                
                return result
                
            QuickViewDialog.__init__ = debug_init
            print("✅ QuickViewDialog patché pour debug")
            
    except Exception as e:
        print(f"❌ Erreur patch QuickViewDialog: {e}")

# Patch pour intercepter show_quick_view
def patch_show_quick_view():
    """Patch show_quick_view pour voir quand il est appelé"""
    try:
        from ui.quick_view import QuickViewDialog
        original_show = QuickViewDialog.show_quick_view
        
        def debug_show_quick_view(file_path, parent=None):
            print(f"🚀 DEBUG SHOW_QUICK_VIEW APPELÉ:")
            print(f"   - Fichier: {file_path}")
            print(f"   - Parent: {type(parent).__name__ if parent else None}")
            
            result = original_show(file_path, parent)
            
            print(f"   - Dialog créé: {result is not None}")
            if result:
                print(f"   - Dialog type: {type(result)}")
            
            return result
            
        QuickViewDialog.show_quick_view = staticmethod(debug_show_quick_view)
        print("✅ show_quick_view patché pour debug")
        
    except Exception as e:
        print(f"❌ Erreur patch show_quick_view: {e}")

if __name__ == "__main__":
    print("🔍 DÉMARRAGE DEBUG QUICKVIEW")
    print("=" * 50)
    
    # Appliquer les patches avant d'importer l'application principale
    patch_quickview()
    patch_show_quick_view()
    
    print("📱 Lancement de l'application principale...")
    print("Utilisez QuickView dans l'app et regardez les messages de debug")
    print("=" * 50)
    
    # Lancer l'application normale
    try:
        from main import main
        main()
    except Exception as e:
        print(f"❌ Erreur application: {e}")
        import traceback
        traceback.print_exc()
