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
        "--include-track-c-pilot",
        action="store_true",
        help="Also run the optional non-default Track C benchmark pilot without changing the default gate.",
    )
    parser.add_argument(
        "--require-rust",
        action="store_true",
        help="Fail if rustc/cargo are unavailable instead of skipping the Rust validation slice.",
    )
    parser.add_argument(
        "--include-experimental-python-translation",
        action="store_true",
        help="Also run the non-default experimental Python translation-validation lane without changing the default gate.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    rust_resolution = resolve_rust_toolchain()
    rust_available = bool(rust_resolution["available"])
    rust_env = rust_toolchain_env() if rust_available else None

    benchmark_command = [sys.executable, "scripts/benchmark_contract_dry_run.py"]
    if args.include_track_c_pilot:
        benchmark_command.append("--include-track-c-pilot")

    baseline_commands = [
        [sys.executable, "scripts/validate_repo_contracts.py", "--mode", "validate"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_scirhc_doctrine.py"],
        [sys.executable, "scripts/python_importer_conformance.py", "--mode", "validate-fixtures"],
        [sys.executable, "scripts/rust_importer_conformance.py", "--mode", "validate-fixtures"],
        [sys.executable, "scripts/scir_bootstrap_pipeline.py", "--mode", "validate"],
        [sys.executable, "scripts/scir_sweep.py", "--manifest", "tests/sweeps/python_proof_loop_smoke.json"],
        benchmark_command,
    ]
    deep_rust_commands = [
        [sys.executable, "scripts/scir_bootstrap_pipeline.py", "--language", "rust", "--mode", "validate"],
    ]
    experimental_python_translation_command = [
        sys.executable,
        "scripts/validate_translation.py",
        "--include-experimental-python",
    ]

    for command in baseline_commands:
        run_command(command)

    deep_rust_status = "skipped_not_requested"
    conditional_track_c_status = "skipped_not_requested"
    experimental_python_translation_status = "skipped_not_requested"
    if args.require_rust:
        if not rust_available:
            print(
                f"Rust validation requires a usable toolchain: {rust_resolution['reason']}",
                file=sys.stderr,
            )
            return 1
        for command in deep_rust_commands:
            run_command(command, env=rust_env)
        deep_rust_status = "executed"
    if args.include_track_c_pilot:
        conditional_track_c_status = "executed"
    if args.include_experimental_python_translation:
        run_command(experimental_python_translation_command)
        experimental_python_translation_status = "executed"

    print(
        json.dumps(
            {
                "rust_toolchain_available": rust_available,
                "rust_toolchain_selected": rust_resolution["selected_toolchain"],
                "rust_toolchain_selection_source": rust_resolution["selection_source"],
                "rust_toolchain_reason": rust_resolution["reason"],
                "cargo_version": rust_resolution["cargo_version"],
                "rustc_version": rust_resolution["rustc_version"],
                "baseline_validation_status": "executed",
                "rust_importer_validation_status": "executed",
                "benchmark_validation_status": "executed",
                "sweep_validation_status": "executed",
                "conditional_track_c_validation_status": conditional_track_c_status,
                "experimental_python_translation_validation_status": experimental_python_translation_status,
                "deep_rust_validation_status": deep_rust_status,
                "full_rust_validation_command": "python scripts/run_repo_validation.py --require-rust",
                "conditional_track_c_validation_command": "python scripts/run_repo_validation.py --include-track-c-pilot",
                "experimental_python_translation_validation_command": "python scripts/run_repo_validation.py --include-experimental-python-translation",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
