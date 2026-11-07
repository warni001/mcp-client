# mcp-client

A generic MCP (Model Context Protocol) client CLI. Connect to any MCP
server — stdio or Streamable HTTP — list its tools, or call one tool
and get the JSON result back.

Built so an AI agent (or a human) without a native MCP client can still
use any MCP server's tools.

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

List tools on a stdio server:

```bash
.venv/bin/python mcp_call.py --server-cmd "uvx agent-harnesses-mcp" --list-tools
```

Call a tool:

```bash
.venv/bin/python mcp_call.py --server-cmd "uvx agent-harnesses-mcp" \
    --tool recommend --args '{"need": "a turnkey coding agent for Python work"}'
```

Streamable HTTP server:

```bash
.venv/bin/python mcp_call.py --server-url http://127.0.0.1:8000/mcp --list-tools
```

Pass environment variables to a stdio server:

```bash
.venv/bin/python mcp_call.py --server-cmd "my-server" --env API_KEY=xxx --list-tools
```

Pass headers to an HTTP server:

```bash
.venv/bin/python mcp_call.py --server-url https://example.com/mcp \
    --header "Authorization: Bearer TOKEN" --list-tools
```

## Notes

- Each invocation starts a fresh server process (stdio) or connection
  (HTTP). There is no persistent session.
- The server command must be on PATH or absolute. `uvx` works if `uv`
  is installed; otherwise install the server package with pip and call
  its console script directly.
- Output is JSON on stdout; errors go to stderr with a non-zero exit.

## Established alternatives

This is a small learning exercise, not a novel tool. If you want a
maintained generic MCP client, use one of these instead:

- **MCP Inspector** (official, `@modelcontextprotocol/inspector`) — the
  canonical client, with a scriptable CLI mode:
  `npx @modelcontextprotocol/inspector --cli <server> --method tools/list --format json`
  and `--method tools/call --tool-name <name> --tool-arg k=v`.
- **mcp-cli** (philschmid/mcp-cli) — a standalone binary built
  specifically for coding agents to call MCP servers:
  `mcp-cli call <server> <tool> '<json>'`.
- **cli-mcp** (PyPI) — minimal Python client, reads a Cursor `mcp.json`:
  `uvx cli-mcp call <server> <tool> '<json>'`.
- **call-mcp** (npm) — config-file based, JSON on stdout.
