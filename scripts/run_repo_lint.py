from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tracked_python_files() -> list[Path]:
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
    failures: list[str] = []
    python_files = tracked_python_files()
    for path in python_files:
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=str(path))
        except SyntaxError as exc:
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
