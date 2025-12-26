"""MCP (Model Context Protocol) server for dossier management."""

import asyncio
import json
import sys
from typing import Any

from dossier.database import DossierDatabase
from dossier.json_merge_patch import merge_patch
from dossier.models import Dossier


class MCPServer:
    """MCP server for dossier operations."""

    def __init__(self) -> None:
        """Initialize MCP server."""
        self.db = DossierDatabase()
        self.tools = {
            "dossier_update": self._dossier_update,
            "dossier_get": self._dossier_get,
            "dossier_create": self._dossier_create,
            "dossier_delete": self._dossier_delete,
            "dossier_list": self._dossier_list,
        }
        self.resources = {
            "dossier": self._get_dossier_resource,
        }

    async def _dossier_update(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Apply a JSON Merge Patch to the dossier and persist it.

        Args:
            params: Dictionary containing 'dossier_id' and 'patch'

        Returns:
            Updated dossier data

        """
        dossier_id = params.get("dossier_id")
        patch = params.get("patch", {})

        if not dossier_id:
            return {"error": "dossier_id is required"}

        dossier = self.db.get(dossier_id)
        if not dossier:
            return {"error": f"Dossier with id {dossier_id} not found"}

        # Apply JSON Merge Patch
        updated_data = merge_patch(dossier.data, patch)

        # Update in database
        updated_dossier = self.db.update(dossier_id, updated_data)

        if updated_dossier:
            return {
                "success": True,
                "dossier": updated_dossier.to_dict(),
            }
        return {"error": "Failed to update dossier"}

    async def _dossier_get(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get a dossier by ID."""
        dossier_id = params.get("dossier_id")
        if not dossier_id:
            return {"error": "dossier_id is required"}

        dossier = self.db.get(dossier_id)
        if dossier:
            return {"success": True, "dossier": dossier.to_dict()}
        return {"error": f"Dossier with id {dossier_id} not found"}

    async def _dossier_create(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new dossier."""
        dossier_id = params.get("dossier_id")
        player_name = params.get("player_name")
        data = params.get("data", {})

        if not dossier_id or not player_name:
            return {"error": "dossier_id and player_name are required"}

        dossier = Dossier(id=dossier_id, player_name=player_name, data=data)
        created_dossier = self.db.create(dossier)
        return {"success": True, "dossier": created_dossier.to_dict()}

    async def _dossier_delete(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete a dossier."""
        dossier_id = params.get("dossier_id")
        if not dossier_id:
            return {"error": "dossier_id is required"}

        success = self.db.delete(dossier_id)
        if success:
            return {"success": True, "message": f"Dossier {dossier_id} deleted"}
        return {"error": f"Dossier with id {dossier_id} not found"}

    async def _dossier_list(self, _params: dict[str, Any]) -> dict[str, Any]:
        """List all dossiers."""
        dossiers = self.db.list_all()
        return {
            "success": True,
            "dossiers": [d.to_dict() for d in dossiers],
        }

    async def _get_dossier_resource(self, uri: str) -> dict[str, Any]:
        """Get a dossier resource by URI."""
        # URI format: dossier://<dossier_id>
        if uri.startswith("dossier://"):
            dossier_id = uri[10:]
            dossier = self.db.get(dossier_id)
            if dossier:
                return {"success": True, "resource": dossier.to_dict()}
        return {"error": "Resource not found"}

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Handle incoming MCP request."""
        method = request.get("method")
        params = request.get("params", {})

        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": "dossier_update",
                        "description": "Apply a JSON Merge Patch to the dossier and persist it.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dossier_id": {"type": "string"},
                                "patch": {"type": "object"},
                            },
                            "required": ["dossier_id", "patch"],
                        },
                    },
                    {
                        "name": "dossier_get",
                        "description": "Get a dossier by ID",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dossier_id": {"type": "string"},
                            },
                            "required": ["dossier_id"],
                        },
                    },
                    {
                        "name": "dossier_create",
                        "description": "Create a new dossier",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dossier_id": {"type": "string"},
                                "player_name": {"type": "string"},
                                "data": {"type": "object"},
                            },
                            "required": ["dossier_id", "player_name"],
                        },
                    },
                    {
                        "name": "dossier_delete",
                        "description": "Delete a dossier",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dossier_id": {"type": "string"},
                            },
                            "required": ["dossier_id"],
                        },
                    },
                    {
                        "name": "dossier_list",
                        "description": "List all dossiers",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                        },
                    },
                ],
            }

        if method == "resources/list":
            return {
                "resources": [
                    {
                        "uri": "dossier://*",
                        "name": "Dossier Resource",
                        "description": "Access dossier data by URI",
                    },
                ],
            }

        if method == "tools/call":
            tool_name = params.get("name")
            tool_params = params.get("arguments", {})

            if tool_name in self.tools:
                result = await self.tools[tool_name](tool_params)
                return {"content": [{"type": "text", "text": json.dumps(result)}]}
            return {"error": f"Unknown tool: {tool_name}"}

        if method == "resources/read":
            uri = params.get("uri")
            result = await self._get_dossier_resource(uri)
            return {
                "contents": [
                    {"uri": uri, "mimeType": "application/json", "text": json.dumps(result)},
                ],
            }

        return {"error": f"Unknown method: {method}"}

    async def run_stdio(self) -> None:
        """Run server in stdio mode."""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                request = json.loads(line)
                response = await self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON"}), flush=True)
            except Exception as e:
                print(json.dumps({"error": str(e)}), flush=True)


async def main() -> None:
    """Run the MCP server."""
    server = MCPServer()
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
