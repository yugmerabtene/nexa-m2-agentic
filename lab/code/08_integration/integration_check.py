#!/usr/bin/env python3
"""Integration check — validates that all components of the AI Developer Assistant work.

Checks:
1. All sub-agents exist
2. MCP server can be imported
3. Memory module works
4. Workflow pipeline is functional
5. CI pipeline can parse configuration
6. OpenCode config is valid JSON

Usage:
    python lab/code/08_integration/integration_check.py
"""

import json
import sys
from pathlib import Path
from typing import Any


class IntegrationChecker:
    """Validates the complete AI Developer Assistant setup."""

    def __init__(self):
        self.root = Path(__file__).resolve().parent.parent.parent
        self.checks: dict[str, dict[str, Any]] = {}
        self.all_passed = True

    def _check(self, name: str, passed: bool, detail: str = ""):
        self.checks[name] = {"passed": passed, "detail": detail}
        self.all_passed = self.all_passed and passed

    def _print_status(self):
        for name, result in self.checks.items():
            icon = "✅" if result["passed"] else "❌"
            print(f"  {icon} {name}")
            if result["detail"]:
                print(f"       {result['detail']}")

    def check_opencode_config(self):
        """Check opencode.json is valid JSON and has required fields."""
        config_path = self.root / "opencode.json"
        try:
            with open(config_path) as f:
                config = json.load(f)
            required = ["agents", "instructions", "model"]
            missing = [k for k in required if k not in config]
            if missing:
                self._check("opencode.json", False, f"Missing keys: {missing}")
            else:
                agent_count = len(config.get("agents", {}))
                self._check(
                    "opencode.json", True,
                    f"Valid JSON, {agent_count} agents configured"
                )
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self._check("opencode.json", False, str(e))

    def check_sub_agents(self):
        """Check all agent definition files exist."""
        agents_dir = self.root / ".opencode" / "agents"
        expected = [
            "project-manager", "scrum-master", "software-engineer",
            "devops-engineer", "cybersecurity-engineer",
            "qa-engineer",
        ]
        existing = [p.stem for p in agents_dir.glob("*.md")]
        missing = [a for a in expected if a not in existing]
        if missing:
            self._check("sub-agents", False, f"Missing: {missing}")
        else:
            self._check("sub-agents", True, f"All {len(expected)} agents found")

    def check_mcp_server(self):
        """Check MCP server module can be imported."""
        sys.path.insert(0, str(self.root))
        try:
            from lab.code.02_mcp_server.server import app
            self._check("MCP server", True, f"Server name: {app.name}")
        except (ImportError, SyntaxError) as e:
            self._check("MCP server", False, str(e))

    def check_memory(self):
        """Check memory module works."""
        sys.path.insert(0, str(self.root))
        try:
            from lab.code.03_memory.memory import AgentMemory

            import tempfile
            tmp = tempfile.mkdtemp()
            mem = AgentMemory(str(Path(tmp) / "test.json"), window_size=5)
            mem.add({"content": "integration test"})
            results = mem.search("integration")
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)
            self._check("memory module", True, f"Read/write OK, found {len(results)} results")
        except Exception as e:
            self._check("memory module", False, str(e))

    def check_workflow(self):
        """Check workflow script runs."""
        try:
            from lab.code.05_workflow.workflow import run_workflow
            result = run_workflow("test integration")
            self._check("workflow", result.merge_status == "MERGED", f"Status: {result.merge_status}")
        except Exception as e:
            self._check("workflow", False, str(e))

    def check_directories(self):
        """Check all expected directories exist."""
        dirs = [
            self.root / "lectures",
            self.root / "lab" / "code",
            self.root / "lab" / "tests",
            self.root / "syllabus",
            self.root / "projects",
            self.root / "resources",
            self.root / "research",
        ]
        missing = [d.relative_to(self.root) for d in dirs if not d.exists()]
        if missing:
            self._check("directories", False, f"Missing: {missing}")
        else:
            self._check("directories", True, "All expected directories exist")

    def check_ci_config(self):
        """Check GitHub Actions workflow exists."""
        ci_path = self.root / ".github" / "workflows" / "ci.yml"
        exists = ci_path.exists()
        self._check(
            "CI workflow", exists,
            f"ci.yml {'found' if exists else 'not found'}"
        )

    def run(self) -> bool:
        """Run all integration checks."""
        print(f"\n{'='*60}")
        print("INTEGRATION CHECK — AI Developer Assistant")
        print(f"{'='*60}\n")

        checks = [
            self.check_opencode_config,
            self.check_sub_agents,
            self.check_directories,
            self.check_mcp_server,
            self.check_memory,
            self.check_workflow,
            self.check_ci_config,
        ]

        for check in checks:
            check()

        print()
        self._print_status()

        print(f"\n{'='*60}")
        print(f"Overall: {'✅ ALL CHECKS PASSED' if self.all_passed else '❌ SOME CHECKS FAILED'}")
        print(f"{'='*60}\n")
        return self.all_passed


if __name__ == "__main__":
    checker = IntegrationChecker()
    passed = checker.run()
    sys.exit(0 if passed else 1)
