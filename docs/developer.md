# Developer Guide

This guide covers development setup, testing procedures, and quality assurance for the HubSpot MCP Server.

## 🧪 Testing and Quality

The project maintains high quality standards through comprehensive testing and automated quality checks.

### Quick Quality Check

Run all quality checks with a single command:

```bash
just check
```

This command performs:
- ✅ Code formatting verification
- 🔍 Linting and code quality checks  
- 🎯 Static type checking
- 🧪 Full test suite with coverage
- 🔒 Security vulnerability scanning

### Individual Quality Commands

#### Testing

```bash
# Run all tests with coverage
just test

# Run tests in watch mode (during development)
just test-watch

# Generate HTML coverage report
just test-html
```

#### Code Quality

```bash
# Format code automatically
just format

# Run linting checks
just lint

# Static type checking
just type-check

# Security scanning
just security
```

### Testing Standards

**Current Status:** ✅ 140+ tests passed with comprehensive coverage

#### Coverage Requirements
- **Minimum coverage**: 90%
- **Target coverage**: 100% for new features
- **Coverage includes**: AI/embedding functionality, cache system, all HubSpot tools

#### Test Types
- **Unit tests**: Individual component testing
- **Integration tests**: HubSpot API integration
- **AI/ML tests**: Semantic search and embedding functionality
- **Cache tests**: TTL cache behavior validation

#### Test Categories
- ✅ **HubSpot API Tools**: All 14 tools thoroughly tested
- ✅ **Cache System**: TTL cache with isolation testing
- ✅ **Semantic Search**: AI-powered search functionality
- ✅ **Error Handling**: Comprehensive error scenarios
- ✅ **Performance**: Response time and memory usage
- ✅ **Integration Testing**: Client integration verification

#### Integration Testing

For testing MCP client integrations and end-to-end functionality:

📖 **[Complete Integration Testing Guide →](integration-testing.md)**

This guide covers:
- Claude Desktop integration testing
- MCP client communication validation
- Automated testing scripts
- CI/CD integration examples
- Performance and load testing

### Development Workflow

#### 1. Setup Development Environment

```bash
# Install development dependencies
just install-dev

# Setup pre-commit hooks (optional)
git config core.hooksPath .githooks
```

#### 2. Development Cycle

```bash
# Format code
just format

# Run tests during development
just test-watch

# Full quality check before commit
just check
```

#### 3. Pre-commit Checklist

- [ ] `just check` passes completely
- [ ] New features have 100% test coverage
- [ ] Documentation updated (if applicable)
- [ ] Semantic commit message prepared

### Quality Tools Configuration

#### Testing Framework
- **pytest**: Primary testing framework
- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Async test support
- **pytest-mock**: Mocking utilities

#### Code Quality Tools
- **black**: Code formatting
- **isort**: Import sorting
- **ruff**: Fast Python linter
- **mypy**: Static type checking
- **bandit**: Security vulnerability scanner

#### CI/CD Pipeline
- Automated testing on Python 3.12 and 3.13
- Coverage reporting and enforcement
- Quality gate: all checks must pass

### Performance Testing

The test suite includes performance benchmarks for:
- API response times
- Cache hit/miss ratios
- Semantic search query speed
- Memory usage during operations

### Contributing Guidelines

#### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for public APIs
- Maintain test coverage above 90%

#### Testing Requirements  
- Write tests before implementing features (TDD)
- Test both success and error scenarios
- Mock external dependencies (HubSpot API)
- Include performance considerations

#### Documentation
- Update relevant documentation files
- Include examples for new features
- Maintain Tools documentation accuracy

### Troubleshooting Tests

#### Common Issues

**Import Errors:**
```bash
# Ensure proper installation
just install-dev
```

**API Key Issues:**
```bash
# Set test environment
export HUBSPOT_API_KEY="test-key-for-mocking"
```

**Cache Issues:**
```bash
# Clear cache before tests
just test  # Automatically handles cache isolation
```

#### Debug Mode

```bash
# Run tests with verbose output
uv run pytest -v -s

# Run specific test file
uv run pytest tests/test_specific_module.py -v

# Run with debugger
uv run pytest --pdb
```

### Continuous Integration

The project uses GitHub Actions for:
- Multi-version Python testing (3.12, 3.13)
- Quality gate enforcement
- Coverage reporting to Codecov
- Security vulnerability scanning
- Performance regression testing

All pull requests must pass the complete CI pipeline before merging.

## 🔐 Secure Environment Configuration

The project uses a secure approach for handling sensitive information:

### 🛡️ **Local Development Setup**

1. **Copy the example configuration:**
   ```bash
   cp .env.example .env.local
   ```

2. **Edit `.env.local` with your real secrets:**
   ```bash
   # Replace with your actual HubSpot API key
   HUBSPOT_API_KEY="pat-na1-your-actual-api-key-here"
   ```

3. **The environment loads automatically with direnv:**
   ```bash
   direnv allow  # Enables automatic loading
   ```

### 🔒 **Security Features**

- ✅ **`.env.local`** - Contains your real secrets (never committed)
- ✅ **`.env.example`** - Safe template file (committed to git)
- ✅ **`.envrc`** - Automatically sources `.env.local` if available
- ✅ **Git protection** - `.env.local` is in `.gitignore`
- ✅ **Clean history** - All secrets removed from Git history

### ⚠️ **Important Security Notes**

- **Never commit** `.env.local` - it contains your real API keys
- **Always use** `.env.example` as a template for new setups
- **Git history** has been cleaned of any exposed secrets
- **Production deployments** use Kubernetes secrets via External Secrets Operator


## 🔗 Related Documentation

- [Contributing Guide](contributing.md) - Detailed contribution process
- [Installation Guide](installation.md) - Setup instructions
- [Integration Guide](integration.md) - MCP client configuration 
