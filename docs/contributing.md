# Contributing Guide

## Development Conventions

This project follows strict conventions to maintain code consistency and quality. Check the `.cursor/rules/mcp-tools-conventions.md` file for complete details.

## Structure for a New MCP Tool

### 1. Client (`src/hubspot_mcp/client.py`)

Add a method in the `HubSpotClient` class:

```python
async def get_new_resource(self, limit: int = 100, filters: dict = None) -> List[dict]:
    """Retrieves new resources from HubSpot."""
    # Implementation with error handling
    pass
```

### 2. Formatter (`src/hubspot_mcp/formatters.py`)

Create a formatting function:

```python
def format_new_resources(resources: List[dict]) -> str:
    """Formats the list of new resources for display."""
    if not resources:
        return "❌ **No resources found**"

    # Formatting with emojis and consistent structure
    pass
```

### 3. Tool (`src/hubspot_mcp/tools/`)

Create a new file `new_resource_tool.py`:

```python
from mcp.types import Tool
from ..client import HubSpotClient
from ..formatters import format_new_resources

class NewResourceTool:
    def __init__(self, client: HubSpotClient):
        self.client = client

    @property
    def definition(self) -> Tool:
        return Tool(
            name="list_hubspot_new_resources",
            description="Clear description of the tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number to retrieve",
                        "default": 100
                    }
                }
            }
        )

    async def execute(self, limit: int = 100, filters: dict = None) -> str:
        # Implementation with error handling
        pass
```

### 4. Registration

Update `src/hubspot_mcp/__init__.py` and `src/hubspot_mcp/handlers.py`.

### 5. Tests

Create tests in `tests/` with at minimum:

- Normal execution test
- Error handling test
- Formatting test

### 6. Documentation

Update `docs/api-reference.md` with complete documentation.

## Development Process

### 1. Preparation

```bash
# Clone and install
git clone <repo>
cd hubspot-mcp-server
uv sync

# Install Git hooks (recommended)
./scripts/install_hooks.sh

# Create a branch
git checkout -b feature/new-tool
```

### 2. Development

1. **Implementation**: Follow the structure above
2. **Tests**: Write tests before or during development
3. **Documentation**: Update documentation

### 3. Validation

```bash
# Complete quality check (recommended)
./scripts/check_quality.sh

# Or individual checks:
# Run tests
uv run pytest

# Check coverage
uv run pytest --cov=src --cov-report=html

# Code formatting
uv run black src/ tests/ scripts/
uv run isort src/ tests/ scripts/

# Static analysis
uv run flake8 src/ tests/ scripts/
uv run mypy src/

# Complete quality report
uv run python scripts/lint_check.py
```

### 4. Commit and PR

```bash
# Semantic versioning commits
git add .
git commit -m "feat: add new_resource tool with HubSpot API integration"
git commit -m "test: add comprehensive unit tests for new_resource tool"
git commit -m "docs: update tools documentation with new_resource tool"

# Push and PR
git push origin feature/new-tool
```

## Quality Standards

### Pre-commit Checklist

- [ ] **Structure**: Respect architecture (client/formatter/tool)
- [ ] **Naming**: Convention `list_hubspot_*` or `get_*_by_*`
- [ ] **JSON Schema**: Properties with types and descriptions
- [ ] **Error Handling**: Try/catch with consistent messages
- [ ] **Formatting**: Emojis and uniform structure
- [ ] **Tests**: Minimum 90% coverage
- [ ] **Documentation**: Complete section in Tools
- [ ] **Types**: Python type annotations
- [ ] **Async/await**: Asynchronous methods
- [ ] **Logging**: Appropriate informative messages

### Code Standards

#### Tool Naming

- **List**: `list_hubspot_[resource]` (e.g., `list_hubspot_contacts`)
- **Search**: `get_[resource]_by_[field]` (e.g., `get_deal_by_name`)

#### Response Formatting

- **Title**: `📋 **HubSpot Resources** (X found)`
- **Emojis**: Consistent by data type
- **Structure**: Bold name, indented properties
- **Errors**: `❌ **Error message**`

#### Error Handling

```python
try:
    # API call
    pass
except Exception as e:
    logger.error(f"Error during retrieval: {e}")
    return f"❌ Error retrieving resources: {str(e)}"
```

## Tests

### Test Structure

```python
import pytest
from unittest.mock import AsyncMock, patch
from src.hubspot_mcp.tools.new_resource_tool import NewResourceTool

class TestNewResourceTool:
    @pytest.fixture
    def mock_client(self):
        return AsyncMock()

    @pytest.fixture
    def tool(self, mock_client):
        return NewResourceTool(mock_client)

    @pytest.mark.asyncio
    async def test_execute_success(self, tool, mock_client):
        # Test normal case
        pass

    @pytest.mark.asyncio
    async def test_execute_error(self, tool, mock_client):
        # Test error handling
        pass
```

