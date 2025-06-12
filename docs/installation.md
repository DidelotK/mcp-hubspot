# Installation et Configuration

## Prérequis

- Python 3.12 ou supérieur
- uv (gestionnaire de paquets Python)
- Clé API HubSpot valide

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd hubspot-mcp-server
```

### 2. Installation des dépendances

```bash
uv sync
```

### 3. Configuration des variables d'environnement

Créez un fichier `.envrc` ou définissez les variables d'environnement :

```bash
export HUBSPOT_API_KEY="votre_cle_api_hubspot"
```

## Configuration HubSpot

Le serveur nécessite une clé API HubSpot valide. Vous pouvez obtenir cette clé depuis votre compte HubSpot :

1. Connectez-vous à votre compte HubSpot
2. Allez dans Paramètres > Intégrations > Clés API privées
3. Créez une nouvelle clé API privée
4. Définissez la variable d'environnement HUBSPOT_API_KEY

### Permissions requises

Assurez-vous que votre clé API a les permissions suivantes :
- **Contacts** : Lecture
- **Companies** : Lecture  
- **Deals** : Lecture
- **CRM Search** : Lecture

## Démarrage du serveur

### Mode stdio (pour Claude Desktop)

```bash
uv run python main.py --mode stdio
```

### Mode SSE (pour autres clients MCP)

```bash
uv run python main.py --mode sse --host 127.0.0.1 --port 8080
```

## Vérification de l'installation

Pour vérifier que tout fonctionne correctement :

```bash
# Lancer les tests
uv run pytest

# Vérifier la connexion HubSpot
uv run python -c "from src.hubspot_mcp.client import HubSpotClient; client = HubSpotClient(); print('✅ Connexion HubSpot OK')"
``` 