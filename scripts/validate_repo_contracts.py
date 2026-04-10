#!/usr/bin/env python3
"""Repository contract checker for the consolidated SCIR baseline."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys
import tempfile

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    Draft202012Validator = None


ROOT = pathlib.Path(__file__).resolve().parents[1]

LIVE_REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "SYSTEM_BOUNDARY.md",
    "CURRENT_FOCUS.md",
    "BACKLOG.md",
    "ARCHITECTURE.md",
    "DECISION_REGISTER.md",
    "OPEN_QUESTIONS.md",
    "REPO_MAP.md",
    "IMPLEMENTATION_PLAN.md",
    "VALIDATION_STRATEGY.md",
    "BENCHMARK_STRATEGY.md",
    "LOWERING_CONTRACT.md",
    "IDENTITY_MODEL.md",
    "Makefile",
    "pyproject.toml",
    "docs/target_profiles.md",
    "docs/preservation_contract.md",
    "docs/feature_tiering.md",
    "docs/unsupported_cases.md",
    "specs/scir_h_spec.md",
    "specs/scir_hc_doctrine.md",
    "specs/scir_l_spec.md",
    "specs/type_effect_capability_model.md",
    "specs/ownership_alias_model.md",
    "specs/interop_and_opaque_boundary_spec.md",
    "specs/validator_invariants.md",
    "specs/provenance_and_stable_id_spec.md",
    "specs/concurrency_model.md",
    "schemas/module_manifest.schema.json",
    "schemas/corpus_manifest.schema.json",
    "schemas/profile_claim.schema.json",
    "schemas/preservation_report.schema.json",
    "schemas/feature_tier_report.schema.json",
    "schemas/validation_report.schema.json",
    "schemas/benchmark_manifest.schema.json",
    "schemas/benchmark_result.schema.json",
    "schemas/benchmark_report.schema.json",
    "schemas/comparison_summary.schema.json",
    "schemas/contamination_report.schema.json",
    "schemas/reconstruction_report.schema.json",
    "schemas/opaque_boundary_contract.schema.json",
    "schemas/sweep_manifest.schema.json",
    "schemas/sweep_result.schema.json",
    "schemas/sweep_summary.schema.json",
    "schemas/regression_summary.schema.json",
    "schemas/decision_register.schema.json",
    "schemas/open_questions.schema.json",
    "scir/__init__.py",
    "frontend/typescript/NOT_ACTIVE.md",
    "tests/typescript_importer/NOT_ACTIVE.md",
    "scripts/validate_repo_contracts.py",
    "scripts/run_repo_validation.py",
    "scripts/run_repo_build.py",
    "scripts/run_repo_lint.py",
    "scripts/scir_h_bootstrap_model.py",
    "scripts/scir_python_bootstrap.py",
    "scripts/scir_rust_bootstrap.py",
    "scripts/wasm_backend_metadata.py",
    "scripts/benchmark_contract_metadata.py",
    "scripts/python_importer_conformance.py",
    "scripts/rust_importer_conformance.py",
    "scripts/typescript_importer_conformance.py",
    "scripts/NOT_ACTIVE.md",
    "scripts/scir_bootstrap_pipeline.py",
    "scripts/scir_sweep.py",
    "scripts/benchmark_audit_common.py",
    "scripts/benchmark_contract_dry_run.py",
    "scripts/benchmark_repro.py",
    "scripts/sync_python_proof_loop_artifacts.py",
    "reports/examples/module_manifest.example.json",
    "reports/examples/corpus_manifest.example.json",
    "reports/examples/feature_tier_report.example.json",
    "reports/examples/validation_report.example.json",
    "reports/examples/profile_claim.example.json",
    "reports/examples/preservation_report.example.json",
    "reports/examples/preservation_source_to_h.example.json",
    "reports/examples/preservation_h_to_l.example.json",
    "reports/examples/preservation_h_to_python.example.json",
    "reports/examples/preservation_l_to_wasm.example.json",
    "reports/examples/reconstruction_report.example.json",
    "reports/examples/opaque_boundary_contract.example.json",
    "reports/examples/sweep_manifest.example.json",
    "reports/examples/sweep_result.example.json",
    "reports/examples/sweep_summary.example.json",
    "reports/examples/regression_summary.example.json",
    "reports/examples/benchmark_manifest.example.json",
    "reports/examples/benchmark_result.example.json",
    "reports/examples/benchmark_report.example.json",
    "reports/examples/comparison_summary.example.json",
    "reports/examples/contamination_report.example.json",
    "reports/examples/benchmark_track_c_manifest.example.json",
    "reports/examples/benchmark_track_c_result.example.json",
    "tests/README.md",
    "tests/corpora/python_tier_a_micro_corpus.json",
    "tests/corpora/python_proof_loop_corpus.json",
    "tests/corpora/python_preservation_negative_corpus.json",
    "tests/invalid_scir_h/README.md",
    "tests/invalid_scir_h/manifest.json",
    "tests/invalid_scir_l/README.md",
    "tests/invalid_scir_l/manifest.json",
    "tests/sweeps/python_proof_loop_smoke.json",
    "tests/sweeps/python_proof_loop_full.json",
]

AUDIT_REQUIRED_FILES = [
    "plans/PLANS.md",
    "plans/2026-04-10-repo-reset-consolidation.md",
    "docs/project_overview.md",
    "docs/reconstruction_policy.md",
    "docs/scir_h_overview.md",
    "docs/scir_l_overview.md",
    "docs/runtime_doctrine.md",
    "docs/repository_map.md",
    "frontend/README.md",
    "frontend/python/IMPORT_SCOPE.md",
    "frontend/rust/IMPORT_SCOPE.md",
    "frontend/typescript/IMPORT_SCOPE.md",
    "frontend/typescript/NOT_ACTIVE.md",
    "validators/README.md",
    "validators/validator_contracts.md",
    "backends/README.md",
    "backends/wasm/README.md",
    "benchmarks/README.md",
    "benchmarks/tracks.md",
    "benchmarks/baselines.md",
    "benchmarks/corpora_policy.md",
    "benchmarks/contamination_controls.md",
    "benchmarks/success_failure_gates.md",
    "tooling/README.md",
    "tooling/NOT_ACTIVE.md",
    "tooling/agent_api.md",
    "tooling/formatter_contract.md",
    "tooling/checker_contract.md",
    "tooling/explorer_contract.md",
    "ci/README.md",
    "ci/validation_pipeline.md",
    "ci/benchmark_pipeline.md",
    ".github/workflows/validate.yml",
    ".github/workflows/benchmarks.yml",
    "reports/README.md",
    "tests/typescript_importer/README.md",
    "tests/typescript_importer/NOT_ACTIVE.md",
    "scripts/typescript_importer_conformance.py",
]

EXAMPLE_ARTIFACTS = [
    ("reports/examples/module_manifest.example.json", "schemas/module_manifest.schema.json"),
    ("reports/examples/corpus_manifest.example.json", "schemas/corpus_manifest.schema.json"),
    ("reports/examples/feature_tier_report.example.json", "schemas/feature_tier_report.schema.json"),
    ("reports/examples/validation_report.example.json", "schemas/validation_report.schema.json"),
    ("reports/examples/profile_claim.example.json", "schemas/profile_claim.schema.json"),
    ("reports/examples/preservation_report.example.json", "schemas/preservation_report.schema.json"),
    ("reports/examples/preservation_source_to_h.example.json", "schemas/preservation_report.schema.json"),
    ("reports/examples/preservation_h_to_l.example.json", "schemas/preservation_report.schema.json"),
    ("reports/examples/preservation_h_to_python.example.json", "schemas/preservation_report.schema.json"),
    ("reports/examples/preservation_l_to_wasm.example.json", "schemas/preservation_report.schema.json"),
    ("reports/examples/reconstruction_report.example.json", "schemas/reconstruction_report.schema.json"),
    ("reports/examples/opaque_boundary_contract.example.json", "schemas/opaque_boundary_contract.schema.json"),
    ("reports/examples/sweep_manifest.example.json", "schemas/sweep_manifest.schema.json"),
    ("reports/examples/sweep_result.example.json", "schemas/sweep_result.schema.json"),
    ("reports/examples/sweep_summary.example.json", "schemas/sweep_summary.schema.json"),
    ("reports/examples/regression_summary.example.json", "schemas/regression_summary.schema.json"),
    ("reports/examples/benchmark_manifest.example.json", "schemas/benchmark_manifest.schema.json"),
    ("reports/examples/benchmark_result.example.json", "schemas/benchmark_result.schema.json"),
    ("reports/examples/benchmark_report.example.json", "schemas/benchmark_report.schema.json"),
    ("reports/examples/comparison_summary.example.json", "schemas/comparison_summary.schema.json"),
    ("reports/examples/contamination_report.example.json", "schemas/contamination_report.schema.json"),
    ("reports/examples/benchmark_track_c_manifest.example.json", "schemas/benchmark_manifest.schema.json"),
    ("reports/examples/benchmark_track_c_result.example.json", "schemas/benchmark_result.schema.json"),
]

LIVE_NOT_ACTIVE_MARKERS = {
    "frontend/typescript/NOT_ACTIVE.md": ["NOT ACTIVE", "frontend/typescript", "default validation"],
    "tests/typescript_importer/NOT_ACTIVE.md": ["NOT ACTIVE", "tests/typescript_importer", "default validation"],
    "scripts/NOT_ACTIVE.md": ["NOT ACTIVE", "scripts/typescript_importer_conformance.py", "default validation"],
}

AUDIT_NOT_ACTIVE_MARKERS = {
    "tooling/NOT_ACTIVE.md": ["NOT ACTIVE", "tooling/agent_api.md", "tooling/explorer_contract.md"],
}

ACTIVE_FOCUS_MARKERS = [
    "Python subset importer",
    "SCIR-H",
    "validator hardening",
]

REMOVED_SURFACE_MARKERS = [
    "EXECUTION_QUEUE.md",
    "build_execution_queue.py",
    "reports/exports/",
]
CAPABILITY_DEPENDENCY_PREFIX = "capability:"


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    # Hash text fixtures after LF normalization so corpus manifests are stable
    # across Windows and Unix checkouts.
    return "sha256:" + hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def matches_type(value, expected_type):
    if isinstance(expected_type, list):
        return any(matches_type(value, item) for item in expected_type)
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": is_number(value),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected_type, True)


def normalize_for_uniqueness(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _fallback_validation_errors(instance, schema, path="$"):
    failures = []
    expected_type = schema.get("type")
    if expected_type is not None and not matches_type(instance, expected_type):
        return [(path, f"expected type {expected_type!r}")]

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        additional = schema.get("additionalProperties", True)
        for key in required:
            if key not in instance:
                failures.append((path, f"missing required property {key}"))
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                failures.extend(_fallback_validation_errors(value, properties[key], child_path))
            elif additional is False:
                failures.append((path, f"unexpected property {key}"))
            elif isinstance(additional, dict):
                failures.extend(_fallback_validation_errors(value, additional, child_path))

    if isinstance(instance, list):
        if schema.get("uniqueItems"):
            normalized = [normalize_for_uniqueness(item) for item in instance]
            if len(normalized) != len(set(normalized)):
                failures.append((path, "expected unique items"))
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                failures.extend(_fallback_validation_errors(item, item_schema, f"{path}[{index}]"))

    if "enum" in schema and instance not in schema["enum"]:
        failures.append((path, f"expected one of {schema['enum']!r}"))
    if "minLength" in schema and isinstance(instance, str) and len(instance) < schema["minLength"]:
        failures.append((path, f"expected string length >= {schema['minLength']}"))
    if "pattern" in schema and isinstance(instance, str):
        if re.fullmatch(schema["pattern"], instance) is None:
            failures.append((path, f"expected string matching {schema['pattern']!r}"))

    return failures


def collect_instance_validation_errors(instance, schema):
    if Draft202012Validator is None:
        return _fallback_validation_errors(instance, schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: ([str(part) for part in error.absolute_path], error.message),
    )
    failures = []
    for error in errors:
        path = "$"
        for part in error.absolute_path:
            path += f"[{part}]" if isinstance(part, int) else f".{part}"
        failures.append((path, error.message))
    return failures


def capability_dependency_entries(module_manifest: dict | None):
    if not isinstance(module_manifest, dict):
        return set()
    dependencies = module_manifest.get("dependencies", [])
    if not isinstance(dependencies, list):
        return set()
    return {
        dependency
        for dependency in dependencies
        if isinstance(dependency, str) and dependency.startswith(CAPABILITY_DEPENDENCY_PREFIX)
    }


def boundary_capability_entries(boundary_contract: dict | None):
    if not isinstance(boundary_contract, dict):
        return set(), []
    capability_entries = set()
    failures = []
    for entry in boundary_contract.get("capabilities", []):
        if not isinstance(entry, str) or not entry:
            failures.append("capabilities entries must be non-empty strings")
            continue
        if not entry.startswith(CAPABILITY_DEPENDENCY_PREFIX):
            failures.append(
                f"capability entry {entry!r} must use the {CAPABILITY_DEPENDENCY_PREFIX}<name> form"
            )
            continue
        capability_entries.add(entry)
    return capability_entries, failures


def validate_boundary_capability_contract(
    module_manifest: dict | None,
    boundary_contract: dict | None,
    *,
    label: str,
    allow_capabilities: bool,
):
    failures = []
    capability_imports = capability_dependency_entries(module_manifest)
    boundary_capabilities, capability_failures = boundary_capability_entries(boundary_contract)
    for item in capability_failures:
        failures.append(f"{label}: {item}")

    if not allow_capabilities:
        if boundary_capabilities:
            failures.append(f"{label}: non-boundary fixtures must not declare capability requirements")
        if capability_imports:
            failures.append(f"{label}: non-boundary fixtures must not declare capability imports {sorted(capability_imports)!r}")
        return failures

    missing_capabilities = sorted(boundary_capabilities - capability_imports)
    if missing_capabilities:
        failures.append(f"{label}: missing capability imports for boundary requirements {missing_capabilities!r}")

    unused_capabilities = sorted(capability_imports - boundary_capabilities)
    if unused_capabilities:
        failures.append(f"{label}: unused capability imports not referenced by the boundary contract {unused_capabilities!r}")

    return failures


def validate_instance(root: pathlib.Path, payload, schema_rel: str, label: str) -> list[str]:
    schema = load_json(root / schema_rel)
    return [f"{label} {path}: {message}" for path, message in collect_instance_validation_errors(payload, schema)]


def check_required_files(root: pathlib.Path, required_files: list[str]) -> list[str]:
    return [f"missing file: {rel}" for rel in required_files if not (root / rel).exists()]


def check_focus_alignment(root: pathlib.Path) -> list[str]:
    failures = []
    focus_text = (root / "CURRENT_FOCUS.md").read_text(encoding="utf-8")
    backlog_text = (root / "BACKLOG.md").read_text(encoding="utf-8")
    readme_text = (root / "README.md").read_text(encoding="utf-8")
    architecture_text = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
    boundary_text = (root / "SYSTEM_BOUNDARY.md").read_text(encoding="utf-8")
    for marker in ACTIVE_FOCUS_MARKERS:
        for rel, text in [
            ("CURRENT_FOCUS.md", focus_text),
            ("README.md", readme_text),
            ("ARCHITECTURE.md", architecture_text),
            ("SYSTEM_BOUNDARY.md", boundary_text),
        ]:
            if marker not in text:
                failures.append(f"{rel}: missing active-focus marker {marker!r}")
    if "## Frozen support work" not in backlog_text:
        failures.append("BACKLOG.md: missing frozen support work section")
    plan_rel = "plans/2026-04-10-repo-reset-consolidation.md"
    if plan_rel not in focus_text:
        failures.append("CURRENT_FOCUS.md: active plan link missing")
    plan_path = root / plan_rel
    if not plan_path.exists():
        failures.append(f"CURRENT_FOCUS.md: active plan missing {plan_rel}")
    else:
        plan_text = plan_path.read_text(encoding="utf-8")
        if "Status: in-progress" not in plan_text and "Status: complete" not in plan_text:
            failures.append(f"{plan_rel}: expected Status: in-progress or Status: complete")
    return failures


def check_decision_register(root: pathlib.Path) -> list[str]:
    text = (root / "DECISION_REGISTER.md").read_text(encoding="utf-8")
    failures = []
    for marker in ["| ID | Status | Decision | Constraint imposed | Reversible | First validation |", "DR-001", "DR-008"]:
        if marker not in text:
            failures.append(f"DECISION_REGISTER.md: missing marker {marker!r}")
    if "EXECUTION_QUEUE" in text:
        failures.append("DECISION_REGISTER.md: queue-era surface should not remain in the decision register")
    return failures


def check_removed_surface_references(root: pathlib.Path) -> list[str]:
    failures = []
    for rel in [
        "README.md",
        "AGENTS.md",
        "CURRENT_FOCUS.md",
        "BACKLOG.md",
        "ARCHITECTURE.md",
        "REPO_MAP.md",
        "VALIDATION_STRATEGY.md",
        "reports/README.md",
        "scripts/run_repo_validation.py",
        "Makefile",
    ]:
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in REMOVED_SURFACE_MARKERS:
            if marker in text:
                failures.append(f"{rel}: stale removed-surface reference {marker!r}")
    return failures


def check_not_active_markers(root: pathlib.Path, marker_map: dict[str, list[str]]) -> list[str]:
    failures = []
    for rel, markers in marker_map.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel}: missing NOT_ACTIVE marker {marker!r}")
    return failures


def check_examples(root: pathlib.Path) -> list[str]:
    failures = []
    for artifact_rel, schema_rel in EXAMPLE_ARTIFACTS:
        payload = load_json(root / artifact_rel)
        failures.extend(validate_instance(root, payload, schema_rel, artifact_rel))
    return failures


def check_manifest_hashes(root: pathlib.Path, manifest_rel: str, schema_rel: str) -> list[str]:
    manifest = load_json(root / manifest_rel)
    failures = validate_instance(root, manifest, schema_rel, manifest_rel)
    for fixture in manifest.get("fixtures", []):
        path = root / fixture["path"]
        if not path.exists():
            failures.append(f"{manifest_rel}: missing fixture path {fixture['path']}")
            continue
        if fixture.get("hash") != sha256_file(path):
            failures.append(f"{manifest_rel}: hash drift for {fixture['path']}")
        boundary_contract = fixture.get("boundary_contract_path")
        if boundary_contract and not (root / boundary_contract).exists():
            failures.append(f"{manifest_rel}: missing boundary contract {boundary_contract}")
    return failures


def check_sweep_manifest(root: pathlib.Path, manifest_rel: str) -> list[str]:
    manifest = load_json(root / manifest_rel)
    failures = validate_instance(root, manifest, "schemas/sweep_manifest.schema.json", manifest_rel)
    corpus_manifest_rel = manifest.get("corpus_manifest")
    if corpus_manifest_rel and not (root / corpus_manifest_rel).exists():
        failures.append(f"{manifest_rel}: referenced corpus manifest missing {corpus_manifest_rel}")
    return failures


def run_checks(root: pathlib.Path, *, include_audit: bool = False) -> list[str]:
    failures = []
    failures.extend(check_required_files(root, LIVE_REQUIRED_FILES))
    if include_audit:
        failures.extend(check_required_files(root, AUDIT_REQUIRED_FILES))
    if failures:
        return failures
    failures.extend(check_focus_alignment(root))
    failures.extend(check_decision_register(root))
    failures.extend(check_removed_surface_references(root))
    failures.extend(check_not_active_markers(root, LIVE_NOT_ACTIVE_MARKERS))
    if include_audit:
        failures.extend(check_not_active_markers(root, AUDIT_NOT_ACTIVE_MARKERS))
    failures.extend(check_examples(root))
    failures.extend(check_manifest_hashes(root, "tests/invalid_scir_h/manifest.json", "schemas/corpus_manifest.schema.json"))
    failures.extend(check_manifest_hashes(root, "tests/invalid_scir_l/manifest.json", "schemas/corpus_manifest.schema.json"))
    failures.extend(check_manifest_hashes(root, "tests/corpora/python_tier_a_micro_corpus.json", "schemas/corpus_manifest.schema.json"))
    failures.extend(check_manifest_hashes(root, "tests/corpora/python_proof_loop_corpus.json", "schemas/corpus_manifest.schema.json"))
    failures.extend(check_manifest_hashes(root, "tests/corpora/python_preservation_negative_corpus.json", "schemas/corpus_manifest.schema.json"))
    failures.extend(check_sweep_manifest(root, "tests/sweeps/python_proof_loop_smoke.json"))
    failures.extend(check_sweep_manifest(root, "tests/sweeps/python_proof_loop_full.json"))
    return failures


def mutate_remove_required_file(root: pathlib.Path) -> None:
    (root / "CURRENT_FOCUS.md").unlink()


def mutate_break_focus_alignment(root: pathlib.Path) -> None:
    path = root / "README.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("validator hardening", "validator work", 1), encoding="utf-8")


def mutate_remove_audit_file(root: pathlib.Path) -> None:
    (root / "tooling" / "README.md").unlink()


def run_negative_fixture(
    root: pathlib.Path,
    name: str,
    mutate,
    expected_markers: list[str],
    *,
    include_audit: bool = False,
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="scir_repo_check_") as tmp:
        fixture_root = pathlib.Path(tmp) / "repo"
        shutil.copytree(root, fixture_root, ignore=shutil.ignore_patterns(".git", "__pycache__", "artifacts"))
        mutate(fixture_root)
        failures = run_checks(fixture_root, include_audit=include_audit)
    if not failures:
        return [f"self-test {name}: expected failure but validation passed"]
    missing = [marker for marker in expected_markers if not any(marker in failure for failure in failures)]
    if missing:
        return [f"self-test {name}: missing expected failure markers {', '.join(missing)}"]
    return []


def run_self_tests(root: pathlib.Path) -> list[str]:
    failures = []
    failures.extend(
        run_negative_fixture(root, "missing required file", mutate_remove_required_file, ["missing file: CURRENT_FOCUS.md"])
    )
    failures.extend(
        run_negative_fixture(
            root,
            "focus drift",
            mutate_break_focus_alignment,
            ["README.md: missing active-focus marker 'validator hardening'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "missing audit file",
            mutate_remove_audit_file,
            ["missing file: tooling/README.md"],
            include_audit=True,
        )
    )
    return failures


def print_success(mode: str, *, self_test_count: int | None = None) -> None:
    if mode == "audit":
        print("[audit] retained-surface repository audit passed")
        print(
            "Checked live blockers plus retained docs, placeholder surfaces, CI docs, and auxiliary contracts "
            "kept on disk outside the default blocking surface."
        )
    else:
        print(f"[{mode}] repository contract validation passed")
        print(
            "Checked live-surface blockers, current-focus alignment, removed-surface cleanup, TypeScript quarantine markers, "
            "schema-valid examples, and manifest hash integrity for active and negative corpora."
        )
    if mode == "test" and self_test_count is not None:
        print(f"Repository checker self-tests passed ({self_test_count} negative fixtures).")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="validate", choices=["audit", "test", "validate"])
    parser.add_argument("--root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve() if args.root else ROOT
    include_audit = args.mode in {"audit", "test"}
    failures = run_checks(root, include_audit=include_audit)
    if failures:
        print(f"[{args.mode}] repository contract validation failed")
        for item in failures:
            print(f" - {item}")
        return 1

    self_test_count = None
    if args.mode == "test":
        self_test_failures = run_self_tests(root)
        self_test_count = 3
        if self_test_failures:
            print("[test] repository contract self-tests failed")
            for item in self_test_failures:
                print(f" - {item}")
            return 1

    print_success(args.mode, self_test_count=self_test_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
