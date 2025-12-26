"""Run MCP server in stdio mode."""

import asyncio

from dossier.mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())
