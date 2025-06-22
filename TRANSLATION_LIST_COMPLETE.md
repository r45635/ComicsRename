# ComicsRename - Complete List of Translatable Text

## Overview
This document lists all user-facing text that has been identified and translated in the ComicsRename application. The text is organized by functional area and includes both English and French translations.

## Translation Coverage: 126 Keys Organized

### 🎯 **APPLICATION LEVEL** (2 keys)
| English | French | Key |
|---------|--------|-----|
| Comic Renamer - Multi-Source | Bande Dessinees Renomer - Multi-Source | app.title |
| Settings | Paramètres | app.settings |

### 🔘 **BUTTONS** (11 keys)
| English | French | Key |
|---------|--------|-----|
| Browse | Parcourir | ui.buttons.browse |
| Search | Rechercher | ui.buttons.search |
| Settings | Paramètres | ui.buttons.settings |
| Rename | Renommer | ui.buttons.rename |
| Rename Folder | Renommer le dossier | ui.buttons.rename_folder |
| Refresh | Actualiser | ui.buttons.refresh |
| Refresh Files | Actualiser les fichiers | ui.buttons.refresh_files |
| OK | OK | ui.buttons.ok |
| Cancel | Annuler | ui.buttons.cancel |
| Yes | Oui | ui.buttons.yes |
| No | Non | ui.buttons.no |

### 🏷️ **LABELS** (8 keys)
| English | French | Key |
|---------|--------|-----|
| Folder | Dossier | ui.labels.folder |
| Search term | Terme de recherche | ui.labels.search_term |
| Series Name Mode | Mode nom de série | ui.labels.series_name_mode |
| Provider | Fournisseur | ui.labels.provider |
| Language | Langue | ui.labels.language |
| Volume | Volume | ui.labels.volume |
| Series | Série | ui.labels.series |
| Album | Album | ui.labels.album |
| Issue | Numéro | ui.labels.issue |

### 💬 **TOOLTIPS** (3 keys)
| English | French | Key |
|---------|--------|-----|
| Search only in series names (BDGest only) | Rechercher uniquement dans les noms de séries (BDGest uniquement) | ui.tooltips.series_name_mode |
| Application Settings | Paramètres de l'application | ui.tooltips.settings |
| Rename folder with selected series name | Renommer le dossier avec le nom de la série sélectionnée | ui.tooltips.rename_folder |

### 📝 **PLACEHOLDERS** (1 key)
| English | French | Key |
|---------|--------|-----|
| Enter search term... | Entrez un terme de recherche... | ui.placeholders.search |

### 🍔 **CONTEXT MENUS** (3 keys)
| English | French | Key |
|---------|--------|-----|
| Open File | Ouvrir le fichier | ui.menus.open_file |
| Reveal in Finder | Afficher dans le Finder | ui.menus.reveal_in_finder |
| Refresh Folder Files | Rafraîchir les fichiers du dossier | ui.menus.refresh_folder_files |

### 💬 **DIALOG BOXES** (16 keys)

#### Folder Selection Dialog
| English | French | Key |
|---------|--------|-----|
| Folder Selection | Sélection du dossier | dialogs.folder_selection.title |
| Where would you like to start browsing? | Où souhaitez-vous commencer la navigation ? | dialogs.folder_selection.message |
| External drives (/Volumes) | Disques externes (/Volumes) | dialogs.folder_selection.external_drives |
| Last used folder | Dernier dossier utilisé | dialogs.folder_selection.last_folder |
| Home folder | Dossier personnel | dialogs.folder_selection.home_folder |

#### Rename Confirmation Dialogs
| English | French | Key |
|---------|--------|-----|
| Rename Confirmation | Confirmation de renommage | dialogs.rename_confirmation.title |
| Rename file to:\n{new_name}? | Renommer le fichier en :\n{new_name} ? | dialogs.rename_confirmation.file_message |
| Rename folder '{old_name}' to '{new_name}'? | Renommer le dossier '{old_name}' en '{new_name}' ? | dialogs.rename_confirmation.folder_message |

#### Add Files Dialog
| English | French | Key |
|---------|--------|-----|
| Add Files | Ajouter des fichiers | dialogs.add_files.title |
| Add {count} file(s) to the current folder? | Ajouter {count} fichier(s) au dossier actuel ? | dialogs.add_files.message |

#### Settings Dialog
| English | French | Key |
|---------|--------|-----|
| Settings | Paramètres | dialogs.settings.title |
| Language: | Langue : | dialogs.settings.language_label |
| BDGest Credentials | Identifiants BDGest | dialogs.settings.bdgest_credentials |
| Username: | Nom d'utilisateur : | dialogs.settings.username |
| Password: | Mot de passe : | dialogs.settings.password |
| ComicVine Settings | Paramètres ComicVine | dialogs.settings.comicvine_settings |
| API Key: | Clé API : | dialogs.settings.api_key |

