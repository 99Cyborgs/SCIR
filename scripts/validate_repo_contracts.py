#!/usr/bin/env python3
"""File: scripts/validate_repo_contracts.py
Purpose: Enforce the frozen repository contract for the active SCIR MVP surface.
Role in system: Acts as the repo-level integrity gate used by validation, build, and importer checks to catch drift between specs, docs, examples, manifests, and retained support surfaces.
Key dependencies: jsonschema (optional), scir_python_bootstrap.PYTHON_PROOF_LOOP_METADATA, wasm_backend_metadata.WASM_BACKEND_METADATA, benchmark_contract_metadata.TRACK_C_MVP_POSTURE.
Side effects: Reads many repository files, hashes fixtures, validates example JSON artifacts, and in self-test mode clones the repo into temporary directories and mutates copies to verify expected failures.
"""
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

from scir_python_bootstrap import PYTHON_PROOF_LOOP_METADATA
from wasm_backend_metadata import WASM_BACKEND_METADATA
from benchmark_contract_metadata import TRACK_C_MVP_POSTURE


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
    "Frozen and retired",
    "strong-baseline falsification",
    "SCIR_USEFUL_BUT_UNNECESSARY",
]
ACTIVE_PLAN_REL = "plans/2026-04-13-project-freeze-retirement-summary.md"
ACTIVE_ITEM_MARKER = "retirement record"
EXECUTABLE_SUBSET_REQUIRED_MARKERS = {
    "specs/scir_h_spec.md": [
        "| `loop` | yes | exact fixed proof-loop shapes are executable; broader forms remain deferred |",
        "| `break` | yes | exact fixed proof-loop shapes are executable; broader forms remain deferred |",
        "| `continue` | yes | exact fixed proof-loop shapes are executable; broader forms remain deferred |",
    ],
    "specs/validator_invariants.md": [
        "the fixed `b_while_call_update` and `b_while_break_continue` loop-control slices are admitted through lowering and reconstruction; broader loop forms remain deferred",
    ],
    "scripts/scir_h_bootstrap_model.py": [
        '"construct": "`loop`"',
        '"spec_downstream_status": "exact fixed proof-loop shapes are executable; broader forms remain deferred"',
        '"construct": "single-handler `try` / `catch name Type`"',
        '"spec_downstream_status": "exact single-handler `ValueError` proof-loop slice only; broader forms importer-only or deferred"',
    ],
    "SPEC_COMPLETENESS_CHECKLIST.md": [
        "| `loop` | yes | yes | yes | yes for the exact `b_while_call_update` and `b_while_break_continue` slices | yes for the exact `b_while_call_update` and `b_while_break_continue` slices | yes | subset-bound executable support | kept as exact-shape proof-loop support; broader loop forms remain deferred |",
        "| `break` | yes | yes | yes | yes for the exact `b_while_break_continue` slice | yes for the exact `b_while_break_continue` slice | yes | subset-bound executable support | kept as an exact-shape proof-loop control form; broader break forms remain deferred |",
        "| `continue` | yes | yes | yes | yes for the exact `b_while_break_continue` slice | yes for the exact `b_while_break_continue` slice | yes | subset-bound executable support | kept as an exact-shape proof-loop control form; broader continue forms remain deferred |",
    ],
    "frontend/python/IMPORT_SCOPE.md": [
        "There are no active importer-only Python fixture cases in the frozen MVP corpus.",
    ],
    "frontend/python/AGENTS.md": [
        "do not reclassify any of those cases back to importer-only",
    ],
    "tests/README.md": [
        "fixture bundles for the active Python importer proof loop plus the explicit rejected case",
    ],
}
EXECUTABLE_SUBSET_FORBIDDEN_MARKERS = {
    "specs/scir_h_spec.md": [
        "canonical parser/validator surface only; importer-only beyond that",
    ],
    "specs/validator_invariants.md": [
        "loop forms may exist in importer-only `SCIR-H` slices without active lowering",
    ],
    "scripts/scir_h_bootstrap_model.py": [
        '"spec_downstream_status": "canonical parser/validator surface only; importer-only beyond that"',
    ],
    "SPEC_COMPLETENESS_CHECKLIST.md": [
        "| `loop` | yes | yes | validator-only | no | no | yes | canonical parser/validator surface only | kept as importer-only `SCIR-H` surface beyond parser/validator |",
        "| `break` | yes | yes | validator-only | no | no | yes | canonical parser/validator surface only | kept as importer-only `SCIR-H` surface beyond parser/validator |",
        "| `continue` | yes | yes | validator-only | no | no | yes | canonical parser/validator surface only | kept as importer-only `SCIR-H` surface beyond parser/validator |",
    ],
    "docs/project_overview.md": [
        "importer-only Tier `B` `SCIR-H` evidence cases",
    ],
    "frontend/python/AGENTS.md": [
        "keep importer-only follow-on function and async cases Tier `B`",
    ],
    "tests/README.md": [
        "active Python importer proof loop and importer-only follow-on cases",
    ],
}
BACKLOG_DECISION_MARKER = (
    "Keep broader object and exception semantics beyond the exact admitted class and `d_try_except` slices rejected or deferred until new canonical fixtures and decision-register updates exist."
)
RECONSTRUCTION_POLICY_DRIFT_CASE_MARKER = "d_try_except"
FROZEN_PYTHON_EXECUTABLE_CASES = [
    "a_basic_function",
    "a_async_await",
    "b_direct_call",
    "c_opaque_call",
    "b_if_else_return",
    "b_async_arg_await",
    "b_while_call_update",
    "b_while_break_continue",
    "b_class_init_method",
    "b_class_field_update",
    "d_try_except",
]
FROZEN_PYTHON_IMPORTER_ONLY_CASES = []
FROZEN_PYTHON_REJECTED_CASES = ["d_exec_eval"]
FROZEN_PYTHON_BOUNDARY_ONLY_CASES = ["c_opaque_call"]
FROZEN_PYTHON_WASM_EMITTABLE_CASES = [
    "a_basic_function",
    "b_direct_call",
    "b_if_else_return",
]
IMPLEMENTATION_PHASE_FREEZE_MARKERS = [
    "Phase 2 exit gate is satisfied by the fixed 11-case Python proof loop.",
    "The active item after Phase 2 completion is post-proof-loop freeze enforcement and contract reset, not further Python widening.",
    "Phase 3 is not auto-activated; Rust remains importer-first for the remainder of the MVP, and any future Rust proof-loop, backend, or benchmark activation is a post-MVP reactivation decision.",
    "Phase 4 is not auto-activated; helper-free Wasm remains a bounded retained support lane for the remainder of the MVP, and any future Wasm widening, backend activation, or benchmark promotion is a post-MVP reactivation decision.",
    "Phase 6 is not auto-activated; Track `C` remains a retained non-default diagnostic pilot for the remainder of the MVP, and any future promotion into the default executable gate or broader benchmark claim surface is a post-MVP reactivation decision.",
]
RUST_SUPPORT_FREEZE_MARKERS = [
    "The Rust MVP scope is importer-only safe-subset evidence.",
    "Rust importer evidence is retained for the MVP as importer-first support only.",
    "It must not be presented as an active round-trip, backend, or benchmark claim unless a post-MVP reactivation decision updates the root roadmap, benchmark strategy, and repo-contract surfaces together.",
]
README_WASM_FREEZE_MARKERS = [
    "Helper-free Wasm remains retained backend evidence only for the MVP; it is not the next automatic implementation phase, and any future backend widening requires a fresh post-MVP reactivation decision.",
]
ARCHITECTURE_WASM_FREEZE_MARKERS = [
    "Wasm remains a retained bounded backend surface aligned to the same derivative `SCIR-L` contract and is not an auto-activating post-proof-loop implementation lane.",
]
BACKEND_SURFACE_FREEZE_MARKERS = [
    "Only Wasm is a retained backend surface in the MVP.",
    "That surface remains bounded and validated on disk, but it is not an active scope-expansion lane.",
    "Any future Wasm widening or backend activation is a post-MVP reactivation decision that must update roadmap, profile/preservation doctrine, and repo-contract surfaces together.",
]
WASM_SUPPORT_FREEZE_MARKERS = [
    "Wasm is the retained helper-free reference backend surface for the current MVP boundary.",
    "It remains validated and preserved on disk, but it is not the current widening target.",
    "It must not be presented as an active backend-expansion or benchmark lane unless a post-MVP reactivation decision updates the root roadmap, benchmark strategy, target-profile and preservation docs, and repo-contract surfaces together.",
]
TARGET_PROFILE_FREEZE_MARKERS = [
    "Profile `P` remains active only for the bounded helper-free Wasm support lane; it is not the current widening target.",
    "Any future profile-`P` widening or backend activation requires a post-MVP reactivation decision.",
]
PRESERVATION_WASM_FREEZE_MARKERS = [
    "That slice remains retained support evidence only for the MVP. It does not auto-activate a new backend implementation phase, and any future Wasm widening requires a post-MVP reactivation decision plus synchronized roadmap and contract updates.",
]
TRACK_C_FREEZE_MARKERS = [
    "Track `C` is conditional.",
    "It remains non-default, and the checked-in sample artifacts stay outside the default executable benchmark gate.",
    "do not promote to default executable gate",
    *TRACK_C_MVP_POSTURE,
]
TRACK_C_TRACKS_DOC_MARKERS = [
    "retained non-default pilot only",
    "retain bounded diagnostic pilot",
    "do not promote to default executable gate",
    *TRACK_C_MVP_POSTURE,
]
TRACK_C_METADATA_MARKERS = [
    *TRACK_C_MVP_POSTURE,
    '"mvp_posture": list(TRACK_C_MVP_POSTURE)',
]
RUST_BENCHMARK_FREEZE_MARKERS = [
    "Rust importer evidence remains outside the active benchmark corpus and outside active benchmark claims for the MVP.",
]
WASM_BENCHMARK_FREEZE_MARKERS = [
    "Helper-free Wasm evidence remains outside the active benchmark corpus and outside active benchmark claims for the MVP.",
]
TYPESCRIPT_ARCHIVE_PROFILES = ["D-JS"]
VALIDATION_PIPELINE_REQUIRED_MARKERS = [
    "repo-contract checks",
    "importer fixture conformance",
    "bootstrap pipeline validation",
    "sweep smoke plus regression, comparison, and contamination summaries",
]
VALIDATION_PIPELINE_FORBIDDEN_MARKERS = [
    "validate derived exports",
]

