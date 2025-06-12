# HubSpot MCP Server

Serveur MCP (Model Context Protocol) pour intégrer HubSpot avec Claude Desktop et autres clients MCP. Permet d'accéder aux contacts, entreprises et transactions HubSpot via des outils conversationnels.

## 🚀 Démarrage rapide

```bash
# Installation
git clone <url-du-repo>
cd hubspot-mcp-server
uv sync

# Configuration
export HUBSPOT_API_KEY="votre_cle_api"

# Démarrage
uv run python main.py --mode stdio
```

## 📚 Documentation

| Section | Description |
|---------|-------------|
| **[Installation](docs/installation.md)** | Guide d'installation et configuration |
| **[Intégration](docs/integration.md)** | Configuration avec Claude Desktop et autres clients MCP |
| **[Référence API](docs/api-reference.md)** | Documentation complète des 4 outils disponibles |
| **[Exemples](docs/examples.md)** | Cas d'usage et conversations types avec Claude |
| **[Contribution](docs/contributing.md)** | Guide pour développer de nouveaux outils |

## 🛠️ Outils disponibles

| Outil | Description |
|-------|-------------|
| `list_hubspot_contacts` | Liste et filtre les contacts HubSpot |
| `list_hubspot_companies` | Liste et filtre les entreprises HubSpot |
| `list_hubspot_deals` | Liste et filtre les transactions HubSpot |
| `get_transaction_by_name` | Recherche une transaction par nom exact |

## ⚡ Utilisation avec Claude

Une fois configuré, utilisez des phrases naturelles :

- *"Liste mes contacts HubSpot"*
- *"Trouve les entreprises du secteur tech"*
- *"Affiche les transactions en cours"*
- *"Recherche le deal 'Projet X'"*

## 🧪 Tests et qualité

```bash
# Lancer les tests
uv run pytest

# Couverture de code
uv run pytest --cov=src --cov-report=html
```

**Statut actuel :** ✅ 24 tests passés, 91% de couverture

## 📋 Prérequis

- Python 3.12+
- uv (gestionnaire de paquets)
- Clé API HubSpot avec permissions CRM

## 🤝 Contribution

Consultez le [guide de contribution](docs/contributing.md) pour :
- Standards de développement
- Processus de création d'outils
- Conventions de code et tests
- Workflow Git et semantic versioning

## 📄 Licence

[Licence du projet]

---

**Liens utiles :**
- [Configuration Claude Desktop](docs/integration.md#intégration-avec-claude-desktop)
- [Exemples d'utilisation](docs/examples.md#conversations-dexemple)
- [Référence complète des outils](docs/api-reference.md)
- [Dépannage](docs/integration.md#dépannage)
