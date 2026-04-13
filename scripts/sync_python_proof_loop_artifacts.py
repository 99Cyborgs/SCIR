#!/usr/bin/env python3
"""File: scripts/sync_python_proof_loop_artifacts.py
Purpose: Check or rewrite generated Python proof-loop artifacts so checked-in fixtures stay aligned with authoritative generators.
Role in system: This script is the synchronization helper for importer goldens and retained Track C sample artifacts.
Key dependencies: benchmark_contract_dry_run, scir_bootstrap_pipeline, scir_python_bootstrap metadata and bundle generation.
Side effects: In write mode it overwrites checked-in fixture artifacts and Track C sample files; in check mode it reads them and reports drift.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from benchmark_contract_dry_run import augment_track_c_pilot_outputs
from scir_bootstrap_pipeline import run_track_c_pilot
from scir_python_bootstrap import PYTHON_PROOF_LOOP_METADATA, build_bundle


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "python_importer" / "cases"
TRACK_C_MANIFEST_PATH = ROOT / "reports" / "examples" / "benchmark_track_c_manifest.example.json"
TRACK_C_RESULT_PATH = ROOT / "reports" / "examples" / "benchmark_track_c_result.example.json"


class SyncError(Exception):
    """Represents: A blocking failure while regenerating authoritative proof-loop artifacts.

    Invariants:
      - Raised when authoritative generation fails before drift can be assessed or written back.
    Relationships:
      - Caught in main() so the script can report a mode-specific synchronization failure.
    """
    pass


def expected_fixture_artifacts(root: Path) -> dict[str, dict[str, str]]:
    """Purpose: Rebuild the authoritative generated artifact set for every frozen Python proof-loop case.

    Inputs:
      - root: Path repository root used to resolve source fixtures.
    Outputs:
      - dict[str, dict[str, str]] per-case generated artifact contents keyed by filename.
    Side Effects:
      - Reads source fixtures and runs the bundle generator.
    Assumptions:
      - The checked-in artifact set should exactly match what build_bundle currently emits for each case.
    Failure Modes:
      - Propagates bundle-generation failures from build_bundle.
    """
    artifacts: dict[str, dict[str, str]] = {}
    for case_name in PYTHON_PROOF_LOOP_METADATA["case_order"]:
        source_path = root / "tests" / "python_importer" / "cases" / case_name / "source.py"
        bundle = build_bundle(root, source_path)
        artifacts[case_name] = dict(bundle.files)
    return artifacts


def expected_track_c_samples(root: Path) -> tuple[str, str]:
    """Purpose: Regenerate the retained Track C sample manifest and result text from the authoritative pilot path.

    Inputs:
      - root: Path repository root used by the Track C pilot runner.
    Outputs:
      - tuple[str, str] canonical JSON text for the sample manifest and sample result.
    Side Effects:
      - Runs the non-default Track C pilot generation path in-process.
    Assumptions:
      - Checked-in Track C samples are derived artifacts, not hand-edited sources of truth.
    Failure Modes:
      - Raises SyncError if Track C generation reports failures.
    """
    failures, manifest, result = run_track_c_pilot(root)
    if failures:
        raise SyncError(
            "Track C sample generation failed before synchronization:\n"
            + "\n".join(f" - {item}" for item in failures)
        )
    augment_track_c_pilot_outputs(root, manifest, result)
    return (
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
    )


def collect_drift(root: Path) -> list[str]:
    """Purpose: Compare checked-in proof-loop artifacts against the current authoritative generators.

    Inputs:
      - root: Path repository root.
    Outputs:
      - list[str] human-readable drift messages. Empty means the repo is synchronized.
    Side Effects:
      - Reads checked-in fixture artifacts and Track C sample files.
      - Regenerates expected fixture and Track C sample content in memory.
    Assumptions:
      - Synchronization means both the artifact set and each artifact's content match the generators exactly.
    Failure Modes:
      - Propagates SyncError from Track C sample generation.
    """
    drifts: list[str] = []
    for case_name, expected_files in expected_fixture_artifacts(root).items():
        case_dir = FIXTURE_ROOT / case_name
        actual_names = sorted(path.name for path in case_dir.iterdir() if path.is_file() and path.name != "source.py")
        expected_names = sorted(expected_files)
        if actual_names != expected_names:
            drifts.append(
                f"tests/python_importer/cases/{case_name}: expected artifact set {expected_names!r}, found {actual_names!r}"
            )
            continue
        for name, expected_text in expected_files.items():
            actual_text = (case_dir / name).read_text(encoding="utf-8")
            if actual_text != expected_text:
                drifts.append(f"tests/python_importer/cases/{case_name}/{name}: content drifted from generated bundle")

    expected_manifest, expected_result = expected_track_c_samples(root)
    if TRACK_C_MANIFEST_PATH.read_text(encoding="utf-8") != expected_manifest:
        drifts.append("reports/examples/benchmark_track_c_manifest.example.json: content drifted from generated Track C sample manifest")
    if TRACK_C_RESULT_PATH.read_text(encoding="utf-8") != expected_result:
        drifts.append("reports/examples/benchmark_track_c_result.example.json: content drifted from generated Track C sample result")
    return drifts


def write_synced_artifacts(root: Path) -> list[str]:
    """Purpose: Rewrite checked-in proof-loop artifacts to match the current authoritative generators.

    Inputs:
      - root: Path repository root.
    Outputs:
      - list[str] repository-relative paths that were updated.
    Side Effects:
      - Overwrites generated fixture artifacts and Track C sample files on disk.
    Assumptions:
      - Only files that differ from the regenerated authoritative content should be rewritten.
    Failure Modes:
      - Propagates SyncError from Track C sample generation or filesystem exceptions from writes.
    """
    updated: list[str] = []
    for case_name, expected_files in expected_fixture_artifacts(root).items():
        case_dir = FIXTURE_ROOT / case_name
        for name, expected_text in expected_files.items():
            path = case_dir / name
            if not path.exists() or path.read_text(encoding="utf-8") != expected_text:
                path.write_text(expected_text, encoding="utf-8")
                updated.append(path.relative_to(root).as_posix())

    expected_manifest, expected_result = expected_track_c_samples(root)
    if TRACK_C_MANIFEST_PATH.read_text(encoding="utf-8") != expected_manifest:
        TRACK_C_MANIFEST_PATH.write_text(expected_manifest, encoding="utf-8")
        updated.append(TRACK_C_MANIFEST_PATH.relative_to(root).as_posix())
    if TRACK_C_RESULT_PATH.read_text(encoding="utf-8") != expected_result:
        TRACK_C_RESULT_PATH.write_text(expected_result, encoding="utf-8")
        updated.append(TRACK_C_RESULT_PATH.relative_to(root).as_posix())
    return updated


def parse_args() -> argparse.Namespace:
    """Purpose: Declare the CLI contract for artifact synchronization checks and writes.

    Inputs:
      - None.
    Outputs:
      - argparse.Namespace parsed CLI arguments.
    Side Effects:
      - argparse may print help or usage errors.
    Assumptions:
      - The script supports only `check` and `write` modes plus an optional root override.
    Failure Modes:
      - argparse exits on invalid CLI usage.
    """
    parser = argparse.ArgumentParser(
        description="Synchronize generated Python proof-loop artifacts from the authoritative generators."
    )
    parser.add_argument("--mode", choices=["check", "write"], default="check")
    parser.add_argument("--root")
    return parser.parse_args()


def main() -> int:
    """Purpose: Run proof-loop artifact synchronization in either drift-check or writeback mode.

    Inputs:
      - CLI arguments selecting `check` or `write` mode and an optional root override.
    Outputs:
      - int process status code for synchronization.
    Side Effects:
      - Reads generated artifact state.
      - Optionally rewrites checked-in generated artifacts on disk.
      - Prints detailed drift or update summaries.
    Assumptions:
      - Check mode is the default because synchronization drift should usually be reviewed before writing.
    Failure Modes:
      - Returns 1 on detected drift in check mode or on generation failures in either mode.
    """
    args = parse_args()
    root = Path(args.root).resolve() if args.root else ROOT

    try:
        if args.mode == "check":
            drifts = collect_drift(root)
            if drifts:
                print("[check] python proof-loop artifact synchronization failed")
                for item in drifts:
                    print(f" - {item}")
                return 1
            print("[check] python proof-loop artifacts are synchronized")
            print(
                "Checked generated Python importer bundles and checked-in Track C sample artifacts against the current authoritative generators."
            )
            return 0

        updated = write_synced_artifacts(root)
    except SyncError as exc:
        print(f"[{args.mode}] python proof-loop artifact synchronization failed")
        print(str(exc))
        return 1

    if updated:
        print("[write] synchronized Python proof-loop artifacts")
        for path in updated:
            print(f" - {path}")
    else:
        print("[write] Python proof-loop artifacts already synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
