"""File: scripts/run_repo_build.py
Purpose: Produce the repo's required build sanity artifact as a wheel under artifacts/build.
Role in system: This is the implementation behind the top-level `make build` contract.
Key dependencies: shutil, subprocess, pip wheel, and the local package metadata.
Side effects: Deletes and recreates artifacts/build, invokes pip wheel, writes wheel files, and prints the built artifact names.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "build"


def main() -> int:
    """Purpose: Build a fresh wheel artifact into the governed build output directory.

    Inputs:
      - None.
    Outputs:
      - int process status code for the wheel build.
    Side Effects:
      - Removes any previous `artifacts/build` directory.
      - Creates a new build output directory.
      - Executes `python -m pip wheel` against the repository root.
      - Prints built wheel names for operators and CI logs.
    Assumptions:
      - The build contract requires a real artifact, not a no-op success marker.
    Failure Modes:
      - Returns the wheel command's non-zero exit code on build failure.
    """
    output_dir = DEFAULT_OUTPUT_DIR
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "pip",
        "wheel",
        "--no-deps",
        "--no-build-isolation",
        "--wheel-dir",
        str(output_dir),
        ".",
    ]
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        return completed.returncode

    built_wheels = sorted(path.name for path in output_dir.glob("*.whl"))
    print(f"[build] built wheel artifacts in {output_dir}")
    for wheel in built_wheels:
        print(f" - {wheel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