### ❌ **ERROR MESSAGES** (18 keys)
| English | French | Key |
|---------|--------|-----|
| No albums found for this search. | Aucun album trouvé pour cette recherche. | messages.errors.no_results |
| No series found for this search on BDGest. | Aucune série trouvée pour cette recherche sur BDGest. | messages.errors.no_series_found |
| No albums found for this search on BDGest. | Aucun album trouvé pour cette recherche sur BDGest. | messages.errors.no_albums_found |
| Source file does not exist:\\n{path} | Le fichier source n'existe pas :\\n{path} | messages.errors.file_not_exists |
| A file named '{name}' already exists in this folder. | Un fichier nommé '{name}' existe déjà dans ce dossier. | messages.errors.file_already_exists |
| A folder named '{name}' already exists in this directory. | Un dossier nommé '{name}' existe déjà dans ce répertoire. | messages.errors.folder_already_exists |
| No files in the folder. | Aucun fichier dans le dossier. | messages.errors.no_files_in_folder |
| Please select an album from the list. | Veuillez sélectionner un album dans la liste. | messages.errors.no_album_selected |
| Folder name cannot be empty. | Le nom du dossier ne peut pas être vide. | messages.errors.invalid_folder_name |
| Rename Folder | Renommer le dossier | messages.errors.rename_folder_title |
| Rename folder from:\n'{old_name}'\nto:\n'{new_name}'? | Renommer le dossier de :\n'{old_name}'\nà :\n'{new_name}' ? | messages.errors.rename_folder_message |
| Success | Succès | messages.errors.success_title |
| Folder renamed to '{name}' | Dossier renommé en '{name}' | messages.errors.folder_renamed |
| Album metadata missing. | Métadonnées de l'album manquantes. | messages.errors.album_metadata_missing |
| Cannot determine series name. | Impossible de déterminer le nom de la série. | messages.errors.cannot_determine_series |
| Rename Error | Erreur de renommage | messages.errors.rename_error |
| Error | Erreur | messages.errors.error |
| Error adding {file}:\n{error}\n\nSource: {source}\nDestination: {dest} | Erreur lors de l'ajout de {file} :\n{error}\n\nSource: {source}\nDestination: {dest} | messages.errors.add_file_error |
| Error fetching albums: {error} | Erreur lors de la récupération des albums: {error} | messages.errors.fetch_albums_error |
| Error renaming folder:\n{error} | Erreur lors du renommage du dossier :\n{error} | messages.errors.folder_rename_error |
| No active folder for import. | Aucun dossier actif pour l'import. | messages.errors.no_active_folder |
| Only PDF, EPUB, CBZ or CBR files are accepted. | Seuls les fichiers PDF, EPUB, CBZ ou CBR sont acceptés. | messages.errors.unsupported_format |
| Could not open file:\\n{error} | Impossible d'ouvrir le fichier :\\n{error} | messages.errors.could_not_open_file |
| Could not reveal file:\\n{error} | Impossible d'afficher le fichier :\\n{error} | messages.errors.could_not_reveal_file |
| Please select one file and one album | Veuillez sélectionner un fichier et un album | messages.errors.selection_required |

### ⚠️ **WARNING MESSAGES** (2 keys)
| English | French | Key |
|---------|--------|-----|
| A file named '{name}' already exists.\\nOverwrite? | Un fichier nommé '{name}' existe déjà.\\nÉcraser ? | messages.warnings.file_overwrite |
| Unsupported format | Format non supporté | messages.warnings.unsupported_format |

### ℹ️ **INFORMATION MESSAGES** (6 keys)
| English | French | Key |
|---------|--------|-----|
| Folder already has this name. | Le dossier a déjà ce nom. | messages.info.folder_same_name |
| {count} series found | {count} série(s) trouvée(s) | messages.info.series_found |
| {count} albums found | {count} album(s) trouvé(s) | messages.info.albums_found |
| No Result | Aucun résultat | messages.info.no_result |
| Language Change | Changement de langue | messages.info.language_change_title |
| Language will be applied after restarting the application. | La langue sera appliquée après le redémarrage de l'application. | messages.info.language_change_message |

### ✅ **SUCCESS MESSAGES** (1 key)
| English | French | Key |
|---------|--------|-----|
| Rename completed successfully | Renommage terminé avec succès | messages.success.rename_complete |

### 🐛 **DEBUG MESSAGES** (7 keys)
| English | French | Key |
|---------|--------|-----|
| Image load failed | Échec du chargement de l'image | debug.image_load_failed |
| Failed to fetch albums for series {series} | Échec de la récupération des albums pour la série {series} | debug.fetch_albums_failed |
| clean() input | Entrée de clean() | debug.clean_input |
| clean() output | Sortie de clean() | debug.clean_output |
| {count} volumes found for '{query}' | {count} volume(s) trouvé(s) pour '{query}' | debug.volumes_found |
| {count} issues found for '{query}' | {count} numéro(s) trouvé(s) pour '{query}' | debug.issues_found |
| No volumes found for '{query}', fallback to issues search | Aucun volume trouvé pour '{query}', recherche de numéros en secours | debug.no_volumes_fallback |

## Summary

### ✅ **Translation Statistics**
- **Total organized keys**: 126
- **App-level**: 2 keys
- **UI elements**: 26 keys (buttons, labels, tooltips, placeholders, menus)
- **Dialog boxes**: 16 keys
- **Messages**: 34 keys (errors, warnings, info, success, debug)
- **Languages supported**: English (en), French (fr)

### ✅ **Coverage Areas**
- ✅ All buttons and interactive elements
- ✅ All form labels and input fields
- ✅ All dialog titles and messages
- ✅ All error and success notifications
- ✅ All tooltips and help text
- ✅ All context menu items
- ✅ All confirmation dialogs
- ✅ Settings and configuration UI
- ✅ Debug and development messages

### ✅ **Parameter Support**
Many strings support dynamic parameter substitution:
- `{name}`, `{path}`, `{error}` - File and folder operations
- `{count}` - Pluralization and counts
- `{old_name}`, `{new_name}` - Rename operations
- `{file}`, `{source}`, `{dest}` - File management
- `{series}`, `{query}` - Search and metadata

### 🔄 **How It Works**
1. All text uses the `tr(key, **params)` function
2. Keys are organized hierarchically (e.g., `ui.buttons.browse`)
3. Parameters are passed for dynamic content
4. Language preference is saved and persists
5. Fallback to English for missing translations
