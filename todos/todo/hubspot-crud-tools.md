# HubSpot CRUD Tools - TODO

**Priority**: Medium
**Category**: Feature Development
**Created**: 2024
**Estimated Effort**: 4-6 hours

## Overview

Implement additional CRUD (Create, Read, Update, Delete) tools for HubSpot entities to complement the existing tools. Currently, we have read operations and `create_deal`/`update_deal` tools, but we need to complete the CRUD functionality for contacts and companies.

## Tasks to Complete

### 🧑‍💼 Contact Operations

#### 1. Create Contact Tool

- **Description**: Implement a tool to create new contacts in HubSpot
- **File**: `src/hubspot_mcp/tools/create_contact_tool.py`
- **Dependencies**:
  - Existing HubSpot client contact creation methods
  - Follow patterns from `create_deal_tool.py`
- **Required Fields**:
  - `email` (required)
  - `firstname` (optional)
  - `lastname` (optional)
  - Additional contact properties (optional)
- **Test File**: `tests/unit/test_tools/test_create_contact_tool.py`

#### 2. Update Contact Tool

- **Description**: Implement a tool to update existing contacts in HubSpot
- **File**: `src/hubspot_mcp/tools/update_contact_tool.py`
- **Dependencies**:
  - Existing HubSpot client contact update methods
  - Follow patterns from `update_deal_tool.py`
- **Required Fields**:
  - `contact_id` (required)
  - Contact properties to update (at least one required)
- **Test File**: `tests/unit/test_tools/test_update_contact_tool.py`

### 🏢 Company Operations

#### 3. Create Company Tool

- **Description**: Implement a tool to create new companies in HubSpot
- **File**: `src/hubspot_mcp/tools/create_company_tool.py`
- **Dependencies**:
  - Existing HubSpot client company creation methods
  - Follow patterns from `create_deal_tool.py`
- **Required Fields**:
  - `name` (required)
  - Additional company properties (optional)
- **Test File**: `tests/unit/test_tools/test_create_company_tool.py`

#### 4. Update Company Tool

- **Description**: Implement a tool to update existing companies in HubSpot
- **File**: `src/hubspot_mcp/tools/update_company_tool.py`
- **Dependencies**:
  - Existing HubSpot client company update methods
  - Follow patterns from `update_deal_tool.py`
- **Required Fields**:
  - `company_id` (required)
  - Company properties to update (at least one required)
- **Test File**: `tests/unit/test_tools/test_update_company_tool.py`

## Implementation Guidelines

### 🏗️ Architecture Patterns to Follow

1. **Inherit from `BaseTool`**: Use the existing base tool class
2. **Follow existing patterns**: Reference `create_deal_tool.py` and `update_deal_tool.py`
3. **Error handling**: Implement proper HTTPX error handling
4. **Type hints**: Use Python 3.12+ type annotations
5. **Tool registration**: Add tools to `src/hubspot_mcp/tools/__init__.py`

### 📋 Quality Requirements

- **Test Coverage**: Minimum 80% coverage for all new tools
- **Documentation**: Docstrings for all public methods
- **Error Handling**: Proper exception handling and user-friendly error messages
- **Validation**: Input validation for required fields
- **Formatting**: Use existing HubSpot formatter patterns

### 🔧 HubSpot Client Integration

**Required Client Methods** (may need to be implemented):

For Contacts:

- `create_contact(properties: Dict[str, Any]) -> Dict[str, Any]`
- `update_contact(contact_id: str, properties: Dict[str, Any]) -> Dict[str, Any]`

For Companies:

- `create_company(properties: Dict[str, Any]) -> Dict[str, Any]`
- `update_company(company_id: str, properties: Dict[str, Any]) -> Dict[str, Any]`

### 🧪 Testing Requirements

Each tool must have:

- Unit tests for successful operations
- Unit tests for error handling
- Unit tests for input validation
- Mock HubSpot API responses
- Test tool definition structure

### 📚 Documentation Updates

Update the following files after implementation:

- `docs/tools.md` - Add new tool documentation
- `examples/` - Add usage examples if needed
- `README.md` - Update tool list if necessary

## Acceptance Criteria

### ✅ Definition of Done

- [ ] All 4 tools implemented following existing patterns
- [ ] All tools registered in `__init__.py`
- [ ] Unit tests written with >80% coverage
- [ ] All tests pass (`just check`)
- [ ] Error handling implemented and tested
- [ ] Tool definitions follow MCP specification
- [ ] Documentation updated
- [ ] Code review completed

### 🎯 Success Metrics

- Tools integrate seamlessly with existing MCP server
- Consistent API with existing CRUD tools
- Proper error messages for common failure scenarios
- Tools work with Claude Desktop and other MCP clients

## Notes

- **API Limits**: Consider HubSpot API rate limits in implementation
- **Permissions**: Ensure proper HubSpot API permissions are documented
- **Validation**: Follow HubSpot field validation requirements
- **Consistency**: Maintain consistency with existing tool naming and structure

## Related Files

- `src/hubspot_mcp/tools/create_deal_tool.py` - Reference implementation
- `src/hubspot_mcp/tools/update_deal_tool.py` - Reference implementation
- `src/hubspot_mcp/client/hubspot_client.py` - Client methods
- `src/hubspot_mcp/tools/base.py` - Base tool class
- `tests/unit/test_tools/` - Test examples
