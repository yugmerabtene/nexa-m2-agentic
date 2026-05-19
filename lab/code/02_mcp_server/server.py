"""MCP Server — expose tools and resources to opencode agents."""

import subprocess
from mcp.server import Server
from mcp.types import Tool, Resource, TextContent

app = Server("dev-assistant")


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="read_file",
            description="Read a file from disk",
            inputSchema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        ),
        Tool(
            name="search_code",
            description="Search for patterns in code",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string", "default": "."},
                },
                "required": ["pattern"],
            },
        ),
        Tool(
            name="run_python",
            description="Execute Python code safely",
            inputSchema={
                "type": "object",
                "properties": {"code": {"type": "string"}},
                "required": ["code"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "read_file":
        with open(arguments["path"]) as f:
            return [TextContent(type="text", text=f.read())]
    elif name == "search_code":
        result = subprocess.run(
            ["grep", "-rn", arguments["pattern"], arguments.get("path", ".")],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return [
            TextContent(
                type="text", text=result.stdout[:3000] or "No matches"
            )
        ]
    elif name == "run_python":
        result = subprocess.run(
            ["python3", "-c", arguments["code"]],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return [
            TextContent(
                type="text", text=result.stdout + result.stderr
            )
        ]
    raise ValueError(f"Unknown tool: {name}")


@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="docs://agent-patterns",
            name="Agent Design Patterns",
            description="Common agent architecture patterns",
        ),
        Resource(
            uri="docs://mcp-guide",
            name="MCP Quick Reference",
            description="MCP protocol summary",
        ),
    ]


@app.read_resource()
async def read_resource(uri: str):
    docs = {
        "docs://agent-patterns": (
            "# Patterns\n1. ReAct Loop\n2. Plan-Execute\n"
            "3. Supervisor\n4. Reflection\n5. Tool-use"
        ),
        "docs://mcp-guide": (
            "# MCP\n- JSON-RPC 2.0\n"
            "- Primitives: Tools, Resources, Prompts\n"
            "- Transports: stdio, HTTP+SSE"
        ),
    }
    return TextContent(type="text", text=docs.get(uri, ""))


if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import anyio

    anyio.run(stdio_server, app)
