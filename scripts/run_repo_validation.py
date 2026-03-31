from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from rust_toolchain import resolve_rust_toolchain, rust_toolchain_env


ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str], *, env: dict[str, str] | None = None) -> None:
    completed = subprocess.run(command, cwd=ROOT, check=False, env=env)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the canonical SCIR validation baseline with optional Rust enforcement."
    )
    parser.add_argument(
        "--require-rust",
        action="store_true",
        help="Fail if rustc/cargo are unavailable instead of skipping the Rust validation slice.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    rust_resolution = resolve_rust_toolchain()
    rust_available = bool(rust_resolution["available"])
    rust_env = rust_toolchain_env() if rust_available else None

    non_rust_commands = [
        [sys.executable, "scripts/validate_repo_contracts.py", "--mode", "validate"],
        [sys.executable, "scripts/python_importer_conformance.py", "--mode", "validate-fixtures"],
        [sys.executable, "scripts/scir_bootstrap_pipeline.py", "--mode", "validate"],
    ]
    rust_commands = [
        [sys.executable, "scripts/rust_importer_conformance.py", "--mode", "validate-fixtures"],
        [sys.executable, "scripts/scir_bootstrap_pipeline.py", "--language", "rust", "--mode", "validate"],
        [sys.executable, "scripts/benchmark_contract_dry_run.py"],
    ]

    for command in non_rust_commands:
        run_command(command)

    rust_status = "executed"
    benchmark_status = "executed"
    if rust_available:
        for command in rust_commands:
            run_command(command, env=rust_env)
    elif args.require_rust:
        print(
            f"Rust validation requires a usable toolchain: {rust_resolution['reason']}",
            file=sys.stderr,
        )
        return 1
    else:
        rust_status = "skipped_unusable_toolchain"
        benchmark_status = "skipped_unusable_toolchain"

    print(
        json.dumps(
            {
                "rust_toolchain_available": rust_available,
                "rust_toolchain_selected": rust_resolution["selected_toolchain"],
                "rust_toolchain_selection_source": rust_resolution["selection_source"],
                "rust_toolchain_reason": rust_resolution["reason"],
                "cargo_version": rust_resolution["cargo_version"],
                "rustc_version": rust_resolution["rustc_version"],
                "rust_validation_status": rust_status,
                "benchmark_validation_status": benchmark_status,
                "full_rust_validation_command": "python scripts/run_repo_validation.py --require-rust",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
