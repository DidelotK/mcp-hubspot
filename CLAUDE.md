# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a HubSpot MCP (Model Context Protocol) Server - a Python 3.12+ application that provides natural language access to HubSpot CRM data. The server supports both stdio mode (for Claude Desktop) and SSE mode (for web clients) with AI-powered semantic search capabilities.

## AI Assistant Behavior Rules

**MANDATORY**: Before starting any work, Claude MUST read ALL files in `.cursor/rules/` to understand project conventions:

- Read `.cursor/rules/python-standards.mdc` for Python-specific rules
- Read `.cursor/rules/coding-conventions.mdc` for general coding standards
- Read `.cursor/rules/coding-conventions.mdc` for general coding standards
- Read ALL other `.cursor/rules/*.mdc` files for complete project conventions
- Apply these rules strictly to all code modifications

Follow all the rules defined in the folder : `.cursor/rules/`

# important-instruction-reminders

Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
