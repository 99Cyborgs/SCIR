from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from benchmark_audit_common import file_sha256


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reproduce a benchmark claim run from a recorded run_id.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--root")
    return parser


def manifest_drift_failures(root: Path, locked_manifest: dict) -> list[str]:
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


def main() -> int:
    args = build_arg_parser().parse_args()
    root = Path(args.root).resolve() if args.root else ROOT
    run_dir = root / "artifacts" / "benchmark_runs" / args.run_id
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
