# Semantic Release Automation

This project uses automated semantic versioning and release management through [semantic-release](https://github.com/semantic-release/semantic-release) and [Conventional Commits](https://www.conventionalcommits.org/).

## 🚀 How It Works

### Automated Release Process

1. **Commit Analysis**: When commits are pushed to the `main` branch, semantic-release analyzes commit messages
2. **Version Calculation**: Determines the next version based on commit types following semantic versioning
3. **Changelog Generation**: Automatically generates release notes from commit messages
4. **Version Updates**: Updates `pyproject.toml` with the new version number
5. **GitHub Release**: Creates a GitHub release with generated changelog
6. **Repository Tagging**: Tags the repository with the new version

### Commit Message Format

All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## 📋 Commit Types and Release Impact

| Type | Release | Description | Example |
|------|---------|-------------|---------|
| `feat` | **MINOR** | New feature | `feat: add contact search by email` |
| `fix` | **PATCH** | Bug fix | `fix: handle API timeout errors` |
| `perf` | **PATCH** | Performance improvement | `perf: optimize cache lookup` |
| `refactor` | **PATCH** | Code refactoring | `refactor: simplify error handling` |
| `BREAKING CHANGE` | **MAJOR** | Breaking change | `feat!: change API response format` |
| `docs` | **NO RELEASE** | Documentation | `docs: update API reference` |
| `test` | **NO RELEASE** | Tests | `test: add unit tests for client` |
| `chore` | **NO RELEASE** | Maintenance | `chore: update dependencies` |
| `style` | **NO RELEASE** | Code style | `style: fix formatting` |
| `ci` | **NO RELEASE** | CI/CD changes | `ci: add release workflow` |
| `build` | **NO RELEASE** | Build system | `build: update Docker config` |

## 🔧 Configuration

### Package Dependencies

The project includes Node.js dependencies for semantic-release:

```json
{
  "devDependencies": {
    "semantic-release": "^22.0.12",
    "@semantic-release/changelog": "^6.0.3",
    "@semantic-release/git": "^10.0.1",
    "@semantic-release/github": "^9.2.6",
    "@semantic-release/exec": "^6.0.3"
  }
}
```

### Semantic Release Configuration (`.releaserc.json`)

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    ["@semantic-release/exec", {
      "prepareCmd": "sed -i 's/version = \".*\"/version = \"${nextRelease.version}\"/' pyproject.toml"
    }],
    ["@semantic-release/git", {
      "assets": ["CHANGELOG.md", "pyproject.toml"],
      "message": "chore(release): ${nextRelease.version} [skip ci]"
    }],
    "@semantic-release/github"
  ]
}
```

### GitHub Actions Workflow (`.github/workflows/release.yml`)

- **Triggers**: Automatically on pushes to `main` branch
- **Requirements**: Node.js 20, Python 3.12
- **Authentication**: Uses `GITHUB_TOKEN` automatically provided by GitHub Actions
- **Skip Condition**: Skips if commit message contains `[skip ci]`

## 📝 Version Bumping Rules

### Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
  - Use `feat!:` or `fix!:` with breaking change
  - Or include `BREAKING CHANGE:` in commit footer

- **MINOR** (1.0.0 → 1.1.0): New features
  - Use `feat:` for new functionality

- **PATCH** (1.0.0 → 1.0.1): Bug fixes and improvements
  - Use `fix:` for bug fixes
  - Use `perf:` for performance improvements
  - Use `refactor:` for code refactoring

## 📚 Examples

### Feature Release (Minor Version)

```bash
git commit -m "feat: add semantic search for contacts

Implement FAISS-based semantic search allowing natural language
queries to find contacts based on meaning rather than exact matches.

- Add embedding generation for contact data
- Implement similarity search with configurable thresholds
- Include fallback to traditional search when embeddings unavailable

Closes #123"
```

**Result**: 1.2.3 → 1.3.0

### Bug Fix Release (Patch Version)

```bash
git commit -m "fix: handle empty API responses gracefully

Prevent crashes when HubSpot API returns empty results by adding
proper null checks and default empty arrays."
```

**Result**: 1.2.3 → 1.2.4

### Breaking Change Release (Major Version)

```bash
git commit -m "feat!: change tool response format to structured JSON

BREAKING CHANGE: All tool responses now return structured JSON instead
of formatted strings. This improves programmatic access but breaks
existing integrations expecting text responses.

Migration guide:
- Update MCP clients to parse JSON responses
- Use new 'formatted_text' field for display purposes"
```

**Result**: 1.2.3 → 2.0.0

### Documentation Update (No Release)

```bash
git commit -m "docs: add examples for semantic search tool

- Add usage examples with different query types
- Document configuration options
- Include troubleshooting section"
```

**Result**: No release created

## 🛠️ Testing and Validation

### Dry Run Testing

Test what would be released without actually creating a release:

```bash
# Requires GITHUB_TOKEN for full simulation
npx semantic-release --dry-run
```

### Commit Message Validation

Install commitizen for interactive commit creation:

```bash
# Install globally
npm install -g commitizen

# Use interactive commit helper
cz commit
```

## 🔍 Release Management

### Automated Releases

- **Frequency**: Every push to `main` branch with qualifying commits
- **Timing**: Typically completes within 5 minutes
- **Notification**: GitHub release notifications sent automatically

### Manual Release (Emergency)

For emergency situations, releases can be triggered manually:

```bash
# Trigger workflow manually via GitHub CLI
```

### Release Rollback

Use GitHub's release management for rollbacks:

1. Go to GitHub repository releases page
2. Edit the problematic release
3. Mark as pre-release or delete
4. Revert problematic commits if needed

## 📊 Release Information

### Version Badges

The README includes badges showing:

- Latest release version
- Semantic release status
- Conventional commits compliance

### Changelog

- **Location**: `CHANGELOG.md`
- **Format**: Markdown with emoji-enhanced sections
- **Content**: Automatically generated from commit messages
- **Grouping**: Features, bug fixes, performance improvements, etc.

### GitHub Releases

Each release includes:

- Version tag (e.g., `v1.2.3`)
- Release notes generated from commits
- Links to compare changes
- Asset downloads (if applicable)

## 🔐 Security and Permissions

### GitHub Token

- **Automatic**: GitHub Actions provides `GITHUB_TOKEN` automatically
- **Permissions**: Content write, issues write, pull requests write
- **Scope**: Limited to the repository

### Branch Protection

Recommended branch protection rules for `main`:

- Require status checks to pass
- Require branches to be up to date
- Require review before merging
- Restrict pushes to main branch

## 🚨 Troubleshooting

### Common Issues

1. **Release Skipped**: Check commit message format and ensure it follows conventional commits
2. **Permission Denied**: Verify GitHub token permissions and branch protection rules
3. **Version Conflict**: Ensure no manual version changes conflict with automation
4. **CI Failure**: All CI checks must pass before release creation

### Debug Mode

Enable debug logging in GitHub Actions:

```yaml
- name: Release
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    DEBUG: semantic-release:*
  run: npx semantic-release
```

### Support

- **Documentation**: [Semantic Release Docs](https://semantic-release.gitbook.io/)
- **Conventional Commits**: [Specification](https://www.conventionalcommits.org/)
- **Issues**: Create GitHub issue for project-specific problems
