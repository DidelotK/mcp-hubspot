#!/usr/bin/env python3
"""
Clear and Reindex HubSpot Data.

This script demonstrates how to clear and reindex HubSpot data using the
SSE server HTTP endpoints.

Usage:
    python clear_and_reindex.py --server-url http://localhost:8080 [--auth-key YOUR_AUTH_KEY]

Environment variables:
    SSE_SERVER_URL: URL of the SSE server (default: http://localhost:8080)
    SSE_AUTH_KEY: Authentication key for the SSE server (optional)
    DATA_PROTECTION_DISABLED: Set to true to disable authentication requirements
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Optional

import aiohttp


class HubSpotDataManager:
    """Manager for clearing and reindexing HubSpot data."""

    def __init__(self, server_url: str, auth_key: Optional[str] = None):
        """
        Initialize the data manager.

        Args:
            server_url: Base URL of the SSE server
            auth_key: Optional authentication key
        """
        self.server_url = server_url.rstrip("/")
        self.auth_key = auth_key
        self.headers = {}

        if self.auth_key:
            self.headers["X-API-Key"] = self.auth_key

    async def check_server_health(self) -> bool:
        """
        Check if the SSE server is healthy and reachable.

        Returns:
            bool: True if server is healthy, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Server is healthy: {data}")
                        return True
                    else:
                        print(f"❌ Server health check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False

    async def check_server_readiness(self) -> bool:
        """
        Check if the SSE server is ready to process requests.

        Returns:
            bool: True if server is ready, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/ready") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Server is ready: {data}")
                        return True
                    else:
                        print(f"❌ Server readiness check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Failed to check server readiness: {e}")
            return False

    async def get_current_faiss_data(self) -> Optional[dict]:
        """
        Get current FAISS index data and statistics.

        Returns:
            dict: Current FAISS data or None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.server_url}/faiss-data", headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"📊 Current FAISS data: {json.dumps(data, indent=2)}")
                        return data
                    else:
                        print(f"⚠️ Failed to get FAISS data: {response.status}")
                        if response.status == 401:
                            print(
                                "❌ Authentication required. Check your auth key or set DATA_PROTECTION_DISABLED=true"
                            )
                        return None
        except Exception as e:
            print(f"❌ Failed to get FAISS data: {e}")
            return None

    async def force_reindex(self) -> bool:
        """
        Force complete reindexing of all HubSpot data.

        Returns:
            bool: True if reindexing succeeded, False otherwise
        """
        print("🔄 Starting force reindex process...")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.server_url}/force-reindex", headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ Force reindex completed successfully!")

                        # Display process log
                        if "process_log" in data:
                            print("\n📋 Process Log:")
                            for log_entry in data["process_log"]:
                                print(f"  {log_entry}")

                        # Display summary
                        if "summary" in data:
                            summary = data["summary"]
                            print(f"\n📈 Summary:")
                            print(
                                f"  • Entity types processed: {summary.get('total_entity_types', 0)}"
                            )
                            print(
                                f"  • Successful types: {summary.get('successful_entity_types', 0)}"
                            )
                            print(
                                f"  • Total entities loaded: {summary.get('total_entities_loaded', 0)}"
                            )
                            print(
                                f"  • Embeddings ready: {summary.get('embeddings_ready', False)}"
                            )
                            print(
                                f"  • Semantic search available: {summary.get('semantic_search_available', False)}"
                            )

                        # Display entity results
                        if "entity_results" in data:
                            print(f"\n🏢 Entity Results:")
                            for entity_type, result in data["entity_results"].items():
                                status = result.get("status", "unknown")
                                if status == "success":
                                    count = result.get("entities_loaded", 0)
                                    embeddings = (
                                        "✅"
                                        if result.get("embeddings_built", False)
                                        else "❌"
                                    )
                                    print(
                                        f"  • {entity_type}: {count} entities loaded, embeddings: {embeddings}"
                                    )
                                else:
                                    error = result.get("error", "unknown error")
                                    print(f"  • {entity_type}: ❌ {error}")

                        return True
                    else:
                        print(f"❌ Force reindex failed: {response.status}")
                        if response.status == 401:
                            print(
                                "❌ Authentication required. Check your auth key or set DATA_PROTECTION_DISABLED=true"
                            )
                        elif response.status == 500:
                            try:
                                error_data = await response.json()
                                print(
                                    f"❌ Server error: {error_data.get('message', 'Unknown error')}"
                                )
                                if "process_log" in error_data:
                                    print("\n📋 Error Log:")
                                    for log_entry in error_data["process_log"]:
                                        print(f"  {log_entry}")
                            except Exception:
                                text = await response.text()
                                print(f"❌ Server error: {text}")
                        return False
        except Exception as e:
            print(f"❌ Failed to force reindex: {e}")
            return False

    async def clear_and_reindex(self) -> bool:
        """
        Complete workflow: check server, get current data, and reindex.

        Returns:
            bool: True if successful, False otherwise
        """
        print("🚀 Starting HubSpot data clear and reindex process")
        print("=" * 60)

        # Step 1: Check server health
        print("\n1️⃣ Checking server health...")
        if not await self.check_server_health():
            return False

        # Step 2: Check server readiness
        print("\n2️⃣ Checking server readiness...")
        if not await self.check_server_readiness():
            return False

        # Step 3: Get current data (optional, for info)
        print("\n3️⃣ Getting current FAISS data...")
        await self.get_current_faiss_data()

        # Step 4: Force reindex (this includes clearing)
        print("\n4️⃣ Force reindexing all data...")
        success = await self.force_reindex()

        if success:
            print("\n🎉 Clear and reindex process completed successfully!")
            print("\n5️⃣ Verifying final state...")
            await self.get_current_faiss_data()
        else:
            print("\n❌ Clear and reindex process failed!")

        return success


def main():
    """Run the main entry point."""
    parser = argparse.ArgumentParser(
        description="Clear and reindex HubSpot data through SSE server endpoints"
    )
    parser.add_argument(
        "--server-url",
        default=os.getenv("SSE_SERVER_URL", "http://localhost:8080"),
        help="SSE server URL (default: http://localhost:8080 or SSE_SERVER_URL env var)",
    )
    parser.add_argument(
        "--auth-key",
        default=os.getenv("SSE_AUTH_KEY"),
        help="Authentication key (optional, or use SSE_AUTH_KEY env var)",
    )

    args = parser.parse_args()

    print("🔧 HubSpot Data Clear and Reindex Tool")
    print("=" * 50)
    print(f"Server URL: {args.server_url}")
    print(f"Auth Key: {'✅ Provided' if args.auth_key else '❌ Not provided'}")

    # Check environment variables
    data_protection_disabled = (
        os.getenv("DATA_PROTECTION_DISABLED", "false").lower() == "true"
    )
    if data_protection_disabled:
        print("🔓 Data protection is disabled - authentication not required")
    elif not args.auth_key:
        print("⚠️ No auth key provided - some endpoints may require authentication")

    # Create manager and run
    manager = HubSpotDataManager(args.server_url, args.auth_key)

    try:
        success = asyncio.run(manager.clear_and_reindex())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
