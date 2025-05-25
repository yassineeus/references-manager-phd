"""
Module de recherche unifiée dans toutes les sources de références
"""

import os
import re
from datetime import datetime
from pathlib import Path

# Import conditionnel des managers
try:
    from google_drive_manager import GoogleDriveManager
    from github_manager import GitHubManager  
    from local_files_manager import LocalFilesManager
except ImportError as e:
    print(f"Erreur d'import dans reference_search: {e}")

class ReferenceSearch:
    def __init__(self):
        self.drive_manager = None
        self.github_manager = None
        self.local_manager = None
        
        # Initialiser les managers disponibles
        try:
            self.drive_manager = GoogleDriveManager()
        except Exception as e:
            print(f"Google Drive non disponible: {e}")
        
        try:
            self.github_manager = GitHubManager()
        except Exception as e:
            print(f"GitHub non disponible: {e}")
        
        try:
            self.local_manager = LocalFilesManager()
        except Exception as e:
            print(f"Gestionnaire local non disponible: {e}")
    
    def search(self, sources='all', keyword=None, author=None, year=None, limit=50):
        """Recherche unifiée dans toutes les sources"""
        results = []
        
        # Déterminer les sources à rechercher
        search_sources = self._determine_sources(sources)
        
        for source in search_sources:
            try:
                source_results = self._search_in_source(source, keyword, author, year)
                results.extend(source_results)
            except Exception as e:
                print(f"Erreur lors de la recherche dans {source}: {e}")
        
        # Filtrer et trier les résultats
        filtered_results = self._filter_results(results, keyword, author, year)
        sorted_results = self._sort_results(filtered_results)
        
        return sorted_results[:limit]
    
    def _determine_sources(self, sources):
        """Déterminer quelles sources rechercher"""
        available_sources = []
        
        if sources == 'all':
            if self.drive_manager:
                available_sources.append('drive')
            if self.github_manager:
                available_sources.append('github')
            if self.local_manager:
                available_sources.append('local')
        else:
            if sources == 'drive' and self.drive_manager:
                available_sources.append('drive')
            elif sources == 'github' and self.github_manager:
                available_sources.append('github')
            elif sources == 'local' and self.local_manager:
                available_sources.append('local')
        
        return available_sources
    
    def _search_in_source(self, source, keyword, author, year):
        """Rechercher dans une source spécifique"""
        results = []
        
        if source == 'drive' and self.drive_manager:
            # Récupérer les fichiers du cache Drive
            files = self.drive_manager.get_cached_files()
            if not files:
                # Si pas de cache, synchroniser d'abord
                self.drive_manager.sync()
                files = self.drive_manager.get_cached_files()
            
            for file_info in files:
                result = self._convert_drive_file(file_info)
                if result:
                    results.append(result)
        
        elif source == 'github' and self.github_manager:
            # Récupérer les fichiers du cache GitHub
            files = self.github_manager.get_cached_files()
            if not files:
                # Si pas de cache, synchroniser d'abord
                self.github_manager.sync()
                files = self.github_manager.get_cached_files()
            
            for file_info in files:
                result = self._convert_github_file(file_info)
                if result:
                    results.append(result)
        
        elif source == 'local' and self.local_manager:
            # Récupérer les fichiers du cache local
            files = self.local_manager.get_cached_files()
            if not files:
                # Si pas de cache, scanner d'abord
                self.local_manager.scan()
                files = self.local_manager.get_cached_files()
            
            for file_info in files:
                result = self._convert_local_file(file_info)
                if result:
                    results.append(result)
        
        return results
    
    def _convert_drive_file(self, file_info):
        """Convertir un fichier Drive en format unifié"""
        try:
            # Extraire l'auteur et l'année du nom de fichier si possible
            name = file_info.get('name', '')
            author, year = self._extract_metadata_from_filename(name)
            
            return {
                'id': file_info.get('id', ''),
                'title': self._clean_title(name),
                'author': author,
                'year': year,
                'source': 'Google Drive',
                'path': file_info.get('link', ''),
                'size': file_info.get('size', 0),
                'modified': file_info.get('modified', ''),
                'type': 'pdf',
                'score': 0  # Score de pertinence, sera calculé plus tard
            }
        except Exception as e:
            print(f"Erreur conversion fichier Drive: {e}")
            return None
    
    def _convert_github_file(self, file_info):
        """Convertir un fichier GitHub en format unifié"""
        try:
            name = file_info.get('name', '')
            author, year = self._extract_metadata_from_filename(name)
            
            return {
                'id': file_info.get('sha', ''),
                'title': self._clean_title(name),
                'author': author,
                'year': year,
                'source': 'GitHub',
                'path': file_info.get('html_url', ''),
                'size': file_info.get('size', 0),
                'modified': '',  # GitHub ne fournit pas facilement cette info
                'type': Path(name).suffix.lower()[1:] if Path(name).suffix else 'unknown',
                'score': 0
            }
        except Exception as e:
            print(f"Erreur conversion fichier GitHub: {e}")
            return None
    
    def _convert_local_file(self, file_info):
        """Convertir un fichier local en format unifié"""
        try:
            name = file_info.get('name', '')
            author, year = self._extract_metadata_from_filename(name)
            
            return {
                'id': file_info.get('id', ''),
                'title': self._clean_title(name),
                'author': author,
                'year': year,
                'source': 'Local',
                'path': file_info.get('path', ''),
                'size': file_info.get('size', 0),
                'modified': file_info.get('modified', ''),
                'type': file_info.get('extension', '')[1:] if file_info.get('extension') else 'unknown',
                'score': 0
            }
        except Exception as e:
            print(f"Erreur conversion fichier local: {e}")
            return None
    
    def _extract_metadata_from_filename(self, filename):
        """Extraire auteur et année du nom de fichier"""
        author = 'Inconnu'
        year = None
        
        try:
            # Nettoyer le nom de fichier
            name = Path(filename).stem
            
            # Patterns pour extraire l'année (4 chiffres)
            year_pattern = r'\b(19|20)\d{2}\b'
            year_match = re.search(year_pattern, name)
            if year_match:
                year = int(year_match.group())
            
            # Patterns pour extraire l'auteur (supposé être au début)
            # Chercher des patterns comme "Smith_2020", "John-Smith_2020", etc.
            author_pattern = r'^([A-Za-z][A-Za-z\-_\s]+?)(?:_|\s|-)(?:19|20)\d{2}'
            author_match = re.search(author_pattern, name)
            if author_match:
                author = author_match.group(1).replace('_', ' ').replace('-', ' ').strip()
            else:
                # Fallback: prendre les premiers mots avant un nombre ou underscore
                words = re.split(r'[_\-\s]+', name)
                if words:
                    author = words[0]
            
            # Patterns spéciaux pour "Mayrand" (superviseur)
            if 'mayrand' in name.lower():
                author = 'Mayrand, Maxence'
        
        except Exception as e:
            print(f"Erreur extraction métadonnées: {e}")
        
        return author, year
    
    def _clean_title(self, filename):
        """Nettoyer le titre (enlever extension, caractères spéciaux)"""
        try:
            title = Path(filename).stem
            # Remplacer underscores et tirets par espaces
            title = re.sub(r'[_\-]+', ' ', title)
            # Enlever les patterns d'année
            title = re.sub(r'\b(19|20)\d{2}\b', '', title)
            # Nettoyer les espaces multiples
            title = re.sub(r'\s+', ' ', title).strip()
            return title if title else filename
        except:
            return filename
    
    def _filter_results(self, results, keyword, author, year):
        """Filtrer les résultats selon les critères"""
        filtered = []
        
        for result in results:
            # Calculer le score de pertinence
            score = 0
            
            # Filtre par mot-clé
            if keyword:
                keyword_lower = keyword.lower()
                if keyword_lower in result['title'].lower():
                    score += 10
                if keyword_lower in result['author'].lower():
                    score += 5
                # Si aucune correspondance, on garde quand même mais avec score faible
                if score == 0:
                    if any(keyword_lower in str(v).lower() for v in result.values() if v):
                        score += 1
            else:
                score += 1  # Pas de filtre mot-clé
            
            # Filtre par auteur
            if author:
                if author.lower() in result['author'].lower():
                    score += 15
                elif score == 0:
                    continue  # Exclure si l'auteur ne correspond pas
            else:
                score += 1  # Pas de filtre auteur
            
            # Filtre par année
            if year:
                try:
                    if result['year'] == int(year):
                        score += 10
                    elif score == 0:
                        continue  # Exclure si l'année ne correspond pas
                except:
                    pass
            else:
                score += 1  # Pas de filtre année
            
            # Bonus pour certaines sources ou types
            if 'mayrand' in result['author'].lower():
                score += 5  # Bonus pour le superviseur
            
            result['score'] = score
            
            if score > 0:
                filtered.append(result)
        
        return filtered
    
    def _sort_results(self, results):
        """Trier les résultats par pertinence"""
        return sorted(results, key=lambda x: (
            x['score'],                    # Score principal
            x['year'] or 0,               # Année (plus récent = mieux)  
            x['author'].lower(),          # Auteur alphabétique
            x['title'].lower()            # Titre alphabétique
        ), reverse=True)
    
    def get_all_authors(self):
        """Obtenir la liste de tous les auteurs"""
        authors = set()
        
        # Rechercher dans toutes les sources
        results = self.search(sources='all', limit=1000)
        
        for result in results:
            if result['author'] and result['author'] != 'Inconnu':
                authors.add(result['author'])
        
        return sorted(list(authors))
    
    def get_all_years(self):
        """Obtenir la liste de toutes les années"""
        years = set()
        
        # Rechercher dans toutes les sources
        results = self.search(sources='all', limit=1000)
        
        for result in results:
            if result['year']:
                years.add(result['year'])
        
        return sorted(list(years), reverse=True)
    
    def get_stats(self):
        """Obtenir les statistiques globales"""
        results = self.search(sources='all', limit=1000)
        
        stats = {
            'total_references': len(results),
            'by_source': {},
            'by_year': {},
            'by_author': {},
            'by_type': {}
        }
        
        for result in results:
            # Par source
            source = result['source']
            stats['by_source'][source] = stats['by_source'].get(source, 0) + 1
            
            # Par année
            year = result['year'] or 'Inconnue'
            stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
            
            # Par auteur
            author = result['author'] or 'Inconnu'
            stats['by_author'][author] = stats['by_author'].get(author, 0) + 1
            
            # Par type
            file_type = result['type'] or 'unknown'
            stats['by_type'][file_type] = stats['by_type'].get(file_type, 0) + 1
        
        return stats