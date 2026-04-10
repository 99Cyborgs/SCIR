from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "artifacts" / "build"


def main() -> int:
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
