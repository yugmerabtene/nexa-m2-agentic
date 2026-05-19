#!/usr/bin/env python3
"""Security audit script for the AI Developer Assistant."""

import json
import os
import subprocess
import sys


def check_file_permissions():
    """Check for world-readable secrets or dangerous permissions."""
    issues = []
    for root, dirs, files in os.walk("."):
        for f in files:
            path = os.path.join(root, f)
            if ".git" in path:
                continue
            try:
                mode = os.stat(path).st_mode
                if mode & 0o007:
                    issues.append(f"{path}: world-accessible")
            except OSError:
                pass
    return issues


def check_hardcoded_secrets():
    """Scan for potential secrets in code."""
    issues = []
    patterns = [
        b"api_key",
        b"secret",
        b"password",
        b"token",
        b"sk-",
    ]
    for root, dirs, files in os.walk("lab/code"):
        for f in files:
            if f.endswith((".py", ".sh", ".json", ".yaml", ".yml")):
                path = os.path.join(root, f)
                try:
                    content = open(path, "rb").read()
                    for pat in patterns:
                        if pat in content.lower():
                            issues.append(
                                f"{path}: possible secret ({pat.decode()})"
                            )
                except OSError:
                    pass
    return issues


def check_dependency_vulns():
    """Run pip audit if available."""
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return json.loads(result.stdout).get("vulnerabilities", [])
    except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return [{"error": "pip-audit not available"}]
    return []


def main():
    issues = []
    issues.extend(("permission", i) for i in check_file_permissions())
    issues.extend(("secret", i) for i in check_hardcoded_secrets())
    issues.extend(("dependency", str(i)) for i in check_dependency_vulns())

    if issues:
        print(f"Found {len(issues)} issue(s):")
        for severity, desc in issues:
            print(f"  [{severity}] {desc}")
        sys.exit(1)
    else:
        print("Security audit passed — no issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
