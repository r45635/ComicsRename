# Corrections SafeRename et Format de Nom - 5 juillet 2025

## Problèmes identifiés et résolus

### Problème 1 : SafeRename non appelé automatiquement en drag & drop ❌

**Cause :** 
- SafeRename n'était pas présent dans l'interface des paramètres
- Métadonnées incomplètes transmises lors du drag & drop
- Aucun appel à `_perform_safe_rename_check` dans le code de drop

**Solutions appliquées :** ✅

1. **Ajout de SafeRename aux paramètres UI** (`ui/dialogs.py`)
   ```python
   # Ajout de la checkbox SafeRename
   self.safe_rename_cb = QCheckBox()
   self.safe_rename_cb.setChecked(self.settings.value('safe_rename', 'false') == 'true')
   self.safe_rename_cb.setToolTip(tr("ui.tooltips.safe_rename"))
   self.layout.addRow(tr("ui.labels.safe_rename"), self.safe_rename_cb)
   
   # Sauvegarde du paramètre
   self.settings.setValue("safe_rename", 'true' if self.safe_rename_cb.isChecked() else 'false')
   ```

2. **Amélioration des métadonnées en drag & drop** (`ui/tables.py`)
   ```python
   # Stockage des métadonnées complètes en JSON au lieu du simple texte
   meta = it.data(Qt.ItemDataRole.UserRole)
   if meta:
       meta_json = json.dumps(meta, default=str)
       mime.setData('application/x-comic-meta', QByteArray(meta_json.encode()))
   ```

3. **Intégration SafeRename dans dropEvent** (`ui/tables.py`)
   ```python
   # Vérification SafeRename pour les PDFs
   if safe_rename_enabled and is_pdf:
       proceed = self.main._perform_safe_rename_check(f, meta)
       if not proceed:
           return  # User cancelled
   ```

4. **Ajout de debug extensif**
   - Messages de debug dans `mouseMoveEvent`
   - Messages de debug dans `dropEvent`
   - Messages de debug dans `_perform_safe_rename_check`

### Problème 2 : Format de nom de fichier incorrect ❌

**Problème :** Le nom final devait être `Serie Name - Album Number - Album Title (Year)`

**Solution appliquée :** ✅

```python
# Format unifié dans drag & drop ET renommage par bouton
base = f"{clean(series)} - {format_num(num)} - {clean(title)}"
if y:
    base += f" ({y})"
```

## Fichiers modifiés

### `ui/dialogs.py`
- ✅ Ajout de la checkbox SafeRename dans SettingsDialog
- ✅ Ajout de la sauvegarde du paramètre safe_rename

### `ui/tables.py` 
- ✅ Modification de `mouseMoveEvent` pour transmettre métadonnées JSON complètes
- ✅ Modification de `dropEvent` pour parser JSON et appeler SafeRename
- ✅ Ajout de debug extensif
- ✅ Correction du format de nom de fichier

### `comicsFileRenamer_v3.py`
- ✅ Ajout de debug dans `_perform_safe_rename_check`

### Nouveaux fichiers de test/debug
- ✅ `test_drag_drop_debug.py` - Script pour tester le drag & drop
- ✅ `test_corrections.py` - Script pour valider les corrections
- ✅ `docs/SAFE_RENAME_DRAG_DROP_FIX.md` - Documentation technique

## Test des corrections

### Comment tester SafeRename en drag & drop :

1. **Lancez l'application :**
   ```bash
   python3 main.py
   ```

2. **Activez SafeRename :**
   - Menu Paramètres → Cochez "Renommage Sécurisé"

3. **Testez avec un PDF :**
   - Cherchez un album avec couverture
   - Glissez-déposez sur un fichier PDF
   - Vérifiez les messages de debug dans la console

### Messages de debug attendus :

```
[DEBUG] Drag started - Text: Album Name
[DEBUG] Drag started - Meta available: True
[DEBUG] Drag started - Cover URL: https://...

[DEBUG] Drop event triggered
[DEBUG] Drop - Successfully parsed JSON metadata
[DEBUG] Drop - Cover URL: https://...
[DEBUG] Drop - Safe Rename enabled: True
[DEBUG] SafeRename - Starting check for file.pdf
[DEBUG] SafeRename - Cover URL: https://...
```

### Test du format de nom :

```bash
python3 test_corrections.py
```

## Résultat

✅ **SafeRename fonctionne maintenant en drag & drop**
✅ **Format de nom cohérent : "Serie Name - Album Number - Album Title (Year)"**
✅ **Interface utilisateur complète avec option SafeRename**
✅ **Debug extensif pour faciliter le diagnostic**

---

**Date :** 5 juillet 2025  
**Status :** ✅ Corrigé et testé  
**Version :** 3.4.3+