REMOVED_SURFACE_MARKERS = [
    "EXECUTION_QUEUE.md",
    "build_execution_queue.py",
    "reports/exports/",
]
CAPABILITY_DEPENDENCY_PREFIX = "capability:"


def load_json(path: pathlib.Path):
    """Purpose: Read a UTF-8 JSON file into Python objects for contract checks."""
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    """Purpose: Compute the repository's canonical text hash for fixture files.

    Inputs:
      - path: pathlib.Path for the on-disk artifact being fingerprinted.
    Outputs:
      - str: ``sha256:<digest>`` after line-ending normalization.
    Side Effects:
      - Reads file bytes from disk.
    Assumptions:
      - The file is small enough to read into memory in one shot.
    Failure Modes:
      - Propagates filesystem errors if the file is missing or unreadable.
    """
    # Hash text fixtures after LF normalization so corpus manifests are stable
    # across Windows and Unix checkouts.
    return "sha256:" + hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def canonical_json_hash(payload) -> str:
    """Purpose: Hash structured JSON content using the repo's canonical serialization."""
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def is_number(value):
    """Purpose: Treat ints and floats as numbers while excluding booleans."""
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def matches_type(value, expected_type):
    """Purpose: Evaluate a JSON Schema ``type`` constraint for the fallback validator."""
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
    """Purpose: Canonicalize JSON-like values before comparing ``uniqueItems`` semantics."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _fallback_validation_errors(instance, schema, path="$"):
    """Purpose: Provide a small schema-validation fallback when ``jsonschema`` is unavailable.

    Inputs:
      - instance: JSON-like value being validated.
      - schema: Schema fragment expressed as a Python mapping.
      - path: JSON pointer-like location used for error reporting.
    Outputs:
      - list[tuple[str, str]]: ``(path, message)`` pairs describing validation failures.
    Side Effects:
      - None.
    Assumptions:
      - Only the subset of schema features encoded here is required for repo-contract checks.
    Failure Modes:
      - Deliberately ignores unsupported schema keywords rather than approximating them incorrectly.
    """
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
    """Purpose: Collect validation failures using ``jsonschema`` when installed, or the fallback checker otherwise."""
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
    """Purpose: Extract capability-prefixed dependency declarations from a module manifest."""
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
    """Purpose: Parse and validate capability requirements declared by an opaque-boundary contract."""
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
    """Purpose: Enforce that boundary capability imports and boundary contracts stay synchronized.

    Inputs:
      - module_manifest: Optional module manifest payload for one fixture.
      - boundary_contract: Optional opaque-boundary contract payload for the same fixture.
      - label: Human-readable prefix for emitted failures.
      - allow_capabilities: Whether this fixture is allowed to declare host capability requirements.
    Outputs:
      - list[str]: Human-readable validation failures.
    Side Effects:
      - None.
    Assumptions:
      - Only boundary fixtures may import or declare host capabilities.
    Failure Modes:
      - Reports malformed capability entries, missing imports, and unused imports.
    """
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
    """Purpose: Validate one JSON payload against a repository schema and prefix the resulting failures."""
    schema = load_json(root / schema_rel)
    return [f"{label} {path}: {message}" for path, message in collect_instance_validation_errors(payload, schema)]


def check_required_files(root: pathlib.Path, required_files: list[str]) -> list[str]:
    """Purpose: Confirm that all files in a required-surface list still exist on disk."""
    return [f"missing file: {rel}" for rel in required_files if not (root / rel).exists()]


def markdown_bullets_under_heading(text: str, heading: str) -> list[str] | None:
    """Purpose: Read a flat bullet list under a specific Markdown heading for cross-doc drift checks."""
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return None

    items = []
    for line in lines[start + 1 :]:
        if line.startswith("## ") or line.startswith("### "):
            break
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            if item.startswith("`") and item.endswith("`"):
                item = item[1:-1]
            items.append(item)
    return items


def check_focus_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Enforce that the root roadmap documents share the same frozen-focus markers."""
    failures = []
    focus_text = (root / "CURRENT_FOCUS.md").read_text(encoding="utf-8")
    backlog_text = (root / "BACKLOG.md").read_text(encoding="utf-8")
    readme_text = (root / "README.md").read_text(encoding="utf-8")
    architecture_text = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
    boundary_text = (root / "SYSTEM_BOUNDARY.md").read_text(encoding="utf-8")
    # Literal marker matching is intentional here: phase wording drift across the
    # root docs is treated as contract drift, not as harmless editorial variance.
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
    if ACTIVE_ITEM_MARKER not in focus_text:
        failures.append(f"CURRENT_FOCUS.md: missing active-item marker {ACTIVE_ITEM_MARKER!r}")
    if BACKLOG_DECISION_MARKER not in backlog_text:
        failures.append("BACKLOG.md: next-decision marker drifted from the frozen proof-loop reset")
    if ACTIVE_PLAN_REL not in focus_text:
        failures.append("CURRENT_FOCUS.md: active plan link missing")
    plan_path = root / ACTIVE_PLAN_REL
    if not plan_path.exists():
        failures.append(f"CURRENT_FOCUS.md: active plan missing {ACTIVE_PLAN_REL}")
    else:
        plan_text = plan_path.read_text(encoding="utf-8")
        if "Status: in-progress" not in plan_text and "Status: complete" not in plan_text:
            failures.append(f"{ACTIVE_PLAN_REL}: expected Status: in-progress or Status: complete")
    return failures


