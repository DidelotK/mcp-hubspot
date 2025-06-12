# Exemples d'utilisation

## Exemples d'utilisation avec Claude

Une fois le serveur MCP configuré avec Claude Desktop, voici des exemples d'interactions :

## Conversations d'exemple

### Exemple 1 : Lister les contacts

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

**Marie Martin**
  📧 Email: marie.martin@techcorp.com
  🏢 Entreprise: TechCorp Solutions
  📞 Téléphone: +33987654321
  🆔 ID: 12346
...
```

### Exemple 2 : Rechercher une transaction

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

### Exemple 3 : Filtrer les entreprises

**Utilisateur :** *"Montre-moi les entreprises du secteur 'technology'"*

**Claude :** *Je recherche les entreprises du secteur technologique.*

*[Claude utilise l'outil `list_hubspot_companies` avec filters: {"search": "technology"}]*

**Résultat affiché :**
```
🏢 **Entreprises HubSpot** (3 trouvées)

**TechCorp Solutions**
  🌐 Domaine: techcorp.com
  🏭 Secteur: Technology
  👥 Employés: 150
  🆔 ID: 67890

**InnovateTech**
  🌐 Domaine: innovatetech.fr
  🏭 Secteur: Software Technology
  👥 Employés: 75
  🆔 ID: 67891
```

### Exemple 4 : Analyser les transactions

**Utilisateur :** *"Quelles sont les transactions de plus de 10 000€ ?"*

**Claude :** *Je vais chercher les transactions importantes dans votre pipeline.*

*[Claude utilise l'outil `list_hubspot_deals` avec filters: {"amount_gte": 10000}]*

---

**Utilisateur :** *"Quelles sont les propriétés disponibles pour les contacts HubSpot ?"*

**Claude :** *Je vais récupérer la liste des propriétés des contacts avec leurs types et descriptions.*

*[Claude utilise l'outil `get_hubspot_contact_properties`]*

**Résultat affiché :**
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

**📞 Numéro de téléphone**
  🏷️ Nom: `phone`
  🔧 Type: string (text)
  📝 Description: Le numéro de téléphone principal du contact

## 📁 demographic_information

**📅 Date de naissance**
  🏷️ Nom: `date_of_birth`
  🔧 Type: date (date)
  📝 Description: La date de naissance du contact
...
```

## Commandes utiles pour Claude

### Recherche de contacts
- *"Liste tous mes contacts HubSpot"*
- *"Trouve les contacts de l'entreprise Acme"*
- *"Cherche le contact jean.dupont@example.com"*
- *"Affiche les 20 derniers contacts"*

### Gestion des entreprises
- *"Montre-moi toutes les entreprises"*
- *"Trouve les entreprises françaises"*
- *"Cherche les entreprises du secteur automobile"*
- *"Liste les entreprises avec plus de 100 employés"*

### Analyse des transactions
- *"Affiche toutes les transactions"*
- *"Quelles sont les transactions en cours ?"*
- *"Trouve les deals dans le pipeline 'enterprise'"*
- *"Recherche le deal 'Projet X'"*
- *"Montre les transactions fermées ce mois"*

### Exploration des données
- *"Quelles sont les propriétés disponibles pour les contacts ?"*
- *"Montre-moi les champs de contact HubSpot"*
- *"Liste les types de données des contacts"*

### Recherches combinées
- *"Trouve tous les contacts de TechCorp et leurs transactions"*
- *"Analyse les performances du secteur technologique"*
- *"Quels sont les plus gros deals en cours ?"*

## Cas d'usage métier

### 1. Suivi commercial quotidien

**Scenario :** Un commercial veut faire le point sur ses prospects

**Commandes :**
1. *"Liste mes 10 derniers contacts"*
2. *"Quelles transactions sont en phase de négociation ?"*
3. *"Montre-moi les deals qui se ferment cette semaine"*

### 2. Analyse sectorielle

**Scenario :** Analyser les opportunités dans un secteur

**Commandes :**
1. *"Trouve toutes les entreprises du secteur 'fintech'"*
2. *"Quelles sont leurs transactions en cours ?"*
3. *"Quel est le montant total des deals fintech ?"*

### 3. Préparation de réunion

**Scenario :** Préparer une réunion client

**Commandes :**
1. *"Trouve l'entreprise 'Acme Corp'"*
2. *"Liste tous les contacts de cette entreprise"*
3. *"Quelles sont leurs transactions actives ?"*

### 4. Reporting hebdomadaire

**Scenario :** Générer un rapport d'activité

**Commandes :**
1. *"Liste toutes les transactions créées cette semaine"*
2. *"Combien de nouveaux contacts avons-nous ?"*
3. *"Quels sont les deals les plus prometteurs ?"*

## Exemples de filtres avancés

### Recherche par montant
```
"Trouve les transactions entre 5000€ et 50000€"
→ filters: {"amount_gte": 5000, "amount_lte": 50000}
```

### Recherche par étape
```
"Montre les deals en phase de proposition"
→ filters: {"stage": "proposal"}
```

### Recherche textuelle
```
"Cherche les contacts avec 'manager' dans leur titre"
→ filters: {"search": "manager"}
```

### Combinaison de filtres
```
"Trouve les entreprises tech avec plus de 50 employés"
→ filters: {"search": "tech", "employees_gte": 50}
``` 