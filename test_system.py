#!/usr/bin/env python3
"""
Test global du gestionnaire de références
"""

print("🔬 Test du Gestionnaire de Références PhD")
print("=" * 50)

# Test 1: Vérifier l'environnement
print("✅ Python fonctionne")

# Test 2: Tester les imports
try:
    import os
    import sys
    print("✅ Modules de base OK")
except ImportError as e:
    print(f"❌ Erreur modules de base: {e}")

# Test 3: Tester les bibliothèques installées
libraries = [
    ("click", "Interface en ligne de commande"),
    ("rich", "Affichage coloré"),
    ("requests", "Requêtes HTTP"),
    ("pandas", "Manipulation de données"),
    ("pathlib", "Gestion des chemins"),
]

for lib, desc in libraries:
    try:
        __import__(lib)
        print(f"✅ {lib} - {desc}")
    except ImportError:
        print(f"❌ {lib} - {desc} - NON INSTALLÉ")

# Test 4: Vérifier la structure du projet
print("\n📁 Structure du projet:")
required_files = [
    "src/main.py",
    "src/google_drive_manager.py", 
    "src/github_manager.py",
    "src/local_files_manager.py",
    "src/reference_search.py",
    "config/.env",
    "config/credentials.json",
    "requirements.txt"
]

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"✅ {file_path}")
    else:
        print(f"❌ {file_path} - MANQUANT")

# Test 5: Vérifier le fichier .env
print("\n⚙️ Configuration:")
from dotenv import load_dotenv
load_dotenv('config/.env')

env_vars = [
    "GITHUB_TOKEN",
    "GITHUB_REPO", 
    "LOCAL_REFS_PATH",
    "GOOGLE_CREDENTIALS_FILE"
]

for var in env_vars:
    value = os.getenv(var)
    if value and value != "your_token_here":
        print(f"✅ {var} configuré")
    else:
        print(f"❌ {var} - NON CONFIGURÉ")

print("\n🎯 Test terminé!")