def check_python_import_scope_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Verify that Python importer scope docs mirror the canonical proof-loop metadata."""
    failures = []
    text = (root / "frontend" / "python" / "IMPORT_SCOPE.md").read_text(encoding="utf-8")
    executable_cases = markdown_bullets_under_heading(text, "### Executable proof-loop cases")
    importer_only_cases = markdown_bullets_under_heading(text, "### Importer-only canonical `SCIR-H` cases")
    if executable_cases is None:
        failures.append("frontend/python/IMPORT_SCOPE.md: missing executable proof-loop cases section")
    elif executable_cases != PYTHON_PROOF_LOOP_METADATA["executable_cases"]:
        failures.append(
            "frontend/python/IMPORT_SCOPE.md: executable proof-loop case list drifted from PYTHON_PROOF_LOOP_METADATA"
        )
    if importer_only_cases is None:
        failures.append("frontend/python/IMPORT_SCOPE.md: missing importer-only canonical `SCIR-H` cases section")
    elif importer_only_cases != PYTHON_PROOF_LOOP_METADATA["importer_only_cases"]:
        failures.append(
            "frontend/python/IMPORT_SCOPE.md: importer-only case list drifted from PYTHON_PROOF_LOOP_METADATA"
        )
    return failures


def check_reconstruction_policy_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Keep reconstruction-policy documentation aligned with the active executable Python cases."""
    failures = []
    text = (root / "docs" / "reconstruction_policy.md").read_text(encoding="utf-8")
    active_cases = markdown_bullets_under_heading(text, "## Active reconstruction cases")
    if active_cases is None:
        failures.append("docs/reconstruction_policy.md: missing active reconstruction cases section")
    elif active_cases != PYTHON_PROOF_LOOP_METADATA["executable_cases"]:
        failures.append(
            "docs/reconstruction_policy.md: active reconstruction cases drifted from PYTHON_PROOF_LOOP_METADATA executable cases"
        )
    return failures


