# Update Company Tool - TODO

**Priority**: Medium
**Category**: Feature Development
**Estimated Effort**: 1-2 hours
**Status**: Todo

## Overview

Implement a tool to update existing companies in HubSpot through the MCP server. This will allow clients to modify company properties for existing company records.

## Task Description

Create a new MCP tool that allows clients to update company properties in HubSpot by company ID.

## Implementation Details

### 📄 Files to Create

- `src/hubspot_mcp/tools/update_company_tool.py` - Main tool implementation
- `tests/unit/test_tools/test_update_company_tool.py` - Unit tests

### 🏗️ Implementation Pattern

Follow the existing pattern from `update_deal_tool.py`:

- Inherit from `BaseTool`
- Implement proper error handling
- Use HubSpot client methods
- Validate required fields

### 📋 Required Fields

- `company_id` (required) - HubSpot company ID to update
- Company properties to update (at least one required) - Properties to modify

### 🔧 HubSpot Client Integration

May need to implement `update_company()` method in `hubspot_client.py` if not already available.

### 🧪 Testing Requirements

- Unit tests for successful company updates
- Unit tests for error handling (API errors, company not found)
- Unit tests for input validation
- Mock HubSpot API responses

### ✅ Acceptance Criteria

- [ ] Tool can update existing companies by ID
- [ ] Tool validates company_id is provided
- [ ] Tool requires at least one property to update
- [ ] Tool handles company not found scenarios
- [ ] Proper error handling for API failures
- [ ] Unit tests with >80% coverage
- [ ] Tool registered in `__init__.py`
- [ ] Follows existing code patterns and conventions

### 📚 Related Files

- `src/hubspot_mcp/tools/update_deal_tool.py` - Reference implementation
- `src/hubspot_mcp/client/hubspot_client.py` - Client methods
- `src/hubspot_mcp/tools/base.py` - Base tool class
