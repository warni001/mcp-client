#!/usr/bin/env python3
"""Generic MCP client for Muse.

Connects to any MCP server (stdio or Streamable HTTP), lists its tools,
or calls one tool and prints the JSON result.

Usage:
    # List tools on a stdio server
    mcp_call.py --server-cmd "uvx agent-harnesses-mcp" --list-tools

    # Call a tool
    mcp_call.py --server-cmd "uvx agent-harnesses-mcp" \\
        --tool recommend --args '{"query": "best coding agent"}'

    # Streamable HTTP server
    mcp_call.py --server-url http://127.0.0.1:8000/mcp --list-tools

    # Pass environment variables to the server
    mcp_call.py --server-cmd "my-server" --env KEY=VALUE --list-tools

Each invocation starts a fresh server process (stdio) or connection
(HTTP). For stdio servers the command must be on PATH or absolute.
"""

import argparse
import asyncio
import json
import sys

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client


def _parse_server_cmd(cmd: str) -> tuple[str, list[str]]:
    """Split a server command string into program + args (no shell)."""
    parts = cmd.split()
    if not parts:
        raise ValueError("empty --server-cmd")
    return parts[0], parts[1:]


def _parse_env(pairs: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for pair in pairs:
        key, _, value = pair.partition("=")
        if not key:
            raise ValueError(f"bad --env entry: {pair!r}")
        env[key] = value
    return env


async def _run_stdio(
    cmd: str, env: dict[str, str], tool: str | None, args: dict
) -> dict:
    program, argv = _parse_server_cmd(cmd)
    params = StdioServerParameters(
        command=program, args=argv, env={**__import__("os").environ, **env} if env else None
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await _dispatch(session, tool, args)


async def _run_http(
    url: str, headers: dict[str, str], tool: str | None, args: dict
) -> dict:
    async with streamablehttp_client(url, headers=headers or None) as (
        read,
        write,
        _get_session_id,
    ):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await _dispatch(session, tool, args)


async def _dispatch(session: ClientSession, tool: str | None, args: dict) -> dict:
    if tool is None:
        result = await session.list_tools()
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema,
                }
                for t in result.tools
            ]
        }
    result = await session.call_tool(tool, args)
    return {
        "tool": tool,
        "isError": result.isError,
        "content": [
            {"type": c.type, **{k: v for k, v in vars(c).items() if k != "type"}}
            for c in result.content
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--server-cmd", help="stdio server command, e.g. 'uvx agent-harnesses-mcp'")
    group.add_argument("--server-url", help="Streamable HTTP server URL")
    parser.add_argument("--list-tools", action="store_true", help="list tools and exit")
    parser.add_argument("--tool", help="tool name to call")
    parser.add_argument("--args", default="{}", help="JSON arguments for --tool")
    parser.add_argument("--env", action="append", default=[], help="KEY=VALUE passed to a stdio server")
    parser.add_argument("--header", action="append", default=[], help="Header: value for an HTTP server")
    opts = parser.parse_args()

    if not opts.list_tools and not opts.tool:
        parser.error("need --list-tools or --tool")
    if opts.tool and opts.list_tools:
        parser.error("--list-tools and --tool are mutually exclusive")

    try:
        args = json.loads(opts.args)
    except json.JSONDecodeError as exc:
        print(f"bad --args JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(args, dict):
        print("--args must be a JSON object", file=sys.stderr)
        return 2

    headers = dict(h.split(":", 1) for h in (x.strip() for x in opts.header))
    headers = {k.strip(): v.strip() for k, v in headers.items()}

    try:
        if opts.server_cmd:
            result = asyncio.run(
                _run_stdio(opts.server_cmd, _parse_env(opts.env), opts.tool, args)
            )
        else:
            result = asyncio.run(
                _run_http(opts.server_url, headers, opts.tool, args)
            )
    except Exception as exc:  # noqa: BLE001 - surface any connect/call failure
        print(f"mcp error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
