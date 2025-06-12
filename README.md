# Serveur MCP HubSpot

> **Note** : La branche principale de ce projet est `main` (anciennement `master`).

Ce serveur MCP permet d'interagir avec l'API HubSpot pour lister les contacts, entreprises et transactions (deals) avec des capacités de filtrage, ainsi que récupérer des transactions spécifiques par nom.

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

### list_hubspot_deals

Liste les transactions (deals) HubSpot avec possibilité de filtrage.

Paramètres :
- limit (optionnel) : Nombre maximum de transactions à retourner (défaut: 100, max: 1000)
- filters (optionnel) : Objet contenant les filtres de recherche
  - search : Terme de recherche pour filtrer les transactions

Propriétés retournées pour chaque transaction :
- dealname : Nom de la transaction
- amount : Montant de la transaction (formaté en euros)
- dealstage : Étape actuelle du pipeline
- pipeline : Pipeline de vente associé
- closedate : Date de clôture prévue
- createdate : Date de création
- lastmodifieddate : Date de dernière modification
- hubspot_owner_id : Propriétaire de la transaction
- id : Identifiant unique

### get_transaction_by_name

Récupère une transaction HubSpot spécifique par son nom exact.

Paramètres :
- deal_name (obligatoire) : Nom exact de la transaction à rechercher

Propriétés retournées pour la transaction :
- dealname : Nom de la transaction
- amount : Montant de la transaction (formaté en euros)
- dealstage : Étape actuelle du pipeline
- pipeline : Pipeline de vente associé
- closedate : Date de clôture prévue
- createdate : Date de création
- lastmodifieddate : Date de dernière modification
- hubspot_owner_id : Propriétaire de la transaction
- id : Identifiant unique

## Configuration

### Configuration HubSpot

Le serveur nécessite une clé API HubSpot valide. Vous pouvez obtenir cette clé depuis votre compte HubSpot :

1. Connectez-vous à votre compte HubSpot
2. Allez dans Paramètres > Intégrations > Clés API privées
3. Créez une nouvelle clé API privée
4. Définissez la variable d'environnement HUBSPOT_API_KEY

### Intégration avec Claude Desktop

Pour utiliser ce serveur MCP avec Claude Desktop, suivez ces étapes :

#### 1. Configuration Claude Desktop

Éditez le fichier de configuration Claude Desktop :

**Sur macOS :**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Sur Windows :**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Sur Linux :**
```bash
~/.config/claude/claude_desktop_config.json
```

#### 2. Ajout du serveur MCP

Ajoutez la configuration suivante dans le fichier JSON (ou copiez le fichier `claude_desktop_config.example.json` fourni) :

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "uv",
      "args": [
        "run", 
        "python", 
        "/chemin/vers/votre/projet/main.py",
        "--mode", 
        "stdio"
      ],
      "env": {
        "HUBSPOT_API_KEY": "votre_cle_api_hubspot"
      }
    }
  }
}
```

#### 3. Configuration avec uv installé globalement

Si vous avez installé le projet globalement avec uv :

```json
{
  "mcpServers": {
    "hubspot": {
      "command": "hubspot-mcp-server",
      "env": {
        "HUBSPOT_API_KEY": "votre_cle_api_hubspot"
      }
    }
  }
}
```

#### 4. Redémarrage de Claude Desktop

Après avoir modifié la configuration :
1. Fermez complètement Claude Desktop
2. Relancez l'application
3. Les outils HubSpot seront disponibles dans Claude

### Intégration avec d'autres clients MCP

#### Mode SSE (Server-Sent Events)

Pour intégrer avec d'autres clients MCP supportant SSE :

1. **Démarrez le serveur en mode SSE :**
```bash
uv run python main.py --mode sse --host 127.0.0.1 --port 8080
```

2. **Connectez votre client MCP à :**
```
http://127.0.0.1:8080
```

#### Mode stdio

Pour les clients supportant stdio :

```bash
uv run python main.py --mode stdio
```

Le serveur communiquera via stdin/stdout selon le protocole MCP.

### Test de l'intégration

Une fois configuré, vous pouvez tester les outils dans Claude en utilisant des phrases comme :

- *"Liste les contacts HubSpot"*
- *"Trouve-moi les entreprises dans le secteur technologique"*
- *"Affiche toutes les transactions"*
- *"Recherche la transaction nommée 'Contrat Premium'"*

Claude utilisera automatiquement les outils MCP appropriés pour répondre à vos demandes.

### Dépannage

#### Problèmes courants

**1. Claude ne voit pas les outils HubSpot**
- Vérifiez que le fichier de configuration est dans le bon répertoire
- Assurez-vous que la syntaxe JSON est correcte
- Redémarrez complètement Claude Desktop
- Vérifiez les logs de Claude Desktop pour les erreurs

**2. Erreur "Clé API invalide"**
- Vérifiez que votre clé API HubSpot est correcte
- Assurez-vous que la clé a les permissions nécessaires (contacts, deals, companies)
- Testez la clé avec l'API HubSpot directement

**3. Serveur ne démarre pas**
- Vérifiez que Python 3.12+ est installé
- Assurez-vous que uv est installé : `pip install uv`
- Vérifiez que toutes les dépendances sont installées : `uv sync`

**4. En mode SSE, impossible de se connecter**
- Vérifiez que le port 8080 n'est pas utilisé par un autre service
- Testez avec un autre port : `--port 8081`
- Vérifiez les permissions de firewall

#### Logs et débogage

Pour activer les logs détaillés :

```bash
export PYTHONPATH=/chemin/vers/projet
export LOG_LEVEL=DEBUG
uv run python main.py --mode stdio
```

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

Lister toutes les transactions :
Appel de l'outil list_hubspot_deals sans paramètres

Lister les 20 premières transactions :
Appel de l'outil list_hubspot_deals avec limit: 20

Rechercher des transactions par nom :
Appel de l'outil list_hubspot_deals avec filters: {"search": "contrat"}

Récupérer une transaction spécifique :
Appel de l'outil get_transaction_by_name avec deal_name: "Nom Exact Du Deal"

## Exemples d'utilisation avec Claude

Une fois le serveur MCP configuré avec Claude Desktop, voici des exemples d'interactions :

### Conversations d'exemple

**Utilisateur :** *"Peux-tu me lister les 10 premiers contacts HubSpot ?"*

**Claude :** *Je vais récupérer les 10 premiers contacts de votre HubSpot.*

*[Claude utilise automatiquement l'outil `list_hubspot_contacts` avec limit: 10]*

**Résultat affiché :**
```
📋 **Contacts HubSpot** (10 trouvés)

