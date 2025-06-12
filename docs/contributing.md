# Guide de contribution

## Conventions de développement

Ce projet suit des conventions strictes pour maintenir la cohérence et la qualité du code. Consultez le fichier `.cursor/rules/mcp-tools-conventions.md` pour les détails complets.

## Structure d'un nouvel outil MCP

### 1. Client (`src/hubspot_mcp/client.py`)

Ajoutez une méthode dans la classe `HubSpotClient` :

```python
async def get_new_resource(self, limit: int = 100, filters: dict = None) -> List[dict]:
    """Récupère les nouvelles ressources depuis HubSpot."""
    # Implémentation avec gestion d'erreurs
    pass
```

### 2. Formatter (`src/hubspot_mcp/formatters.py`)

Créez une fonction de formatage :

```python
def format_new_resources(resources: List[dict]) -> str:
    """Formate la liste des nouvelles ressources pour affichage."""
    if not resources:
        return "❌ **Aucune ressource trouvée**"
    
    # Formatage avec emojis et structure cohérente
    pass
```

### 3. Tool (`src/hubspot_mcp/tools/`)

Créez un nouveau fichier `new_resource_tool.py` :

```python
from mcp.types import Tool
from ..client import HubSpotClient
from ..formatters import format_new_resources

class NewResourceTool:
    def __init__(self, client: HubSpotClient):
        self.client = client
    
    @property
    def definition(self) -> Tool:
        return Tool(
            name="list_hubspot_new_resources",
            description="Description claire de l'outil",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Nombre maximum à récupérer",
                        "default": 100
                    }
                }
            }
        )
    
    async def execute(self, limit: int = 100, filters: dict = None) -> str:
        # Implémentation avec gestion d'erreurs
        pass
```

### 4. Enregistrement

Mettez à jour `src/hubspot_mcp/__init__.py` et `src/hubspot_mcp/handlers.py`.

### 5. Tests

Créez des tests dans `tests/` avec au minimum :
- Test d'exécution normale
- Test de gestion d'erreur
- Test de formatage

### 6. Documentation

Mettez à jour `docs/api-reference.md` avec la documentation complète.

## Processus de développement

### 1. Préparation

```bash
# Cloner et installer
git clone <repo>
cd hubspot-mcp-server
uv sync

# Créer une branche
git checkout -b feature/nouveau-tool
```

### 2. Développement

1. **Implémentation** : Suivre la structure ci-dessus
2. **Tests** : Écrire les tests avant ou pendant le développement
3. **Documentation** : Mettre à jour la documentation

### 3. Validation

```bash
# Lancer les tests
uv run pytest

# Vérifier la couverture
uv run pytest --cov=src --cov-report=html

# Linter (si configuré)
uv run ruff check src/
```

### 4. Commit et PR

```bash
# Commits semantic versioning
git add .
git commit -m "feat: add new_resource tool with HubSpot API integration"
git commit -m "test: add comprehensive unit tests for new_resource tool"
git commit -m "docs: update API reference with new_resource tool"

# Push et PR
git push origin feature/nouveau-tool
```

## Standards de qualité

### Checklist avant commit

- [ ] **Structure** : Respect de l'architecture (client/formatter/tool)
- [ ] **Nommage** : Convention `list_hubspot_*` ou `get_*_by_*`
- [ ] **Schéma JSON** : Propriétés avec types et descriptions
- [ ] **Gestion d'erreurs** : Try/catch avec messages cohérents
- [ ] **Formatage** : Emojis et structure uniforme
- [ ] **Tests** : Couverture minimale 90%
- [ ] **Documentation** : Section complète dans API reference
- [ ] **Types** : Annotations de type Python
- [ ] **Async/await** : Méthodes asynchrones
- [ ] **Logging** : Messages informatifs appropriés

### Standards de code

#### Nommage des outils
- **Liste** : `list_hubspot_[resource]` (ex: `list_hubspot_contacts`)
- **Recherche** : `get_[resource]_by_[field]` (ex: `get_transaction_by_name`)

#### Formatage des réponses
- **Titre** : `📋 **Ressources HubSpot** (X trouvées)`
- **Emojis** : Cohérents par type de donnée
- **Structure** : Nom en gras, propriétés indentées
- **Erreurs** : `❌ **Message d'erreur**`

#### Gestion d'erreurs
```python
try:
    # Appel API
    pass
except Exception as e:
    logger.error(f"Erreur lors de la récupération: {e}")
    return f"❌ Erreur lors de la récupération des ressources: {str(e)}"
```

## Tests

### Structure des tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from src.hubspot_mcp.tools.new_resource_tool import NewResourceTool

class TestNewResourceTool:
    @pytest.fixture
    def mock_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def tool(self, mock_client):
        return NewResourceTool(mock_client)
    
    @pytest.mark.asyncio
    async def test_execute_success(self, tool, mock_client):
        # Test cas nominal
        pass
    
    @pytest.mark.asyncio
    async def test_execute_error(self, tool, mock_client):
        # Test gestion d'erreur
        pass
```

### Couverture requise

- **Minimum** : 90% de couverture globale
- **Nouveau code** : 100% de couverture
- **Tests obligatoires** :
  - Exécution normale
  - Gestion d'erreurs
  - Formatage des données
  - Validation des paramètres

## Documentation

### API Reference

Chaque nouvel outil doit avoir une section complète dans `docs/api-reference.md` :

```markdown
## nouveau_tool

Description de l'outil.

### Paramètres

| Paramètre | Type | Obligatoire | Description | Défaut |
|-----------|------|-------------|-------------|---------|

### Exemple d'utilisation

### Réponse
```

### Exemples

Ajoutez des exemples concrets dans `docs/examples.md`.

## Déploiement

### Semantic Versioning

- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Refactoring
- `chore:` - Maintenance

### Release

1. Tous les tests passent
2. Documentation à jour
3. Couverture de tests maintenue
4. Commits semantic versioning
5. PR reviewée et approuvée 