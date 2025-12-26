"""HTTP server for MCP dossier service."""

import asyncio
import json
from typing import Any

from aiohttp import web

from dossier.mcp_server import MCPServer


class MCPHTTPServer:
    """HTTP wrapper for MCP server."""

    def __init__(self, host: str = "localhost", port: int = 7331) -> None:
        """Initialize HTTP server."""
        self.host = host
        self.port = port
        self.mcp_server = MCPServer()
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup HTTP routes."""
        self.app.router.add_post("/mcp", self.handle_mcp_request)
        self.app.router.add_get("/health", self.health_check)

    async def handle_mcp_request(self, request: web.Request) -> web.Response:
        """Handle MCP request via HTTP."""
        try:
            data = await request.json()
            response = await self.mcp_server.handle_request(data)
            return web.json_response(response)
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({"status": "ok"})

    async def run(self) -> None:
        """Run the HTTP server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"MCP HTTP Server running on http://{self.host}:{self.port}")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            await runner.cleanup()


async def main() -> None:
    """Main entry point for HTTP server."""
    server = MCPHTTPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
