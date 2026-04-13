"""File: scripts/run_repo_lint.py
Purpose: Perform the repository's minimal Python static sanity check by parsing tracked source files.
Role in system: This is the lightweight lint surface behind `make lint` for the preserved Python codebase.
Key dependencies: ast, git ls-files, pathlib, and tracked repository state.
Side effects: Calls git, reads tracked Python files, prints lint diagnostics, and exits non-zero on syntax errors.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tracked_python_files() -> list[Path]:
    """Purpose: Resolve the tracked Python file set so lint only checks governed repository inputs.

    Inputs:
      - None.
    Outputs:
      - list[Path] absolute paths for tracked `.py` files sorted for deterministic reporting.
    Side Effects:
      - Executes `git ls-files`.
    Assumptions:
      - Git is available and the current checkout reflects the authoritative tracked surface.
    Failure Modes:
      - Raises SystemExit with git's exit code if file enumeration fails.
    """
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    paths = []
    for line in completed.stdout.splitlines():
        if line.endswith(".py"):
            paths.append(ROOT / line)
    return sorted(paths)


def main() -> int:
    """Purpose: Parse every tracked Python file and report syntax failures in a stable format.

    Inputs:
      - None.
    Outputs:
      - int exit status for the lint pass.
    Side Effects:
      - Reads tracked Python source files and prints success or failure summaries.
    Assumptions:
      - Syntax validity is the minimum required static check for the repo's Python surface.
    Failure Modes:
      - Returns 1 when any tracked Python file fails to parse.
    """
    failures: list[str] = []
    python_files = tracked_python_files()
    for path in python_files:
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            # Preserve file-relative diagnostics so lint failures are actionable
            # without exposing machine-specific absolute paths.
            failures.append(
                f"{path.relative_to(ROOT)}:{exc.lineno}:{exc.offset}: {exc.msg}"
            )

    if failures:
        print("[lint] tracked Python syntax check failed")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print(f"[lint] parsed {len(python_files)} tracked Python files without syntax errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
