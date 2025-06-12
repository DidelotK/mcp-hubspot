# Commit Conventions - Semantic Versioning

## Required Format
ALWAYS use Semantic Versioning format for commits:

**Format**: `<type>: <description>`

## Allowed Types

### Main Types:
- **feat:** new feature
- **fix:** bug fix  
- **docs:** documentation only
- **style:** formatting, no logical changes
- **refactor:** refactoring without adding/removing functionality
- **test:** adding/modifying tests
- **chore:** maintenance, dependencies

### Secondary Types:
- **ci:** CI/CD configuration
- **perf:** performance improvement
- **build:** build system
- **revert:** commit reversion

## Strict Rules
- Use imperative present tense ("add" not "added")
- Short description (≤ 50 characters)
- Optional scope: `feat(auth): add OAuth integration`
- Details in body if necessary
- **All commit messages must be in English**

## Compliant Examples
```
feat: add user authentication system
fix: resolve memory leak in data processing
docs: update API documentation
test: add unit tests for payment module
chore: update dependencies to latest versions
ci: add GitHub Actions workflow
```

## Language Policy
- ✅ **ALWAYS** write commit messages in English
- ❌ **NEVER** use French or other languages in commit messages
- ✅ Use English technical terms consistently
- ✅ Keep descriptions clear and concise in English 