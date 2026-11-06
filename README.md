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
