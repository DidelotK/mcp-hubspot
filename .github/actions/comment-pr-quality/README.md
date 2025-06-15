# PR Quality Comment Action

GitHub Action to automatically comment on Pull Requests with code quality reports.

## Features

- Analyzes quality reports (lint, coverage, tests)
- Adds or updates comments on PRs automatically
- Handles errors and edge cases intelligently
- Configurable comment format
- Supports multiple report types

## Usage

```yaml
name: Quality Check
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run quality checks
        run: |
          # Your quality check commands here
          ./scripts/check_quality.sh

      - name: Comment PR with quality report
        uses: ./.github/actions/comment-pr-quality
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          report-path: 'lint_report.md'
          comment-title: '📊 Code Quality Report'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `github-token` | GitHub token for API access | ✅ | |
| `report-path` | Path to the quality report file | ✅ | |
| `comment-title` | Title for the PR comment | ❌ | `📊 Quality Report` |
| `update-existing` | Update existing comment instead of creating new ones | ❌ | `true` |

## Dependencies

- `actions/checkout@v4` - To access repository files
- `peter-evans/find-comment@v3` - To find existing comments
- `peter-evans/create-or-update-comment@v3` - To create/update comments

## Behavior

1. **Report Analysis**: Reads the quality report file
2. **Comment Management**:
   - Searches for existing comments with the same title
   - Updates existing comment or creates a new one
3. **Error Handling**: Handles cases where the report doesn't exist
4. **Format**: Maintains consistent comment formatting

## Example Report Format

The action expects reports in Markdown format:

```markdown
## 📊 Code Quality Report

✅ **Black Formatting**: OK
✅ **Import Organization (isort)**: OK
❌ **PEP 8 Compliance (flake8)**: Issues found
✅ **Type Checking (mypy)**: OK

### 🔧 How to fix:
```bash
# Auto-fix formatting and imports
black src/ tests/
isort src/ tests/
```

## File Structure

```
.github/actions/comment-pr-quality/
├── action.yml          # Action definition
├── README.md          # This documentation
└── scripts/
    └── comment.sh     # Main script logic
```

## Development

To modify this action:

1. Edit `action.yml` for input/output definitions
2. Modify `scripts/comment.sh` for logic changes
3. Test with a sample PR
4. Update this README if needed

## Contributing

This action is part of the HubSpot MCP project quality pipeline. Follow the project's contributing guidelines when making changes.
