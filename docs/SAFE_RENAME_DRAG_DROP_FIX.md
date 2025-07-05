# SafeRename Drag & Drop Integration Fix

## Problème identifié

La fonctionnalité **SafeRename** n'était pas appelée lors du renommage par **drag & drop** (glisser-déposer) d'albums vers des fichiers. Cette fonction importante vérifie que la première page d'un PDF correspond à la couverture de l'album avant de procéder au renommage.

## Solution implémentée

### 1. Modification du stockage des métadonnées

**Fichier:** `ui/tables.py` - Méthode `mouseMoveEvent()` (ligne ~282)

```python
def mouseMoveEvent(self, event):
    it = self.itemAt(event.pos())
    if not it:
        return
    
    # Get the full metadata stored in UserRole
    import json
    from PySide6.QtCore import Qt
    
    meta = it.data(Qt.ItemDataRole.UserRole)
    if meta:
        # Store complete metadata as JSON
        meta_json = json.dumps(meta, default=str)
        mime = QMimeData()
        mime.setData('application/x-comic-meta', QByteArray(meta_json.encode()))
    else:
        # Fallback to text-only if no metadata
        mime = QMimeData()
        mime.setData('application/x-comic-meta', QByteArray(it.text().encode()))
    
    drag = QDrag(self)
    drag.setMimeData(mime)
    drag.exec(Qt.CopyAction)
```

**Changement:** Au lieu de stocker seulement le texte (`it.text()`), on stocke maintenant les métadonnées complètes en JSON, incluant les URLs de couverture nécessaires pour SafeRename.

### 2. Modification de la réception du drag & drop

**Fichier:** `ui/tables.py` - Méthode `dropEvent()` (ligne ~57)

```python
def dropEvent(self, event):
    # Internal drag & drop (DnD rename)
    if event.mimeData().hasFormat('application/x-comic-meta'):
        # ... existing code ...
        
        payload = event.mimeData().data('application/x-comic-meta').data().decode()
        
        # Try to parse as JSON (complete metadata)
        try:
            import json
            meta = json.loads(payload)
            
            # Extract information from metadata
            series = meta.get('series', meta.get('album_name', ''))
            num = meta.get('num', meta.get('issue_number', ''))
            title = meta.get('title', meta.get('album_name', ''))
            y = meta.get('year', meta.get('parution', ''))
            
            # Use the complete metadata for SafeRename
            use_complete_meta = True
            
        except (json.JSONDecodeError, TypeError):
            # Fallback to parsing text format
            use_complete_meta = False
            # ... créer métadonnées basiques ...
        
        # ... code de renommage ...
        
        # Check if Safe Rename is enabled for PDFs
        is_pdf = f['ext'].lower() == '.pdf'
        safe_rename_enabled = self.main.settings.value('safe_rename', 'false') == 'true'
        
        if safe_rename_enabled and is_pdf:
            # Perform Safe Rename check with complete metadata
            proceed = self.main._perform_safe_rename_check(f, meta)
            if not proceed:
                return  # User cancelled
        
        # Proceed with rename
        os.rename(f['path'], new_path)
```

**Changement:** Ajout de la vérification SafeRename avec les métadonnées complètes avant le renommage.

## Bénéfices de cette correction

1. **Sécurité renforcée** : SafeRename fonctionne maintenant avec le drag & drop
2. **Métadonnées complètes** : Les URLs de couverture sont disponibles pour la comparaison
3. **Compatibilité** : Rétro-compatibilité avec l'ancien format texte
4. **Cohérence** : Même comportement entre renommage par bouton et par drag & drop

## Test de la correction

1. Activer SafeRename dans les paramètres
2. Chercher un album avec une couverture
3. Glisser-déposer l'album vers un fichier PDF
4. Vérifier que la boîte de dialogue de comparaison apparaît si les couvertures ne correspondent pas

## Avant/Après

**Avant :**
- Drag & drop → Renommage direct sans vérification
- Risque de renommer avec les mauvaises métadonnées

**Après :**
- Drag & drop → Vérification SafeRename → Renommage sécurisé
- Même niveau de sécurité qu'avec le bouton de renommage

## Fichiers modifiés

- `ui/tables.py` : Méthodes `mouseMoveEvent()` et `dropEvent()`
- `docs/SAFE_RENAME_DRAG_DROP_FIX.md` : Cette documentation

## Date de correction

**5 juillet 2025** - Correction implémentée et testée

---

Cette correction résout complètement le problème de SafeRename qui n'était pas appelé lors du drag & drop.
