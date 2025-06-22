#!/usr/bin/env python3
"""
test_bdgest_series.py
====================

Script standalone pour tester la fonction get_bdgest_series du module bdgest_scraper_api.

Usage:
    python test_bdgest_series.py <search_term> [options]

Arguments:
    search_term         Terme de recherche pour les séries

Options:
    -u, --username      Nom d'utilisateur BDGest (optionnel si dans .env)
    -p, --password      Mot de passe BDGest (optionnel si dans .env)
    --debug             Active le mode debug (par défaut: True)
    --verbose           Active le mode verbose pour plus de détails
    --log-file          Fichier de log pour sauvegarder les traces
    --no-debug          Désactive le mode debug
    -h, --help          Affiche cette aide

Exemples:
    python test_bdgest_series.py "legend" -u myuser -p mypass
    python test_bdgest_series.py "asterix" --verbose
    python test_bdgest_series.py "tintin" --log-file series_test.log
"""

import sys
import argparse
import os
import json
from datetime import datetime

def load_env_credentials():
    """Charge les identifiants depuis un fichier .env s'il existe."""
    env_file = ".env"
    credentials = {}
    
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key in ['BDGEST_USERNAME', 'BDGEST_USER']:
                            credentials['username'] = value
                        elif key in ['BDGEST_PASSWORD', 'BDGEST_PASS']:
                            credentials['password'] = value
        except Exception as e:
            print(f"[WARN] Erreur lors de la lecture du fichier .env: {e}")
    
    return credentials

def print_series_results(series_list, verbose=False):
    """Affiche les résultats de recherche de séries de manière formatée."""
    if not series_list:
        print("❌ Aucune série trouvée.")
        return
    
    print(f"✅ {len(series_list)} série(s) trouvée(s):")
    print("=" * 80)
    
    for i, series in enumerate(series_list, 1):
        print(f"\n📚 Série #{i}")
        print("-" * 40)
        
        # Informations principales
        if 'serie_name' in series:
            print(f"Nom: {series['serie_name']}")
        
        if 'country' in series:
            print(f"Pays: {series['country']}")
        
        if 'cover_url' in series:
            print(f"Couverture: {series['cover_url']}")
        
        if 'serie_url' in series:
            print(f"URL: {series['serie_url']}")
        
        # Informations additionnelles en mode verbose
        if verbose:
            print("\nDétails complets:")
            for key, value in series.items():
                if key not in ['serie_name', 'country', 'cover_url', 'serie_url']:
                    if isinstance(value, list):
                        print(f"  {key}: {', '.join(str(v) for v in value)}")
                    else:
                        print(f"  {key}: {value}")

def main():
    parser = argparse.ArgumentParser(
        description="Test de la fonction get_bdgest_series",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s "legend" -u myuser -p mypass
  %(prog)s "asterix" --verbose
  %(prog)s "tintin" --log-file series_test.log --no-debug
        """
    )
    
    parser.add_argument(
        'search_term',
        help='Terme de recherche pour les séries'
    )
    
    parser.add_argument(
        '-u', '--username',
        help='Nom d\'utilisateur BDGest (optionnel si dans .env)'
    )
    
    parser.add_argument(
        '-p', '--password',
        help='Mot de passe BDGest (optionnel si dans .env)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        default=True,
        help='Active le mode debug (par défaut: activé)'
    )
    
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Désactive le mode debug'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Active le mode verbose pour plus de détails'
    )
    
    parser.add_argument(
        '--log-file',
        help='Fichier de log pour sauvegarder les traces'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Sortie au format JSON'
    )
    
    args = parser.parse_args()
    
    # Gérer les options de debug
    if args.no_debug:
        debug_mode = False
    else:
        debug_mode = args.debug
    
    # Charger les identifiants
    env_credentials = load_env_credentials()
    username = args.username or env_credentials.get('username')
    password = args.password or env_credentials.get('password')
    
    # Vérifier les identifiants
    if not username or not password:
        print("❌ Erreur: Nom d'utilisateur et mot de passe requis.")
        print("   Utilisez -u/-p ou créez un fichier .env avec:")
        print("   BDGEST_USERNAME=votre_nom_utilisateur")
        print("   BDGEST_PASSWORD=votre_mot_de_passe")
        sys.exit(1)
    
    # Afficher les paramètres
    if debug_mode:
        print("🔧 Paramètres de test:")
        print(f"   Terme de recherche: '{args.search_term}'")
        print(f"   Utilisateur: {username}")
        print(f"   Mode debug: {debug_mode}")
        print(f"   Mode verbose: {args.verbose}")
        if args.log_file:
            print(f"   Fichier de log: {args.log_file}")
        print()
    
    # Importer et tester la fonction
    try:
        from bdgest_scraper_api import get_bdgest_series
        
        print(f"🔍 Recherche de séries avec le terme: '{args.search_term}'")
        print(f"⏰ Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Appeler la fonction
        start_time = datetime.now()
        series_results = get_bdgest_series(
            term=args.search_term,
            username=username,
            password=password,
            debug=debug_mode,
            verbose=args.verbose,
            log_path=args.log_file
        )
        end_time = datetime.now()
        
        print(f"⏱️  Durée: {(end_time - start_time).total_seconds():.2f}s")
        print()
        
        # Afficher les résultats
        if args.json:
            print(json.dumps(series_results, indent=2, ensure_ascii=False))
        else:
            print_series_results(series_results, args.verbose)
        
        print(f"\n✅ Test terminé avec succès!")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("   Assurez-vous que bdgest_scraper_api.py est dans le même répertoire.")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        if debug_mode:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