def check_executable_subset_truth_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Detect wording drift around the exact executable subset admitted by the frozen MVP."""
    failures = []
    for rel, markers in EXECUTABLE_SUBSET_REQUIRED_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel}: missing executable-subset truth marker {marker!r}")
    for rel, markers in EXECUTABLE_SUBSET_FORBIDDEN_MARKERS.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker in text:
                failures.append(f"{rel}: stale executable-subset wording {marker!r}")
    return failures


def check_frozen_python_proof_loop_contract(root: pathlib.Path) -> list[str]:
    """Purpose: Prove that the active Python proof-loop corpus, contracts, and Wasm slice remain frozen together.

    Inputs:
      - root: Repository root used to read metadata and corpus files.
    Outputs:
      - list[str]: Contract failures for executable-case membership, benchmark scope, boundary-only cases, and Wasm-emittable coverage.
    Side Effects:
      - Reads bootstrap metadata and corpus manifests from disk.
    Assumptions:
      - The 11-case Python proof loop is the current canonical executable corpus.
    Failure Modes:
      - Flags any mismatch between bootstrap metadata, corpus splits, fixture IDs, or per-case preservation-stage expectations.
    """
    failures = []
    metadata = PYTHON_PROOF_LOOP_METADATA
    expected_fixture_ids = [f"fixture.python_importer.{case_name}" for case_name in FROZEN_PYTHON_EXECUTABLE_CASES]
    if metadata["executable_cases"] != FROZEN_PYTHON_EXECUTABLE_CASES:
        failures.append(
            "scripts/scir_python_bootstrap.py: frozen Python executable-case set drifted from the active MVP corpus"
        )
    if metadata["benchmark_cases"] != FROZEN_PYTHON_EXECUTABLE_CASES:
        failures.append(
            "scripts/scir_python_bootstrap.py: frozen Python benchmark-case set must remain the executable-case set"
        )
    if metadata["importer_only_cases"] != FROZEN_PYTHON_IMPORTER_ONLY_CASES:
        failures.append(
            "scripts/scir_python_bootstrap.py: frozen Python importer-only case set must remain empty"
        )
    if metadata["rejected_cases"] != FROZEN_PYTHON_REJECTED_CASES:
        failures.append(
            "scripts/scir_python_bootstrap.py: frozen Python rejected-case set drifted from the active MVP corpus"
        )
    contract_cases = list(metadata["executable_case_contracts"].keys())
    if contract_cases != FROZEN_PYTHON_EXECUTABLE_CASES:
        failures.append(
            "scripts/scir_python_bootstrap.py: executable case contracts drifted from the frozen Python executable-case set"
        )
    boundary_only_cases = [
        case_name
        for case_name, contract in metadata["executable_case_contracts"].items()
        if contract["requires_opaque_boundary"]
    ]
    if boundary_only_cases != FROZEN_PYTHON_BOUNDARY_ONLY_CASES:
        failures.append(
            "scripts/scir_python_bootstrap.py: frozen Python boundary-only executable-case set drifted from the active MVP corpus"
        )
    wasm_emittable_cases = [
        case_name
        for case_name, contract in metadata["executable_case_contracts"].items()
        if contract["wasm_emittable"]
    ]
    if wasm_emittable_cases != FROZEN_PYTHON_WASM_EMITTABLE_CASES:
        failures.append(
            "scripts/scir_python_bootstrap.py: frozen helper-free Wasm-emittable Python case set drifted from the active MVP corpus"
        )
    corpus = load_json(root / "tests" / "corpora" / "python_proof_loop_corpus.json")
    if corpus.get("split_contract", {}).get("test") != expected_fixture_ids:
        failures.append(
            "tests/corpora/python_proof_loop_corpus.json: split_contract.test drifted from the frozen Python executable-case set"
        )
    fixture_ids = [fixture.get("id") for fixture in corpus.get("fixtures", [])]
    if fixture_ids != expected_fixture_ids:
        failures.append(
            "tests/corpora/python_proof_loop_corpus.json: fixture id list drifted from the frozen Python executable-case set"
        )
    observed_wasm_fixture_ids = []
    for fixture in corpus.get("fixtures", []):
        stage_behavior = fixture.get("expected_preservation_stage_behavior", {})
        pipeline_stages = fixture.get("pipeline_stages", [])
        has_wasm = "l_to_wasm" in stage_behavior or "l_to_wasm" in pipeline_stages
        if has_wasm:
            observed_wasm_fixture_ids.append(fixture["id"])
    expected_wasm_fixture_ids = [f"fixture.python_importer.{case_name}" for case_name in FROZEN_PYTHON_WASM_EMITTABLE_CASES]
    if observed_wasm_fixture_ids != expected_wasm_fixture_ids:
        failures.append(
            "tests/corpora/python_proof_loop_corpus.json: helper-free Wasm stage coverage drifted from the frozen emittable Python case set"
        )
    return failures


def check_support_lane_freeze_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Ensure Rust, Wasm, and Track C remain documented as retained support lanes rather than active widening targets."""
    failures = []
    readme_text = (root / "README.md").read_text(encoding="utf-8")
    architecture_text = (root / "ARCHITECTURE.md").read_text(encoding="utf-8")
    implementation_text = (root / "IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
    rust_text = (root / "frontend" / "rust" / "IMPORT_SCOPE.md").read_text(encoding="utf-8")
    backend_text = (root / "backends" / "README.md").read_text(encoding="utf-8")
    wasm_text = (root / "backends" / "wasm" / "README.md").read_text(encoding="utf-8")
    target_profiles_text = (root / "docs" / "target_profiles.md").read_text(encoding="utf-8")
    preservation_text = (root / "docs" / "preservation_contract.md").read_text(encoding="utf-8")
    benchmark_text = (root / "BENCHMARK_STRATEGY.md").read_text(encoding="utf-8")
    benchmark_tracks_text = (root / "benchmarks" / "tracks.md").read_text(encoding="utf-8")
    benchmark_metadata_text = (root / "scripts" / "benchmark_contract_metadata.py").read_text(encoding="utf-8")

    for marker in README_WASM_FREEZE_MARKERS:
        if marker not in readme_text:
            failures.append(f"README.md: missing Wasm freeze marker {marker!r}")
    for marker in ARCHITECTURE_WASM_FREEZE_MARKERS:
        if marker not in architecture_text:
            failures.append(f"ARCHITECTURE.md: missing Wasm freeze marker {marker!r}")
    for marker in IMPLEMENTATION_PHASE_FREEZE_MARKERS:
        if marker not in implementation_text:
            failures.append(f"IMPLEMENTATION_PLAN.md: missing phase-freeze marker {marker!r}")
    for marker in RUST_SUPPORT_FREEZE_MARKERS:
        if marker not in rust_text:
            failures.append(f"frontend/rust/IMPORT_SCOPE.md: missing Rust freeze marker {marker!r}")
    for marker in BACKEND_SURFACE_FREEZE_MARKERS:
        if marker not in backend_text:
            failures.append(f"backends/README.md: missing Wasm backend-surface marker {marker!r}")
    for marker in WASM_SUPPORT_FREEZE_MARKERS:
        if marker not in wasm_text:
            failures.append(f"backends/wasm/README.md: missing Wasm freeze marker {marker!r}")
    for marker in TARGET_PROFILE_FREEZE_MARKERS:
        if marker not in target_profiles_text:
            failures.append(f"docs/target_profiles.md: missing Wasm profile-freeze marker {marker!r}")
    for marker in PRESERVATION_WASM_FREEZE_MARKERS:
        if marker not in preservation_text:
            failures.append(f"docs/preservation_contract.md: missing Wasm preservation-freeze marker {marker!r}")
    for marker in TRACK_C_FREEZE_MARKERS:
        if marker not in benchmark_text:
            failures.append(f"BENCHMARK_STRATEGY.md: missing Track C freeze marker {marker!r}")
    for marker in TRACK_C_TRACKS_DOC_MARKERS:
        if marker not in benchmark_tracks_text:
            failures.append(f"benchmarks/tracks.md: missing Track C freeze marker {marker!r}")
    for marker in TRACK_C_METADATA_MARKERS:
        if marker not in benchmark_metadata_text:
            failures.append(f"scripts/benchmark_contract_metadata.py: missing Track C freeze marker {marker!r}")
    for marker in RUST_BENCHMARK_FREEZE_MARKERS:
        if marker not in benchmark_text:
            failures.append(f"BENCHMARK_STRATEGY.md: missing Rust benchmark-freeze marker {marker!r}")
    for marker in WASM_BENCHMARK_FREEZE_MARKERS:
        if marker not in benchmark_text:
            failures.append(f"BENCHMARK_STRATEGY.md: missing Wasm benchmark-freeze marker {marker!r}")
    return failures


def check_wasm_backend_scope_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Cross-check Wasm backend documentation against the authoritative backend metadata tables."""
    failures = []
    wasm_text = (root / "backends" / "wasm" / "README.md").read_text(encoding="utf-8")
    lowering_text = (root / "LOWERING_CONTRACT.md").read_text(encoding="utf-8")

    expected_python_modules = [
        *(f"fixture.python_importer.{case_name}" for case_name in WASM_BACKEND_METADATA["emittable_python_cases"])
    ]
    expected_rust_modules = [
        *(f"fixture.rust_importer.{case_name}" for case_name in WASM_BACKEND_METADATA["emittable_rust_cases"])
    ]

    for heading, expected, label in [
        ("### Admitted Python emitted modules", expected_python_modules, "admitted Python emitted modules"),
        ("### Admitted Rust emitted modules", expected_rust_modules, "admitted Rust emitted modules"),
        ("### Admitted lowering rules", WASM_BACKEND_METADATA["admitted_lowering_rules"], "admitted lowering rules"),
        ("### Non-emittable lowering rules", WASM_BACKEND_METADATA["non_emittable_lowering_rules"], "non-emittable lowering rules"),
    ]:
        observed = markdown_bullets_under_heading(wasm_text, heading)
        if observed is None:
            failures.append(f"backends/wasm/README.md: missing section {heading!r}")
        elif observed != expected:
            failures.append(f"backends/wasm/README.md: {label} drifted from WASM_BACKEND_METADATA")

    for heading, expected, label in [
        ("### Wasm-admitted lowering rules", WASM_BACKEND_METADATA["admitted_lowering_rules"], "Wasm-admitted lowering rules"),
        ("### Wasm-non-emittable lowering rules", WASM_BACKEND_METADATA["non_emittable_lowering_rules"], "Wasm-non-emittable lowering rules"),
    ]:
        observed = markdown_bullets_under_heading(lowering_text, heading)
        if observed is None:
            failures.append(f"LOWERING_CONTRACT.md: missing section {heading!r}")
        elif observed != expected:
            failures.append(f"LOWERING_CONTRACT.md: {label} drifted from WASM_BACKEND_METADATA")

    return failures


def check_decision_register(root: pathlib.Path) -> list[str]:
    """Purpose: Confirm the decision register still carries the frozen MVP constraints and not stale queue-era language."""
    text = (root / "DECISION_REGISTER.md").read_text(encoding="utf-8")
    failures = []
    for marker in [
        "| ID | Status | Decision | Constraint imposed | Reversible | First validation |",
        "DR-001",
        "DR-008",
        "DR-016",
        "DR-017",
        "DR-018",
        "DR-019",
        "11-case Python executable proof loop is frozen as the current MVP corpus",
        "Rust remains importer-first evidence for the remainder of the MVP",
        "Helper-free Wasm remains a bounded retained backend surface for the remainder of the MVP",
        "Track `C` remains a retained non-default diagnostic pilot for the remainder of the MVP",
    ]:
        if marker not in text:
            failures.append(f"DECISION_REGISTER.md: missing marker {marker!r}")
    if "EXECUTION_QUEUE" in text:
        failures.append("DECISION_REGISTER.md: queue-era surface should not remain in the decision register")
    return failures


def check_open_questions_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Verify that resolved Rust-scope questions do not reappear in the active open-questions table."""
    failures = []
    text = (root / "OPEN_QUESTIONS.md").read_text(encoding="utf-8")
    if "OQ-003" in text:
        failures.append("OPEN_QUESTIONS.md: OQ-003 should be resolved and removed after the Rust MVP boundary decision")
    return failures


def check_removed_surface_references(root: pathlib.Path) -> list[str]:
    """Purpose: Catch references to retired files or directories that should no longer appear in live docs and scripts."""
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
    """Purpose: Ensure retained-but-disabled surfaces advertise their quarantine markers explicitly."""
    failures = []
    for rel, markers in marker_map.items():
        text = (root / rel).read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel}: missing NOT_ACTIVE marker {marker!r}")
    return failures


