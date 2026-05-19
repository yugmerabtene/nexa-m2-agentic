"""Hierarchical agent memory with JSON persistence and sliding window."""

import json
import os
from collections import deque
from datetime import datetime


class AgentMemory:
    def __init__(self, path: str, window_size: int = 50):
        self.path = path
        self.window_size = window_size
        self.short_term: deque = deque(maxlen=window_size)
        self.long_term: list = []
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
                self.short_term = deque(
                    data.get("short_term", []), maxlen=self.window_size
                )
                self.long_term = data.get("long_term", [])

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(
                {
                    "short_term": list(self.short_term),
                    "long_term": self.long_term,
                },
                f,
                indent=2,
            )

    def add(self, entry: dict):
        entry["timestamp"] = datetime.now().isoformat()
        self.short_term.append(entry)
        if len(self.short_term) == self.window_size:
            summary = self._consolidate(self.short_term)
            self.long_term.append(summary)
        self._save()

    def search(self, keyword: str) -> list:
        results = []
        for e in list(self.short_term) + self.long_term:
            text = json.dumps(e)
            if keyword.lower() in text.lower():
                results.append(e)
        return results[-10:]

    def _consolidate(self, entries: deque) -> dict:
        return {
            "summary": f"{len(entries)} events from "
            f"{entries[0].get('timestamp', '?')}",
            "count": len(entries),
            "compacted": True,
            "timestamp": datetime.now().isoformat(),
        }

    def get_context(self, limit: int = 10) -> str:
        recent = list(self.short_term)[-limit:]
        return "\n".join(
            f"[{e.get('timestamp', '?')}] {e.get('content', '')}"
            for e in recent
        )
