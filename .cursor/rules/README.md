# Organisation des Règles Cursor

Ce dossier contient les règles de développement organisées par thématique pour une meilleure maintenabilité.

## 📁 Structure des règles

### 🔧 [commit-conventions.md](./commit-conventions.md)
Conventions strictes pour les messages de commit semantic versioning
- Types de commits autorisés
- Format obligatoire
- Exemples et contre-exemples

### 🐍 [python-standards.md](./python-standards.md)
Standards et bonnes pratiques Python
- Règles de codage (PEP 8, type hints)
- Configuration des tests (pytest)
- Outils recommandés

### 🏗️ [project-structure.md](./project-structure.md)
Organisation et structure du projet
- Arborescence des dossiers
- Conventions de nommage
- Fichiers de configuration

### 🔄 [development-workflow.md](./development-workflow.md)
Processus de développement et workflow Git
- Étapes de développement
- Règles de branching
- Processus CI/CD

### 🤖 [cursor-behavior.md](./cursor-behavior.md)
Comportement spécifique de l'assistant Cursor
- Règles de communication
- Priorités d'action
- Interdictions strictes

## 🎯 Utilisation
Cursor lira automatiquement tous ces fichiers pour appliquer les règles correspondantes lors du développement. Cette organisation modulaire permet :

- ✅ **Maintenance facile** : Modification d'une règle dans un seul fichier
- ✅ **Lisibilité** : Règles organisées par thématique
- ✅ **Évolutivité** : Ajout facile de nouvelles catégories
- ✅ **Cohérence** : Standards appliqués de façon systématique 