def check_examples(root: pathlib.Path) -> list[str]:
    """Purpose: Validate every checked-in example artifact against its schema contract."""
    failures = []
    for artifact_rel, schema_rel in EXAMPLE_ARTIFACTS:
        payload = load_json(root / artifact_rel)
        failures.extend(validate_instance(root, payload, schema_rel, artifact_rel))
    return failures


def check_manifest_hashes(root: pathlib.Path, manifest_rel: str, schema_rel: str) -> list[str]:
    """Purpose: Validate a corpus manifest and verify that each declared fixture hash still matches the on-disk file."""
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
    """Purpose: Validate a sweep manifest and ensure its referenced corpus manifest still exists."""
    manifest = load_json(root / manifest_rel)
    failures = validate_instance(root, manifest, "schemas/sweep_manifest.schema.json", manifest_rel)
    corpus_manifest_rel = manifest.get("corpus_manifest")
    if corpus_manifest_rel and not (root / corpus_manifest_rel).exists():
        failures.append(f"{manifest_rel}: referenced corpus manifest missing {corpus_manifest_rel}")
    return failures


def check_typescript_archive_surface(root: pathlib.Path) -> list[str]:
    """Purpose: Keep archived TypeScript placeholder cases quarantined from active canonical surfaces."""
    failures = []
    case_root = root / "tests" / "typescript_importer" / "cases"
    if not case_root.exists():
        return failures

    for case_dir in sorted(path for path in case_root.iterdir() if path.is_dir()):
        manifest_path = case_dir / "module_manifest.json"
        if manifest_path.exists():
            manifest = load_json(manifest_path)
            if manifest.get("declared_tier") != "D":
                failures.append(
                    f"{manifest_path.relative_to(root)}: archived TypeScript placeholder cases must remain declared_tier 'D'"
                )
            if manifest.get("declared_profiles") != TYPESCRIPT_ARCHIVE_PROFILES:
                failures.append(
                    f"{manifest_path.relative_to(root)}: archived TypeScript placeholder cases must remain declared_profiles {TYPESCRIPT_ARCHIVE_PROFILES!r}"
                )

        scirh_path = case_dir / "expected.scirh"
        if scirh_path.exists():
            failures.append(
                f"{scirh_path.relative_to(root)}: archived TypeScript placeholder cases must not carry canonical or placeholder SCIR-H text"
            )
    return failures


def check_validation_pipeline_doc(root: pathlib.Path) -> list[str]:
    """Purpose: Ensure CI documentation still describes the current validation pipeline and excludes retired steps."""
    failures = []
    path = root / "ci" / "validation_pipeline.md"
    text = path.read_text(encoding="utf-8")
    for marker in VALIDATION_PIPELINE_REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"ci/validation_pipeline.md: missing validation-pipeline marker {marker!r}")
    for marker in VALIDATION_PIPELINE_FORBIDDEN_MARKERS:
        if marker in text:
            failures.append(f"ci/validation_pipeline.md: stale validation-pipeline marker {marker!r}")
    return failures


def benchmark_case_ids() -> list[str]:
    """Purpose: Derive benchmark fixture IDs directly from the canonical Python proof-loop metadata."""
    return [f"fixture.python_importer.{case_name}" for case_name in PYTHON_PROOF_LOOP_METADATA["benchmark_cases"]]


