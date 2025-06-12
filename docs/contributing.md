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
uv run black src/ main.py tests/ scripts/
uv run isort src/ main.py tests/ scripts/

# Static analysis
uv run flake8 src/ main.py tests/ scripts/
uv run mypy src/ main.py

# Complete quality report
uv run python scripts/lint_check.py
```

### 4. Commit and PR

```bash
# Semantic versioning commits
git add .
git commit -m "feat: add new_resource tool with HubSpot API integration"
git commit -m "test: add comprehensive unit tests for new_resource tool"
git commit -m "docs: update API reference with new_resource tool"

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
- [ ] **Documentation**: Complete section in API reference
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

### API Reference

Each new tool must have a complete section in `docs/api-reference.md`:

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

### Semantic Versioning

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Refactoring
- `chore:` - Maintenance

### Release

1. All tests pass
2. Documentation updated
3. Test coverage maintained
4. **Code quality validated**
5. Semantic versioning commits
6. PR reviewed and approved 