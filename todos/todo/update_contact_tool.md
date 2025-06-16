# Update Contact Tool - TODO

**Priority**: Medium
**Category**: Feature Development
**Estimated Effort**: 1-2 hours
**Status**: Todo

## Overview

Implement a tool to update existing contacts in HubSpot through the MCP server. This will allow clients to modify contact properties for existing contact records.

## Task Description

Create a new MCP tool that allows clients to update contact properties in HubSpot by contact ID.

## Implementation Details

### 📄 Files to Create

- `src/hubspot_mcp/tools/update_contact_tool.py` - Main tool implementation
- `tests/unit/test_tools/test_update_contact_tool.py` - Unit tests

### 🏗️ Implementation Pattern

Follow the existing pattern from `update_deal_tool.py`:

- Inherit from `BaseTool`
- Implement proper error handling
- Use HubSpot client methods
- Validate required fields

### 📋 Required Fields

- `contact_id` (required) - HubSpot contact ID to update
- Contact properties to update (at least one required) - Properties to modify

### 🔧 HubSpot Client Integration

May need to implement `update_contact()` method in `hubspot_client.py` if not already available.

### 🧪 Testing Requirements

- Unit tests for successful contact updates
- Unit tests for error handling (API errors, contact not found)
- Unit tests for input validation
- Mock HubSpot API responses

### ✅ Acceptance Criteria

- [ ] Tool can update existing contacts by ID
- [ ] Tool validates contact_id is provided
- [ ] Tool requires at least one property to update
- [ ] Tool handles contact not found scenarios
- [ ] Proper error handling for API failures
- [ ] Unit tests with >80% coverage
- [ ] Tool registered in `__init__.py`
- [ ] Follows existing code patterns and conventions

### 📚 Related Files

- `src/hubspot_mcp/tools/update_deal_tool.py` - Reference implementation
- `src/hubspot_mcp/client/hubspot_client.py` - Client methods
- `src/hubspot_mcp/tools/base.py` - Base tool class
