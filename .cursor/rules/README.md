# Cursor Rules Organization

This folder contains development rules organized by topic for better maintainability.

## 📁 Rules Structure

### 🔧 [commit-conventions.md](./commit-conventions.md)
Strict conventions for semantic versioning commit messages
- Allowed commit types
- Required format
- Examples and counter-examples

### 🐍 [python-standards.md](./python-standards.md)
Python standards and best practices
- Coding rules (PEP 8, type hints)
- Test configuration (pytest)
- Recommended tools

### 🏗️ [project-structure.md](./project-structure.md)
Project organization and structure
- Folder hierarchy
- Naming conventions
- Configuration files

### 🔄 [development-workflow.md](./development-workflow.md)
Development process and Git workflow
- Development steps
- Branching rules
- CI/CD process

### 🤖 [cursor-behavior.md](./cursor-behavior.md)
Specific behavior for Cursor assistant
- Communication rules
- Action priorities
- Strict prohibitions

### 🛠️ [mcp-tools-conventions.md](./mcp-tools-conventions.md)
Conventions specific to HubSpot MCP tools
- Required file structure
- Technical standards and naming
- Development and testing process
- Complete quality checklist

## 🎯 Usage
Cursor will automatically read all these files to apply corresponding rules during development. This modular organization allows:

- ✅ **Easy maintenance**: Modify a rule in a single file
- ✅ **Readability**: Rules organized by topic
- ✅ **Scalability**: Easy addition of new categories
- ✅ **Consistency**: Standards applied systematically 