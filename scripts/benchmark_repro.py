"""File: scripts/benchmark_repro.py
Purpose: Re-run a benchmark claim from recorded artifacts and verify that its locked corpus still matches the repository.
Role in system: This is the benchmark reproducibility helper for preserved claim-grade audit runs.
Key dependencies: argparse, json, subprocess, pathlib, and benchmark_audit_common.file_sha256.
Side effects: Reads benchmark artifacts, writes reproduction outputs under artifacts/, executes the benchmark dry-run script, and prints status messages.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from benchmark_audit_common import file_sha256


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    """Purpose: Read a UTF-8 JSON artifact used by the benchmark reproduction flow.

    Inputs:
      - path: Path location of the JSON file to load.
    Outputs:
      - dict decoded JSON payload.
    Side Effects:
      - Reads from disk.
    Assumptions:
      - The target file contains a JSON object encoded as UTF-8.
    Failure Modes:
      - Raises JSONDecodeError or filesystem exceptions if the artifact is invalid or missing.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def build_arg_parser() -> argparse.ArgumentParser:
    """Purpose: Declare the CLI contract for reproducing a prior benchmark run.

    Inputs:
      - None.
    Outputs:
      - argparse.ArgumentParser for run-id driven reproduction requests.
    Side Effects:
      - None beyond parser construction.
    Assumptions:
      - Reproduction is anchored by a recorded run_id and may optionally override the root or output directory.
    Failure Modes:
      - argparse exits on invalid CLI usage.
    """
    parser = argparse.ArgumentParser(description="Reproduce a benchmark claim run from a recorded run_id.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--root")
    return parser


def manifest_drift_failures(root: Path, locked_manifest: dict) -> list[str]:
    """Purpose: Detect whether the fixture set behind a historical benchmark run has drifted since it was locked.

    Inputs:
      - root: Path repository root used to resolve locked fixture entries.
      - locked_manifest: dict manifest-lock payload containing fixture paths and hashes.
    Outputs:
      - list[str] human-readable drift diagnostics. Empty means the lock still matches disk.
    Side Effects:
      - Reads fixture files from disk.
    Assumptions:
      - The manifest lock uses the same hash normalization contract as benchmark_audit_common.file_sha256.
    Failure Modes:
      - Reports missing fixtures or hash mismatches as drift failures instead of raising.
    """
    failures = []
    for entry in locked_manifest["manifest"]["fixtures"]:
        fixture_path = root / entry["path"]
        if not fixture_path.exists():
            failures.append(f"missing fixture path {entry['path']}")
            continue
        actual_hash = file_sha256(fixture_path)
        if actual_hash != entry["hash"]:
            failures.append(f"hash drift for {entry['path']}: expected {entry['hash']} found {actual_hash}")
    return failures


def resolve_run_dir(root: Path, run_id: str) -> Path | None:
    """Purpose: Locate the artifact directory that recorded the requested benchmark run.

    Inputs:
      - root: Path repository root containing `artifacts/benchmark_runs`.
      - run_id: str logical run identifier to match.
    Outputs:
      - Path | None matching run directory, or None when no matching recorded context exists.
    Side Effects:
      - Reads candidate run directories and their JSON context files.
    Assumptions:
      - A valid recorded run includes both `benchmark_run_context.json` and `manifest_lock.json`.
    Failure Modes:
      - Ignores malformed JSON contexts and returns None when no valid match is found.
    """
    benchmark_root = root / "artifacts" / "benchmark_runs"
    direct_match = benchmark_root / run_id
    if (direct_match / "benchmark_run_context.json").exists() and (direct_match / "manifest_lock.json").exists():
        return direct_match
    if not benchmark_root.exists():
        return None
    for candidate in sorted(path for path in benchmark_root.iterdir() if path.is_dir()):
        context_path = candidate / "benchmark_run_context.json"
        manifest_lock_path = candidate / "manifest_lock.json"
        if not context_path.exists() or not manifest_lock_path.exists():
            continue
        try:
            context = load_json(context_path)
        except json.JSONDecodeError:
            continue
        if context.get("run_id") == run_id:
            return candidate
    return None


