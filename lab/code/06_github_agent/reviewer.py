#!/usr/bin/env python3
"""GitHub-style code reviewer — simulates a PR review agent.

This script mimics a GitHub Custom Agent that reviews pull requests:
1. Checks code style (ruff rules)
2. Scans for security issues
3. Validates test coverage
4. Produces a structured review report

Usage:
    python lab/code/06_github_agent/reviewer.py [--file path/to/file.py]
"""

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Any


class CodeReviewer:
    """Simulates a GitHub PR review agent."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.content = self.filepath.read_text() if self.filepath.exists() else ""
        self.issues: list[dict[str, Any]] = []

    def _add_issue(self, severity: str, category: str, line: int, msg: str):
        self.issues.append({
            "severity": severity,
            "category": category,
            "line": line,
            "message": msg,
        })

    def check_style(self):
        """Check basic PEP8-style issues."""
        for i, line in enumerate(self.content.split("\n"), 1):
            if len(line) > 100:
                self._add_issue("minor", "style", i, "Line too long (>100 chars)")
            if line.endswith(" ") or line.endswith("\t"):
                self._add_issue("minor", "style", i, "Trailing whitespace")

    def check_security(self):
        """Scan for security-sensitive patterns."""
        patterns = {
            r"eval\s*\(": "Use of eval() — potential code injection",
            r"exec\s*\(": "Use of exec() — potential code injection",
            r"subprocess\..*shell=True": "shell=True — command injection risk",
            r"os\.system\s*\(": "Use of os.system() — prefer subprocess",
            r"pickle\.loads\s*\(": "Unsafe deserialization",
        }
        for i, line in enumerate(self.content.split("\n"), 1):
            for pattern, msg in patterns.items():
                if re.search(pattern, line):
                    self._add_issue("critical", "security", i, msg)

    def check_tests(self):
        """Check if test file exists nearby."""
        test_paths = [
            self.filepath.parent / f"test_{self.filepath.name}",
            self.filepath.parent.parent / "tests" / f"test_{self.filepath.name}",
        ]
        found = any(p.exists() for p in test_paths)
        if not found:
            self._add_issue(
                "major", "tests", 0,
                f"No test file found for {self.filepath.name}",
            )

    def check_syntax(self):
        """Validate Python syntax."""
        try:
            ast.parse(self.content)
        except SyntaxError as e:
            self._add_issue("critical", "syntax", e.lineno or 0, str(e))

    def review(self) -> dict[str, Any]:
        """Run all review checks."""
        self.check_syntax()
        self.check_style()
        self.check_security()
        self.check_tests()

        severity_order = {"critical": 0, "major": 1, "minor": 2}
        self.issues.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return {
            "file": str(self.filepath),
            "total_issues": len(self.issues),
            "by_severity": {
                "critical": sum(1 for i in self.issues if i["severity"] == "critical"),
                "major": sum(1 for i in self.issues if i["severity"] == "major"),
                "minor": sum(1 for i in self.issues if i["severity"] == "minor"),
            },
            "issues": self.issues,
            "passed": not any(i["severity"] in ("critical", "major") for i in self.issues),
        }

    def print_report(self, result: dict[str, Any]):
        """Print a formatted review report."""
        print(f"\n{'='*60}")
        print(f"PR REVIEW: {result['file']}")
        print(f"{'='*60}")
        print(f"Status: {'✅ PASSED' if result['passed'] else '❌ BLOCKED'}")
        print(f"Total issues: {result['total_issues']}")
        print(f"  Critical: {result['by_severity']['critical']}")
        print(f"  Major: {result['by_severity']['major']}")
        print(f"  Minor: {result['by_severity']['minor']}")
        print()

        for issue in result["issues"]:
            sev = {"critical": "🔴", "major": "🟡", "minor": "🔵"}.get(
                issue["severity"], "⚪"
            )
            line_info = f":{issue['line']}" if issue["line"] else ""
            print(f"  {sev} [{issue['severity'].upper()}] {issue['category']}{line_info}")
            print(f"    {issue['message']}")

        print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="PR Code Reviewer Agent")
    parser.add_argument("--file", default="lab/code/05_workflow/workflow.py",
                        help="Python file to review")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"Error: file not found: {filepath}")
        sys.exit(1)

    reviewer = CodeReviewer(str(filepath))
    result = reviewer.review()
    reviewer.print_report(result)

    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