### Required Coverage

- **Minimum**: 90% global coverage
- **New code**: 100% coverage
- **Required tests**:
  - Normal execution
  - Error handling
  - Data formatting
  - Parameter validation

## Documentation

### Tools

Each new tool must have a complete section in `docs/tools.md`:

```markdown
## new_tool

Tool description.

### Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|

### Usage Example

### Response
```

### Examples

Add concrete examples in `docs/examples.md`.

## Code Quality

### Verification Tools

The project uses several tools to maintain quality:

- **black**: Automatic code formatting
- **isort**: Automatic import sorting
- **flake8**: Static analysis and PEP 8 style
- **mypy**: Type checking
- **bandit**: Security analysis
- **pytest**: Unit tests with coverage

### Available Scripts

```bash
# Complete check (recommended before commit)
./scripts/check_quality.sh

# Install Git hooks
./scripts/install_hooks.sh

# Detailed quality report
uv run python scripts/lint_check.py
```

### Automatic Git Hooks

Installed Git hooks automatically execute:

- **pre-commit**: Formatting, imports, static analysis
- **pre-push**: Unit tests

To temporarily bypass:

```bash
git commit --no-verify
git push --no-verify
```

### CI/CD

Quality checks run automatically:

- ✅ **On all pushes** to main/develop
- ✅ **On all pull requests**
- ❌ **Build failure** if quality is not satisfactory

## Deployment

### Semantic Versioning and Automated Releases

This project uses [Conventional Commits](https://www.conventionalcommits.org/) and automated semantic versioning to manage releases.

#### Commit Message Format

All commit messages must follow the conventional commits specification:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Commit Types

| Type | Release | Description | Example |
|------|---------|-------------|---------|
| `feat` | **minor** | New feature | `feat: add contact search tool` |
| `fix` | **patch** | Bug fix | `fix: handle empty API responses` |
| `BREAKING CHANGE` | **major** | Breaking change | `feat!: change API interface` |
| `docs` | none | Documentation | `docs: update API reference` |
| `test` | none | Tests | `test: add unit tests for client` |
| `refactor` | patch | Code refactoring | `refactor: optimize cache implementation` |
| `perf` | patch | Performance improvement | `perf: improve query response time` |
| `style` | none | Code style | `style: fix formatting` |
| `chore` | none | Maintenance | `chore: update dependencies` |
| `ci` | none | CI/CD changes | `ci: add release workflow` |
| `build` | none | Build system | `build: update Docker config` |

#### Breaking Changes

For breaking changes, use either:

- `feat!: description` (with exclamation mark)
- Or include `BREAKING CHANGE:` in the footer

#### Examples

```bash
# New feature (minor version bump)
git commit -m "feat: add company search by domain tool"

# Bug fix (patch version bump)
git commit -m "fix: handle null values in contact properties"

# Breaking change (major version bump)
git commit -m "feat!: change tool response format to JSON"

# Documentation (no version bump)
git commit -m "docs: add examples for deal management tools"

# Multiple changes
git commit -m "feat: add bulk contact export

Support exporting up to 10,000 contacts with filtering options.
Includes pagination and rate limiting.

Closes #123"
```

#### Automated Release Process

When commits are pushed to the main branch:

1. **Analysis**: Semantic-release analyzes commit messages since the last release
2. **Version Calculation**: Determines the next version number based on commit types
3. **Changelog Generation**: Creates release notes from commit messages
4. **Version Update**: Updates `pyproject.toml` with the new version
5. **GitHub Release**: Creates a GitHub release with the changelog
6. **Tagging**: Tags the repository with the new version

#### Version Bumping Rules

- **Major** (1.0.0 → 2.0.0): Breaking changes (`BREAKING CHANGE` or `!`)
- **Minor** (1.0.0 → 1.1.0): New features (`feat`)
- **Patch** (1.0.0 → 1.0.1): Bug fixes (`fix`), performance improvements (`perf`), refactoring (`refactor`)
- **No release**: Documentation, tests, chores, styles, CI changes

#### Pre-commit Validation

Install commitizen for commit message validation:

```bash
# Install commitizen (optional but recommended)
pip install commitizen

# Use interactive commit helper
cz commit

# Or validate existing commit messages
cz check --commit-msg-file .git/COMMIT_EDITMSG
```

### Release Management

1. **Automated**: All releases are created automatically when changes are merged to main
2. **Quality Gates**: All CI checks must pass before release
3. **Manual Override**: Emergency releases can be triggered manually
4. **Rollback**: Use GitHub's release management for rollbacks

#### Manual Release (Emergency Only)

```bash
# Only for emergency situations
gh workflow run release.yml
```

#### Pre-release Testing

Test semantic release without publishing:

```bash
# Dry run to see what would be released
npx semantic-release --dry-run
```
