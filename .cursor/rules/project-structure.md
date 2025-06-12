# Project Structure

## Folder Organization
```
project/
├── .cursor/rules/          # Cursor rules (thematic organizations)
├── .github/workflows/      # GitHub Actions CI/CD
├── src/                    # Main source code
├── tests/                  # Unit tests
├── rules/                  # Rules documentation
├── pyproject.toml          # Python configuration and dependencies
├── uv.lock                 # Dependencies lock file
├── pytest.ini             # pytest configuration
└── README.md               # Main documentation
```

## Structure Rules
- **Source code**: Must be in `src/`
- **Tests**: Must be in `tests/`
- **Configuration**: Centralized in `pyproject.toml`
- **Dependencies**: Managed exclusively with `uv`
- **CI/CD**: Workflows in `.github/workflows/`
- **Documentation**: All documentation in English

## Naming Conventions
- **Modules**: snake_case (e.g., `hubspot_client.py`)
- **Packages**: snake_case (e.g., `hubspot_mcp/`)
- **Classes**: PascalCase (e.g., `HubSpotClient`)
- **Functions**: snake_case (e.g., `get_contacts`)
- **Constants**: UPPER_CASE (e.g., `API_BASE_URL`)
- **Language**: All names in English only

## Important Files
- **pyproject.toml**: Main project configuration
- **uv.lock**: Never modify manually
- **pytest.ini**: Test configuration
- **.gitignore**: Git exclusions (auto-generated)
- **README.md**: User documentation in English

## Language Policy
- ✅ **ALWAYS** use English for file names
- ✅ **ALWAYS** use English for folder names
- ✅ **ALWAYS** write configuration in English
- ✅ **ALWAYS** document in English
- ❌ **NEVER** use French in project structure 