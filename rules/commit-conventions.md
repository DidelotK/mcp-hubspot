# Conventions de Commit - Semantic Versioning

## Format des messages de commit

Toujours utiliser le format **Semantic Versioning** pour les messages de commit :

```
<type>: <description>

[optional body]

[optional footer]
```

## Types de commit

### Types principaux :
- **feat:** Nouvelle fonctionnalité
- **fix:** Correction de bug
- **docs:** Changements dans la documentation uniquement
- **style:** Changements qui n'affectent pas le sens du code (espaces, formatage, etc.)
- **refactor:** Changement de code qui ne corrige pas de bug ni n'ajoute de fonctionnalité
- **test:** Ajout ou modification de tests
- **chore:** Changements dans le processus de build ou outils auxiliaires

### Types secondaires :
- **perf:** Amélioration des performances
- **ci:** Changements dans les fichiers de configuration CI
- **build:** Changements qui affectent le système de build
- **revert:** Annulation d'un commit précédent

## Exemples de messages de commit

### ✅ Bons exemples :
```
feat: add user authentication system
fix: resolve memory leak in data processing
docs: update API documentation for v2.0
test: add unit tests for payment module
chore: update dependencies to latest versions
ci: add GitHub Actions workflow for automated testing
```

### ❌ Mauvais exemples :
```
added new feature
fixed bug
updated docs
test
```

## Règles spécifiques au projet

1. **Langue** : Messages en français ou anglais selon le contexte
2. **Longueur** : Description courte (≤ 50 caractères), détails dans le body si nécessaire
3. **Impératif** : Utiliser l'impératif présent ("add" pas "added")
4. **Scope optionnel** : Utiliser des scopes si pertinent : `feat(auth): add OAuth integration`

## Workflow de commit

1. Vérifier que tous les tests passent
2. Ajouter les fichiers avec `git add`
3. Committer avec un message semantic versioning
4. Pousser vers la branche appropriée

## Outils recommandés

- **Pre-commit hooks** pour valider le format des messages
- **Commitizen** pour aider à la création de messages conformes
- **Conventional Changelog** pour générer automatiquement les changelogs