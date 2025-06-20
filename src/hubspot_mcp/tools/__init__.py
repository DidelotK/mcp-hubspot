"""Module containing MCP tools for HubSpot."""

from .bulk_cache_loader import BulkCacheLoaderTool
from .cache_management_tool import CacheManagementTool
from .companies import CompaniesTool
from .company_properties_tool import CompanyPropertiesTool
from .contact_properties_tool import ContactPropertiesTool
from .contacts import ContactsTool
from .create_deal_tool import CreateDealTool
from .deal_by_name_tool import DealByNameTool
from .deal_properties_tool import DealPropertiesTool
from .deals import DealsTool
from .embedding_management_tool import EmbeddingManagementTool
from .engagements import EngagementsTool
from .enhanced_base import EnhancedBaseTool
from .faiss_data_tool import FaissDataTool
from .search_companies import SearchCompaniesTool
from .search_contacts import SearchContactsTool
from .search_deals import SearchDealsTool
from .semantic_search_tool import SemanticSearchTool
from .update_deal_tool import UpdateDealTool

# List of all available tool classes
AVAILABLE_TOOLS = [
    BulkCacheLoaderTool,
    CacheManagementTool,
    ContactsTool,
    CompaniesTool,
    DealsTool,
    CreateDealTool,
    DealByNameTool,
    ContactPropertiesTool,
    CompanyPropertiesTool,
    DealPropertiesTool,
    UpdateDealTool,
    EngagementsTool,
    SearchDealsTool,
    SearchContactsTool,
    SearchCompaniesTool,
    SemanticSearchTool,
    EmbeddingManagementTool,
    FaissDataTool,
]

__all__ = [
    "BulkCacheLoaderTool",
    "CacheManagementTool",
    "ContactsTool",
    "CompaniesTool",
    "DealsTool",
    "CreateDealTool",
    "DealByNameTool",
    "ContactPropertiesTool",
    "CompanyPropertiesTool",
    "DealPropertiesTool",
    "UpdateDealTool",
    "EngagementsTool",
    "SearchDealsTool",
    "SearchContactsTool",
    "SearchCompaniesTool",
    "EnhancedBaseTool",
    "SemanticSearchTool",
    "EmbeddingManagementTool",
    "FaissDataTool",
    "AVAILABLE_TOOLS",
]
