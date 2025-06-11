# Serveur MCP HubSpot

Ce serveur MCP permet d'interagir avec l'API HubSpot pour lister les contacts et entreprises avec des capacités de filtrage.

## Installation

1. Installez [uv](https://docs.astral.sh/uv/getting-started/installation/) si ce n'est pas déjà fait :
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Installez les dépendances :
```bash
uv sync
```

   Ou pour installer uniquement les dépendances de production :
```bash
uv pip install .
```

3. Configurez le serveur :

   Définissez votre clé API HubSpot dans les variables d'environnement :
```bash
   export HUBSPOT_API_KEY=votre_cle_api_hubspot
```

4. Démarrez le serveur :

   Mode stdio (par défaut) :
```bash
uv run python main.py --mode stdio
```
   
   Mode SSE :
```bash
uv run python main.py --mode sse --host 127.0.0.1 --port 8080
```

## Outils disponibles

### list_hubspot_contacts

Liste les contacts HubSpot avec possibilité de filtrage.

Paramètres :
- limit (optionnel) : Nombre maximum de contacts à retourner (défaut: 100, max: 1000)
- filters (optionnel) : Objet contenant les filtres de recherche
  - search : Terme de recherche pour filtrer les contacts

Propriétés retournées pour chaque contact :
- firstname, lastname : Prénom et nom
- email : Adresse email
- company : Entreprise associée
- phone : Numéro de téléphone
- createdate : Date de création
- lastmodifieddate : Date de dernière modification
- id : Identifiant unique

### list_hubspot_companies

Liste les entreprises HubSpot avec possibilité de filtrage.

Paramètres :
- limit (optionnel) : Nombre maximum d'entreprises à retourner (défaut: 100, max: 1000)
- filters (optionnel) : Objet contenant les filtres de recherche
  - search : Terme de recherche pour filtrer les entreprises

Propriétés retournées pour chaque entreprise :
- name : Nom de l'entreprise
- domain : Domaine web
- city, state, country : Localisation
- industry : Secteur d'activité
- createdate : Date de création
- lastmodifieddate : Date de dernière modification
- id : Identifiant unique

## Configuration

Le serveur nécessite une clé API HubSpot valide. Vous pouvez obtenir cette clé depuis votre compte HubSpot :

1. Connectez-vous à votre compte HubSpot
2. Allez dans Paramètres > Intégrations > Clés API privées
3. Créez une nouvelle clé API privée
4. Définissez la variable d'environnement HUBSPOT_API_KEY

## Gestion des erreurs

Le serveur gère automatiquement les erreurs suivantes :
- Clé API manquante ou invalide
- Erreurs de l'API HubSpot (limites de taux, permissions, etc.)
- Erreurs de réseau et de connectivité
- Paramètres invalides

Les messages d'erreur sont formatés de manière claire pour faciliter le débogage.

## Exemples d'utilisation

Lister tous les contacts :
Appel de l'outil list_hubspot_contacts sans paramètres

Lister les 50 premiers contacts :
Appel de l'outil list_hubspot_contacts avec limit: 50

Rechercher des contacts par terme :
Appel de l'outil list_hubspot_contacts avec filters: {"search": "john"}

Lister toutes les entreprises :
Appel de l'outil list_hubspot_companies sans paramètres

Rechercher des entreprises par secteur :
Appel de l'outil list_hubspot_companies avec filters: {"search": "technology"}

## Tests

Pour exécuter les tests unitaires :

```bash
# Installation (une seule fois)
uv venv --python 3.13
source .venv/bin/activate
uv pip install -e '.[dev]'

# Lancer les tests
pytest
```
