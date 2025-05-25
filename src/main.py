print("=== SCRIPT DEMARRE ===")
#!/usr/bin/env python3
"""
Gestionnaire de références avancé
Accès à Google Drive, fichiers locaux et GitHub via terminal
"""

import os
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv('config/.env')

# Ajouter le dossier src au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from google_drive_manager import GoogleDriveManager
    from github_manager import GitHubManager
    from local_files_manager import LocalFilesManager
    from reference_search import ReferenceSearch
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print("Assurez-vous que tous les modules sont créés.")

console = Console()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """🔬 Gestionnaire de Références PhD - Interface Terminal Avancée
    
    Gérez vos références depuis Google Drive, GitHub et fichiers locaux.
    Développé par Yassine pour son doctorat en mathématiques.
    """
    console.print("[bold blue]📚 Gestionnaire de Références PhD - Yassine[/bold blue]")

@cli.command()
@click.option('--source', '-s', 
              type=click.Choice(['drive', 'local', 'github', 'all']), 
              default='all', 
              help='Source des références à rechercher')
@click.option('--keyword', '-k', help='Mot-clé de recherche')
@click.option('--author', '-a', help='Nom de l\'auteur')
@click.option('--year', '-y', help='Année de publication')
@click.option('--limit', '-l', default=10, help='Nombre max de résultats')
def search(source, keyword, author, year, limit):
    """🔍 Rechercher dans les références"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Recherche dans {source}...", total=None)
        
        try:
            searcher = ReferenceSearch()
            results = searcher.search(
                sources=source,
                keyword=keyword,
                author=author,
                year=year,
                limit=limit
            )
            progress.stop()
            
            if not results:
                console.print("[yellow]Aucun résultat trouvé.[/yellow]")
                return
            
            # Affichage des résultats
            table = Table(title=f"Résultats de recherche ({len(results)} trouvés)")
            table.add_column("Source", style="cyan", width=12)
            table.add_column("Titre", style="magenta", max_width=40)
            table.add_column("Auteur", style="green", max_width=20)
            table.add_column("Année", style="yellow", width=8)
            table.add_column("Chemin", style="blue", max_width=30)
            
            for result in results[:limit]:
                table.add_row(
                    result.get('source', 'N/A'),
                    result.get('title', 'N/A')[:40] + '...' if len(result.get('title', '')) > 40 else result.get('title', 'N/A'),
                    result.get('author', 'N/A')[:20] + '...' if len(result.get('author', '')) > 20 else result.get('author', 'N/A'),
                    str(result.get('year', 'N/A')),
                    result.get('path', 'N/A')[-30:] if result.get('path') else 'N/A'
                )
            
            console.print(table)
            
        except Exception as e:
            progress.stop()
            console.print(f"[red]Erreur lors de la recherche: {e}[/red]")

@cli.command()
def sync():
    """🔄 Synchroniser toutes les sources"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Google Drive
        task1 = progress.add_task("Synchronisation Google Drive...", total=None)
        try:
            drive_manager = GoogleDriveManager()
            drive_count = drive_manager.sync()
            progress.update(task1, description=f"✅ Google Drive ({drive_count} fichiers)")
        except Exception as e:
            progress.update(task1, description=f"❌ Google Drive: {e}")
        
        # GitHub
        task2 = progress.add_task("Synchronisation GitHub...", total=None)
        try:
            github_manager = GitHubManager()
            github_count = github_manager.sync()
            progress.update(task2, description=f"✅ GitHub ({github_count} fichiers)")
        except Exception as e:
            progress.update(task2, description=f"❌ GitHub: {e}")
        
        # Fichiers locaux
        task3 = progress.add_task("Scan fichiers locaux...", total=None)
        try:
            local_manager = LocalFilesManager()
            local_count = local_manager.scan()
            progress.update(task3, description=f"✅ Local ({local_count} fichiers)")
        except Exception as e:
            progress.update(task3, description=f"❌ Local: {e}")
    
    console.print("[bold green]🎉 Synchronisation terminée![/bold green]")

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--title', '-t', help='Titre de la référence')
@click.option('--author', '-a', help='Auteur de la référence')
@click.option('--year', '-y', help='Année de publication')
def add(file_path, title, author, year):
    """📄 Ajouter une nouvelle référence"""
    
    console.print(f"[bold blue]Ajout de: {file_path}[/bold blue]")
    
    try:
        local_manager = LocalFilesManager()
        success = local_manager.add_reference(
            file_path=file_path,
            title=title,
            author=author,
            year=year
        )
        
        if success:
            console.print("[bold green]✅ Référence ajoutée avec succès![/bold green]")
        else:
            console.print("[red]❌ Erreur lors de l'ajout de la référence.[/red]")
            
    except Exception as e:
        console.print(f"[red]Erreur: {e}[/red]")

@cli.command()
def status():
    """📊 Statut des références"""
    console.print("[bold blue]📊 Statut du système de références[/bold blue]")
    
    try:
        # Compter les références par source
        drive_manager = GoogleDriveManager()
        github_manager = GitHubManager()
        local_manager = LocalFilesManager()
        
        table = Table(title="Statistiques des références")
        table.add_column("Source", style="cyan")
        table.add_column("Nombre", style="magenta")
        table.add_column("Dernière sync", style="green")
        table.add_column("Status", style="yellow")
        
        # Google Drive
        try:
            drive_count = drive_manager.count()
            drive_sync = drive_manager.last_sync()
            table.add_row("Google Drive", str(drive_count), drive_sync, "✅ OK")
        except Exception as e:
            table.add_row("Google Drive", "0", "Jamais", f"❌ {str(e)[:20]}")
        
        # GitHub
        try:
            github_count = github_manager.count()
            github_sync = github_manager.last_sync()
            table.add_row("GitHub", str(github_count), github_sync, "✅ OK")
        except Exception as e:
            table.add_row("GitHub", "0", "Jamais", f"❌ {str(e)[:20]}")
        
        # Local
        try:
            local_count = local_manager.count()
            local_sync = local_manager.last_scan()
            table.add_row("Local", str(local_count), local_sync, "✅ OK")
        except Exception as e:
            table.add_row("Local", "0", "Jamais", f"❌ {str(e)[:20]}")
        
        console.print(table)
        
        # Informations système
        console.print(f"\n[bold]Chemin du projet:[/bold] {Path.cwd()}")
        console.print(f"[bold]Configuration:[/bold] config/.env")
        console.print(f"[bold]Cache:[/bold] data/cache/")
        
    except Exception as e:
        console.print(f"[red]Erreur lors de l'affichage du statut: {e}[/red]")

@cli.command()
def config():
    """⚙️ Afficher la configuration"""
    console.print("[bold blue]⚙️ Configuration actuelle[/bold blue]")
    
    config_table = Table(title="Variables d'environnement")
    config_table.add_column("Variable", style="cyan")
    config_table.add_column("Valeur", style="magenta")
    
    env_vars = [
        "GOOGLE_DRIVE_FOLDER_ID",
        "GITHUB_REPO", 
        "LOCAL_REFS_PATH",
        "CACHE_DIR",
        "LOG_LEVEL"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "Non défini")
        if "TOKEN" in var:
            value = "***masqué***" if value != "Non défini" else value
        config_table.add_row(var, value)
    
    console.print(config_table)

if __name__ == '__main__':
    cli()
    print("=== FIN DU SCRIPT ===")