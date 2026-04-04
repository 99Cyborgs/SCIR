from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=os.getcwd())
    parser.add_argument("--changed", nargs="*", default=[])
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    changed = [Path(path) for path in args.changed]

    required_files = [
        "AGENTS.md",
        "ARCHITECTURE.md",
        "VALIDATION_STRATEGY.md",
        "BENCHMARK_STRATEGY.md",
        "specs/scir_h_spec.md",
        "specs/scir_l_spec.md",
        "specs/validator_invariants.md",
    ]

    required_status = [
        {"path": str(repo_root / path), "exists": (repo_root / path).exists()}
        for path in required_files
    ]

    spec_surface = [str(path) for path in changed if "specs" in {part.lower() for part in path.parts}]
    schema_surface = [str(path) for path in changed if "schemas" in {part.lower() for part in path.parts}]
    validator_surface = [str(path) for path in changed if "validators" in {part.lower() for part in path.parts}]
    benchmark_surface = [str(path) for path in changed if "benchmark" in path.as_posix().lower()]
    python_importer_surface = [str(path) for path in changed if "python" in path.as_posix().lower() and "importer" in path.as_posix().lower()]
    rust_importer_surface = [str(path) for path in changed if "rust" in path.as_posix().lower() and "importer" in path.as_posix().lower()]
    typescript_importer_surface = [str(path) for path in changed if "typescript" in path.as_posix().lower() and "importer" in path.as_posix().lower()]
    wasm_surface = [str(path) for path in changed if "wasm" in path.as_posix().lower()]

    recommended_commands = ["python scripts/run_repo_validation.py"]
    if any([spec_surface, schema_surface, validator_surface, benchmark_surface, wasm_surface]):
        recommended_commands.append("python scripts/benchmark_contract_dry_run.py --claim-run")
        recommended_commands.append("python scripts/sync_python_proof_loop_artifacts.py --mode check")
    if python_importer_surface:
        recommended_commands.append("python scripts/python_importer_conformance.py")
    if rust_importer_surface:
        recommended_commands.append("python scripts/rust_importer_conformance.py")
    if typescript_importer_surface:
        recommended_commands.append("python scripts/typescript_importer_conformance.py")

    manual_followups = []
    if benchmark_surface:
        manual_followups.append("python scripts/benchmark_repro.py --run-id <run-id>")

    payload = {
        "repo_root": str(repo_root),
        "semantic_authority": {
            "authoritative": "SCIR-H",
            "derived": "SCIR-Hc",
            "derivative_only": "SCIR-L",
        },
        "required_files": required_status,
        "spec_surface": spec_surface,
        "schema_surface": schema_surface,
        "validator_surface": validator_surface,
        "benchmark_surface": benchmark_surface,
        "python_importer_surface": python_importer_surface,
        "rust_importer_surface": rust_importer_surface,
        "typescript_importer_surface": typescript_importer_surface,
        "wasm_surface": wasm_surface,
        "recommended_commands": recommended_commands,
        "manual_followups": manual_followups,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
