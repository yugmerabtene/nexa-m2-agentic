#!/usr/bin/env python3
"""Dev workflow pipeline — simulates a complete agentic dev cycle.

Demonstrates a 6-step workflow:
  Plan → Code → Test → Review → Audit → Merge

Usage:
    python lab/code/05_workflow/workflow.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class WorkflowState:
    """State passed through the workflow pipeline."""
    task: str
    plan: str = ""
    code: str = ""
    test_result: str = ""
    review: str = ""
    audit: str = ""
    merge_status: str = ""
    logs: list[str] = field(default_factory=list)

    def log(self, step: str, msg: str) -> None:
        entry = f"[{datetime.now().strftime('%H:%M:%S')}] {step}: {msg}"
        self.logs.append(entry)
        print(entry)


def step_plan(state: WorkflowState) -> WorkflowState:
    """Step 1: Plan — decompose the task into sub-tasks."""
    state.plan = (
        f"1. Read existing codebase\n"
        f"2. Implement {state.task}\n"
        f"3. Write unit tests\n"
        f"4. Run tests and fix issues\n"
        f"5. Security review"
    )
    state.log("PLAN", f"Task decomposed:\n{state.plan}")
    return state


def step_code(state: WorkflowState) -> WorkflowState:
    """Step 2: Code — implement the solution."""
    state.code = (
        f"def fibonacci(n):\n"
        f"    if n <= 1:\n"
        f"        return n\n"
        f"    return fibonacci(n-1) + fibonacci(n-2)\n"
    )
    state.log("CODE", "Implementation written")
    return state


def step_test(state: WorkflowState) -> WorkflowState:
    """Step 3: Test — write and run tests."""
    test_code = (
        "def test_fibonacci():\n"
        "    assert fibonacci(0) == 0\n"
        "    assert fibonacci(1) == 1\n"
        "    assert fibonacci(10) == 55\n"
    )
    state.test_result = f"Tests written:\n{test_code}\n\nAll tests PASSED"
    state.log("TEST", state.test_result)
    return state


def step_review(state: WorkflowState) -> WorkflowState:
    """Step 4: Review — check code quality."""
    state.review = (
        "Code quality: GOOD\n"
        "- Function naming: OK\n"
        "- Edge cases (n=0, n<0): PARTIAL\n"
        "- Performance (recursion): OK for small n\n"
        "- Suggestion: add memoization for large n"
    )
    state.log("REVIEW", state.review)
    return state


def step_audit(state: WorkflowState) -> WorkflowState:
    """Step 5: Audit — security check (read-only)."""
    state.audit = (
        "Security audit: PASSED\n"
        "- No hardcoded secrets: OK\n"
        "- No subprocess calls: OK\n"
        "- No file writes outside scope: OK"
    )
    state.log("AUDIT", state.audit)
    return state


def step_merge(state: WorkflowState) -> WorkflowState:
    """Step 6: Merge — final validation."""
    checks = all([
        state.code, state.test_result,
        "PASSED" in state.review, "PASSED" in state.audit,
    ])
    state.merge_status = "MERGED" if checks else "BLOCKED"
    state.log("MERGE", f"Status: {state.merge_status}")
    return state


def run_workflow(task: str) -> WorkflowState:
    """Execute the complete 6-step dev workflow."""
    state = WorkflowState(task=task)

    pipeline = [
        step_plan, step_code, step_test,
        step_review, step_audit, step_merge,
    ]

    print(f"\n{'='*60}")
    print(f"DEV WORKFLOW: {task}")
    print(f"{'='*60}\n")

    for step in pipeline:
        state = step(state)
        print("-" * 40)

    print(f"\n{'='*60}")
    print(f"FINAL STATUS: {state.merge_status}")
    print(f"{'='*60}")
    return state


if __name__ == "__main__":
    run_workflow("Add fibonacci function with tests")
