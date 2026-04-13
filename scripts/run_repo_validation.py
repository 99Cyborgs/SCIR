"""File: scripts/run_repo_validation.py
Purpose: Run the repository's canonical validation gate and report which optional slices executed.
Role in system: This is the Windows-safe orchestration entrypoint named by root repo governance docs.
Key dependencies: argparse, subprocess, rust_toolchain helpers, and the repository validation scripts.
Side effects: Executes child processes, inspects Rust toolchain availability, prints JSON status, and exits non-zero on validation failure.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from rust_toolchain import resolve_rust_toolchain, rust_toolchain_env


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_SWEEP_OUTPUT_DIR = "artifacts/validation/sweep-smoke"
VALIDATION_BENCHMARK_OUTPUT_DIR = "artifacts/validation/benchmark-smoke"


def run_command(command: list[str], *, env: dict[str, str] | None = None) -> None:
    """Purpose: Run one validation command inside the repo root and fail fast on non-zero exit.

    Inputs:
      - command: list[str] shell-safe argv for the child validation step.
      - env: dict[str, str] | None environment overrides for toolchain-specific runs.
    Outputs:
      - None. The subprocess output streams directly to the caller's terminal.
    Side Effects:
      - Spawns a child process with the repository root as cwd.
      - Raises SystemExit when the command fails.
    Assumptions:
      - command targets a checked-in script or module that is valid relative to ROOT.
    Failure Modes:
      - Propagates the child process exit code via SystemExit.
    """
    completed = subprocess.run(command, cwd=ROOT, check=False, env=env)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def build_arg_parser() -> argparse.ArgumentParser:
    """Purpose: Define the supported validation toggles without changing the default repo gate.

    Inputs:
      - None.
    Outputs:
      - argparse.ArgumentParser configured for the canonical validation entrypoint.
    Side Effects:
      - None beyond parser construction.
    Assumptions:
      - Optional Rust and Track C work must stay opt-in under repository policy.
    Failure Modes:
      - argparse handles invalid CLI usage by printing help and exiting.
    """
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
    return parser


def main() -> int:
    """Purpose: Execute the preserved validation sequence and emit a machine-readable status summary.

    Inputs:
      - CLI flags parsed from sys.argv.
    Outputs:
      - int process status code for the orchestration run.
    Side Effects:
      - Runs repository validation scripts and tests.
      - Reads the Rust toolchain state to decide whether the deep Rust slice is allowed.
      - Prints a JSON summary consumed by operators and automation.
    Assumptions:
      - The repository root contains the checked-in scripts referenced by the validation contract.
      - The default gate must stay Python-first, with deeper Rust and Track C slices remaining explicit opt-ins.
    Failure Modes:
      - Returns 1 when --require-rust is set but a usable toolchain cannot be resolved.
      - Exits early through run_command if any required validation step fails.
    """
    args = build_arg_parser().parse_args()
    rust_resolution = resolve_rust_toolchain()
    rust_available = bool(rust_resolution["available"])
    rust_env = rust_toolchain_env() if rust_available else None

    benchmark_command = [
        sys.executable,
        "scripts/benchmark_contract_dry_run.py",
        "--output-dir",
        VALIDATION_BENCHMARK_OUTPUT_DIR,
    ]
    if args.include_track_c_pilot:
        benchmark_command.append("--include-track-c-pilot")

    # Keep the default gate aligned with VALIDATION_STRATEGY.md: execute the
    # preserved baseline surfaces first, then widen only when explicitly asked.
    baseline_commands = [
        [sys.executable, "scripts/validate_repo_contracts.py", "--mode", "validate"],
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_scirhc_doctrine.py"],
        [sys.executable, "scripts/python_importer_conformance.py", "--mode", "validate-fixtures"],
        [sys.executable, "scripts/rust_importer_conformance.py", "--mode", "validate-fixtures"],
        [sys.executable, "scripts/scir_bootstrap_pipeline.py", "--mode", "validate"],
        [
            sys.executable,
            "scripts/scir_sweep.py",
            "--manifest",
            "tests/sweeps/python_proof_loop_smoke.json",
            "--output-dir",
            VALIDATION_SWEEP_OUTPUT_DIR,
        ],
        benchmark_command,
    ]
    deep_rust_commands = [
        [sys.executable, "scripts/scir_bootstrap_pipeline.py", "--language", "rust", "--mode", "test"],
    ]

    for command in baseline_commands:
        run_command(command)

    deep_rust_status = "skipped_not_requested"
    conditional_track_c_status = "skipped_not_requested"
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

    # Emit a stable summary so CI and local operators can tell which preserved
    # support lanes actually ran without scraping human-oriented logs.
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
                "benchmark_output_dir": VALIDATION_BENCHMARK_OUTPUT_DIR,
                "sweep_output_dir": VALIDATION_SWEEP_OUTPUT_DIR,
                "conditional_track_c_validation_status": conditional_track_c_status,
                "deep_rust_validation_status": deep_rust_status,
                "full_rust_validation_command": "python scripts/run_repo_validation.py --require-rust",
                "conditional_track_c_validation_command": "python scripts/run_repo_validation.py --include-track-c-pilot",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
