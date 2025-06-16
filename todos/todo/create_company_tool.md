# Create Company Tool - TODO

**Priority**: Medium
**Category**: Feature Development
**Estimated Effort**: 1-2 hours
**Status**: Todo

## Overview

Implement a tool to create new companies in HubSpot through the MCP server. This will complement the existing company operations (get companies, search companies) by adding the ability to create new company records.

## Task Description

Create a new MCP tool that allows clients to create companies in HubSpot with the necessary properties.

## Implementation Details

### 📄 Files to Create

- `src/hubspot_mcp/tools/create_company_tool.py` - Main tool implementation
- `tests/unit/test_tools/test_create_company_tool.py` - Unit tests

### 🏗️ Implementation Pattern

Follow the existing pattern from `create_deal_tool.py`:

- Inherit from `BaseTool`
- Implement proper error handling
- Use HubSpot client methods
- Validate required fields

### 📋 Required Fields

- `name` (required) - Company name
- Additional company properties (optional) - Any other HubSpot company properties

### 🔧 HubSpot Client Integration

May need to implement `create_company()` method in `hubspot_client.py` if not already available.

### 🧪 Testing Requirements

- Unit tests for successful company creation
- Unit tests for error handling (API errors, validation errors)
- Unit tests for input validation
- Mock HubSpot API responses

### ✅ Acceptance Criteria

- [ ] Tool can create companies with name as minimum required field
- [ ] Tool validates company name is provided
- [ ] Tool supports additional HubSpot company properties
- [ ] Proper error handling for API failures
- [ ] Unit tests with >80% coverage
- [ ] Tool registered in `__init__.py`
- [ ] Follows existing code patterns and conventions

### 📚 Related Files

- `src/hubspot_mcp/tools/create_deal_tool.py` - Reference implementation
- `src/hubspot_mcp/client/hubspot_client.py` - Client methods
- `src/hubspot_mcp/tools/base.py` - Base tool class