def check_benchmark_example_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Verify that the checked-in benchmark report example cites the current canonical benchmark case set."""
    failures = []
    expected_case_ids = benchmark_case_ids()
    report = load_json(root / "reports" / "examples" / "benchmark_report.example.json")
    lineage = report.get("scir_h_lineage_references", {})
    if set(lineage.keys()) != set(expected_case_ids) or len(lineage) != len(expected_case_ids):
        failures.append(
            "reports/examples/benchmark_report.example.json: scir_h_lineage_references drifted from PYTHON_PROOF_LOOP_METADATA benchmark cases"
        )
    claim_gate = report.get("claim_gate", {})
    for idx, condition in enumerate(claim_gate.get("evaluated_conditions", [])):
        if condition.get("scir_h_evidence") != expected_case_ids:
            failures.append(
                "reports/examples/benchmark_report.example.json: "
                f"claim_gate.evaluated_conditions[{idx}].scir_h_evidence drifted from PYTHON_PROOF_LOOP_METADATA benchmark cases"
            )
    for idx, claim in enumerate(report.get("claims", [])):
        if claim.get("scir_h_evidence") != expected_case_ids:
            failures.append(
                "reports/examples/benchmark_report.example.json: "
                f"claims[{idx}].scir_h_evidence drifted from PYTHON_PROOF_LOOP_METADATA benchmark cases"
            )
    return failures


def check_track_c_example_alignment(root: pathlib.Path) -> list[str]:
    """Purpose: Keep Track C example artifacts aligned with the frozen Python proof-loop counts and corpus hash."""
    failures = []
    track_c_result = load_json(root / "reports" / "examples" / "benchmark_track_c_result.example.json")
    track_c_manifest = load_json(root / "reports" / "examples" / "benchmark_track_c_manifest.example.json")
    expected_repair_task_count = len(PYTHON_PROOF_LOOP_METADATA["benchmark_cases"])
    expected_executable_count = len(
        [
            case_name
            for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items()
            if not contract["requires_opaque_boundary"]
        ]
    )
    expected_boundary_only_count = len(
        [
            case_name
            for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items()
            if contract["requires_opaque_boundary"]
        ]
    )
    if track_c_result.get("metrics", {}).get("accepted_case_count") != expected_executable_count:
        failures.append(
            "reports/examples/benchmark_track_c_result.example.json: accepted_case_count drifted from PYTHON_PROOF_LOOP_METADATA executable-case contracts"
        )
    if track_c_result.get("metrics", {}).get("repair_task_count") != expected_repair_task_count:
        failures.append(
            "reports/examples/benchmark_track_c_result.example.json: repair_task_count drifted from PYTHON_PROOF_LOOP_METADATA benchmark cases"
        )
    if track_c_result.get("metrics", {}).get("boundary_only_case_count") != expected_boundary_only_count:
        failures.append(
            "reports/examples/benchmark_track_c_result.example.json: boundary_only_case_count drifted from PYTHON_PROOF_LOOP_METADATA executable-case contracts"
        )
    expected_corpus_hash = canonical_json_hash(load_json(root / "tests" / "corpora" / "python_proof_loop_corpus.json"))
    if track_c_manifest.get("corpus", {}).get("hash") != expected_corpus_hash:
        failures.append(
            "reports/examples/benchmark_track_c_manifest.example.json: corpus hash drifted from tests/corpora/python_proof_loop_corpus.json"
        )
    if track_c_manifest.get("corpus_manifest_hash") != expected_corpus_hash:
        failures.append(
            "reports/examples/benchmark_track_c_manifest.example.json: corpus_manifest_hash drifted from tests/corpora/python_proof_loop_corpus.json"
        )
    if track_c_result.get("corpus_manifest_hash") != expected_corpus_hash:
        failures.append(
            "reports/examples/benchmark_track_c_result.example.json: corpus_manifest_hash drifted from tests/corpora/python_proof_loop_corpus.json"
        )
    return failures


def check_deferred_track_d_surface(root: pathlib.Path) -> list[str]:
    """Purpose: Reject any active-pipeline residue for deferred Track D work."""
    failures = []
    pipeline_text = (root / "scripts" / "scir_bootstrap_pipeline.py").read_text(encoding="utf-8")
    if "track_d" in pipeline_text or "Track D" in pipeline_text:
        failures.append(
            "scripts/scir_bootstrap_pipeline.py: deferred Track D must not leave executable residue in the active pipeline surface"
        )
    return failures


def run_checks(root: pathlib.Path, *, include_audit: bool = False) -> list[str]:
    """Purpose: Execute the full repository-contract validation suite for live and optional audit surfaces.

    Inputs:
      - root: Repository root to validate.
      - include_audit: Whether to include retained but non-blocking audit surfaces in addition to the live gate.
    Outputs:
      - list[str]: Every contract failure found across docs, manifests, schemas, examples, and retained surfaces.
    Side Effects:
      - Reads repository files extensively.
    Assumptions:
      - Missing required files are treated as a hard stop before more detailed drift checks.
    Failure Modes:
      - Returns accumulated failures rather than raising so callers can print a full report.
    """
    failures = []
    failures.extend(check_required_files(root, LIVE_REQUIRED_FILES))
    if include_audit:
        failures.extend(check_required_files(root, AUDIT_REQUIRED_FILES))
    if failures:
        return failures
    failures.extend(check_focus_alignment(root))
    failures.extend(check_python_import_scope_alignment(root))
    failures.extend(check_reconstruction_policy_alignment(root))
    failures.extend(check_executable_subset_truth_alignment(root))
    failures.extend(check_frozen_python_proof_loop_contract(root))
    failures.extend(check_support_lane_freeze_alignment(root))
    failures.extend(check_wasm_backend_scope_alignment(root))
    failures.extend(check_decision_register(root))
    failures.extend(check_open_questions_alignment(root))
    failures.extend(check_removed_surface_references(root))
    failures.extend(check_typescript_archive_surface(root))
    failures.extend(check_validation_pipeline_doc(root))
    failures.extend(check_benchmark_example_alignment(root))
    failures.extend(check_track_c_example_alignment(root))
    failures.extend(check_deferred_track_d_surface(root))
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


#
# The mutate_* helpers intentionally corrupt one contract surface at a time in a
# temporary repo copy. Self-test mode uses them to prove the checker fails for
# the specific drift classes it claims to guard.
def mutate_remove_required_file(root: pathlib.Path) -> None:
    """Purpose: Remove a live-surface file so self-tests can verify the missing-file guard."""
    (root / "CURRENT_FOCUS.md").unlink()


def mutate_break_focus_alignment(root: pathlib.Path) -> None:
    """Purpose: Introduce active-focus wording drift between root roadmap documents."""
    path = root / "README.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("Frozen and retired", "Retired", 1), encoding="utf-8")


def mutate_break_reconstruction_policy_alignment(root: pathlib.Path) -> None:
    """Purpose: Remove one active reconstruction case to prove policy drift is detected."""
    path = root / "docs" / "reconstruction_policy.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(f"- `{RECONSTRUCTION_POLICY_DRIFT_CASE_MARKER}`\n", "", 1), encoding="utf-8")


def mutate_break_executable_subset_truth_alignment(root: pathlib.Path) -> None:
    """Purpose: Reintroduce stale importer-only wording for the executable subset truth test."""
    path = root / "tests" / "README.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "fixture bundles for the active Python importer proof loop plus the explicit rejected case",
            "fixture bundles for the active Python importer proof loop and importer-only follow-on cases",
            1,
        ),
        encoding="utf-8",
    )


def mutate_remove_audit_file(root: pathlib.Path) -> None:
    """Purpose: Remove an audit-only file so retained-surface checks can fail intentionally."""
    (root / "tooling" / "README.md").unlink()


def mutate_break_typescript_archive_surface(root: pathlib.Path) -> None:
    """Purpose: Promote an archived TypeScript case to an active tier to prove the quarantine guard fires."""
    path = root / "tests" / "typescript_importer" / "cases" / "a_interface_decl" / "module_manifest.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"declared_tier": "D"', '"declared_tier": "A"', 1), encoding="utf-8")


def mutate_break_validation_pipeline_doc(root: pathlib.Path) -> None:
    """Purpose: Re-add a retired validation step to test documentation drift detection."""
    path = root / "ci" / "validation_pipeline.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text + "\n15. validate derived exports\n", encoding="utf-8")


def mutate_reintroduce_track_d_pipeline_residue(root: pathlib.Path) -> None:
    """Purpose: Add Track D residue back into the active pipeline file for negative-fixture coverage."""
    path = root / "scripts" / "scir_bootstrap_pipeline.py"
    path.write_text(path.read_text(encoding="utf-8") + "\n# track_d residue\n", encoding="utf-8")


def mutate_break_benchmark_report_example_alignment(root: pathlib.Path) -> None:
    """Purpose: Rename one benchmark lineage key so the report example drifts from canonical case IDs."""
    path = root / "reports" / "examples" / "benchmark_report.example.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            '"fixture.python_importer.b_while_call_update": {',
            '"fixture.python_importer.b_while_call_update_removed": {',
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_frozen_python_proof_loop_contract(root: pathlib.Path) -> None:
    """Purpose: Break one proof-loop fixture ID to prove corpus freeze enforcement still catches drift."""
    path = root / "tests" / "corpora" / "python_proof_loop_corpus.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace('"fixture.python_importer.d_try_except"', '"fixture.python_importer.d_try_except_removed"', 1),
        encoding="utf-8",
    )


def mutate_break_support_lane_freeze_alignment(root: pathlib.Path) -> None:
    """Purpose: Flip Track C posture text so support-lane freeze docs no longer agree."""
    path = root / "BENCHMARK_STRATEGY.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "outside the default executable benchmark gate",
            "inside the default executable benchmark gate",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_rust_phase_lock(root: pathlib.Path) -> None:
    """Purpose: Pretend Rust auto-activates after Python so phase-lock enforcement can fail intentionally."""
    path = root / "IMPLEMENTATION_PLAN.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "Phase 3 is not auto-activated; Rust remains importer-first for the remainder of the MVP, and any future Rust proof-loop, backend, or benchmark activation is a post-MVP reactivation decision.",
            "Phase 3 is auto-activated after the Python proof loop completes.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_rust_scope_lock(root: pathlib.Path) -> None:
    """Purpose: Rewrite Rust scope from retained evidence to active round-trip support for negative testing."""
    path = root / "frontend" / "rust" / "IMPORT_SCOPE.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "Rust importer evidence is retained for the MVP as importer-first support only.",
            "Rust importer evidence is now an active round-trip MVP lane.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_rust_benchmark_lock(root: pathlib.Path) -> None:
    """Purpose: Promote Rust into active benchmarks to prove the benchmark-freeze guard catches it."""
    path = root / "BENCHMARK_STRATEGY.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "Rust importer evidence remains outside the active benchmark corpus and outside active benchmark claims for the MVP.",
            "Rust importer evidence is now part of the active benchmark corpus.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_reintroduce_rust_open_question(root: pathlib.Path) -> None:
    """Purpose: Reinsert the resolved Rust-scope open question to verify it stays retired."""
    path = root / "OPEN_QUESTIONS.md"
    text = path.read_text(encoding="utf-8")
    insertion = (
        "| OQ-003 | Should Rust remain importer-only in the MVP or grow into an active round-trip proof loop later? "
        "| roadmap scope and validation cost | keep Rust importer-first and do not widen reconstruction or benchmark claims | no |\n"
    )
    path.write_text(
        text.replace(
            "| OQ-001 | How much comment and provenance detail should a future pretty-view retain by default? | review ergonomics and audit tooling | canonical storage stays comment-free; pretty-view may add only non-semantic annotations | no |\n",
            "| OQ-001 | How much comment and provenance detail should a future pretty-view retain by default? | review ergonomics and audit tooling | canonical storage stays comment-free; pretty-view may add only non-semantic annotations | no |\n"
            + insertion,
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_wasm_freeze_contract(root: pathlib.Path) -> None:
    """Purpose: Add Wasm coverage to a non-emittable case so the frozen Wasm slice drifts."""
    path = root / "tests" / "corpora" / "python_proof_loop_corpus.json"
    payload = load_json(path)
    for fixture in payload.get("fixtures", []):
        if fixture.get("id") == "fixture.python_importer.a_async_await":
            fixture["pipeline_stages"] = [*fixture.get("pipeline_stages", []), "l_to_wasm"]
            break
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def mutate_break_wasm_phase_lock(root: pathlib.Path) -> None:
    """Purpose: Pretend Wasm auto-activates in the roadmap so phase-freeze checks fail intentionally."""
    path = root / "IMPLEMENTATION_PLAN.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "Phase 4 is not auto-activated; helper-free Wasm remains a bounded retained support lane for the remainder of the MVP, and any future Wasm widening, backend activation, or benchmark promotion is a post-MVP reactivation decision.",
            "Phase 4 is auto-activated after the Rust importer lock.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_wasm_backend_scope_lock(root: pathlib.Path) -> None:
    """Purpose: Rewrite Wasm README posture from retained support to active widening target."""
    path = root / "backends" / "wasm" / "README.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "It remains validated and preserved on disk, but it is not the current widening target.",
            "It is now the current widening target.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_wasm_backend_doc_alignment(root: pathlib.Path) -> None:
    """Purpose: Remove one admitted Python module from Wasm docs to prove metadata/doc alignment checks work."""
    path = root / "backends" / "wasm" / "README.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "- `fixture.python_importer.b_if_else_return`\n",
            "",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_wasm_benchmark_lock(root: pathlib.Path) -> None:
    """Purpose: Promote Wasm evidence into active benchmarks for negative-fixture coverage."""
    path = root / "BENCHMARK_STRATEGY.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "Helper-free Wasm evidence remains outside the active benchmark corpus and outside active benchmark claims for the MVP.",
            "Helper-free Wasm evidence is now part of the active benchmark corpus.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_wasm_profile_lock(root: pathlib.Path) -> None:
    """Purpose: Recast profile P as an active backend target to test profile-freeze enforcement."""
    path = root / "docs" / "target_profiles.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "Profile `P` remains active only for the bounded helper-free Wasm support lane; it is not the current widening target.",
            "Profile `P` is now the next active backend-expansion target.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_wasm_root_lock(root: pathlib.Path) -> None:
    """Purpose: Rewrite the root README so Wasm becomes the next automatic phase in the negative fixture."""
    path = root / "README.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "Helper-free Wasm remains retained backend evidence only for the MVP; it is not the next automatic implementation phase, and any future backend widening requires a fresh post-MVP reactivation decision.",
            "Helper-free Wasm is the next automatic implementation phase.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_track_c_phase_lock(root: pathlib.Path) -> None:
    """Purpose: Pretend Track C auto-activates so roadmap freeze wording fails the self-test."""
    path = root / "IMPLEMENTATION_PLAN.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "Phase 6 is not auto-activated; Track `C` remains a retained non-default diagnostic pilot for the remainder of the MVP, and any future promotion into the default executable gate or broader benchmark claim surface is a post-MVP reactivation decision.",
            "Phase 6 auto-activates as soon as Track A and B are stable.",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_track_c_benchmark_lock(root: pathlib.Path) -> None:
    """Purpose: Remove one Track C freeze bullet from benchmark strategy for negative-fixture coverage."""
    path = root / "BENCHMARK_STRATEGY.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "- `retain bounded diagnostic pilot for the remainder of the MVP`\n",
            "",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_track_c_tracks_doc_lock(root: pathlib.Path) -> None:
    """Purpose: Remove one Track C freeze bullet from tracks documentation to test retained-doc alignment."""
    path = root / "benchmarks" / "tracks.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            "- `not an auto-activating post-Phase-5 benchmark lane`\n",
            "",
            1,
        ),
        encoding="utf-8",
    )


def mutate_break_track_c_metadata_lock(root: pathlib.Path) -> None:
    """Purpose: Rewrite Track C metadata posture so the checked metadata surface contradicts the frozen docs."""
    path = root / "scripts" / "benchmark_contract_metadata.py"
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text.replace(
            '"mvp_posture": list(TRACK_C_MVP_POSTURE),',
            '"mvp_posture": ["promote Track C into the default executable benchmark gate"],',
            1,
        ),
        encoding="utf-8",
    )


def run_negative_fixture(
    root: pathlib.Path,
    name: str,
    mutate,
    expected_markers: list[str],
    *,
    include_audit: bool = False,
) -> list[str]:
    """Purpose: Run one mutation-based self-test against a temporary repo copy and assert the expected failure markers appear."""
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
    """Purpose: Execute the checker's negative-fixture suite so each claimed drift detector is proven by example."""
    failures = []
    failures.extend(
        run_negative_fixture(root, "missing required file", mutate_remove_required_file, ["missing file: CURRENT_FOCUS.md"])
    )
    failures.extend(
        run_negative_fixture(
            root,
            "focus drift",
            mutate_break_focus_alignment,
            ["README.md: missing active-focus marker 'Frozen and retired'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "reconstruction policy drift",
            mutate_break_reconstruction_policy_alignment,
            ["docs/reconstruction_policy.md: active reconstruction cases drifted from PYTHON_PROOF_LOOP_METADATA executable cases"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "executable subset truth drift",
            mutate_break_executable_subset_truth_alignment,
            ["tests/README.md: stale executable-subset wording"],
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
    failures.extend(
        run_negative_fixture(
            root,
            "typescript archive drift",
            mutate_break_typescript_archive_surface,
            ["archived TypeScript placeholder cases must remain declared_tier 'D'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "validation pipeline doc drift",
            mutate_break_validation_pipeline_doc,
            ["ci/validation_pipeline.md: stale validation-pipeline marker 'validate derived exports'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "track d residue drift",
            mutate_reintroduce_track_d_pipeline_residue,
            ["deferred Track D must not leave executable residue in the active pipeline surface"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "benchmark report example drift",
            mutate_break_benchmark_report_example_alignment,
            ["benchmark_report.example.json: scir_h_lineage_references drifted from PYTHON_PROOF_LOOP_METADATA benchmark cases"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "frozen python proof-loop drift",
            mutate_break_frozen_python_proof_loop_contract,
            ["split_contract.test drifted from the frozen Python executable-case set"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "support lane freeze drift",
            mutate_break_support_lane_freeze_alignment,
            ["BENCHMARK_STRATEGY.md: missing Track C freeze marker"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "wasm freeze drift",
            mutate_break_wasm_freeze_contract,
            ["helper-free Wasm stage coverage drifted from the frozen emittable Python case set"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "wasm phase lock drift",
            mutate_break_wasm_phase_lock,
            ["IMPLEMENTATION_PLAN.md: missing phase-freeze marker 'Phase 4 is not auto-activated; helper-free Wasm remains a bounded retained support lane for the remainder of the MVP, and any future Wasm widening, backend activation, or benchmark promotion is a post-MVP reactivation decision.'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "wasm backend scope drift",
            mutate_break_wasm_backend_scope_lock,
            ["backends/wasm/README.md: missing Wasm freeze marker 'It remains validated and preserved on disk, but it is not the current widening target.'"],
            include_audit=True,
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "wasm backend doc alignment drift",
            mutate_break_wasm_backend_doc_alignment,
            ["backends/wasm/README.md: admitted Python emitted modules drifted from WASM_BACKEND_METADATA"],
            include_audit=True,
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "wasm benchmark lock drift",
            mutate_break_wasm_benchmark_lock,
            ["BENCHMARK_STRATEGY.md: missing Wasm benchmark-freeze marker 'Helper-free Wasm evidence remains outside the active benchmark corpus and outside active benchmark claims for the MVP.'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "wasm profile lock drift",
            mutate_break_wasm_profile_lock,
            ["docs/target_profiles.md: missing Wasm profile-freeze marker 'Profile `P` remains active only for the bounded helper-free Wasm support lane; it is not the current widening target.'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "wasm root lock drift",
            mutate_break_wasm_root_lock,
            ["README.md: missing Wasm freeze marker 'Helper-free Wasm remains retained backend evidence only for the MVP; it is not the next automatic implementation phase, and any future backend widening requires a fresh post-MVP reactivation decision.'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "track c phase lock drift",
            mutate_break_track_c_phase_lock,
            ["IMPLEMENTATION_PLAN.md: missing phase-freeze marker 'Phase 6 is not auto-activated; Track `C` remains a retained non-default diagnostic pilot for the remainder of the MVP, and any future promotion into the default executable gate or broader benchmark claim surface is a post-MVP reactivation decision.'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "track c benchmark lock drift",
            mutate_break_track_c_benchmark_lock,
            ["BENCHMARK_STRATEGY.md: missing Track C freeze marker 'retain bounded diagnostic pilot for the remainder of the MVP'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "track c tracks-doc lock drift",
            mutate_break_track_c_tracks_doc_lock,
            ["benchmarks/tracks.md: missing Track C freeze marker 'not an auto-activating post-Phase-5 benchmark lane'"],
            include_audit=True,
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "track c metadata lock drift",
            mutate_break_track_c_metadata_lock,
            ["scripts/benchmark_contract_metadata.py: missing Track C freeze marker '\"mvp_posture\": list(TRACK_C_MVP_POSTURE)'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "rust phase lock drift",
            mutate_break_rust_phase_lock,
            ["IMPLEMENTATION_PLAN.md: missing phase-freeze marker 'Phase 3 is not auto-activated; Rust remains importer-first for the remainder of the MVP, and any future Rust proof-loop, backend, or benchmark activation is a post-MVP reactivation decision.'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "rust scope lock drift",
            mutate_break_rust_scope_lock,
            ["frontend/rust/IMPORT_SCOPE.md: missing Rust freeze marker 'Rust importer evidence is retained for the MVP as importer-first support only.'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "rust benchmark lock drift",
            mutate_break_rust_benchmark_lock,
            ["BENCHMARK_STRATEGY.md: missing Rust benchmark-freeze marker 'Rust importer evidence remains outside the active benchmark corpus and outside active benchmark claims for the MVP.'"],
        )
    )
    failures.extend(
        run_negative_fixture(
            root,
            "rust open-question drift",
            mutate_reintroduce_rust_open_question,
            ["OPEN_QUESTIONS.md: OQ-003 should be resolved and removed after the Rust MVP boundary decision"],
        )
    )
    return failures


def print_success(mode: str, *, self_test_count: int | None = None) -> None:
    """Purpose: Print a mode-specific success summary that matches the validated contract surface."""
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
    """Purpose: Parse CLI arguments, run the requested validation mode, and return a process exit code."""
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
        self_test_count = 25
        if self_test_failures:
            print("[test] repository contract self-tests failed")
            for item in self_test_failures:
                print(f" - {item}")
            return 1

    print_success(args.mode, self_test_count=self_test_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
