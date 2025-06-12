# Workflow de Développement

## Processus de développement
1. **Branche feature** : Créer une branche à partir de `main`
   ```bash
   git checkout -b feat/description-fonctionnalite
   ```

2. **Développement** : Coder avec tests unitaires
   - Écrire les tests AVANT le code (TDD recommandé)
   - Respecter les standards Python
   - Documenter les fonctions publiques

3. **Tests locaux** : Exécuter tous les tests
   ```bash
   uv run pytest --cov=src --cov-report=term-missing
   ```

4. **Commit semantic** : Utiliser le format semantic versioning
   ```bash
   git commit -m "feat: add new authentication feature"
   ```

5. **Push et PR** : Pousser et créer une Pull Request
   ```bash
   git push origin feat/description-fonctionnalite
   ```

6. **CI validation** : Attendre que tous les tests CI passent
   - Tests sur Python 3.12 et 3.13
   - Couverture de code validée
   - Linting et formatage

7. **Review et merge** : Code review puis merge vers main

## Règles strictes
- ❌ **Jamais** de commit direct sur `main`
- ❌ **Jamais** de merge sans tests qui passent
- ❌ **Jamais** de push sans message semantic
- ✅ **Toujours** créer une branche feature
- ✅ **Toujours** écrire des tests
- ✅ **Toujours** respecter la couverture minimum (80%)

## Branches principales
- **main** : Branche de production, stable
- **develop** : Branche de développement (optionnelle)
- **feat/** : Nouvelles fonctionnalités
- **fix/** : Corrections de bugs
- **hotfix/** : Corrections critiques pour production 