# Poker Therapist - Dossier MCP Server (Therapy Context)

This module implements a Model Context Protocol (MCP) server for managing personal therapy dossiers—the psychiatrist's information on the subject—capturing emotions, feelings, situations, and biographical context, with PostgreSQL storage for persistent recall.

## Features

- **Dossier Management**: Create, read, update, and delete therapy dossiers centered on emotions, feelings, situations, and personal bio data
- **JSON Merge Patch**: Apply RFC 7396 JSON Merge Patch for flexible updates
- **PostgreSQL Storage**: Persistent storage with JSONB support
- **Dual Protocol Support**: Both stdio and HTTP server modes
- **MCP Compliant**: Full MCP protocol implementation with tools and resources

## Architecture

### Components

1. **Models** (`models.py`): Data model for dossier objects
2. **Database** (`database.py`): PostgreSQL operations and schema management
3. **JSON Merge Patch** (`json_merge_patch.py`): RFC 7396 implementation
4. **MCP Server** (`mcp_server.py`): stdio-based MCP server
5. **HTTP Server** (`http_server.py`): HTTP wrapper for MCP server

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL 12+

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Configure database:
```bash
cp .env.example .env
# Edit .env with your PostgreSQL connection string
```

3. The database tables will be created automatically on first run.

## Usage

### Stdio Mode

Run the MCP server in stdio mode:

```bash
python -m dossier.mcp_server
```

Configure in your MCP client with `mcp_config_stdio.json`:

```json
{
  "mcpServers": {
    "dossier": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "dossier.mcp_server"],
      "env": {
        "DATABASE_URL": "postgresql://localhost:5432/poker_therapist"
      }
    }
  }
}
```

### HTTP Mode

Run the HTTP server:

```bash
python -m dossier.http_server
```

Configure in your MCP client with `mcp_config_http.json`:

```json
{
  "mcpServers": {
    "dossier": {
      "type": "http",
      "url": "http://localhost:7331/mcp"
    }
  }
}
```

## Available Tools

### dossier_update

Apply a JSON Merge Patch to a dossier and persist it.

**Parameters:**
- `dossier_id` (string, required): The ID of the dossier to update
- `patch` (object, required): The JSON Merge Patch to apply

**Example:**
```json
{
  "name": "dossier_update",
  "arguments": {
    "dossier_id": "player123",
    "patch": {
      "stats": {
        "wins": 10,
        "losses": 5
      }
    }
  }
}
```

### dossier_get

Retrieve a dossier by ID.

**Parameters:**
- `dossier_id` (string, required): The ID of the dossier to retrieve

### dossier_create

Create a new dossier.

**Parameters:**
- `dossier_id` (string, required): The ID for the new dossier
- `player_name` (string, required): The name of the player
- `data` (object, optional): Initial data for the dossier

### dossier_delete

Delete a dossier.

**Parameters:**
- `dossier_id` (string, required): The ID of the dossier to delete

### dossier_list

List all dossiers.

**Parameters:** None

## Resources

The server exposes dossier resources via URIs:

- `dossier://<dossier_id>`: Access a specific therapy dossier (emotions, feelings, situations)

## Database Schema

```sql
CREATE TABLE dossiers (
    id VARCHAR(255) PRIMARY KEY,
    player_name VARCHAR(255) NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

## JSON Merge Patch

The `dossier_update` tool uses JSON Merge Patch (RFC 7396) for flexible updates:

- Set or update fields: `{"field": "value"}`
- Delete fields: `{"field": null}`
- Nested updates: `{"parent": {"child": "value"}}`

**Example:**
```json
{
  "stats": {
    "wins": 10
  },
  "notes": null
}
```

This will:
- Set or update `stats.wins` to 10
- Delete the `notes` field

## Development

### Running Tests

```bash
pytest tests/
```

### Type Checking

```bash
mypy dossier/
```

### Linting

```bash
ruff check dossier/
```

## License

See LICENSE file in the repository root.
