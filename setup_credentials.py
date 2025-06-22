#!/usr/bin/env python3
"""
Script de configuration sécurisée des identifiants
Usage: python setup_credentials.py
"""

import os
import getpass
from pathlib import Path

def setup_env_file():
    """Configure le fichier .env avec les identifiants de l'utilisateur"""
    
    print("🔐 Configuration Sécurisée des Identifiants")
    print("=" * 45)
    print()
    
    env_file = Path(".env")
    
    if env_file.exists():
        response = input("⚠️  Le fichier .env existe déjà. Le remplacer ? (y/N): ")
        if response.lower() != 'y':
            print("❌ Configuration annulée.")
            return
    
    print("📝 Veuillez entrer vos identifiants:")
    print("   (Ils seront stockés dans .env, protégé par .gitignore)")
    print()
    
    # BDGest credentials
    print("🔸 BDGest (www.bedetheque.com)")
    bdgest_user = input("   Nom d'utilisateur: ").strip()
    bdgest_pass = getpass.getpass("   Mot de passe: ").strip()
    print()
    
    # ComicVine API key
    print("🔸 ComicVine (comicvine.gamespot.com)")
    print("   (Allez dans votre profil → API pour générer une clé)")
    comicvine_key = getpass.getpass("   Clé API: ").strip()
    print()
    
    # Validation
    if not bdgest_user or not bdgest_pass:
        print("❌ Identifiants BDGest manquants.")
        return
    
    if not comicvine_key:
        print("⚠️  Clé ComicVine manquante (optionnel pour BDGest seulement)")
    
    # Création du fichier .env
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# Configuration ComicsRename - Généré automatiquement\\n")
            f.write("# ⚠️ NE JAMAIS COMMITER CE FICHIER !\\n\\n")
            f.write("# Identifiants BDGest\\n")
            f.write(f"BDGEST_USERNAME={bdgest_user}\\n")
            f.write(f"BDGEST_PASSWORD={bdgest_pass}\\n\\n")
            f.write("# Clé API ComicVine\\n")
            f.write(f"COMICVINE_API_KEY={comicvine_key}\\n")
        
        # Sécuriser les permissions du fichier (Unix seulement)
        try:
            os.chmod(env_file, 0o600)  # Lecture/écriture pour le propriétaire seulement
        except:
            pass  # Windows ne supporte pas cette opération
        
        print("✅ Configuration sauvegardée dans .env")
        print("🔒 Permissions sécurisées appliquées")
        print()
        print("🎉 Configuration terminée !")
        print("   Vous pouvez maintenant utiliser ComicsRename en toute sécurité.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")

def check_security():
    """Vérifie l'état de sécurité actuel"""
    
    print("🔍 Vérification de Sécurité")
    print("=" * 30)
    
    issues = []
    
    # Vérifier .env
    if Path(".env").exists():
        print("✅ Fichier .env trouvé")
    else:
        print("⚠️  Fichier .env manquant")
        issues.append("Créer le fichier .env avec vos identifiants")
    
    # Vérifier .gitignore
    gitignore = Path(".gitignore")
    if gitignore.exists():
        content = gitignore.read_text()
        if ".env" in content:
            print("✅ .env protégé dans .gitignore")
        else:
            print("❌ .env non protégé dans .gitignore")
            issues.append("Ajouter .env au .gitignore")
    else:
        print("❌ .gitignore manquant")
        issues.append("Créer un fichier .gitignore")
    
    # Vérifier les variables d'environnement
    env_vars = ['BDGEST_USERNAME', 'BDGEST_PASSWORD', 'COMICVINE_API_KEY']
    for var in env_vars:
        if os.getenv(var):
            print(f"✅ {var} configuré")
        else:
            print(f"⚠️  {var} manquant")
    
    if issues:
        print()
        print("🔧 Actions Recommandées:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print()
        print("🎉 Configuration de sécurité optimale !")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        check_security()
    else:
        setup_env_file()
