#!/usr/bin/env python3
"""
Test script for HubSpot FastAgent SSE setup validation.

This script validates the configuration and connectivity before launching
the full FastAgent system.
"""

import asyncio
import sys
from pathlib import Path

import httpx
import yaml


def load_secrets() -> dict:
    """Load secrets from fastagent.secrets.yaml."""
    example_dir = Path(__file__).parent
    secrets_file = example_dir / "fastagent.secrets.yaml"

    if not secrets_file.exists():
        print("❌ fastagent.secrets.yaml not found")
        print("📝 Copy fastagent.secrets.example.yaml to fastagent.secrets.yaml")
        return {}

    try:
        with open(secrets_file) as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Failed to load secrets: {e}")
        return {}


def validate_secrets(secrets: dict) -> bool:
    """Validate required secrets."""
    required_keys = ["HUBSPOT_API_KEY", "MCP_AUTH_KEY"]
    missing_keys = []

    for key in required_keys:
        value = secrets.get(key, "").strip()
        if not value or value == f"your_{key.lower()}_here":
            missing_keys.append(key)

    if missing_keys:
        print(f"❌ Missing/invalid secrets: {', '.join(missing_keys)}")
        return False

    print("✅ All required secrets are configured")

    # Check optional FAISS security setting
    faiss_secure = secrets.get("FAISS_DATA_SECURE", "true").lower()
    if faiss_secure in ("false", "0", "no", "off"):
        print("⚠️ FAISS data endpoint will be unsecured (FAISS_DATA_SECURE=false)")
    else:
        print("🔒 FAISS data endpoint will be secured (default)")

    return True


async def test_hubspot_api(api_key: str) -> bool:
    """Test HubSpot API connectivity."""
    print("🔍 Testing HubSpot API connectivity...")

    headers = {"Authorization": f"Bearer {api_key}"}
    url = "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)

            if response.status_code == 200:
                print("✅ HubSpot API is accessible")
                return True
            else:
                print(f"❌ HubSpot API error: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False

    except Exception as e:
        print(f"❌ HubSpot API connection failed: {e}")
        return False


async def test_mcp_server_health(auth_key: str) -> bool:
    """Test MCP server health endpoint."""
    print("🏥 Testing MCP server health...")

    health_url = "http://localhost:8080/health"
    headers = {"X-API-Key": auth_key}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(health_url, headers=headers, timeout=5.0)

            if response.status_code == 200:
                data = response.json()
                print("✅ MCP server is healthy")
                print(f"   Server: {data.get('server', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(
                    f"   Auth: {'enabled' if data.get('auth_enabled') else 'disabled'}"
                )
                return True
            else:
                print(f"❌ MCP server health check failed: HTTP {response.status_code}")
                return False

    except httpx.ConnectError:
        print("❌ MCP server is not running or not accessible")
        print(
            "💡 Start it with: uv run hubspot-mcp-server --mode sse --port 8080 --auth-header"
        )
        return False
    except Exception as e:
        print(f"❌ MCP server health check failed: {e}")
        return False


async def test_sse_endpoint(auth_key: str) -> bool:
    """Test SSE endpoint accessibility."""
    print("📡 Testing SSE endpoint...")

    sse_url = "http://localhost:8080/sse"
    headers = {
        "X-API-Key": auth_key,
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    }

    try:
        async with httpx.AsyncClient() as client:
            # Just test if the endpoint is reachable (don't wait for actual stream)
            async with client.stream(
                "GET", sse_url, headers=headers, timeout=3.0
            ) as response:
                if response.status_code == 200:
                    print("✅ SSE endpoint is accessible")
                    return True
                else:
                    print(f"❌ SSE endpoint error: HTTP {response.status_code}")
                    return False

    except httpx.ReadTimeout:
        # Timeout is expected for SSE connections, means endpoint is working
        print("✅ SSE endpoint is accessible (timeout is normal)")
        return True
    except httpx.ConnectError:
        print("❌ SSE endpoint is not accessible")
        return False
    except Exception as e:
        print(f"❌ SSE endpoint test failed: {e}")
        return False


def validate_config() -> bool:
    """Validate fastagent.config.yaml."""
    print("⚙️ Validating FastAgent configuration...")

    example_dir = Path(__file__).parent
    config_file = example_dir / "fastagent.config.yaml"

    if not config_file.exists():
        print("❌ fastagent.config.yaml not found")
        return False

    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)

        # Basic validation
        if "mcp" not in config:
            print("❌ MCP configuration missing")
            return False

        servers = config.get("mcp", {}).get("servers", {})
        if "hubspot-sse" not in servers:
            print("❌ hubspot-sse server configuration missing")
            return False

        sse_config = servers["hubspot-sse"]
        if "transport" not in sse_config:
            print("❌ Transport configuration missing")
            return False

        transport = sse_config["transport"]
        if transport.get("type") != "sse":
            print("❌ Transport type should be 'sse'")
            return False

        if "http://localhost:8080/sse" not in transport.get("url", ""):
            print("⚠️ URL might not be correct for local testing")

        print("✅ FastAgent configuration looks good")
        return True

    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


async def main():
    """Run the main test function."""
    print("🧪 HubSpot FastAgent SSE Setup Test")
    print("=" * 50)

    # Load secrets
    secrets = load_secrets()
    if not secrets:
        sys.exit(1)

    # Validate secrets
    if not validate_secrets(secrets):
        sys.exit(1)

    # Validate configuration
    if not validate_config():
        sys.exit(1)

    # Test HubSpot API
    if not await test_hubspot_api(secrets["HUBSPOT_API_KEY"]):
        print("⚠️ HubSpot API test failed - check your API key")
        # Don't exit here as MCP server might still work

    # Test MCP server
    if not await test_mcp_server_health(secrets["MCP_AUTH_KEY"]):
        print("\n💡 Make sure to start the MCP server first:")
        print("   export HUBSPOT_API_KEY='your_key'")
        print("   export MCP_AUTH_KEY='your_auth_key'")
        print("   uv run hubspot-mcp-server --mode sse --port 8080 --auth-header")
        sys.exit(1)

    # Test SSE endpoint
    if not await test_sse_endpoint(secrets["MCP_AUTH_KEY"]):
        sys.exit(1)

    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your setup is ready.")
    print("🚀 You can now run: uv run agent.py")
    print("   Or use the launcher: uv run launch.py")
    print("=" * 50)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        sys.exit(1)