**Jean Dupont**
  📧 Email: jean.dupont@example.com
  🏢 Entreprise: Acme Corp
  📞 Téléphone: +33123456789
  🆔 ID: 12345
...
```

---

**Utilisateur :** *"Trouve-moi la transaction 'Contrat Premium 2024'"*

**Claude :** *Je recherche cette transaction spécifique dans votre HubSpot.*

*[Claude utilise l'outil `get_transaction_by_name` avec deal_name: "Contrat Premium 2024"]*

**Résultat affiché :**
```
💰 **Transaction HubSpot**

**Contrat Premium 2024**
  💰 Montant: 45,000.00 €
  📊 Étape: proposal
  🔄 Pipeline: enterprise
  📅 Date de clôture: 2024-12-31
  🆔 ID: 789012
```

---

**Utilisateur :** *"Montre-moi les entreprises du secteur 'technology'"*

**Claude :** *Je recherche les entreprises du secteur technologique.*

*[Claude utilise l'outil `list_hubspot_companies` avec filters: {"search": "technology"}]*

### Commandes utiles pour Claude

- *"Liste tous mes contacts HubSpot"*
- *"Trouve les entreprises françaises"*
- *"Affiche les 20 dernières transactions"*
- *"Recherche le deal 'Projet X'"*
- *"Montre-moi les contacts de l'entreprise Acme"*
- *"Quelles sont les transactions en cours ?"*

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

## Conventions de Codage / Contribution

Ce projet suit des standards stricts pour maintenir la qualité du code et la cohérence du développement.

### 📋 Documentation des Conventions

- **[🔧 Conventions de Commit](.cursor/rules/commit-conventions.md)** - Format semantic versioning obligatoire
- **[🐍 Standards Python](.cursor/rules/python-standards.md)** - PEP 8, type hints, tests, etc.
- **[🏗️ Structure du Projet](.cursor/rules/project-structure.md)** - Organisation des fichiers et dossiers
- **[🔄 Workflow de Développement](.cursor/rules/development-workflow.md)** - Processus Git, CI/CD, branches

### 🚀 Démarrage Rapide pour Contributeurs

1. **Cloner et installer** :
   ```bash
   git clone https://github.com/DidelotK/mcp-hubspot.git
   cd mcp-hubspot
   uv sync --dev
   ```

2. **Créer une branche feature** :
   ```bash
   git checkout -b feat/description-fonctionnalite
   ```

3. **Développer avec tests** :
   ```bash
   # Lancer les tests en continu
   uv run pytest --cov=src --cov-report=term-missing
   
   # Vérifier la qualité du code
   uv run python scripts/lint_check.py
   
   # Ou corriger automatiquement le formatage
   uv run black src/ main.py tests/
   uv run isort src/ main.py tests/
   ```

4. **Commit avec format semantic** :
   ```bash
   git commit -m "feat: description de la nouvelle fonctionnalité"
   ```

5. **Push et créer une PR** - Le CI vérifiera automatiquement :
   - **Qualité du code** : Black, isort, flake8, mypy
   - **Tests** sur Python 3.12 et 3.13
   - **Couverture** minimum 80%
   - **Commentaire automatique** sur la PR en cas de problème

### ⚡ Règles Essentielles

- ✅ **Format de commit** : `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- ✅ **Tests obligatoires** pour toute nouvelle fonctionnalité
- ✅ **Type hints** sur toutes les fonctions
- ✅ **Couverture minimum** : 80%
- ❌ **Jamais de commit direct** sur `main`
- ❌ **Jamais de merge** sans tests qui passent
