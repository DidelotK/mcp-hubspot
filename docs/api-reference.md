# Référence API - Outils MCP

Ce serveur MCP expose 5 outils pour interagir avec l'API HubSpot.

## list_hubspot_contacts

Récupère la liste des contacts HubSpot.

### Paramètres

| Paramètre | Type | Obligatoire | Description | Défaut |
|-----------|------|-------------|-------------|---------|
| `limit` | integer | Non | Nombre maximum de contacts à récupérer | 100 |
| `filters` | object | Non | Filtres de recherche | {} |

### Exemple d'utilisation

```json
{
  "name": "list_hubspot_contacts",
  "arguments": {
    "limit": 10,
    "filters": {
      "search": "jean"
    }
  }
}
```

### Réponse

```
📋 **Contacts HubSpot** (10 trouvés)

**Jean Dupont**
  📧 Email: jean.dupont@example.com
  🏢 Entreprise: Acme Corp
  📞 Téléphone: +33123456789
  🆔 ID: 12345
```

## list_hubspot_companies

Récupère la liste des entreprises HubSpot.

### Paramètres

| Paramètre | Type | Obligatoire | Description | Défaut |
|-----------|------|-------------|-------------|---------|
| `limit` | integer | Non | Nombre maximum d'entreprises à récupérer | 100 |
| `filters` | object | Non | Filtres de recherche | {} |

### Exemple d'utilisation

```json
{
  "name": "list_hubspot_companies",
  "arguments": {
    "limit": 5,
    "filters": {
      "search": "technology"
    }
  }
}
```

### Réponse

```
🏢 **Entreprises HubSpot** (5 trouvées)

**TechCorp Solutions**
  🌐 Domaine: techcorp.com
  🏭 Secteur: Technology
  👥 Employés: 150
  🆔 ID: 67890
```

## list_hubspot_deals

Récupère la liste des transactions (deals) HubSpot.

### Paramètres

| Paramètre | Type | Obligatoire | Description | Défaut |
|-----------|------|-------------|-------------|---------|
| `limit` | integer | Non | Nombre maximum de transactions à récupérer | 100 |
| `filters` | object | Non | Filtres de recherche | {} |

### Exemple d'utilisation

```json
{
  "name": "list_hubspot_deals",
  "arguments": {
    "limit": 20,
    "filters": {
      "search": "premium"
    }
  }
}
```

### Réponse

```
💰 **Transactions HubSpot** (20 trouvées)

**Contrat Premium 2024**
  💰 Montant: 45,000.00 €
  📊 Étape: proposal
  🔄 Pipeline: enterprise
  📅 Date de clôture: 2024-12-31
  🆔 ID: 789012
```

## get_transaction_by_name

Récupère une transaction spécifique par son nom exact.

### Paramètres

| Paramètre | Type | Obligatoire | Description |
|-----------|------|-------------|-------------|
| `deal_name` | string | **Oui** | Nom exact de la transaction à rechercher |

### Exemple d'utilisation

```json
{
  "name": "get_transaction_by_name",
  "arguments": {
    "deal_name": "Contrat Premium 2024"
  }
}
```

### Réponse - Transaction trouvée

```
💰 **Transaction HubSpot**

**Contrat Premium 2024**
  💰 Montant: 45,000.00 €
  📊 Étape: proposal
  🔄 Pipeline: enterprise
  📅 Date de clôture: 2024-12-31
  🆔 ID: 789012
```

### Réponse - Transaction non trouvée

```
❌ **Transaction non trouvée**

Aucune transaction trouvée avec le nom: "Contrat Inexistant"
```

## get_hubspot_contact_properties

Récupère la liste des propriétés disponibles pour les contacts HubSpot avec leurs types et descriptions.

### Paramètres

Aucun paramètre requis.

### Exemple d'utilisation

```json
{
  "name": "get_hubspot_contact_properties",
  "arguments": {}
}
```

### Réponse

```
🔧 **Propriétés des Contacts HubSpot** (405 propriétés)

## 📁 contactinformation

**📧 Adresse e-mail**
  🏷️ Nom: `email`
  🔧 Type: string (text)
  📝 Description: L'adresse e-mail du contact

**📝 Prénom**
  🏷️ Nom: `firstname`
  🔧 Type: string (text)
  📝 Description: Le prénom du contact

**📝 Nom de famille**
  🏷️ Nom: `lastname`
  🔧 Type: string (text)
  📝 Description: Le nom de famille du contact

**📞 Numéro de téléphone**
  🏷️ Nom: `phone`
  🔧 Type: string (text)
  📝 Description: Le numéro de téléphone principal du contact

## 📁 demographic_information

**📅 Date de naissance**
  🏷️ Nom: `date_of_birth`
  🔧 Type: date (date)
  📝 Description: La date de naissance du contact

## 📁 company_information

**📋 Secteur d'activité**
  🏷️ Nom: `industry`
  🔧 Type: enumeration (select)
  📝 Description: Le secteur d'activité de l'entreprise
  📋 Options: Technologie, Finance, Santé, ... et 25 autres
```

### Utilité

Cet outil est particulièrement utile pour :
- **Découvrir les champs disponibles** dans HubSpot
- **Comprendre les types de données** (text, date, select, etc.)
- **Voir les options disponibles** pour les champs de sélection
- **Planifier l'intégration** avec d'autres systèmes
- **Déboguer les problèmes** de synchronisation de données

## Gestion des erreurs

Tous les outils gèrent les erreurs de manière cohérente :

### Erreurs d'authentification

```
❌ Erreur d'authentification HubSpot. Vérifiez votre clé API.
```

### Erreurs de réseau

```
❌ Erreur de connexion à l'API HubSpot. Vérifiez votre connexion internet.
```

### Erreurs de paramètres

```
❌ Paramètre manquant: deal_name est obligatoire pour get_transaction_by_name
```

## Filtres de recherche

Les filtres supportent les propriétés suivantes :

### Pour les contacts
- `search` : Recherche textuelle dans nom, email, entreprise
- `email` : Filtrage par email exact
- `company` : Filtrage par nom d'entreprise

### Pour les entreprises
- `search` : Recherche textuelle dans nom, domaine, secteur
- `domain` : Filtrage par domaine exact
- `industry` : Filtrage par secteur d'activité

### Pour les transactions
- `search` : Recherche textuelle dans nom, étape, pipeline
- `stage` : Filtrage par étape de vente
- `pipeline` : Filtrage par pipeline de vente
- `amount_gte` : Montant minimum
- `amount_lte` : Montant maximum 