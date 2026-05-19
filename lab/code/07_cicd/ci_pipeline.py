#!/usr/bin/env python3
"""Local CI pipeline — validates code quality without GitHub Actions.

Simulates a CI/CD pipeline locally:
  lint → test → security audit → build

Usage:
    python lab/code/07_cicd/ci_pipeline.py [--path lab/code]
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


class CIRunner:
    """Local CI pipeline runner."""

    def __init__(self, code_path: str):
        self.code_path = Path(code_path)
        self.results: dict[str, dict[str, Any]] = {}

    def _run_step(self, name: str, cmd: list[str], timeout: int = 30) -> dict[str, Any]:
        """Run a pipeline step and time it."""
        print(f"\n  ▶ {name}...", end=" ", flush=True)
        start = time.time()
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            duration = time.time() - start
            passed = result.returncode == 0
            status = "✅" if passed else "❌"
            print(f"{status} ({duration:.1f}s)")
            return {
                "name": name,
                "passed": passed,
                "duration": duration,
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500],
                "returncode": result.returncode,
            }
        except FileNotFoundError:
            print("⚠ skipped (tool not found)")
            return {
                "name": name,
                "passed": True,
                "duration": 0,
                "stdout": "tool not available",
                "stderr": "",
                "returncode": 0,
                "skipped": True,
            }
        except subprocess.TimeoutExpired:
            print("⚠ timeout")
            return {
                "name": name,
                "passed": False,
                "duration": timeout,
                "stdout": "",
                "stderr": "timeout",
                "returncode": -1,
            }

    def run_lint(self):
        """Step 1: Lint with ruff."""
        self.results["lint"] = self._run_step(
            "ruff lint", ["ruff", "check", str(self.code_path)]
        )

    def run_mypy(self):
        """Step 2: Type check with mypy."""
        self.results["mypy"] = self._run_step(
            "mypy", ["mypy", str(self.code_path), "--ignore-missing-imports"]
        )

    def run_tests(self):
        """Step 3: Run pytest."""
        self.results["test"] = self._run_step(
            "pytest", ["python", "-m", "pytest", "lab/tests/", "-v"]
        )

    def run_security_audit(self):
        """Step 4: Run the security audit script."""
        audit_script = Path("lab/code/08_integration/security_audit.py")
        if audit_script.exists():
            self.results["security"] = self._run_step(
                "security audit",
                ["python", str(audit_script)],
            )
        else:
            print("  ▶ security audit... ⚠ script not found")

    def run(self) -> bool:
        """Execute the full CI pipeline."""
        print(f"\n{'='*60}")
        print(f"CI PIPELINE: {self.code_path}")
        print(f"{'='*60}")

        self.run_lint()
        self.run_mypy()
        self.run_tests()
        self.run_security_audit()

        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        all_passed = True
        for name, result in self.results.items():
            status = "✅" if result["passed"] else "❌"
            duration = f"{result['duration']:.1f}s"
            skipped = result.get("skipped", False)
            if skipped:
                duration = "skipped"
            print(f"  {status} {name} ({duration})")
            if not result["passed"] and result["stderr"]:
                print(f"    Error: {result['stderr'][:200]}")
            all_passed = all_passed and result["passed"]

        print(f"\nOverall: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        print(f"{'='*60}\n")
        return all_passed


def main():
    parser = argparse.ArgumentParser(description="Local CI Pipeline")
    parser.add_argument("--path", default="lab/code", help="Code path to check")
    args = parser.parse_args()

    ci = CIRunner(args.path)
    passed = ci.run()
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
