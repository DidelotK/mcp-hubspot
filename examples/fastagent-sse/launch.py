#!/usr/bin/env python3
"""
Launch script for HubSpot FastAgent SSE Example.

This script helps coordinate the startup of both the MCP server in SSE mode
and the FastAgent client, with proper error handling and logging.
"""

import asyncio
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import httpx
import yaml


class SSELauncher:
    """Launcher for HubSpot FastAgent SSE setup."""

    def __init__(self):
        """Initialize the SSE launcher with project paths."""
        self.server_process: Optional[subprocess.Popen] = None
        self.project_root = Path(__file__).parent.parent.parent
        self.example_dir = Path(__file__).parent

    def load_secrets(self) -> dict:
        """Load secrets from fastagent.secrets.yaml."""
        secrets_file = self.example_dir / "fastagent.secrets.yaml"

        if not secrets_file.exists():
            print(f"❌ Secrets file not found: {secrets_file}")
            print(
                "📝 Please copy fastagent.secrets.example.yaml to fastagent.secrets.yaml"
            )
            print("   and fill in your actual values.")
            sys.exit(1)

        try:
            with open(secrets_file) as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load secrets: {e}")
            sys.exit(1)

    def validate_secrets(self, secrets: dict) -> None:
        """Validate that required secrets are present."""
        required_keys = ["HUBSPOT_API_KEY", "MCP_AUTH_KEY"]
        missing_keys = []

        for key in required_keys:
            value = secrets.get(key, "").strip()
            if not value or value == f"your_{key.lower()}_here":
                missing_keys.append(key)

        if missing_keys:
            print(f"❌ Missing or invalid secrets: {', '.join(missing_keys)}")
            print(
                "📝 Please update your fastagent.secrets.yaml file with actual values."
            )
            sys.exit(1)

    async def check_server_health(self, auth_key: str, max_attempts: int = 30) -> bool:
        """Check if the MCP server is running and healthy."""
        health_url = "http://localhost:8080/health"
        headers = {"X-API-Key": auth_key}

        async with httpx.AsyncClient() as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.get(
                        health_url, headers=headers, timeout=2.0
                    )
                    if response.status_code == 200:
                        return True
                except Exception:
                    pass  # Server not ready yet

                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)

        return False

    def start_mcp_server(self, secrets: dict) -> subprocess.Popen:
        """Start the MCP server in SSE mode."""
        print("🚀 Starting HubSpot MCP Server in SSE mode...")

        # Prepare environment
        env = os.environ.copy()
        env.update(
            {
                "HUBSPOT_API_KEY": secrets["HUBSPOT_API_KEY"],
                "MCP_AUTH_KEY": secrets["MCP_AUTH_KEY"],
                "HUBSPOT_API_URL": secrets.get(
                    "HUBSPOT_API_URL", "https://api.hubapi.com"
                ),
                "FAISS_DATA_SECURE": secrets.get("FAISS_DATA_SECURE", "true"),
            }
        )

        # Start server process
        cmd = [
            "uv",
            "run",
            "hubspot-mcp-server",
            "--mode",
            "sse",
            "--port",
            "8080",
            "--auth-header",
        ]

        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.server_process = process
            return process
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            sys.exit(1)

    def start_fastagent(self) -> subprocess.Popen:
        """Start the FastAgent client."""
        print("🤖 Starting FastAgent client...")

        cmd = ["uv", "run", "agent.py"]

        try:
            return subprocess.Popen(cmd, cwd=self.example_dir, text=True)
        except Exception as e:
            print(f"❌ Failed to start FastAgent: {e}")
            sys.exit(1)

    def cleanup(self) -> None:
        """Clean up processes on exit."""
        if self.server_process:
            print("\n🛑 Stopping MCP server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()

    def signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        print(f"\n📡 Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)

    async def run(self) -> None:
        """Execute the main run method."""
        print("🎯 HubSpot FastAgent SSE Launcher")
        print("=" * 50)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Load and validate configuration
        secrets = self.load_secrets()
        self.validate_secrets(secrets)

        print("✅ Configuration loaded successfully")

        # Start MCP server
        server_process = self.start_mcp_server(secrets)

        # Wait for server to be ready
        print("⏳ Waiting for MCP server to be ready...")
        if not await self.check_server_health(secrets["MCP_AUTH_KEY"]):
            print("❌ MCP server failed to start or is not healthy")
            self.cleanup()
            sys.exit(1)

        print("✅ MCP server is running and healthy")

        # Start FastAgent
        agent_process = self.start_fastagent()

        print("✅ FastAgent started successfully")
        print("\n" + "=" * 50)
        print("🎉 Setup complete! Both services are running.")
        print("💡 You can now interact with FastAgent to access your HubSpot CRM.")
        print("🛑 Press Ctrl+C to stop all services.")
        print("=" * 50)

        # Wait for processes
        try:
            # Monitor both processes
            while True:
                # Check if server is still running
                if server_process.poll() is not None:
                    print("❌ MCP server has stopped unexpectedly")
                    break

                # Check if agent is still running
                if agent_process.poll() is not None:
                    print("ℹ️ FastAgent has exited")
                    break

                await asyncio.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        finally:
            self.cleanup()
            if agent_process.poll() is None:
                agent_process.terminate()


def main():
    """Run the main entry point."""
    launcher = SSELauncher()

    try:
        asyncio.run(launcher.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
