# Structure du Projet

## Organisation des dossiers
```
projet/
├── .cursor/rules/          # Règles Cursor (thématiques)
├── .github/workflows/      # CI/CD GitHub Actions
├── src/                    # Code source principal
├── tests/                  # Tests unitaires
├── rules/                  # Documentation des règles
├── pyproject.toml          # Configuration Python et dépendances
├── uv.lock                 # Lock file des dépendances
├── pytest.ini             # Configuration pytest
└── README.md               # Documentation principale
```

## Règles de structure
- **Code source** : Obligatoirement dans `src/`
- **Tests** : Obligatoirement dans `tests/`
- **Configuration** : Centralisée dans `pyproject.toml`
- **Dépendances** : Gérées exclusivement avec `uv`
- **CI/CD** : Workflows dans `.github/workflows/`

## Conventions de nommage
- **Modules** : snake_case (ex: `hubspot_client.py`)
- **Packages** : snake_case (ex: `hubspot_mcp/`)
- **Classes** : PascalCase (ex: `HubSpotClient`)
- **Fonctions** : snake_case (ex: `get_contacts`)
- **Constantes** : UPPER_CASE (ex: `API_BASE_URL`)

## Files importantes
- **pyproject.toml** : Configuration principale du projet
- **uv.lock** : Ne jamais modifier manuellement
- **pytest.ini** : Configuration des tests
- **.gitignore** : Exclusions Git (généré automatiquement)
- **README.md** : Documentation utilisateur 