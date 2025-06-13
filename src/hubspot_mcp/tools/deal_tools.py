"""Tools for interacting with HubSpot deals."""

from typing import Any, Dict, List, Optional

from ..client import HubSpotClient
from ..formatters.hubspot_formatter import HubSpotFormatter


def list_hubspot_deals(
    limit: int = 100, filters: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """List HubSpot deals with optional filters.

    Args:
        limit: Maximum number of deals to retrieve
        filters: Optional search filters

    Returns:
        List of deals matching the criteria
    """
    client = HubSpotClient()
    api_response = client.crm.deals.basic_api.get_page(
        limit=limit,
        properties=["dealname", "amount", "dealstage", "pipeline", "closedate"],
        archived=False,
    )
    return [HubSpotFormatter.format_single_deal(deal) for deal in api_response.results]


def create_deal(
    dealname: str,
    amount: Optional[str] = None,
    dealstage: Optional[str] = None,
    pipeline: Optional[str] = None,
    closedate: Optional[str] = None,
    hubspot_owner_id: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new deal in HubSpot.

    Args:
        dealname: Name of the deal
        amount: Deal amount
        dealstage: Deal stage
        pipeline: Deal pipeline
        closedate: Expected close date (YYYY-MM-DD)
        hubspot_owner_id: Deal owner ID
        description: Deal description

    Returns:
        Created deal information
    """
    client = HubSpotClient()
    properties = {
        "dealname": dealname,
    }
    if amount:
        properties["amount"] = amount
    if dealstage:
        properties["dealstage"] = dealstage
    if pipeline:
        properties["pipeline"] = pipeline
    if closedate:
        properties["closedate"] = closedate
    if hubspot_owner_id:
        properties["hubspot_owner_id"] = hubspot_owner_id
    if description:
        properties["description"] = description

    api_response = client.crm.deals.basic_api.create(properties)
    return HubSpotFormatter.format_single_deal(api_response)


def get_deal_by_name(deal_name: str) -> Optional[Dict[str, Any]]:
    """Get a specific deal by its exact name.

    Args:
        deal_name: Exact name of the deal to search for

    Returns:
        Deal information if found, None otherwise
    """
    client = HubSpotClient()
    api_response = client.crm.deals.basic_api.get_page(
        limit=1,
        properties=["dealname", "amount", "dealstage", "pipeline", "closedate"],
        filter_groups=[
            {
                "filters": [
                    {
                        "propertyName": "dealname",
                        "operator": "EQ",
                        "value": deal_name,
                    }
                ]
            }
        ],
        archived=False,
    )
    if not api_response.results:
        return None
    return HubSpotFormatter.format_single_deal(api_response.results[0])


def get_hubspot_deal_properties() -> List[Dict[str, Any]]:
    """Get the list of available properties for HubSpot deals.

    Returns:
        List of deal properties with their types and descriptions
    """
    client = HubSpotClient()
    api_response = client.crm.properties.core_api.get_all(
        object_type="deals",
        archived=False,
    )
    return HubSpotFormatter.format_deal_properties(api_response)


def update_deal(deal_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing deal in HubSpot.

    Args:
        deal_id: ID of the deal to update
        properties: Properties to update

    Returns:
        Updated deal information
    """
    client = HubSpotClient()
    api_response = client.crm.deals.basic_api.update(
        deal_id=deal_id,
        properties=properties,
    )
    return HubSpotFormatter.format_single_deal(api_response)
