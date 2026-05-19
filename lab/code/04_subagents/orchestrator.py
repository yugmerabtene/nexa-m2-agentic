#!/usr/bin/env python3
"""Sub-agent orchestrator demo — chains task delegation to multiple agents.

This script demonstrates the opencode sub-agent pattern:
1. A tech-lead agent decomposes a task
2. Delegates to specialized sub-agents via task()
3. Consolidates results

Usage:
    python lab/code/04_subagents/orchestrator.py
"""

import json
import sys
from typing import Any


class SubAgent:
    """Simulates an opencode sub-agent with a role and permission set."""

    def __init__(self, name: str, role: str, permissions: list[str]):
        self.name = name
        self.role = role
        self.permissions = permissions

    def execute(self, task: str, context: dict[str, Any] | None = None) -> str:
        """Simulate task execution by a sub-agent."""
        print(f"  [{self.name}/{self.role}] executing: {task[:60]}...")
        return f"[{self.name}] Result: processed '{task}'"


class Orchestrator:
    """Orchestrates a pipeline of sub-agents, mimicking opencode's task tool."""

    def __init__(self):
        self.agents: dict[str, SubAgent] = {
            "software-engineer": SubAgent(
                "software-engineer",
                "Code & Dev",
                ["read", "edit", "python"],
            ),
            "qa-engineer": SubAgent(
                "qa-engineer",
                "Tests & Validation",
                ["read", "pytest"],
            ),
            "cybersecurity-engineer": SubAgent(
                "cybersecurity-engineer",
                "Security Audit",
                ["read"],
            ),
        }

    def task(self, agent_name: str, prompt: str) -> str:
        """Delegate a task to a sub-agent, like opencode's task() tool."""
        agent = self.agents.get(agent_name)
        if not agent:
            return f"Error: unknown agent '{agent_name}'"
        context = {"previous_results": getattr(self, "_last_result", None)}
        result = agent.execute(prompt, context)
        self._last_result = result
        return result

    def run_pipeline(self, user_request: str) -> dict[str, str]:
        """Run a complete dev pipeline: plan → code → review → audit."""
        print(f"\n{'='*60}")
        print(f"User request: {user_request}")
        print(f"{'='*60}\n")

        steps = [
            ("software-engineer", f"Implement: {user_request}"),
            ("qa-engineer", f"Test the implementation for: {user_request}"),
            ("cybersecurity-engineer", f"Audit security for: {user_request}"),
        ]

        results: dict[str, str] = {}
        for agent_name, prompt in steps:
            print(f"\n--- Delegating to {agent_name} ---")
            results[agent_name] = self.task(agent_name, prompt)

        print(f"\n{'='*60}")
        print("Pipeline complete. Results:")
        for agent, result in results.items():
            print(f"  {agent}: {result}")
        return results


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run_pipeline(
        "Add a fibonacci function to math_utils.py with tests"
    )
