# 🔐 SÉCURITÉ - Configuration des Identifiants

## ⚠️ IMPORTANT : Protection des Identifiants

Ce projet nécessite des identifiants sensibles qui **NE DOIVENT JAMAIS** être stockés dans le code source.

## 📋 Configuration Requise

### 1. Fichier .env (RECOMMANDÉ)

Copiez `.env.example` vers `.env` et remplissez vos identifiants :

```bash
cp .env.example .env
```

Éditez `.env` avec vos vraies informations :
```bash
# Identifiants BDGest
BDGEST_USERNAME=votre_nom_utilisateur_bdgest
BDGEST_PASSWORD=votre_mot_de_passe_bdgest

# Clé API ComicVine
COMICVINE_API_KEY=votre_cle_api_comicvine
```

### 2. Variables d'Environnement (ALTERNATIF)

```bash
export BDGEST_USERNAME="votre_nom_utilisateur"
export BDGEST_PASSWORD="votre_mot_de_passe"
export COMICVINE_API_KEY="votre_cle_api"
```

## 🛡️ Bonnes Pratiques de Sécurité

### ✅ À FAIRE :
- ✅ Utiliser des variables d'environnement ou fichier .env
- ✅ Ajouter .env au .gitignore (déjà fait)
- ✅ Ne jamais commiter les identifiants réels
- ✅ Utiliser des identifiants de test différents des identifiants de production

### ❌ À NE JAMAIS FAIRE :
- ❌ Stocker les identifiants directement dans le code
- ❌ Commiter le fichier .env
- ❌ Partager vos identifiants publiquement
- ❌ Utiliser les mêmes identifiants pour tests et production

## 🔧 Obtenir les Identifiants

### BDGest
1. Créez un compte sur https://www.bedetheque.com/
2. Utilisez votre nom d'utilisateur et mot de passe

### ComicVine
1. Créez un compte sur https://comicvine.gamespot.com/
2. Allez dans votre profil → API
3. Générez une nouvelle clé API

## 🚨 En Cas de Compromission

Si vos identifiants sont compromis :

1. **Changez immédiatement** vos mots de passe
2. **Révoquéz** les clés API compromises
3. **Générez** de nouvelles clés API
4. **Vérifiez** l'historique Git pour les identifiants exposés

## 📞 Support

En cas de problème de sécurité, contactez l'équipe de développement immédiatement.
