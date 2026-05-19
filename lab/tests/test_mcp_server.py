"""Tests for MCP server tools."""

import subprocess
import tempfile
from pathlib import Path

import pytest


def test_read_file_tool():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("test content")
        f.flush()
        path = f.name

    result = subprocess.run(
        ["python3", "-c", f"""
import sys
sys.path.insert(0, 'lab/code/02_mcp_server')
from server import call_tool
import anyio
async def test():
    res = await call_tool("read_file", {{"path": "{path}"}})
    print(res[0].text)
anyio.run(test)
"""],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert "test content" in result.stdout


def test_search_code_tool():
    result = subprocess.run(
        ["python3", "-c", f"""
import sys
sys.path.insert(0, 'lab/code/02_mcp_server')
from server import call_tool
import anyio
async def test():
    res = await call_tool("search_code", {{"pattern": "def test_", "path": "lab/tests"}})
    print(res[0].text)
anyio.run(test)
"""],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert "test_" in result.stdout


def test_resources():
    result = subprocess.run(
        ["python3", "-c", f"""
import sys
sys.path.insert(0, 'lab/code/02_mcp_server')
from server import list_resources
import anyio
async def test():
    res = await list_resources()
    for r in res:
        print(r.name)
anyio.run(test)
"""],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert "Agent Design Patterns" in result.stdout
