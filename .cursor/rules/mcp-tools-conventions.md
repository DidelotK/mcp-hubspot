# Conventions de Développement des Tools MCP HubSpot

## Règles obligatoires pour chaque nouveau tool

### 📋 Structure de fichiers requise

Pour chaque nouveau tool `{entity}` (ex: contacts, companies, deals) :

#### 1. **Fichier Tool** : `src/hubspot_mcp/tools/{entity}.py`
```python
"""Outil MCP pour gérer les {entity} HubSpot."""

from typing import Any, Dict, List
import mcp.types as types
from ..formatters import HubSpotFormatter
from .base import BaseTool

class {Entity}Tool(BaseTool):
    """Outil pour lister les {entity} HubSpot."""
    
    def get_tool_definition(self) -> types.Tool:
        # OBLIGATOIRE: Définition avec schema JSON complet
        
    async def execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        # OBLIGATOIRE: Implémentation avec gestion d'erreurs
```

#### 2. **Méthode Client** : `src/hubspot_mcp/client/hubspot_client.py`
```python
async def get_{entity}(self, limit: int = 100, filters: Optional[Dict] = None) -> List[Dict]:
    """Récupère la liste des {entity} avec filtrage optionnel."""
    # OBLIGATOIRE: URL API, propriétés, gestion filtres
```

#### 3. **Formatter** : `src/hubspot_mcp/formatters/hubspot_formatter.py`
```python
@staticmethod
def format_{entity}({entity}: List[Dict[str, Any]]) -> str:
    """Formate la liste des {entity} pour l'affichage."""
    # OBLIGATOIRE: Formatage avec emojis, titre, propriétés structurées
```

### 🧪 Tests obligatoires

#### 1. **Tests unitaires** : `tests/test_tools.py`
- Test d'exécution basique
- Test avec filtres
- Test de gestion d'erreur
- Test de définition du tool

#### 2. **Tests de formatage** : `tests/test_formatters.py`
- Test avec données complètes
- Test avec données partielles
- Test avec liste vide
- Test avec données invalides

### 📚 Documentation obligatoire

#### 1. **README.md - Section "Outils disponibles"**
```markdown
### list_hubspot_{entity}

Liste les {entity} HubSpot avec possibilité de filtrage.

Paramètres :
- limit (optionnel) : Nombre maximum de {entity} à retourner (défaut: 100, max: 1000)
- filters (optionnel) : Objet contenant les filtres de recherche
  - search : Terme de recherche pour filtrer les {entity}

Propriétés retournées pour chaque {entity} :
- [OBLIGATOIRE: Lister toutes les propriétés avec descriptions]
```

#### 2. **README.md - Section "Exemples d'utilisation"**
```markdown
Lister tous les {entity} :
Appel de l'outil list_hubspot_{entity} sans paramètres

Lister les X premiers {entity} :
Appel de l'outil list_hubspot_{entity} avec limit: X

Rechercher des {entity} par terme :
Appel de l'outil list_hubspot_{entity} avec filters: {"search": "terme"}
```

### 🔧 Standards techniques

#### 1. **Nommage obligatoire**
- Tool name: `list_hubspot_{entity}`
- Class name: `{Entity}Tool`
- Client method: `get_{entity}`
- Formatter method: `format_{entity}`
- Test functions: `test_{entity}_*`

#### 2. **Schéma JSON requis**
```python
{
    "type": "object",
    "properties": {
        "limit": {
            "type": "integer",
            "description": "Nombre maximum de {entity} à retourner (défaut: 100)",
            "default": 100,
            "minimum": 1,
            "maximum": 1000,
        },
        "filters": {
            "type": "object",
            "description": "Filtres optionnels pour la recherche",
            "properties": {
                "search": {
                    "type": "string",
                    "description": "Terme de recherche pour filtrer les {entity}",
                }
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}
```

#### 3. **Propriétés API HubSpot standards**
Toujours inclure :
- `createdate` : Date de création
- `lastmodifieddate` : Date de dernière modification  
- `id` : Identifiant unique

#### 4. **Formatage d'affichage**
```python
result = f"🎯 **{Entity.title()} HubSpot** ({len(data)} trouvé(e)s)\n\n"

for item in data:
    props = item.get("properties", {})
    result += f"**{props.get('name', 'Nom non spécifié')}**\n"
    # [Propriétés spécifiques avec emojis]
    result += f"  🆔 ID: {item.get('id')}\n\n"
```

### 📝 Processus de développement

#### 1. **Ordre de développement**
1. Créer la méthode client (`get_{entity}`)
2. Créer le formatter (`format_{entity}`)
3. Créer la classe tool (`{Entity}Tool`)
4. Enregistrer dans `__init__.py` et `handlers.py`
5. Écrire les tests unitaires
6. Mettre à jour la documentation README

#### 2. **Tests avant commit**
```bash
# Tests obligatoires
uv run pytest tests/ --cov=src --cov-report=term-missing -v

# Couverture minimum requise: 90%
# Tous les tests doivent passer
```

#### 3. **Commits semantic**
```bash
git commit -m "feat: add {entity} tool with HubSpot API integration"
git commit -m "test: add comprehensive unit tests for {entity} tool"
git commit -m "docs: update README with {entity} tool documentation"
```

### ✅ Checklist pour nouveau tool

Avant de considérer un tool comme terminé :

**Code :**
- [ ] Classe `{Entity}Tool` héritant de `BaseTool`
- [ ] Méthode `get_{entity}` dans `HubSpotClient`
- [ ] Méthode `format_{entity}` dans `HubSpotFormatter`
- [ ] Enregistrement dans `tools/__init__.py`
- [ ] Enregistrement dans `server/handlers.py`
- [ ] Schéma JSON complet avec validation

**Tests :**
- [ ] Test d'exécution normale
- [ ] Test avec filtres de recherche
- [ ] Test de gestion d'erreurs API
- [ ] Test de formatage avec données variées
- [ ] Couverture ≥ 90%

**Documentation :**
- [ ] Section tool dans README.md
- [ ] Exemples d'utilisation dans README.md
- [ ] Mise à jour description principale
- [ ] Docstrings en français sur toutes les méthodes

**Qualité :**
- [ ] Respect PEP 8 et conventions projet
- [ ] Type hints sur toutes les fonctions
- [ ] Gestion d'erreurs robuste
- [ ] Messages d'erreur en français
- [ ] Formatage utilisateur avec emojis

### 🚨 Règles strictes

- ❌ **Jamais** créer un tool sans tests complets
- ❌ **Jamais** omettre la documentation README
- ❌ **Jamais** utiliser des noms différents des conventions
- ❌ **Jamais** commit sans vérifier la couverture de tests
- ✅ **Toujours** suivre l'ordre de développement
- ✅ **Toujours** utiliser les emojis dans le formatage
- ✅ **Toujours** inclure des exemples d'utilisation
- ✅ **Toujours** tester les cas d'erreur 