def main() -> int:
    """Purpose: Reproduce a locked benchmark claim run while guarding against silent corpus drift.

    Inputs:
      - CLI arguments specifying the source run id and optional root or output locations.
    Outputs:
      - int process status code for the reproduction attempt.
    Side Effects:
      - Reads recorded run artifacts.
      - Writes locked manifest and reproduction context files.
      - Launches `scripts/benchmark_contract_dry_run.py --claim-run`.
      - Prints success or failure context for operators.
    Assumptions:
      - Claim reproduction is only meaningful if the fixture hashes still match the locked manifest.
    Failure Modes:
      - Returns 1 when the recorded run context is missing or fixture drift is detected.
      - Propagates the benchmark command's exit code only when it fails before emitting the expected reproduced artifacts.
    """
    args = build_arg_parser().parse_args()
    root = Path(args.root).resolve() if args.root else ROOT
    run_dir = resolve_run_dir(root, args.run_id)
    if run_dir is None:
        print(
            f"missing benchmark run context for run_id {args.run_id} under "
            f"{root / 'artifacts' / 'benchmark_runs'}",
            file=sys.stderr,
        )
        return 1
    context_path = run_dir / "benchmark_run_context.json"
    manifest_lock_path = run_dir / "manifest_lock.json"
    if not context_path.exists():
        print(f"missing benchmark run context: {context_path}", file=sys.stderr)
        return 1
    if not manifest_lock_path.exists():
        print(f"missing manifest lock: {manifest_lock_path}", file=sys.stderr)
        return 1

    context = load_json(context_path)
    manifest_lock = load_json(manifest_lock_path)
    drift_failures = manifest_drift_failures(root, manifest_lock)
    if drift_failures:
        print("[benchmark-repro] fixture drift detected", file=sys.stderr)
        for item in drift_failures:
            print(f" - {item}", file=sys.stderr)
        return 1

    repro_root = root / "artifacts" / "benchmark_repro" / args.run_id
    repro_root.mkdir(parents=True, exist_ok=True)
    locked_manifest_path = repro_root / "locked_corpus_manifest.json"
    locked_manifest_path.write_text(json.dumps(manifest_lock["manifest"], indent=2) + "\n", encoding="utf-8")
    output_dir = Path(args.output_dir).resolve() if args.output_dir else repro_root / "reproduced_run"
    relative_manifest = locked_manifest_path.relative_to(root).as_posix()

    command = [
        sys.executable,
        "scripts/benchmark_contract_dry_run.py",
        "--claim-run",
        "--corpus-manifest",
        relative_manifest,
        "--output-dir",
        str(output_dir),
    ]
    completed = subprocess.run(command, cwd=root, check=False)
    reproduced_artifacts = [
        output_dir / "benchmark_report.json",
        output_dir / "comparison_summary.json",
        output_dir / "contamination_report.json",
        output_dir / "manifest_lock.json",
    ]
    # A non-zero claim lane can still be diagnostically useful if it produced the
    # expected audit bundle, so only hard-fail when the run also failed to emit it.
    if completed.returncode != 0 and any(not path.exists() for path in reproduced_artifacts):
        return completed.returncode

    (repro_root / "reproduction_context.json").write_text(
        json.dumps(
            {
                "source_run_id": args.run_id,
                "reproduced_from_manifest_hash": manifest_lock["corpus_manifest_hash"],
                "source_context": context,
                "output_dir": str(output_dir),
                "reproduced_exit_code": completed.returncode,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if completed.returncode == 0:
        print(f"[benchmark-repro] reproduced {args.run_id} into {output_dir}")
    else:
        print(
            f"[benchmark-repro] reproduced {args.run_id} into {output_dir} "
            f"(claim lane exited {completed.returncode}; see reproduced artifacts)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
