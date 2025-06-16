#!/usr/bin/env python3
"""Test script for the force reindex endpoint."""

import asyncio
import json
import os
import sys
import time

import httpx


async def test_force_reindex_endpoint():
    """Test the force reindex endpoint."""
    # Configuration
    base_url = os.getenv("MCP_SERVER_URL", "http://localhost:8080")
    auth_key = os.getenv("MCP_AUTH_KEY")

    # Prepare headers
    headers = {"Content-Type": "application/json"}
    if auth_key:
        headers["Authorization"] = f"Bearer {auth_key}"

    print("🧪 Testing Force Reindex Endpoint")
    print(f"📡 Server URL: {base_url}")
    print(f"🔐 Auth: {'Enabled' if auth_key else 'Disabled'}")
    print("-" * 50)

    async with httpx.AsyncClient(timeout=600.0) as client:  # 10 minute timeout
        try:
            # Test health check first
            print("1️⃣ Testing health check...")
            health_response = await client.get(f"{base_url}/health")

            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"✅ Health check passed: {health_data.get('status')}")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                return False

            # Test readiness check
            print("2️⃣ Testing readiness check...")
            ready_response = await client.get(f"{base_url}/ready")

            if ready_response.status_code == 200:
                ready_data = ready_response.json()
                print(f"✅ Readiness check passed: {ready_data.get('status')}")
            else:
                print(f"❌ Readiness check failed: {ready_response.status_code}")
                return False

            # Test force reindex endpoint
            print("3️⃣ Testing force reindex endpoint...")
            print("⏳ This may take several minutes...")

            start_time = time.time()

            reindex_response = await client.post(
                f"{base_url}/force-reindex", headers=headers
            )

            end_time = time.time()
            duration = end_time - start_time

            print(f"⏱️ Request completed in {duration:.1f} seconds")

            if reindex_response.status_code == 200:
                reindex_data = reindex_response.json()

                print("✅ Force reindex completed successfully!")
                print("-" * 50)

                # Display results
                print("📊 Results Summary:")
                summary = reindex_data.get("summary", {})
                print(
                    f"  • Total entity types: {summary.get('total_entity_types_processed', 0)}"
                )
                print(
                    f"  • Successful types: {summary.get('successful_entity_types', 0)}"
                )
                print(f"  • Failed types: {summary.get('failed_entity_types', 0)}")
                print(
                    f"  • Total entities loaded: {summary.get('total_entities_loaded', 0)}"
                )
                print(f"  • Embeddings ready: {summary.get('embeddings_ready', False)}")
                print(
                    f"  • Semantic search available: {summary.get('semantic_search_available', False)}"
                )

                print("\n📝 Process Log:")
                for log_entry in reindex_data.get("process_log", []):
                    print(f"  {log_entry}")

                print("\n🏷️ Entity Results:")
                for entity_type, result in reindex_data.get(
                    "entity_results", {}
                ).items():
                    status = result.get("status", "unknown")
                    if status == "success":
                        entities_loaded = result.get("entities_loaded", 0)
                        embeddings_built = result.get("embeddings_built", False)
                        print(
                            f"  • {entity_type}: ✅ {entities_loaded} entities ({'🧠 with embeddings' if embeddings_built else '❌ no embeddings'})"
                        )
                    else:
                        error = result.get("error", "Unknown error")
                        print(f"  • {entity_type}: ❌ Failed - {error}")

                # Display final stats
                final_stats = reindex_data.get("final_stats", {})
                if final_stats:
                    print("\n📈 Final FAISS Stats:")
                    print(f"  • Status: {final_stats.get('status', 'unknown')}")
                    print(f"  • Total entities: {final_stats.get('total_entities', 0)}")
                    print(
                        f"  • Vector dimension: {final_stats.get('dimension', 'N/A')}"
                    )
                    print(f"  • Index type: {final_stats.get('index_type', 'N/A')}")
                    print(f"  • Model: {final_stats.get('model_name', 'N/A')}")

                return True

            else:
                print(f"❌ Force reindex failed: {reindex_response.status_code}")
                try:
                    error_data = reindex_response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except Exception:
                    print(f"Error text: {reindex_response.text}")
                return False

        except httpx.ConnectError:
            print(f"❌ Cannot connect to server at {base_url}")
            print("💡 Make sure the MCP server is running in SSE mode:")
            print("   python -m hubspot_mcp --mode sse --port 8080")
            return False
        except httpx.TimeoutException:
            print("❌ Request timed out (10 minutes)")
            print("💡 The reindexing process may still be running on the server")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False


def main():
    """Run the force reindex test."""
    print("🚀 HubSpot MCP Force Reindex Test")
    print("=" * 50)

    # Check environment variables
    if not os.getenv("HUBSPOT_API_KEY"):
        print("⚠️  Warning: HUBSPOT_API_KEY not set - reindexing may fail")

    # Run the test
    success = asyncio.run(test_force_reindex_endpoint())

    if success:
        print("\n🎉 All tests passed!")
        print("💡 Your HubSpot data is now indexed and ready for semantic search!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        print("💡 Check the server logs for more details")
        sys.exit(1)


if __name__ == "__main__":
    main()
