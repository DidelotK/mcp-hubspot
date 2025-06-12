# Standards Python

## Règles de codage obligatoires
- **PEP 8** : Respecter strictement le style guide Python
- **Type hints** : Utiliser les annotations de type pour toutes les fonctions
- **Docstrings** : Documenter les classes et fonctions publiques
- **Snake_case** : Noms de variables et fonctions en snake_case
- **PascalCase** : Noms de classes en PascalCase

## Tests unitaires
- **Obligatoires** pour toutes nouvelles fonctionnalités
- **Framework** : pytest exclusivement
- **Structure** : Tests dans `tests/` avec noms `test_*.py`
- **Coverage** : Minimum 80% de couverture de code
- **Async** : Utiliser pytest-asyncio pour les tests asynchrones

## Imports et dépendances
- **Ordre des imports** : standard library, third-party, local
- **Imports absolus** préférés aux imports relatifs
- **Gestionnaire** : `uv` pour toutes les dépendances
- **Fichiers** : Configuration dans `pyproject.toml`

## Bonnes pratiques
- **Exceptions** : Capturer des exceptions spécifiques
- **Logging** : Utiliser le module logging standard
- **Constants** : UPPER_CASE pour les constantes
- **Private** : Préfixer avec _ pour les méthodes privées
- **Magic methods** : Implémenter __str__ et __repr__ si pertinent

## Outils recommandés
- **black** : Formatage automatique du code
- **isort** : Organisation des imports
- **mypy** : Vérification des types statiques
- **pylint/flake8** : Analyse statique du code 