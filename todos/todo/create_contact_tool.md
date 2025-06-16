# Create Contact Tool - TODO

**Priority**: Medium
**Category**: Feature Development
**Estimated Effort**: 1-2 hours
**Status**: Todo

## Overview

Implement a tool to create new contacts in HubSpot through the MCP server. This will complement the existing contact operations (get contacts, search contacts) by adding the ability to create new contact records.

## Task Description

Create a new MCP tool that allows clients to create contacts in HubSpot with the necessary properties.

## Implementation Details

### 📄 Files to Create

- `src/hubspot_mcp/tools/create_contact_tool.py` - Main tool implementation
- `tests/unit/test_tools/test_create_contact_tool.py` - Unit tests

### 🏗️ Implementation Pattern

Follow the existing pattern from `create_deal_tool.py`:

- Inherit from `BaseTool`
- Implement proper error handling
- Use HubSpot client methods
- Validate required fields

### 📋 Required Fields

- `email` (required) - Contact's email address
- `firstname` (optional) - Contact's first name
- `lastname` (optional) - Contact's last name
- Additional contact properties (optional) - Any other HubSpot contact properties

### 🔧 HubSpot Client Integration

May need to implement `create_contact()` method in `hubspot_client.py` if not already available.

### 🧪 Testing Requirements

- Unit tests for successful contact creation
- Unit tests for error handling (API errors, validation errors)
- Unit tests for input validation
- Mock HubSpot API responses

### ✅ Acceptance Criteria

- [ ] Tool can create contacts with email as minimum required field
- [ ] Tool validates email format
- [ ] Tool handles optional firstname and lastname
- [ ] Tool supports additional HubSpot contact properties
- [ ] Proper error handling for API failures
- [ ] Unit tests with >80% coverage
- [ ] Tool registered in `__init__.py`
- [ ] Follows existing code patterns and conventions

### 📚 Related Files

- `src/hubspot_mcp/tools/create_deal_tool.py` - Reference implementation
- `src/hubspot_mcp/client/hubspot_client.py` - Client methods
- `src/hubspot_mcp/tools/base.py` - Base tool class
