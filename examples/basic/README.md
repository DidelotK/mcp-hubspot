# Test basique du serveur MCP HubSpot

Ce dossier contient un exemple pratique d'utilisation du serveur MCP HubSpot avec un client Python.

## 📋 Description

Le script `test_mcp_client.py` démontre comment :
- Se connecter au serveur MCP HubSpot via stdio
- Utiliser les 4 outils disponibles
- Gérer les erreurs et afficher les résultats
- Tester différents scénarios d'utilisation

## 🚀 Utilisation

### 1. Prérequis

Assurez-vous d'avoir :
- Python 3.12+
- Le package `mcp` installé
- Une clé API HubSpot valide

### 2. Installation des dépendances

```bash
# Depuis la racine du projet
uv sync

# Ou installer mcp séparément
pip install mcp
```

### 3. Configuration

Définissez votre clé API HubSpot :

```bash
export HUBSPOT_API_KEY="votre_cle_api_hubspot"
```

### 4. Exécution du test

```bash
# Depuis la racine du projet (recommandé)
uv run python examples/basic/test_mcp_client.py

# Ou avec Python directement (si l'environnement est configuré)
python examples/basic/test_mcp_client.py
```

## 🧪 Tests effectués

Le script exécute 4 tests principaux :

### Test 1 : Récupération des contacts
- **Outil** : `list_hubspot_contacts`
- **Paramètres** : `{"limit": 5}`
- **Objectif** : Vérifier la récupération basique des contacts

### Test 2 : Recherche avec filtre
- **Outil** : `list_hubspot_contacts`
- **Paramètres** : `{"limit": 3, "filters": {"search": "test"}}`
- **Objectif** : Tester le filtrage des contacts

### Test 3 : Récupération des entreprises
- **Outil** : `list_hubspot_companies`
- **Paramètres** : `{"limit": 3}`
- **Objectif** : Vérifier l'accès aux données d'entreprises

### Test 4 : Récupération des deals
- **Outil** : `list_hubspot_deals`
- **Paramètres** : `{"limit": 3}`
- **Objectif** : Tester l'accès aux données de deals

## 📊 Sortie attendue

```
============================================================
🧪 TEST DU SERVEUR MCP HUBSPOT
============================================================
🚀 Démarrage du test du serveur MCP HubSpot...
🔑 Clé API HubSpot: pat-eu1-a5...
🔌 Connexion au serveur MCP...
🤝 Initialisation de la session MCP...
📋 Récupération de la liste des outils...
✅ 4 outils disponibles:
  - list_hubspot_contacts: Liste les contacts HubSpot avec possibilité de filtrage
  - list_hubspot_companies: Liste les entreprises HubSpot avec possibilité de filtrage
  - list_hubspot_deals: Liste les deals HubSpot avec possibilité de filtrage
- get_deal_by_name: Récupère un deal HubSpot par son nom exact

🧪 Test 1: Récupération des 5 premiers contacts...
✅ Contacts récupérés avec succès:
📋 **Contacts HubSpot** (5 trouvés)

**Jean Dupont**
  📧 Email: jean.dupont@example.com
  🏢 Entreprise: Acme Corp
  📞 Téléphone: +33123456789
  🆔 ID: 12345
...

🧪 Test 2: Recherche de contacts avec filtre...
✅ Recherche effectuée avec succès:
...

🧪 Test 3: Récupération des entreprises...
✅ Entreprises récupérées avec succès:
...

🧪 Test 4: Récupération des deals...
✅ Deals récupérés avec succès:
...

🎉 Tests terminés avec succès!
✅ Tous les tests ont réussi!
```

## 🔧 Personnalisation

### Modifier les tests

Vous pouvez facilement modifier le script pour :

1. **Tester d'autres outils** :
```python
# Tester get_deal_by_name
result = await session.call_tool(
    "get_deal_by_name",
    arguments={"deal_name": "Nom Exact Du Deal"}
)
```

2. **Changer les paramètres** :
```python
# Récupérer plus de contacts
result = await session.call_tool(
    "list_hubspot_contacts",
    arguments={"limit": 20}
)
```

3. **Ajouter des filtres** :
```python
# Filtrer par email
result = await session.call_tool(
    "list_hubspot_contacts",
    arguments={
        "limit": 10,
        "filters": {"email": "john@example.com"}
    }
)
```

### Gestion d'erreurs

Le script gère automatiquement :
- **Clé API manquante** : Vérification au démarrage
- **Erreurs de connexion** : Retry et messages explicites
- **Erreurs d'outils** : Capture et affichage des erreurs spécifiques
- **Interruption utilisateur** : Gestion propre du Ctrl+C

## 🐛 Dépannage

### Erreur "Package mcp not found"
```bash
pip install mcp
# ou
uv add mcp
```

### Erreur "HUBSPOT_API_KEY not defined"
```bash
export HUBSPOT_API_KEY="votre_cle_api"
# Vérifiez avec:
echo $HUBSPOT_API_KEY
```

### Erreur de connexion au serveur
- Vérifiez que le fichier `main.py` existe à la racine
- Assurez-vous que les dépendances du serveur sont installées
- Testez le serveur manuellement : `python main.py --mode stdio`

### Pas de données retournées
- Vérifiez que votre compte HubSpot contient des données
- Assurez-vous que la clé API a les bonnes permissions
- Testez avec l'API HubSpot directement

## 📚 Ressources

- [Documentation MCP](https://modelcontextprotocol.io/)
- [API HubSpot](https://developers.hubspot.com/docs/api/overview)
- [Guide d'intégration](../../docs/integration.md)
- [Référence API](../../docs/api-reference.md) 