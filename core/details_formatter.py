"""
Details formatting utilities for ComicsRename.

This module provides functionality to format comic metadata into HTML
for display in the details panel.
"""

import re
from typing import Dict, Any, List, Optional


class DetailsFormatter:
    """Handles formatting of comic metadata for display in HTML format."""
    
    def __init__(self, source: str = 'BDGest', debug: bool = False):
        """
        Initialize the DetailsFormatter.
        
        Args:
            source (str): The metadata source ('BDGest' or 'ComicVine')
            debug (bool): Enable debug output
        """
        self.source = source
        self.debug = debug
    
    def make_links_clickable(self, text: str, field_name: Optional[str] = None) -> str:
        """
        Convert URLs in text to clickable HTML links with clean display text.
        
        Args:
            text (str): Text that may contain URLs
            field_name (str, optional): Field name for specialized link formatting
            
        Returns:
            str: Text with URLs converted to HTML links
        """
        # If the text already contains HTML links, return as-is
        if '<a href=' in str(text):
            return str(text)
        
        # URL pattern to match http/https URLs
        url_pattern = r'(https?://[^\s<>"]{2,})'
        
        # If this is a URL field and the entire text is just a URL, make a clean link
        if field_name in ['album_url', 'cover_url', 'api_detail_url', 'image_url'] and re.match(r'^https?://', str(text).strip()):
            url = str(text).strip()
            if field_name == 'album_url':
                if 'comicvine.gamespot.com' in url:
                    return f'<a href="{url}">ComicVine Page</a>'
                elif 'bedetheque.com' in url:
                    return f'<a href="{url}">BDGest Page</a>'
                else:
                    return f'<a href="{url}">Source Page</a>'
            elif field_name == 'api_detail_url':
                return f'<a href="{url}">API Detail</a>'
            elif field_name == 'cover_url':
                return f'<a href="{url}">View Cover</a>'
            elif field_name == 'image_url':
                return f'<a href="{url}">View Image</a>'
            else:
                return f'<a href="{url}">{url}</a>'
        
        # Replace URLs with HTML links
        return re.sub(url_pattern, r'<a href="\1">\1</a>', str(text))
    
    def format_display_value(self, value: Any, field_name: Optional[str] = None) -> Any:
        """
        Format any value for HTML display.
        
        Args:
            value: The value to format
            field_name (str, optional): Field name for specialized formatting
            
        Returns:
            Formatted value (dict for lists, str for simple values)
        """
        if isinstance(value, dict):
            if value.get('type') == 'list':
                # Already structured list data
                return value
            elif field_name == 'volume':
                # Special handling for volume field - show just the name
                if value.get('name'):
                    return f"Name: {value.get('name')}"
                else:
                    # Convert dict to structured list for other volume info
                    items = [f"{k}: {v}" for k, v in value.items()]
                    return {'type': 'list', 'items': items}
            else:
                # Convert dict to structured list
                items = [f"{k}: {v}" for k, v in value.items()]
                return {'type': 'list', 'items': items} if items else self.make_links_clickable(str(value), field_name)
        elif isinstance(value, list):
            # Convert list to structured format
            items = [self.format_display_value(item, field_name) for item in value[:10]]
            return {'type': 'list', 'items': items}
        elif value is None:
            return ''
        else:
            # For URL fields, don't process with make_links_clickable here
            # Let the main display logic handle it
            return self.make_links_clickable(str(value), field_name)
    
    def get_display_name(self, field_name: str) -> str:
        """
        Get a user-friendly display name for fields.
        
        Args:
            field_name (str): Internal field name
            
        Returns:
            str: User-friendly display name
        """
        # Example mapping, can be extended
        mapping_bdgest = {
            'album_url': 'Fiche Album',
            'cover_url': 'Couverture',
            'serie': 'Série',
            'auteurs': 'Auteurs',
            'editeur': 'Éditeur',
            'collection': 'Collection',
            'genre': 'Genre',
            'isbn': 'ISBN',
            'pages': 'Pages',
            'parution': 'Parution',
            'resume': 'Résumé',
        }
        mapping_comicvine = {
            'api_detail_url': 'ComicVine API',
            'image_url': 'Image',
            'volume': 'Volume',
            'publisher': 'Publisher',
            'description': 'Description',
            'count_of_issues': 'Issues',
        }
        if self.source == 'ComicVine':
            return mapping_comicvine.get(field_name, field_name.replace('_', ' ').capitalize())
        else:
            return mapping_bdgest.get(field_name, field_name.replace('_', ' ').capitalize())
    
    def get_field_order(self) -> List[str]:
        """
        Get the preferred field display order based on source.
        
        Returns:
            List[str]: Ordered list of field names
        """
        if self.source == 'BDGest':
            # BDGest-specific order: show most important info first
            return [
                'serie_name',
                'style', 
                'album_name',
                'album_number',
                'ISBN',
                'date',
                'details'  # This will be handled specially
            ]
        else:
            # ComicVine order - optimized for better user experience
            return [
                'name',           # Issue title (most important)
                'issue_number',   # Issue number
                'volume',         # Series/Volume info
                'cover_date',     # Cover date (when published)
                'store_date',     # Store date (when released)
                'description',    # Issue description
                'story_arc',      # Story arc information
                'character_credits', # Characters
                'person_credits', # Creators
                'location_credits', # Locations
                'concept_credits', # Concepts/themes
                'team_credits',   # Teams
                'id',             # ComicVine ID
                'album_url',      # ComicVine page URL
                'api_detail_url', # API detail URL
                'cover_url',      # Cover image URL
                'image'           # Image information
            ]
    
    def get_css_styles(self) -> str:
        """
        Get CSS styles for the HTML details display.
        
        Returns:
            str: CSS styles as a string
        """
        return """
        <style>
        body, div, ul, li, p { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; 
            background: transparent !important; 
            margin: 0; 
            padding: 0; 
        }
        .details-container { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; 
            background: transparent !important;
            color: #333;
            line-height: 1.4;
        }
        .details-container ul { 
            margin: 5px 0; 
            padding-left: 20px; 
            background: transparent !important;
        }
        .details-container li { 
            margin: 2px 0; 
            background: transparent !important;
            list-style-type: disc;
            line-height: 1.3;
        }
        .sub-section { 
            background-color: #f8f9fa !important; 
            padding: 6px 8px; 
            margin: 4px 0; 
            border-radius: 4px; 
            border: 1px solid #e9ecef;
        }
        .sub-section > b { 
            color: #495057; 
            background: transparent !important;
        }
        .sub-list { 
            margin: 5px 0 5px 15px; 
            background: transparent !important;
        }
        .sub-list li { 
            margin: 1px 0; 
            color: #6c757d; 
            font-size: 0.95em; 
            background: transparent !important;
            list-style-type: circle;
        }
        .complex-data { 
            background-color: #e9ecef !important; 
            padding: 4px 6px; 
            border-radius: 3px; 
            margin: 2px 0;
        }
        a { 
            color: #007bff !important; 
            text-decoration: underline;
            background: transparent !important;
        }
        a:hover { 
            color: #0056b3 !important; 
            background: transparent !important;
            text-decoration: underline;
        }
        b, strong { 
            background: transparent !important; 
            font-weight: 600;
        }
        /* Ensure no unwanted backgrounds appear */
        * { 
            background-attachment: scroll !important;
        }
        </style>
        """
    
    def format_metadata_to_html(self, meta: Dict[str, Any]) -> str:
        """
        Format comic metadata to HTML for display.
        
        Args:
            meta (Dict[str, Any]): Comic metadata dictionary
            
        Returns:
            str: Formatted HTML string
        """
        if not meta:
            return "<p>No details available.</p>"
        
        # Start HTML with styles
        html = self.get_css_styles()
        html += '<div class="details-container">'
        
        # For BDGest, we'll handle the structure differently
        if self.source == 'BDGest':
            html += "<ul>"
        else:
            html += "<b>Détails complets :</b><br><ul>"
        
        # Display fields in the preferred order
        field_order = self.get_field_order()
        displayed_fields = set()
        
        for field in field_order:
            if field in meta:
                if field == "details":
                    # Handle details specially - will be processed later
                    continue
                    
                v = meta[field]
                formatted_value = self.format_display_value(v, field)
                display_name = self.get_display_name(field)
                
                if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                    html += f'<li class="sub-section"><b>{display_name} :</b><ul class="sub-list">'
                    for item in formatted_value.get('items', []):
                        html += f"<li>{item}</li>"
                    html += "</ul></li>"
                else:
                    html += f"<li><b>{display_name}</b> : {self.make_links_clickable(str(formatted_value), field)}</li>"
                displayed_fields.add(field)
        
        # Add the details section
        html += self._format_details_section(meta, displayed_fields)
        
        html += "</ul></div>"
        return html
    
    def _format_details_section(self, meta: Dict[str, Any], displayed_fields: set) -> str:
        """
        Format the special details section of metadata.
        
        Args:
            meta (Dict[str, Any]): Comic metadata
            displayed_fields (set): Already displayed field names
            
        Returns:
            str: HTML for details section
        """
        html = ""
        
        if self.source == 'BDGest':
            html += self._format_bdgest_details(meta, displayed_fields)
        else:
            html += self._format_comicvine_details(meta, displayed_fields)
        
        return html
    
    def _format_bdgest_details(self, meta: Dict[str, Any], displayed_fields: set) -> str:
        """Format BDGest-specific details section."""
        html = "<li><b>Détails complets :</b><ul>"
        
        # First add album_url and cover_url if they exist
        for url_field in ['album_url', 'cover_url']:
            if url_field in meta and meta[url_field]:
                formatted_value = self.format_display_value(meta[url_field], url_field)
                html += f"<li><b>{url_field}</b> : {self.make_links_clickable(formatted_value, url_field)}</li>"
                displayed_fields.add(url_field)
        
        # Then add the details dict content
        details = meta.get("details")
        if isinstance(details, dict):
            html += "<li><b>Détails :</b><ul>"
            for label, value in details.items():
                formatted_value = self.format_display_value(value, label)
                if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                    # Handle structured list data as styled sub-sections
                    html += f'<li class="sub-section"><b>{label} :</b><ul class="sub-list">'
                    for item in formatted_value.get('items', []):
                        html += f"<li>{item}</li>"
                    html += "</ul></li>"
                else:
                    # Handle regular string/simple data
                    html += f"<li><b>{label}</b> : {self.make_links_clickable(str(formatted_value), label)}</li>"
            html += "</ul></li>"
        
        # Then add any remaining fields
        for k, v in meta.items():
            if k not in displayed_fields and k != "details":
                formatted_value = self.format_display_value(v, k)
                if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                    html += f'<li class="sub-section"><b>{k} :</b><ul class="sub-list">'
                    for item in formatted_value.get('items', []):
                        html += f"<li>{item}</li>"
                    html += "</ul></li>"
                else:
                    html += f"<li><b>{k}</b> : {self.make_links_clickable(str(formatted_value), k)}</li>"
        
        html += "</ul></li>"
        return html
    
    def _format_comicvine_details(self, meta: Dict[str, Any], displayed_fields: set) -> str:
        """Format ComicVine-specific details section."""
        html = "<li><b>Détails ComicVine :</b><ul>"
        
        # Add important links first
        for url_field in ['album_url', 'api_detail_url', 'cover_url']:
            if url_field in meta and meta[url_field]:
                formatted_value = self.format_display_value(meta[url_field], url_field)
                html += f"<li><b>{url_field.replace('_', ' ').title()}</b> : {self.make_links_clickable(formatted_value, url_field)}</li>"
                displayed_fields.add(url_field)
        
        # Add credits section if any credits are available
        credit_fields = ['character_credits', 'person_credits', 'location_credits', 'concept_credits', 'team_credits']
        available_credits = [field for field in credit_fields if field in meta and meta[field]]
        
        if available_credits:
            html += "<li><b>Crédits :</b><ul>"
            for credit_field in available_credits:
                if credit_field in meta and meta[credit_field]:
                    formatted_value = self.format_display_value(meta[credit_field], credit_field)
                    display_name = credit_field.replace('_credits', '').replace('_', ' ').title() + 's'
                    if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                        html += f'<li class="sub-section"><b>{display_name} :</b><ul class="sub-list">'
                        for item in formatted_value.get('items', []):
                            html += f"<li>{item}</li>"
                        html += "</ul></li>"
                    else:
                        html += f"<li><b>{display_name}</b> : {self.make_links_clickable(str(formatted_value), credit_field)}</li>"
                    displayed_fields.add(credit_field)
            html += "</ul></li>"
        
        # Process any details dict if present
        details = meta.get("details")
        if isinstance(details, dict):
            html += "<li><b>Détails supplémentaires :</b><ul>"
            for label, value in details.items():
                formatted_value = self.format_display_value(value, label)
                if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                    # Handle structured list data as styled sub-sections
                    html += f'<li class="sub-section"><b>{label} :</b><ul class="sub-list">'
                    for item in formatted_value.get('items', []):
                        html += f"<li>{item}</li>"
                    html += "</ul></li>"
                else:
                    # Handle regular string/simple data
                    html += f"<li><b>{label}</b> : {self.make_links_clickable(str(formatted_value), label)}</li>"
            html += "</ul></li>"
        
        # Display any remaining fields that weren't in our preferred order
        for k, v in meta.items():
            if k not in displayed_fields and k != "details":
                formatted_value = self.format_display_value(v, k)
                if isinstance(formatted_value, dict) and formatted_value.get('type') == 'list':
                    html += f'<li class="sub-section"><b>{k.replace("_", " ").title()} :</b><ul class="sub-list">'
                    for item in formatted_value.get('items', []):
                        html += f"<li>{item}</li>"
                    html += "</ul></li>"
                else:
                    html += f"<li><b>{k.replace('_', ' ').title()}</b> : {self.make_links_clickable(str(formatted_value), k)}</li>"
        
        html += "</ul></li>"
        return html
