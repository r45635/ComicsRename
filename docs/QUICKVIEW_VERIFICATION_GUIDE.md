# 🔍 Guide de Vérification QuickView

## Comment vérifier que vous utilisez la NOUVELLE version

### 🎯 **Caractéristiques de la NOUVELLE QuickView :**

#### **1. 📊 Barre d'outils complète**
La nouvelle version doit avoir une barre d'outils en haut avec ces boutons :
```
⏮ First | ◀ Previous | Page 1 of X | Next ▶ | Last ⏭ || 🔍- Zoom Out | 🔍+ Zoom In | Fit Width | 🔍 Fit Page || 💾 Export PNG
```

#### **2. 📝 Instructions utilisateur**  
En bas de la barre d'outils, vous devriez voir :
```
Pan: Left-click + Drag (when zoomed) • Zoom: Ctrl + Mouse wheel
```

#### **3. 🖱️ Fonctionnalité Pan**
- **Clic-gauche + glisser** pour déplacer l'image (quand zoomé)
- Le curseur change en main fermée pendant le pan

#### **4. 🧭 Navigation complète**
- Boutons First/Previous/Next/Last actifs
- Compteur de page dynamique

#### **5. 🔍 Contrôles zoom avancés**
- Boutons Zoom In/Out manuels
- Fit Width / Fit Page
- Ctrl + molette souris

#### **6. 💾 Export PNG**
- Bouton "Export PNG" fonctionnel  
- Qualité 300 DPI

---

### ❌ **Signes de l'ANCIENNE version :**

- Pas de boutons First/Last  
- Pas de bouton Export PNG
- Pas d'instructions utilisateur
- Pan ne fonctionne pas avec clic-gauche
- Interface plus simple/basique

---

### 🧪 **Test rapide :**

1. **Lancez ComicsRename** : `python3 main.py`
2. **Chargez un dossier** avec des fichiers PDF
3. **Clic-droit sur un PDF** → "Quick View"
4. **Vérifiez la barre d'outils** - elle doit être COMPLÈTE

### 📋 **Checklist visuelle :**

- [ ] Boutons ⏮ First et Last ⏭ présents
- [ ] Bouton 💾 Export PNG présent  
- [ ] Instructions "Pan: Left-click..." visibles
- [ ] Zoom In/Out boutons présents
- [ ] Pan fonctionne avec clic-gauche + glisser

---

**Si vous ne voyez PAS ces éléments, merci de me le dire et nous débuggerons ensemble !** 🕵️‍♂️
