# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a HubSpot MCP (Model Context Protocol) Server - a Python 3.12+ application that provides natural language access to HubSpot CRM data. The server supports both stdio mode (for Claude Desktop) and SSE mode (for web clients) with AI-powered semantic search capabilities.

## AI Assistant Behavior Rules

**MANDATORY**: Before starting any work, Claude MUST read ALL files in `.cursor/rules/` to understand project conventions:

- Read `.cursor/rules/README.mdc` for overview of all rules and conventions
- Read `.cursor/rules/commit-conventions.mdc` for Git commit conventions rules
- Read `.cursor/rules/python-standards.mdc` for Python-specific rules
- Read `.cursor/rules/coding-conventions.mdc` for general coding standards
- Read `.cursor/rules/development-workflow.mdc` for general development workflow standards
- Read `.cursor/rules/documentation-conventions.mdc` for documentation conventions
- Read `.cursor/rules/cursor-behavior.mdc` for Cursor assistant behavior rules
- Read `.cursor/rules/mcp-tools-conventions.mdc` for HubSpot MCP tools development rules
- Read `.cursor/rules/project-structure.mdc` for project organization and structure rules
- Read `.cursor/rules/security-conventions.mdc` for security and authentication rules
- Read `.cursor/rules/terraform-conventions.mdc` for infrastructure and deployment rules
- Read ALL other `.cursor/rules/*.mdc` files for complete project conventions
- Apply these rules strictly to all code modifications

Follow all the rules defined in the folder : `.cursor/rules/`
