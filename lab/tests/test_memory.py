"""Tests for AgentMemory."""

import json
import tempfile
from pathlib import Path

import pytest

from lab.code.03_memory.memory import AgentMemory


@pytest.fixture
def memory():
    tmp = tempfile.mkdtemp()
    path = Path(tmp) / "memory.json"
    m = AgentMemory(str(path), window_size=5)
    yield m
    if path.exists():
        path.unlink()


def test_add_and_search(memory):
    memory.add({"content": "Hello world"})
    memory.add({"content": "Testing memory"})
    results = memory.search("Hello")
    assert len(results) >= 1
    assert "Hello world" in json.dumps(results)


def test_persistence(memory):
    memory.add({"content": "Persist me"})
    # Create new instance reading same file
    m2 = AgentMemory(memory.path, window_size=5)
    results = m2.search("Persist")
    assert len(results) >= 1


def test_sliding_window(memory):
    for i in range(10):
        memory.add({"content": f"Event {i}"})
    assert len(memory.short_term) == 5
    assert len(memory.long_term) >= 1


def test_get_context(memory):
    memory.add({"content": "Context line 1"})
    memory.add({"content": "Context line 2"})
    ctx = memory.get_context(limit=2)
    assert "Context line 2" in ctx
