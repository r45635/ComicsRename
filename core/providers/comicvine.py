"""
ComicVine provider for fetching comic metadata.
"""
import re
from PySide6.QtCore import QSettings

from .base import MetadataProvider


class ComicVineProvider(MetadataProvider):
    """Provider for ComicVine metadata fetching."""
    
    def search_series(self, query, debug=False):
        from comicVine_scraper_api import search_comicvine_series
        # Pass API key from settings if available
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        if api_key:
            return search_comicvine_series(query, api_key=api_key, debug=debug)
        else:
            return search_comicvine_series(query, debug=debug)

    def search_albums(self, volume_id, debug=False):
        from comicVine_scraper_api import get_comicvine_volume_issues, get_comicvine_issue_details, get_comicvine_volume_details
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        
        # First, get volume details to extract concepts (genres/styles)
        volume_details = get_comicvine_volume_details(volume_id, api_key=api_key, debug=debug) if api_key else get_comicvine_volume_details(volume_id, debug=debug)
        volume_concepts = []
        volume_style = ""
        
        if volume_details and volume_details.get('concepts'):
            concepts = volume_details.get('concepts', [])
            volume_concepts = [concept.get('name') for concept in concepts if concept.get('name')]
            # Use the first concept as the main style, or join multiple concepts
            if volume_concepts:
                volume_style = volume_concepts[0] if len(volume_concepts) == 1 else ', '.join(volume_concepts[:3])
                if debug:
                    print(f"[DEBUG] Volume style from concepts: {volume_style}")
        
        # Get basic volume and issues data
        issues_list = get_comicvine_volume_issues(volume_id, api_key=api_key, debug=debug) if api_key else get_comicvine_volume_issues(volume_id, debug=debug)
        
        if not issues_list:
            return []
        
        # Process issues and fetch individual cover images (limit to first 50 for performance)
        enriched_issues = []
        max_issues = min(50, len(issues_list))  # Limit to 50 issues for performance
        
        for i, issue in enumerate(issues_list[:max_issues]):
            issue_id = issue.get('id')
            if issue_id:
                # Get detailed issue information to fetch individual cover images
                if debug:
                    print(f"[DEBUG] Fetching details for issue {i+1}/{max_issues} (ID: {issue_id})")
                
                issue_details = get_comicvine_issue_details(issue_id, api_key=api_key, debug=debug) if api_key else get_comicvine_issue_details(issue_id, debug=debug)
                
                # Use detailed issue data if available, otherwise fall back to basic issue data
                if issue_details:
                    merged_issue = {**issue, **issue_details}  # Merge basic and detailed data
                else:
                    merged_issue = issue
                
                # Determine publication date with fallback logic
                publication_date = merged_issue.get('cover_date')
                if not publication_date or publication_date == 'Date inconnue':
                    # Use volume start year as fallback
                    if volume_details and volume_details.get('start_year'):
                        publication_date = str(volume_details.get('start_year'))
                    else:
                        publication_date = 'Date inconnue'
                
                enriched_issue = {
                    'id': merged_issue.get('id'),
                    'issue_number': merged_issue.get('issue_number', 'N/A'),
                    'name': merged_issue.get('name', 'Sans titre'),
                    'cover_date': publication_date,
                    'store_date': merged_issue.get('store_date', ''),
                    'description': merged_issue.get('description', ''),
                    'image': merged_issue.get('image', {}) or (volume_details.get('image', {}) if volume_details else {}),  # Prioritize detailed issue image
                    'volume': volume_details,  # Use volume details we already fetched
                    'api_detail_url': merged_issue.get('api_detail_url', ''),
                    # Add computed fields for consistency with BDGest
                    'title': merged_issue.get('name', 'Sans titre'),
                    # Prioritize detailed issue image over volume image for cover URL
                    'cover_url': (merged_issue.get('image', {}).get('original_url', '') or 
                                 (volume_details.get('image', {}).get('original_url', '') if volume_details and volume_details.get('image') else '')),
                    'album_url': f"https://comicvine.gamespot.com/issue/4000-{issue_id}/",
                }
                
                # Create details section like BDGest with automatic structure detection
                details_dict = {}
                
                # Helper function to format any complex data structure
                def format_complex_data(key, value, label):
                    """Format complex data (arrays, objects) into structured display format"""
                    if isinstance(value, list) and value:
                        if isinstance(value[0], dict):
                            # Array of objects - extract meaningful info
                            if key == 'character_credits':
                                items = [char.get('name', 'Unknown') for char in value[:10]]
                            elif key == 'person_credits':
                                items = [f"{person.get('name', 'Unknown')} ({person.get('role', 'N/A')})" for person in value]
                            elif key == 'location_credits':
                                items = [loc.get('name', 'Unknown') for loc in value]
                            else:
                                # Generic handling for any array of objects
                                items = []
                                for item in value[:10]:  # Limit to 10 items
                                    if isinstance(item, dict):
                                        # Try to find a meaningful display value
                                        display_value = (item.get('name') or 
                                                       item.get('title') or 
                                                       item.get('id') or 
                                                       str(item)[:50] + '...' if len(str(item)) > 50 else str(item))
                                        items.append(str(display_value))
                                    else:
                                        items.append(str(item))
                            
                            if items:
                                details_dict[label] = {'type': 'list', 'items': items}
                        else:
                            # Array of simple values
                            details_dict[label] = {'type': 'list', 'items': [str(item) for item in value[:10]]}
                    
                    elif isinstance(value, dict) and value:
                        # Single object - show key-value pairs
                        items = []
                        for k, v in value.items():
                            if isinstance(v, (str, int, float)) and v:
                                # Format key names nicely
                                display_key = k.replace('_', ' ').title()
                                items.append(f"{display_key}: {v}")
                        
                        if items:
                            details_dict[label] = {'type': 'list', 'items': items[:10]}  # Limit to 10 items
                
                # Add basic fields with date fallback logic
                publication_date = None
                if enriched_issue.get('cover_date'):
                    publication_date = enriched_issue.get('cover_date')
                    details_dict['Date de publication'] = publication_date
                elif volume_details and volume_details.get('start_year'):
                    # Use volume start year as fallback when cover_date is not available
                    publication_date = str(volume_details.get('start_year'))
                    details_dict['Date de publication'] = f"{publication_date} (Année du volume)"
                else:
                    details_dict['Date de publication'] = "Date inconnue"
                
                # Store the resolved date for use in issue data
                if publication_date:
                    enriched_issue['cover_date'] = publication_date if enriched_issue.get('cover_date') else publication_date
                
                if enriched_issue.get('store_date'):
                    details_dict['Date en magasin'] = enriched_issue.get('store_date')
                if enriched_issue.get('description'):
                    # Clean HTML from description
                    clean_desc = re.sub('<[^<]+?>', '', enriched_issue.get('description', ''))
                    details_dict['Description'] = clean_desc[:500] + ('...' if len(clean_desc) > 500 else '')
                
                # Add volume style/genre information
                if volume_style:
                    details_dict['Style/Genre'] = volume_style
                
                # Add volume information if available
                if volume_details:
                    vol_info = []
                    if volume_details.get('name'):
                        vol_info.append(f"Nom: {volume_details.get('name')}")
                    if volume_details.get('start_year'):
                        vol_info.append(f"Année: {volume_details.get('start_year')}")
                    if volume_details.get('publisher', {}).get('name'):
                        vol_info.append(f"Éditeur: {volume_details.get('publisher', {}).get('name')}")
                    if vol_info:
                        details_dict['Volume'] = {'type': 'list', 'items': vol_info}
                
                enriched_issue['details'] = details_dict
                
                # Add volume style/genre information for folder renaming
                if volume_style:
                    enriched_issue['style'] = volume_style
                    # Also add to details for consistency with BDGest
                    enriched_issue['details']['Style'] = volume_style
                
                enriched_issues.append(enriched_issue)
            else:
                # Fallback for issues without ID
                fallback_issue = issue.copy()
                if volume_style:
                    fallback_issue['style'] = volume_style
                enriched_issues.append(fallback_issue)
        
        if debug:
            print(f"[DEBUG] Enriched {len(enriched_issues)} issues with detailed information")
        return enriched_issues

    def search_series_only(self, query, debug=False, verbose=False):
        """Search only for series names without fetching detailed album data"""
        from comicVine_scraper_api import search_comicvine_series
        # Pass API key from settings if available
        settings = QSettings("ComicsRename", "App")
        api_key = settings.value('comicvine_api', '')
        
        try:
            if api_key:
                results = search_comicvine_series(query, api_key=api_key, debug=debug)
            else:
                results = search_comicvine_series(query, debug=debug)
            
            # Transform results to match expected format
            series_list = []
            for volume in results:
                series_data = {
                    'serie_name': volume.get('name', 'Unknown'),
                    'volume_id': str(volume.get('id', '')),
                    'start_year': volume.get('start_year'),
                    'publisher': volume.get('publisher', {}).get('name', 'Unknown') if volume.get('publisher') else 'Unknown',
                    'image': volume.get('image'),
                    'api_detail_url': volume.get('api_detail_url'),
                    'raw_data': volume  # Store original data for later use
                }
                series_list.append(series_data)
            
            if debug:
                print(f"[DEBUG][ComicVine] search_series_only returned {len(series_list)} series")
            
            return series_list
        except Exception as e:
            if debug:
                print(f"[ERROR][ComicVine] Error in search_series_only: {e}")
            return []
