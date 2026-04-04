#!/usr/bin/env python3
"""Repository-wide contract checker for SCIR governance artifacts.

This validator ties docs, schemas, examples, manifests, metadata tables, and
bootstrap code together so the repository cannot silently claim support,
preservation, or benchmark posture that the executable surfaces do not justify.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - optional dependency
    Draft202012Validator = None

from benchmark_contract_metadata import (
    BENCHMARK_CONTRACT_METADATA,
    benchmark_track_baselines,
    benchmark_track_contract,
)
from scir_h_bootstrap_model import (
    Module,
    SCIR_H_KERNEL_METADATA,
    canonical_content_hash,
    format_module,
    parse_module,
    render_pretty_module,
    revision_scoped_node_id,
    semantic_lineage_id,
    semantic_lineage_payload,
)
from scir_python_bootstrap import (
    PYTHON_PROOF_LOOP_METADATA,
    SCIRH_MODULES as PYTHON_SCIRH_MODULES,
)
from scir_rust_bootstrap import RUST_IMPORTER_METADATA
from wasm_backend_metadata import WASM_BACKEND_METADATA, wasm_emittable_module_ids


ROOT = pathlib.Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "SYSTEM_BOUNDARY.md",
    "REPO_MAP.md",
    "VALIDATION.md",
    "VALIDATION_STRATEGY.md",
    "BENCHMARK_STRATEGY.md",
    "IMPLEMENTATION_PLAN.md",
    "MVP_SCOPE.md",
    "ROADMAP.md",
    "UNSUPPORTED_CASES.md",
    "DEFERRED_COMPONENTS.md",
    "LOWERING_CONTRACT.md",
    "IDENTITY_MODEL.md",
    "SPEC_COMPLETENESS_CHECKLIST.md",
    "DECISION_REGISTER.md",
    "OPEN_QUESTIONS.md",
    "ASSUMPTIONS.md",
    "EXECUTION_QUEUE.md",
    "Makefile",
    "plans/PLANS.md",
    "plans/2026-04-01-mvp-narrowing-and-contract-hardening.md",
    "plans/2026-04-01-q-06-001-lock-conditional-track-c-python-repair-pilot.md",
    "plans/2026-04-01-q-06-002-assess-non-default-executable-track-c-pilot.md",
    "plans/2026-04-01-q-06-003-decide-track-c-pilot-disposition.md",
    "plans/2026-04-01-q-06-004-lock-track-c-retention-and-retirement-criteria.md",
    "plans/2026-04-01-q-06-005-sync-track-c-sample-evidence-and-lock-criteria.md",
    "plans/2026-04-01-q-06-006-require-track-c-sample-posture-redecision.md",
    "plans/2026-04-01-q-06-007-distinguish-editorial-track-c-sample-refreshes.md",
    "plans/2026-04-01-q-06-008-require-track-c-refresh-regeneration-provenance.md",
    "plans/2026-04-02-q-02-003-sync-python-proof-loop-artifacts.md",
    "plans/2026-04-03-benchmark-credibility-hardening.md",
    "docs/project_overview.md",
    "docs/SCIR_HC_FAILURE_MODES.md",
    "docs/scir_h_overview.md",
    "docs/scir_l_overview.md",
    "docs/target_profiles.md",
    "docs/preservation_contract.md",
    "docs/feature_tiering.md",
    "docs/unsupported_cases.md",
    "docs/reconstruction_policy.md",
    "docs/runtime_doctrine.md",
    "docs/repository_map.md",
    "specs/scir_h_spec.md",
    "specs/scir_hc_doctrine.md",
    "specs/scir_l_spec.md",
    "specs/type_effect_capability_model.md",
    "specs/ownership_alias_model.md",
    "specs/concurrency_model.md",
    "specs/interop_and_opaque_boundary_spec.md",
    "specs/validator_invariants.md",
    "specs/provenance_and_stable_id_spec.md",
    "schemas/module_manifest.schema.json",
    "schemas/corpus_manifest.schema.json",
    "schemas/profile_claim.schema.json",
    "schemas/preservation_report.schema.json",
    "schemas/translation_validation_report.schema.json",
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
    "schemas/execution_queue.schema.json",
    "frontend/README.md",
    "frontend/python/IMPORT_SCOPE.md",
    "frontend/rust/IMPORT_SCOPE.md",
    "frontend/typescript/IMPORT_SCOPE.md",
    "frontend/typescript/NOT_ACTIVE.md",
    "validators/README.md",
    "validators/validator_contracts.md",
    "validators/execution_context_guard.py",
    "validators/lineage_contract.py",
    "validators/diff_audit_validator.py",
    "validators/translation_validator.py",
    "runtime/scirl_interpreter.py",
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
    "ci/validate_scirhc_containment.yml",
    ".github/workflows/validate.yml",
    ".github/workflows/benchmarks.yml",
    ".github/workflows/validate_scirhc_containment.yml",
    "scripts/validate_repo_contracts.py",
    "scripts/build_execution_queue.py",
    "scripts/run_repo_validation.py",
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
    "scripts/validate_translation.py",
    "reports/README.md",
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
    "reports/examples/translation_validation_report.example.json",
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
    "reports/exports/decision_register.export.json",
    "reports/exports/open_questions.export.json",
    "reports/exports/execution_queue.export.json",
    "tests/README.md",
    "tests/corpora/python_tier_a_micro_corpus.json",
    "tests/corpora/python_proof_loop_corpus.json",
    "tests/corpora/python_preservation_negative_corpus.json",
    "tests/test_scirhc_adversarial.py",
    "tests/test_lineage_contract.py",
    "tests/test_translation_validator.py",
    "tests/typescript_importer/README.md",
    "tests/typescript_importer/NOT_ACTIVE.md",
    "tests/invalid_scir_h/README.md",
    "tests/invalid_scir_h/manifest.json",
    "tests/invalid_scir_l/README.md",
    "tests/invalid_scir_l/manifest.json",
    "tests/sweeps/python_proof_loop_smoke.json",
    "tests/sweeps/python_proof_loop_full.json",
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
    ("reports/examples/translation_validation_report.example.json", "schemas/translation_validation_report.schema.json"),
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

PRESERVATION_PATH_EXAMPLES = {
    "source_to_h": "reports/examples/preservation_source_to_h.example.json",
    "h_to_l": "reports/examples/preservation_h_to_l.example.json",
    "h_to_python": "reports/examples/preservation_h_to_python.example.json",
    "l_to_wasm": "reports/examples/preservation_l_to_wasm.example.json",
}

DECISION_REGISTER_HEADER = [
    "ID",
    "Status",
    "Decision",
    "Constraint imposed",
    "Reversible",
    "First validation",
]
OPEN_QUESTIONS_HEADER = [
    "ID",
    "Question",
    "Impact",
    "Default until resolved",
    "Blocker",
]
CHECKLIST_HEADER = [
    "construct",
    "grammar",
    "parser",
    "validator",
    "lowering",
    "reconstruction",
    "tests",
    "MVP status",
    "action taken",
]
SCIR_H_SPEC_KERNEL_HEADER = [
    "construct",
    "canonical parser/formatter",
    "downstream status",
]
CHECKLIST_REQUIRED_ROWS = {
    "module header",
    "`import sym`",
    "record `type` declaration",
    "plain `fn`",
    "`async fn`",
    "`var`",
    "`set` local place",
    "`if` / `else`",
    "single-handler `try` / `catch name Type`",
    "direct call `f(args)`",
    "`await`",
    "`select`",
    "standalone `SCIR-L` text parser",
    "`SCIR-L` lowering-rule coverage",
    "Python reconstruction",
    "Rust reconstruction",
    "Wasm backend emission",
}

DECISION_REGISTER_EXPORT_REL = "reports/exports/decision_register.export.json"
DECISION_REGISTER_SCHEMA_REL = "schemas/decision_register.schema.json"
OPEN_QUESTIONS_EXPORT_REL = "reports/exports/open_questions.export.json"
OPEN_QUESTIONS_SCHEMA_REL = "schemas/open_questions.schema.json"
EXECUTION_QUEUE_EXPORT_REL = "reports/exports/execution_queue.export.json"
EXECUTION_QUEUE_BUILD_SCRIPT_REL = "scripts/build_execution_queue.py"
INVALID_SCIR_H_ROOT = pathlib.Path("tests") / "invalid_scir_h"
INVALID_SCIR_H_MANIFEST_REL = "tests/invalid_scir_h/manifest.json"
INVALID_SCIR_L_ROOT = pathlib.Path("tests") / "invalid_scir_l"
INVALID_SCIR_L_MANIFEST_REL = "tests/invalid_scir_l/manifest.json"
ACTIVE_TIER_A_CORPUS_REL = "tests/corpora/python_tier_a_micro_corpus.json"
ACTIVE_PROOF_LOOP_CORPUS_REL = "tests/corpora/python_proof_loop_corpus.json"
SWEEP_SMOKE_REL = "tests/sweeps/python_proof_loop_smoke.json"
SWEEP_FULL_REL = "tests/sweeps/python_proof_loop_full.json"
PYTHON_IMPORT_SCOPE_EXECUTABLE_HEADING = "### Executable proof-loop cases"
PYTHON_IMPORT_SCOPE_IMPORTER_ONLY_HEADING = "### Importer-only canonical `SCIR-H` cases"
PYTHON_IMPORT_SCOPE_REJECTED_HEADING = "### Rejected cases"
PYTHON_RECONSTRUCTION_CASES_HEADING = "## Active reconstruction cases"
RUST_IMPORT_SCOPE_SUPPORTED_HEADING = "### Importer-first evidence cases"
RUST_IMPORT_SCOPE_TIER_A_HEADING = "### Tier A importer-evidence cases"
RUST_IMPORT_SCOPE_WASM_HEADING = "### Helper-free Wasm-emittable case"
RUST_IMPORT_SCOPE_REJECTED_HEADING = "### Rejected cases"
BENCHMARK_STRATEGY_CASES_HEADING = "### Active executable benchmark cases"
BENCHMARK_TRACKS_ACTIVE_HEADING = "## Active executable tracks"
BENCHMARK_TRACKS_CONDITIONAL_HEADING = "## Conditional tracks"
BENCHMARK_TRACKS_DEFERRED_HEADING = "## Deferred tracks"
BENCHMARK_BASELINES_MANDATORY_HEADING = "### Mandatory active baselines"
BENCHMARK_BASELINES_TRACK_A_EXTRA_HEADING = "### Track A additional executable baselines"
BENCHMARK_BASELINES_TRACK_C_HEADING = "### Track C pilot baselines"
BENCHMARK_CORPORA_TRACK_C_CASES_HEADING = "### Track C pilot cases"
BENCHMARK_GATES_TRACK_A_SUCCESS_HEADING = "### Track A success gates"
BENCHMARK_GATES_TRACK_A_KILL_HEADING = "### Track A kill gates"
BENCHMARK_GATES_TRACK_B_SUCCESS_HEADING = "### Track B success gates"
BENCHMARK_GATES_TRACK_B_KILL_HEADING = "### Track B kill gates"
BENCHMARK_GATES_CONDITIONAL_HEADING = "### Conditional benchmark gate"
BENCHMARK_GATES_TRACK_C_SUCCESS_HEADING = "### Track C pilot success gates"
BENCHMARK_GATES_TRACK_C_KILL_HEADING = "### Track C pilot kill gates"
BENCHMARK_GATES_TRACK_C_RETENTION_HEADING = "### Track C retention criteria"
BENCHMARK_GATES_TRACK_C_RETIREMENT_HEADING = "### Track C retirement triggers"
BENCHMARK_GATES_DEFERRED_HEADING = "### Deferred benchmark misuse gate"
BENCHMARK_STRATEGY_TRACK_C_TASK_FAMILY_HEADING = "### Conditional Track C pilot task family"
BENCHMARK_STRATEGY_TRACK_C_CASES_HEADING = "### Conditional Track C pilot cases"
BENCHMARK_STRATEGY_TRACK_C_ARTIFACT_POSTURE_HEADING = "### Conditional Track C artifact posture"
BENCHMARK_STRATEGY_TRACK_C_EXECUTION_POSTURE_HEADING = "### Conditional Track C executable pilot posture"
BENCHMARK_STRATEGY_TRACK_C_DISPOSITION_HEADING = "### Conditional Track C disposition"
BENCHMARK_STRATEGY_TRACK_C_RETENTION_HEADING = "### Conditional Track C retention criteria"
BENCHMARK_STRATEGY_TRACK_C_RETIREMENT_HEADING = "### Conditional Track C retirement triggers"
BENCHMARK_STRATEGY_TRACK_C_SAMPLE_SYNC_HEADING = "### Conditional Track C sample synchronization"
BENCHMARK_STRATEGY_TRACK_C_SAMPLE_REDECISION_HEADING = "### Conditional Track C sample posture re-decision triggers"
BENCHMARK_STRATEGY_TRACK_C_EDITORIAL_REFRESH_HEADING = "### Conditional Track C editorial-only sample refreshes"
BENCHMARK_STRATEGY_TRACK_C_PROVENANCE_HEADING = "### Conditional Track C non-editorial sample refresh provenance"
BENCHMARK_TRACKS_TRACK_C_TASK_FAMILY_HEADING = "## Track C pilot task family"
BENCHMARK_TRACKS_TRACK_C_EXECUTION_POSTURE_HEADING = "## Track C executable pilot posture"
BENCHMARK_TRACKS_TRACK_C_DISPOSITION_HEADING = "## Track C disposition"
BENCHMARK_TRACKS_TRACK_C_SAMPLE_SYNC_HEADING = "## Track C sample synchronization"
BENCHMARK_TRACKS_TRACK_C_SAMPLE_REDECISION_HEADING = "## Track C sample posture re-decision triggers"
BENCHMARK_TRACKS_TRACK_C_EDITORIAL_REFRESH_HEADING = "## Track C editorial-only sample refreshes"
BENCHMARK_TRACKS_TRACK_C_PROVENANCE_HEADING = "## Track C non-editorial sample refresh provenance"
WASM_README_PYTHON_HEADING = "### Admitted Python emitted modules"
WASM_README_RUST_HEADING = "### Admitted Rust emitted modules"
WASM_README_ADMITTED_RULES_HEADING = "### Admitted lowering rules"
WASM_README_NON_EMITTABLE_RULES_HEADING = "### Non-emittable lowering rules"
LOWERING_CONTRACT_WASM_ADMITTED_HEADING = "### Wasm-admitted lowering rules"
LOWERING_CONTRACT_WASM_NON_EMITTABLE_HEADING = "### Wasm-non-emittable lowering rules"
VALIDATION_STRATEGY_WASM_MODULES_HEADING = "### Admitted helper-free Wasm-emission modules"
CAPABILITY_DEPENDENCY_PREFIX = "capability:"
PRESERVATION_STAGE_NAMES = [
    "source_to_h",
    "scir_h_validation",
    "h_to_l",
    "scir_l_validation",
    "h_to_python",
    "l_to_wasm",
]
PRESERVATION_LEVELS = ["P0", "P1", "P2", "P3", "PX"]
NOT_ACTIVE_MARKERS = {
    "frontend/typescript/NOT_ACTIVE.md": [
        "NOT ACTIVE",
        "frontend/typescript",
        "default validation",
    ],
    "tests/typescript_importer/NOT_ACTIVE.md": [
        "NOT ACTIVE",
        "tests/typescript_importer",
        "default validation",
    ],
    "tooling/NOT_ACTIVE.md": [
        "NOT ACTIVE",
        "tooling/agent_api.md",
        "tooling/explorer_contract.md",
    ],
    "scripts/NOT_ACTIVE.md": [
        "NOT ACTIVE",
        "scripts/typescript_importer_conformance.py",
        "default validation",
    ],
}


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


def collect_fallback_validation_errors(instance, schema, path="$"):
    failures = []
    expected_type = schema.get("type")
    if expected_type is not None and not matches_type(instance, expected_type):
        return [(path, f"expected type {expected_type!r}")]

    expected_enum = schema.get("enum")
    if expected_enum is not None and instance not in expected_enum:
        failures.append((path, f"expected one of {expected_enum!r}"))

    min_length = schema.get("minLength")
    if min_length is not None and isinstance(instance, str) and len(instance) < min_length:
        failures.append((path, f"expected string length >= {min_length}"))

    min_items = schema.get("minItems")
    if min_items is not None and isinstance(instance, list) and len(instance) < min_items:
        failures.append((path, f"expected at least {min_items} items"))

    pattern = schema.get("pattern")
    if pattern is not None and isinstance(instance, str) and re.fullmatch(pattern, instance) is None:
        failures.append((path, f"expected string matching {pattern!r}"))

    if schema.get("uniqueItems") and isinstance(instance, list):
        normalized = [normalize_for_uniqueness(item) for item in instance]
        if len(normalized) != len(set(normalized)):
            failures.append((path, "expected unique items"))

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                failures.append((path, f"missing required property {key}"))
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                failures.extend(
                    collect_fallback_validation_errors(value, properties[key], child_path)
                )
            elif additional is False:
                failures.append((path, f"unexpected property {key}"))
            elif isinstance(additional, dict):
                failures.extend(
                    collect_fallback_validation_errors(value, additional, child_path)
                )

    if isinstance(instance, list) and "items" in schema:
        for idx, item in enumerate(instance):
            failures.extend(
                collect_fallback_validation_errors(item, schema["items"], f"{path}[{idx}]")
            )

    return failures


def collect_instance_validation_errors(instance, schema):
    if Draft202012Validator is None:
        return collect_fallback_validation_errors(instance, schema)
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
    """Require Tier C capability accounting to stay mirrored between manifests and boundary contracts."""

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
        failures.append(
            f"{label}: missing capability imports for boundary requirements {missing_capabilities!r}"
        )

    unused_capabilities = sorted(capability_imports - boundary_capabilities)
    if unused_capabilities:
        failures.append(
            f"{label}: unused capability imports not referenced by the boundary contract {unused_capabilities!r}"
        )

    return failures


def preservation_level_rank(level: str) -> int:
    try:
        return PRESERVATION_LEVELS.index(level)
    except ValueError:  # pragma: no cover - schema should prevent this
        return len(PRESERVATION_LEVELS)


def validate_preservation_stage_behavior(entry: dict, *, manifest_rel: str):
    """Enforce that per-stage preservation expectations cannot silently overclaim or silently degrade."""

    failures = []
    stage_behavior = entry.get("expected_preservation_stage_behavior")
    if not isinstance(stage_behavior, dict):
        return [f"{manifest_rel}: fixture {entry['id']} must declare expected_preservation_stage_behavior"]
    pipeline_stages = entry.get("pipeline_stages", [])
    for stage in pipeline_stages:
        if stage not in stage_behavior:
            failures.append(
                f"{manifest_rel}: fixture {entry['id']} missing expected_preservation_stage_behavior for stage {stage}"
            )
            continue
        stage_expectation = stage_behavior[stage]
        if not isinstance(stage_expectation, dict):
            failures.append(
                f"{manifest_rel}: fixture {entry['id']} stage {stage} must map to an object"
            )
            continue
        status = stage_expectation.get("status")
        preservation_level = stage_expectation.get("preservation_level")
        if status not in {"pass", "warn", "fail", "skip"}:
            failures.append(
                f"{manifest_rel}: fixture {entry['id']} stage {stage} has invalid status {status!r}"
            )
        if preservation_level not in PRESERVATION_LEVELS:
            failures.append(
                f"{manifest_rel}: fixture {entry['id']} stage {stage} has invalid preservation_level {preservation_level!r}"
            )

    expected_ceiling = entry.get("expected_preservation_ceiling")
    if expected_ceiling in PRESERVATION_LEVELS:
        stronger_levels = [
            level
            for level in PRESERVATION_LEVELS
            if preservation_level_rank(level) < preservation_level_rank(expected_ceiling)
        ]
        for stage in pipeline_stages:
            stage_expectation = stage_behavior.get(stage, {})
            preservation_level = stage_expectation.get("preservation_level")
            if preservation_level in stronger_levels:
                failures.append(
                    f"{manifest_rel}: fixture {entry['id']} stage {stage} overclaims stronger preservation {preservation_level} than ceiling {expected_ceiling}"
                )
    return failures


def check_not_active_markers(root: pathlib.Path):
    failures = []
    for rel, required_markers in NOT_ACTIVE_MARKERS.items():
        path = root / rel
        if not path.exists():
            failures.append(f"{rel}: missing NOT_ACTIVE marker")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in required_markers:
            if marker not in text:
                failures.append(f"{rel}: missing marker {marker!r}")
    return failures


def check_required_files(root: pathlib.Path):
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def check_json_files(root: pathlib.Path):
    failures = []
    for path in root.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - bootstrap script
            failures.append(f"{path.relative_to(root)}: {exc}")
    return failures


def check_nonempty_markdown(root: pathlib.Path):
    failures = []
    for path in root.rglob("*.md"):
        if not path.read_text(encoding="utf-8").strip():
            failures.append(f"{path.relative_to(root)}: empty markdown file")
    return failures


def load_json_artifact(root: pathlib.Path, rel_path: str, failures: list[str]):
    try:
        return json.loads((root / rel_path).read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - bootstrap script
        failures.append(f"{rel_path}: {exc}")
        return None


def load_json_file(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(root: pathlib.Path, rel_path: str) -> str:
    digest = hashlib.sha256()
    digest.update((root / rel_path).read_bytes())
    return f"sha256:{digest.hexdigest()}"


def split_markdown_table_row(line: str):
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped.split("|")[1:-1]]


def is_markdown_separator_row(cells):
    return bool(cells) and all(cell and set(cell) <= {"-", ":"} for cell in cells)


def parse_markdown_table(root: pathlib.Path, path_rel: str, header: list[str], keys: list[str]):
    failures = []
    lines = (root / path_rel).read_text(encoding="utf-8").splitlines()
    start = None
    for idx, line in enumerate(lines):
        cells = split_markdown_table_row(line)
        if cells == header:
            start = idx + 1
            break
    if start is None:
        return None, [f"{path_rel}: table header not found"]

    rows = []
    for line in lines[start:]:
        cells = split_markdown_table_row(line)
        if cells is None:
            if rows:
                break
            continue
        if is_markdown_separator_row(cells):
            continue
        if len(cells) != len(header):
            failures.append(
                f"{path_rel}: table row has {len(cells)} columns, expected {len(header)}"
            )
            continue
        rows.append({key: value for key, value in zip(keys, cells)})
    if not rows:
        failures.append(f"{path_rel}: no rows found")
    return rows, failures


def parse_markdown_bullet_list_section(root: pathlib.Path, path_rel: str, heading: str):
    lines = (root / path_rel).read_text(encoding="utf-8").splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == heading:
            start = idx + 1
            break
    if start is None:
        return None, [f"{path_rel}: section {heading!r} not found"]

    items = []
    failures = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            break
        match = re.fullmatch(r"- `([^`]+)`", stripped)
        if match is None:
            failures.append(f"{path_rel}: section {heading!r} expected only `- `case`` bullets")
            continue
        items.append(match.group(1))
    if not items:
        failures.append(f"{path_rel}: section {heading!r} has no case bullets")
    return items, failures


def validate_track_c_result_lock_criteria(track_c_contract: dict, result: dict, label: str):
    failures = []
    metrics = result.get("metrics", {})
    if metrics.get("accepted_case_count") != track_c_contract["expected_accepted_case_count"]:
        failures.append(
            f"{label}: expected accepted_case_count {track_c_contract['expected_accepted_case_count']}"
        )
    if metrics.get("boundary_only_case_count") != len(track_c_contract["boundary_only_cases"]):
        failures.append(
            f"{label}: expected boundary_only_case_count {len(track_c_contract['boundary_only_cases'])}"
        )
    if metrics.get("gate_S2_ready") is not True:
        failures.append(f"{label}: retained Track C pilot requires gate_S2_ready true")
    if metrics.get("gate_K1_hit") is not False:
        failures.append(f"{label}: retained Track C pilot requires gate_K1_hit false")
    if result.get("status") not in track_c_contract["allowed_result_statuses"]:
        failures.append(f"{label}: expected status in {track_c_contract['allowed_result_statuses']}")
    return failures


def validate_track_c_sample_posture(track_c_contract: dict, manifest: dict, result: dict, manifest_label: str, result_label: str):
    failures = []
    corpus = manifest.get("corpus", {})
    if manifest.get("task_family") != track_c_contract["task_family"]:
        failures.append(f"{manifest_label}: sample task-family change requires explicit Track C re-decision")
    if corpus.get("scope") != track_c_contract["corpus_scope"] or corpus.get("hash") != track_c_contract["sample_manifest_hash"]:
        failures.append(f"{manifest_label}: sample case-set posture change requires explicit Track C re-decision")
    if result.get("status") != track_c_contract["sample_result_status"]:
        failures.append(f"{result_label}: sample status change requires explicit Track C re-decision")
    if result.get("evidence") != track_c_contract["sample_evidence"]:
        failures.append(f"{result_label}: sample evidence change requires explicit Track C re-decision")
    metrics = result.get("metrics", {})
    if (
        metrics.get("accepted_case_count") != track_c_contract["expected_accepted_case_count"]
        or metrics.get("boundary_only_case_count") != len(track_c_contract["boundary_only_cases"])
    ):
        failures.append(f"{result_label}: sample case or boundary posture change requires explicit Track C re-decision")
    return failures


def describe_list_export_mismatch(export_rel: str, top_key: str, expected_rows: list[dict], actual):
    if not isinstance(actual, dict):
        return f"{export_rel} $: expected object export"
    actual_rows = actual.get(top_key)
    if not isinstance(actual_rows, list):
        return f"{export_rel} $.{top_key}: expected array export"
    if len(actual_rows) != len(expected_rows):
        return f"{export_rel} $.{top_key}: expected {len(expected_rows)} entries"
    for idx, expected_record in enumerate(expected_rows):
        actual_record = actual_rows[idx]
        if not isinstance(actual_record, dict):
            return f"{export_rel} $.{top_key}[{idx}]: expected object entry"
        for key, expected_value in expected_record.items():
            if actual_record.get(key) != expected_value:
                return f"{export_rel} $.{top_key}[{idx}].{key}: expected {expected_value!r}"
        extra_keys = sorted(set(actual_record) - set(expected_record))
        if extra_keys:
            return f"{export_rel} $.{top_key}[{idx}]: unexpected keys {', '.join(extra_keys)}"
    extra_top = sorted(set(actual) - {top_key})
    if extra_top:
        return f"{export_rel} $: unexpected keys {', '.join(extra_top)}"
    return None


def check_schema_metadata(root: pathlib.Path):
    expectations = {
        "schemas/preservation_report.schema.json": [
            "report_id",
            "subject",
            "path",
            "source_artifact",
            "target_artifact",
            "profile",
            "preservation_level",
            "status",
            "downgrades",
            "boundary_annotations",
            "evidence",
        ],
        "schemas/translation_validation_report.schema.json": [
            "report_id",
            "subject",
            "backend_kind",
            "target_profile",
            "preservation_level",
            "outcome",
            "equivalence_mode",
            "observable_dimensions_checked",
            "backend_subset_class",
            "execution_oracle",
            "validation_strength",
            "downgrade_reason",
            "subset_admission_result",
            "subset_admission_reason",
            "unsupported_features_detected",
            "helper_free_subset_required",
            "contract_assumptions",
            "dimension_results",
            "violations",
            "findings",
            "validated_invocations",
            "suspect_l_nodes",
            "suspect_h_nodes",
            "backend_regions",
            "origin_trace_links",
        ],
        "schemas/validation_report.schema.json": [
            "report_id",
            "artifact",
            "layer",
            "validator",
            "status",
            "diagnostics",
        ],
        "schemas/benchmark_manifest.schema.json": [
            "benchmark_id",
            "track",
            "task_family",
            "corpus",
            "baselines",
            "success_gates",
            "kill_gates",
        ],
        "schemas/benchmark_result.schema.json": [
            "benchmark_id",
            "run_id",
            "system_under_test",
            "track",
            "metrics",
            "baseline_comparison",
            "status",
        ],
        "schemas/benchmark_report.schema.json": [
            "run_id",
            "claim_mode",
            "corpus_manifest_hash",
            "claim_class",
            "evidence_class",
            "claim_gate",
            "claims",
            "reproducibility_block",
        ],
        "schemas/sweep_summary.schema.json": [
            "sweep_id",
            "run_id",
            "commit_sha",
            "corpus_id",
            "generated_at",
            "row_count",
            "slice_rankings",
            "preservation_stage_breakdown",
        ],
        "schemas/regression_summary.schema.json": [
            "sweep_id",
            "run_id",
            "baseline_run_id",
            "generated_at",
            "added_failures",
            "removed_failures",
            "worsened_metrics",
            "improved_metrics",
        ],
    }
    failures = []
    for rel, required_fields in expectations.items():
        schema = json.loads((root / rel).read_text(encoding="utf-8"))
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            failures.append(f"{rel}: expected Draft 2020-12 schema declaration")
        if schema.get("type") != "object":
            failures.append(f"{rel}: expected top-level object schema")
        if schema.get("additionalProperties") is not False:
            failures.append(f"{rel}: expected top-level additionalProperties=false")
        actual_required = schema.get("required", [])
        missing = [field for field in required_fields if field not in actual_required]
        if missing:
            failures.append(f"{rel}: missing required fields {', '.join(missing)}")
    return failures


def check_example_artifacts(root: pathlib.Path):
    failures = []
    for instance_rel, schema_rel in EXAMPLE_ARTIFACTS:
        instance = load_json_artifact(root, instance_rel, failures)
        schema = load_json_artifact(root, schema_rel, failures)
        if instance is None or schema is None:
            continue
        for location, message in collect_instance_validation_errors(instance, schema):
            failures.append(f"{instance_rel} {location}: {message}")
    return failures


def check_decision_register_export(root: pathlib.Path):
    failures = []
    rows, parse_failures = parse_markdown_table(
        root,
        "DECISION_REGISTER.md",
        DECISION_REGISTER_HEADER,
        ["id", "status", "decision", "constraint_imposed", "reversible", "first_validation"],
    )
    failures.extend(parse_failures)
    if rows is None:
        return failures
    derived = {"decisions": rows}
    schema = load_json_artifact(root, DECISION_REGISTER_SCHEMA_REL, failures)
    export = load_json_artifact(root, DECISION_REGISTER_EXPORT_REL, failures)
    if schema is None or export is None:
        return failures
    for label, instance in [("DECISION_REGISTER.md derived export", derived), (DECISION_REGISTER_EXPORT_REL, export)]:
        for location, message in collect_instance_validation_errors(instance, schema):
            failures.append(f"{label} {location}: {message}")
    mismatch = describe_list_export_mismatch(DECISION_REGISTER_EXPORT_REL, "decisions", rows, export)
    if mismatch:
        failures.append(mismatch)
    return failures


def check_open_questions_export(root: pathlib.Path):
    failures = []
    rows, parse_failures = parse_markdown_table(
        root,
        "OPEN_QUESTIONS.md",
        OPEN_QUESTIONS_HEADER,
        ["id", "question", "impact", "default_until_resolved", "blocker"],
    )
    failures.extend(parse_failures)
    if rows is None:
        return failures
    derived = {"open_questions": rows}
    schema = load_json_artifact(root, OPEN_QUESTIONS_SCHEMA_REL, failures)
    export = load_json_artifact(root, OPEN_QUESTIONS_EXPORT_REL, failures)
    if schema is None or export is None:
        return failures
    for label, instance in [("OPEN_QUESTIONS.md derived export", derived), (OPEN_QUESTIONS_EXPORT_REL, export)]:
        for location, message in collect_instance_validation_errors(instance, schema):
            failures.append(f"{label} {location}: {message}")
    mismatch = describe_list_export_mismatch(OPEN_QUESTIONS_EXPORT_REL, "open_questions", rows, export)
    if mismatch:
        failures.append(mismatch)
    return failures


def check_execution_queue_export(root: pathlib.Path):
    command = [sys.executable, str(root / EXECUTION_QUEUE_BUILD_SCRIPT_REL), "--mode", "check"]
    completed = subprocess.run(
        command,
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        return []
    failures = [f"{EXECUTION_QUEUE_EXPORT_REL}: synchronization check failed"]
    output = "\n".join(
        part.strip() for part in [completed.stdout, completed.stderr] if part and part.strip()
    )
    if output:
        failures.extend(f"{EXECUTION_QUEUE_BUILD_SCRIPT_REL}: {line}" for line in output.splitlines())
    return failures


def check_spec_completeness_checklist(root: pathlib.Path):
    failures = []
    rows, parse_failures = parse_markdown_table(
        root,
        "SPEC_COMPLETENESS_CHECKLIST.md",
        CHECKLIST_HEADER,
        [
            "construct",
            "grammar",
            "parser",
            "validator",
            "lowering",
            "reconstruction",
            "tests",
            "mvp_status",
            "action_taken",
        ],
    )
    failures.extend(parse_failures)
    if rows is None:
        return failures
    found = {row["construct"] for row in rows}
    missing = sorted(CHECKLIST_REQUIRED_ROWS - found)
    if missing:
        failures.append("SPEC_COMPLETENESS_CHECKLIST.md: missing required rows " + ", ".join(missing))
    for row in rows:
        if not row["mvp_status"]:
            failures.append(f"SPEC_COMPLETENESS_CHECKLIST.md: empty MVP status for {row['construct']}")
        if not row["action_taken"]:
            failures.append(f"SPEC_COMPLETENESS_CHECKLIST.md: empty action taken for {row['construct']}")
    return failures


def check_scir_h_kernel_alignment(root: pathlib.Path):
    """Cross-check spec, checklist, and executable kernel metadata for the canonical `SCIR-H` subset."""

    failures = []
    spec_rows, spec_parse_failures = parse_markdown_table(
        root,
        "specs/scir_h_spec.md",
        SCIR_H_SPEC_KERNEL_HEADER,
        ["construct", "canonical_parser_formatter", "downstream_status"],
    )
    failures.extend(spec_parse_failures)
    checklist_rows, checklist_parse_failures = parse_markdown_table(
        root,
        "SPEC_COMPLETENESS_CHECKLIST.md",
        CHECKLIST_HEADER,
        [
            "construct",
            "grammar",
            "parser",
            "validator",
            "lowering",
            "reconstruction",
            "tests",
            "mvp_status",
            "action_taken",
        ],
    )
    failures.extend(checklist_parse_failures)
    if spec_rows is None or checklist_rows is None:
        return failures

    expected_rows = {
        row["construct"]: row for row in SCIR_H_KERNEL_METADATA["constructs"]
    }
    spec_map = {row["construct"]: row for row in spec_rows}
    checklist_map = {row["construct"]: row for row in checklist_rows}

    expected_constructs = set(expected_rows)
    actual_spec_constructs = set(spec_map)
    missing_spec_constructs = sorted(expected_constructs - actual_spec_constructs)
    extra_spec_constructs = sorted(actual_spec_constructs - expected_constructs)
    if missing_spec_constructs:
        failures.append(
            "specs/scir_h_spec.md: missing kernel rows " + ", ".join(missing_spec_constructs)
        )
    if extra_spec_constructs:
        failures.append(
            "specs/scir_h_spec.md: unexpected kernel rows " + ", ".join(extra_spec_constructs)
        )

    for construct, expected in expected_rows.items():
        spec_row = spec_map.get(construct)
        if spec_row is not None:
            if spec_row["canonical_parser_formatter"] != expected["spec_canonical_parser_formatter"]:
                failures.append(
                    "specs/scir_h_spec.md: kernel row "
                    f"{construct} expected canonical parser/formatter "
                    f"{expected['spec_canonical_parser_formatter']!r}"
                )
            if spec_row["downstream_status"] != expected["spec_downstream_status"]:
                failures.append(
                    "specs/scir_h_spec.md: kernel row "
                    f"{construct} expected downstream status "
                    f"{expected['spec_downstream_status']!r}"
                )

        checklist_row = checklist_map.get(construct)
        if checklist_row is None:
            failures.append(
                "SPEC_COMPLETENESS_CHECKLIST.md: missing kernel construct row " + construct
            )
            continue
        for key, expected_value in expected["checklist"].items():
            if checklist_row.get(key) != expected_value:
                failures.append(
                    "SPEC_COMPLETENESS_CHECKLIST.md: kernel row "
                    f"{construct} expected {key} {expected_value!r}"
                )

    identity_text = (root / "IDENTITY_MODEL.md").read_text(encoding="utf-8")
    for marker in SCIR_H_KERNEL_METADATA["identity_model_required_markers"]:
        if marker not in identity_text:
            failures.append(f"IDENTITY_MODEL.md: missing kernel identity marker {marker!r}")
    return failures


def check_preservation_path_examples(root: pathlib.Path):
    failures = []
    seen_paths = {}
    for expected_path, rel in PRESERVATION_PATH_EXAMPLES.items():
        instance = json.loads((root / rel).read_text(encoding="utf-8"))
        actual_path = instance.get("path")
        seen_paths[actual_path] = rel
        if actual_path != expected_path:
            failures.append(f"{rel}: expected path {expected_path}, found {actual_path}")
    if set(seen_paths) != set(PRESERVATION_PATH_EXAMPLES):
        failures.append(
            "preservation examples: expected one example for each active path "
            f"{sorted(PRESERVATION_PATH_EXAMPLES)}"
        )
    return failures


def validate_split_contract(manifest: dict, *, manifest_rel: str):
    failures = []
    split_contract = manifest.get("split_contract")
    fixtures = manifest.get("fixtures", [])
    if not isinstance(split_contract, dict):
        return failures

    fixture_ids = [entry.get("id") for entry in fixtures if isinstance(entry.get("id"), str)]
    fixture_id_set = set(fixture_ids)
    split_members = {}
    seen_ids = {}
    for split_name in ["train", "dev", "test"]:
        members = split_contract.get(split_name, [])
        if not isinstance(members, list):
            continue
        split_members[split_name] = members
        for fixture_id in members:
            if fixture_id in seen_ids:
                failures.append(
                    f"{manifest_rel}: split_contract fixture {fixture_id} appears in both {seen_ids[fixture_id]} and {split_name}"
                )
            else:
                seen_ids[fixture_id] = split_name
            if fixture_id not in fixture_id_set:
                failures.append(
                    f"{manifest_rel}: split_contract references unknown fixture id {fixture_id}"
                )

    if fixture_id_set and set(seen_ids) != fixture_id_set:
        missing_ids = sorted(fixture_id_set - set(seen_ids))
        extra_ids = sorted(set(seen_ids) - fixture_id_set)
        if missing_ids:
            failures.append(
                f"{manifest_rel}: split_contract is missing fixture ids {missing_ids!r}"
            )
        if extra_ids:
            failures.append(
                f"{manifest_rel}: split_contract contains non-manifest fixture ids {extra_ids!r}"
            )

    for entry in fixtures:
        fixture_id = entry.get("id")
        split = entry.get("split")
        if not isinstance(fixture_id, str) or not isinstance(split, str):
            continue
        declared_split = seen_ids.get(fixture_id)
        if declared_split is None:
            failures.append(
                f"{manifest_rel}: fixture {fixture_id} has split {split} but is absent from split_contract"
            )
            continue
        if declared_split != split:
            failures.append(
                f"{manifest_rel}: fixture {fixture_id} split {split} disagrees with split_contract {declared_split}"
            )
    return failures


def check_corpus_manifest(root: pathlib.Path, manifest_rel: str):
    failures = []
    manifest = load_json_artifact(root, manifest_rel, failures)
    if manifest is None:
        return failures
    schema = load_json_file(root / "schemas/corpus_manifest.schema.json")
    for location, message in collect_instance_validation_errors(manifest, schema):
        failures.append(f"{manifest_rel} {location}: {message}")
    failures.extend(validate_split_contract(manifest, manifest_rel=manifest_rel))
    for entry in manifest.get("fixtures", []):
        path_rel = entry.get("path")
        if not isinstance(path_rel, str):
            continue
        if not (root / path_rel).exists():
            failures.append(f"{manifest_rel}: fixture path missing {path_rel}")
            continue
        if entry.get("hash") != file_sha256(root, path_rel):
            failures.append(f"{manifest_rel}: hash drift for {path_rel}")
        if manifest.get("kind") == "active_roundtrip":
            failures.extend(validate_preservation_stage_behavior(entry, manifest_rel=manifest_rel))
        boundary_contract_path = entry.get("boundary_contract_path")
        if boundary_contract_path:
            boundary_contract_file = root / boundary_contract_path
            if not boundary_contract_file.exists():
                failures.append(f"{manifest_rel}: missing boundary contract {boundary_contract_path}")
            else:
                boundary_contract = load_json_artifact(root, boundary_contract_path, failures)
                if boundary_contract is not None and manifest.get("kind") != "negative_validation":
                    schema = load_json_file(root / "schemas/opaque_boundary_contract.schema.json")
                    for location, message in collect_instance_validation_errors(boundary_contract, schema):
                        failures.append(f"{boundary_contract_path} {location}: {message}")
    return failures


def check_sweep_manifest(root: pathlib.Path, manifest_rel: str):
    failures = []
    manifest = load_json_artifact(root, manifest_rel, failures)
    if manifest is None:
        return failures
    schema = load_json_file(root / "schemas/sweep_manifest.schema.json")
    for location, message in collect_instance_validation_errors(manifest, schema):
        failures.append(f"{manifest_rel} {location}: {message}")
    corpus_rel = manifest.get("corpus_manifest")
    if isinstance(corpus_rel, str) and not (root / corpus_rel).exists():
        failures.append(f"{manifest_rel}: referenced corpus manifest missing {corpus_rel}")
    return failures


def check_invalid_scir_h_examples(root: pathlib.Path):
    invalid_files = sorted((root / INVALID_SCIR_H_ROOT).glob("*.scirh"))
    if not invalid_files:
        return [f"{INVALID_SCIR_H_ROOT}: expected at least one invalid .scirh fixture"]
    return check_corpus_manifest(root, INVALID_SCIR_H_MANIFEST_REL)


def check_invalid_scir_l_examples(root: pathlib.Path):
    invalid_files = sorted((root / INVALID_SCIR_L_ROOT).glob("*.json"))
    if not invalid_files:
        return [f"{INVALID_SCIR_L_ROOT}: expected at least one invalid .json fixture"]
    return check_corpus_manifest(root, INVALID_SCIR_L_MANIFEST_REL)


def check_active_corpora(root: pathlib.Path):
    failures = []
    failures.extend(check_corpus_manifest(root, ACTIVE_TIER_A_CORPUS_REL))
    failures.extend(check_corpus_manifest(root, ACTIVE_PROOF_LOOP_CORPUS_REL))
    tier_a_manifest = load_json_file(root / ACTIVE_TIER_A_CORPUS_REL)
    proof_loop_manifest = load_json_file(root / ACTIVE_PROOF_LOOP_CORPUS_REL)
    tier_a_ids = [entry["id"] for entry in tier_a_manifest["fixtures"]]
    proof_loop_ids = [entry["id"] for entry in proof_loop_manifest["fixtures"]]
    expected_tier_a_ids = [
        "fixture.python_importer.a_basic_function",
        "fixture.python_importer.a_async_await",
        "fixture.python_importer.b_direct_call",
    ]
    expected_proof_loop_ids = [
        "fixture.python_importer.a_basic_function",
        "fixture.python_importer.a_async_await",
        "fixture.python_importer.b_direct_call",
        "fixture.python_importer.c_opaque_call",
    ]
    if tier_a_ids != expected_tier_a_ids:
        failures.append(f"{ACTIVE_TIER_A_CORPUS_REL}: expected fixtures {expected_tier_a_ids!r}")
    if proof_loop_ids != expected_proof_loop_ids:
        failures.append(f"{ACTIVE_PROOF_LOOP_CORPUS_REL}: expected fixtures {expected_proof_loop_ids!r}")
    return failures


def check_sweep_contract(root: pathlib.Path):
    failures = []
    failures.extend(check_sweep_manifest(root, SWEEP_SMOKE_REL))
    failures.extend(check_sweep_manifest(root, SWEEP_FULL_REL))
    smoke_manifest = load_json_file(root / SWEEP_SMOKE_REL)
    full_manifest = load_json_file(root / SWEEP_FULL_REL)
    if smoke_manifest.get("corpus_manifest") != ACTIVE_TIER_A_CORPUS_REL:
        failures.append(f"{SWEEP_SMOKE_REL}: expected corpus_manifest {ACTIVE_TIER_A_CORPUS_REL}")
    if full_manifest.get("corpus_manifest") != ACTIVE_PROOF_LOOP_CORPUS_REL:
        failures.append(f"{SWEEP_FULL_REL}: expected corpus_manifest {ACTIVE_PROOF_LOOP_CORPUS_REL}")
    return failures


def check_identity_contract(root: pathlib.Path):
    """Verify that lineage and canonical-hash rules remain aligned with the executable identity model."""

    failures = []
    base_module = PYTHON_SCIRH_MODULES["a_async_await"]
    canonical = format_module(base_module)
    reparsed = parse_module(canonical)
    if format_module(reparsed) != canonical:
        failures.append("identity contract: canonical SCIR-H round-trip drifted")

    formatted_variant = "\n" + canonical.replace("\nasync fn load_once", "\n\nasync fn load_once") + "\n"
    try:
        variant_module = parse_module(formatted_variant)
    except Exception as exc:  # pragma: no cover - parser-specific
        failures.append(f"identity contract: formatting-only variant failed to parse ({exc})")
        variant_module = None

    if variant_module is not None:
        if semantic_lineage_id(variant_module) != semantic_lineage_id(reparsed):
            failures.append("identity contract: formatting-only variant changed semantic lineage")
        if canonical_content_hash(variant_module) != canonical_content_hash(reparsed):
            failures.append("identity contract: formatting-only variant changed canonical content hash")

    reordered_module = Module(
        module_id=base_module.module_id,
        imports=base_module.imports,
        type_decls=base_module.type_decls,
        functions=tuple(reversed(base_module.functions)),
    )
    if semantic_lineage_id(reordered_module) != semantic_lineage_id(base_module):
        failures.append("identity contract: declaration reordering changed semantic lineage")
    if canonical_content_hash(reordered_module) == canonical_content_hash(base_module):
        failures.append("identity contract: declaration reordering should change canonical content hash")

    pretty_view = render_pretty_module(base_module, include_identity=True)
    if semantic_lineage_id(base_module) not in pretty_view:
        failures.append("identity contract: pretty view omitted semantic lineage id")
    if canonical_content_hash(base_module) not in pretty_view:
        failures.append("identity contract: pretty view omitted canonical content hash")
    try:
        parse_module(pretty_view)
        failures.append("identity contract: pretty view must not parse as canonical SCIR-H")
    except Exception:
        pass

    payload_json = json.dumps(semantic_lineage_payload(base_module), sort_keys=True)
    if "version" in payload_json.lower():
        failures.append("identity contract: semantic lineage payload must not include spec version")

    rev_a = revision_scoped_node_id(
        base_module,
        decl_name="load_once",
        node_path="function:load_once:return",
        revision_tag="rev-a",
    )
    rev_b = revision_scoped_node_id(
        base_module,
        decl_name="load_once",
        node_path="function:load_once:return",
        revision_tag="rev-b",
    )
    if rev_a == rev_b:
        failures.append("identity contract: revision-scoped node ids must vary by revision tag")
    return failures


def check_python_proof_loop_contract(root: pathlib.Path):
    failures = []
    executable_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "frontend/python/IMPORT_SCOPE.md",
        PYTHON_IMPORT_SCOPE_EXECUTABLE_HEADING,
    )
    failures.extend(parse_failures)
    importer_only_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "frontend/python/IMPORT_SCOPE.md",
        PYTHON_IMPORT_SCOPE_IMPORTER_ONLY_HEADING,
    )
    failures.extend(parse_failures)
    rejected_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "frontend/python/IMPORT_SCOPE.md",
        PYTHON_IMPORT_SCOPE_REJECTED_HEADING,
    )
    failures.extend(parse_failures)
    reconstruction_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "docs/reconstruction_policy.md",
        PYTHON_RECONSTRUCTION_CASES_HEADING,
    )
    failures.extend(parse_failures)

    expected_executable = list(PYTHON_PROOF_LOOP_METADATA["executable_cases"])
    expected_importer_only = list(PYTHON_PROOF_LOOP_METADATA["importer_only_cases"])
    expected_rejected = list(PYTHON_PROOF_LOOP_METADATA["rejected_cases"])

    if executable_cases is not None and executable_cases != expected_executable:
        failures.append(
            "frontend/python/IMPORT_SCOPE.md: executable proof-loop cases expected "
            + repr(expected_executable)
        )
    if importer_only_cases is not None and importer_only_cases != expected_importer_only:
        failures.append(
            "frontend/python/IMPORT_SCOPE.md: importer-only proof-loop cases expected "
            + repr(expected_importer_only)
        )
    if rejected_cases is not None and rejected_cases != expected_rejected:
        failures.append(
            "frontend/python/IMPORT_SCOPE.md: rejected proof-loop cases expected "
            + repr(expected_rejected)
        )
    if reconstruction_cases is not None and reconstruction_cases != expected_executable:
        failures.append(
            "docs/reconstruction_policy.md: active reconstruction cases expected "
            + repr(expected_executable)
        )
    return failures


def check_rust_importer_contract(root: pathlib.Path):
    failures = []
    supported_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "frontend/rust/IMPORT_SCOPE.md",
        RUST_IMPORT_SCOPE_SUPPORTED_HEADING,
    )
    failures.extend(parse_failures)
    tier_a_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "frontend/rust/IMPORT_SCOPE.md",
        RUST_IMPORT_SCOPE_TIER_A_HEADING,
    )
    failures.extend(parse_failures)
    wasm_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "frontend/rust/IMPORT_SCOPE.md",
        RUST_IMPORT_SCOPE_WASM_HEADING,
    )
    failures.extend(parse_failures)
    rejected_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "frontend/rust/IMPORT_SCOPE.md",
        RUST_IMPORT_SCOPE_REJECTED_HEADING,
    )
    failures.extend(parse_failures)

    expected_supported = list(RUST_IMPORTER_METADATA["supported_cases"])
    expected_tier_a = list(RUST_IMPORTER_METADATA["tier_a_cases"])
    expected_rejected = list(RUST_IMPORTER_METADATA["rejected_cases"])
    expected_wasm = [
        case_name
        for case_name, contract in RUST_IMPORTER_METADATA["case_contracts"].items()
        if contract["wasm_emittable"]
    ]

    if supported_cases is not None and supported_cases != expected_supported:
        failures.append(
            "frontend/rust/IMPORT_SCOPE.md: importer-first Rust cases expected "
            + repr(expected_supported)
        )
    if tier_a_cases is not None and tier_a_cases != expected_tier_a:
        failures.append(
            "frontend/rust/IMPORT_SCOPE.md: Tier A Rust importer cases expected "
            + repr(expected_tier_a)
        )
    if wasm_cases is not None and wasm_cases != expected_wasm:
        failures.append(
            "frontend/rust/IMPORT_SCOPE.md: Wasm-emittable Rust cases expected "
            + repr(expected_wasm)
        )
    if rejected_cases is not None and rejected_cases != expected_rejected:
        failures.append(
            "frontend/rust/IMPORT_SCOPE.md: rejected Rust importer cases expected "
            + repr(expected_rejected)
        )
    return failures


def check_active_surface_contract(root: pathlib.Path):
    failures = []
    required_inputs = {
        "README.md": root / "README.md",
        "VALIDATION.md": root / "VALIDATION.md",
        "Makefile": root / "Makefile",
        "scripts/run_repo_validation.py": root / "scripts" / "run_repo_validation.py",
        "scripts/sync_python_proof_loop_artifacts.py": root / "scripts" / "sync_python_proof_loop_artifacts.py",
        "VALIDATION_STRATEGY.md": root / "VALIDATION_STRATEGY.md",
        "BENCHMARK_STRATEGY.md": root / "BENCHMARK_STRATEGY.md",
        "OPEN_QUESTIONS.md": root / "OPEN_QUESTIONS.md",
        "EXECUTION_QUEUE.md": root / "EXECUTION_QUEUE.md",
        "ASSUMPTIONS.md": root / "ASSUMPTIONS.md",
    }
    if any(not path.exists() for path in required_inputs.values()):
        return failures

    readme = required_inputs["README.md"].read_text(encoding="utf-8")
    validation_doc = required_inputs["VALIDATION.md"].read_text(encoding="utf-8")
    makefile = required_inputs["Makefile"].read_text(encoding="utf-8")
    run_repo_validation = required_inputs["scripts/run_repo_validation.py"].read_text(encoding="utf-8")
    sync_python_artifacts = required_inputs["scripts/sync_python_proof_loop_artifacts.py"].read_text(encoding="utf-8")
    validation_strategy = required_inputs["VALIDATION_STRATEGY.md"].read_text(encoding="utf-8")
    benchmark_strategy = required_inputs["BENCHMARK_STRATEGY.md"].read_text(encoding="utf-8")
    open_questions = required_inputs["OPEN_QUESTIONS.md"].read_text(encoding="utf-8")
    execution_queue = required_inputs["EXECUTION_QUEUE.md"].read_text(encoding="utf-8")
    assumptions = required_inputs["ASSUMPTIONS.md"].read_text(encoding="utf-8")

    if "typescript_importer_conformance.py" in makefile:
        failures.append("Makefile: active commands must not invoke archived TypeScript conformance")
    if "typescript_importer_conformance.py" in run_repo_validation:
        failures.append("scripts/run_repo_validation.py: active validation must not invoke archived TypeScript conformance")
    if "--include-track-c-pilot" in makefile:
        failures.append("Makefile: default benchmark commands must not activate the non-default Track C pilot")
    if "benchmark-claim:" not in makefile:
        failures.append("Makefile: benchmark-claim target must remain explicit")
    if "benchmark-repro:" not in makefile:
        failures.append("Makefile: benchmark-repro target must remain explicit")
    if "Track `D`" in benchmark_strategy and "deferred" not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: Track D must remain explicitly deferred")
    for rel_name, text in {"OPEN_QUESTIONS.md": open_questions, "EXECUTION_QUEUE.md": execution_queue}.items():
        for forbidden in ["TypeScript", "D-JS"]:
            if forbidden in text:
                failures.append(f"{rel_name}: must not treat deferred scope as active ({forbidden})")
    if "excludes `select`" not in assumptions:
        failures.append("ASSUMPTIONS.md: select must remain explicitly excluded from the active subset")
    if "Rust reconstruction remains a deferred surface." not in validation_strategy:
        failures.append("VALIDATION_STRATEGY.md: Rust reconstruction must remain explicitly deferred")
    if 'benchmark_command = [sys.executable, "scripts/benchmark_contract_dry_run.py"]' not in run_repo_validation:
        failures.append("scripts/run_repo_validation.py: default benchmark command must remain Track A/B only")
    if 'benchmark_command.append("--include-track-c-pilot")' not in run_repo_validation:
        failures.append("scripts/run_repo_validation.py: optional Track C pilot flag handling must remain explicit")
    if '"conditional_track_c_validation_status"' not in run_repo_validation:
        failures.append("scripts/run_repo_validation.py: Track C validation status reporting must remain explicit")
    if benchmark_track_contract("C")["opt_in_command"] not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: Track C opt-in benchmark command must remain explicit")
    if benchmark_track_contract("C")["opt_in_command"] not in readme:
        failures.append("README.md: Track C opt-in benchmark command must remain explicit")
    if benchmark_track_contract("C")["opt_in_command"] not in validation_doc:
        failures.append("VALIDATION.md: Track C opt-in benchmark command must remain explicit")
    if benchmark_track_contract("C")["opt_in_validation_command"] not in readme:
        failures.append("README.md: Track C opt-in validation command must remain explicit")
    if benchmark_track_contract("C")["opt_in_validation_command"] not in validation_doc:
        failures.append("VALIDATION.md: Track C opt-in validation command must remain explicit")
    if benchmark_track_contract("C")["opt_in_validation_command"] not in validation_strategy:
        failures.append("VALIDATION_STRATEGY.md: Track C opt-in validation command must remain explicit")
    if "python scripts/benchmark_contract_dry_run.py --claim-run" not in readme:
        failures.append("README.md: explicit benchmark claim-run command must remain explicit")
    if "python scripts/benchmark_contract_dry_run.py --claim-run" not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: explicit benchmark claim-run command must remain explicit")
    if "python scripts/benchmark_repro.py --run-id" not in readme:
        failures.append("README.md: benchmark reproduction command must remain explicit")
    if "python scripts/benchmark_repro.py --run-id" not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: benchmark reproduction command must remain explicit")
    if "python scripts/sync_python_proof_loop_artifacts.py --mode check" not in readme:
        failures.append("README.md: Python proof-loop artifact sync check command must remain explicit")
    if "python scripts/sync_python_proof_loop_artifacts.py --mode write" not in readme:
        failures.append("README.md: Python proof-loop artifact sync write command must remain explicit")
    if "python scripts/sync_python_proof_loop_artifacts.py --mode check" not in validation_doc:
        failures.append("VALIDATION.md: Python proof-loop artifact sync check command must remain explicit")
    if "python scripts/sync_python_proof_loop_artifacts.py --mode write" not in validation_doc:
        failures.append("VALIDATION.md: Python proof-loop artifact sync write command must remain explicit")
    if '"--mode", choices=["check", "write"]' not in sync_python_artifacts:
        failures.append("scripts/sync_python_proof_loop_artifacts.py: sync command modes must remain explicit")
    if "run_track_c_pilot" not in sync_python_artifacts or "build_bundle" not in sync_python_artifacts:
        failures.append("scripts/sync_python_proof_loop_artifacts.py: sync command must remain generator-backed")
    return failures


def check_benchmark_contract(root: pathlib.Path):
    """Ensure benchmark docs, schemas, examples, and executable metadata describe the same bounded claim surface."""

    failures = []
    benchmark_strategy = (root / "BENCHMARK_STRATEGY.md").read_text(encoding="utf-8")
    tracks_doc = (root / "benchmarks" / "tracks.md").read_text(encoding="utf-8")
    baselines_doc = (root / "benchmarks" / "baselines.md").read_text(encoding="utf-8")
    corpora_doc = (root / "benchmarks" / "corpora_policy.md").read_text(encoding="utf-8")
    contamination_doc = (root / "benchmarks" / "contamination_controls.md").read_text(encoding="utf-8")
    gates_doc = (root / "benchmarks" / "success_failure_gates.md").read_text(encoding="utf-8")
    benchmarks_readme = (root / "benchmarks" / "README.md").read_text(encoding="utf-8")
    reports_readme = (root / "reports" / "README.md").read_text(encoding="utf-8")

    strategy_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_CASES_HEADING,
    )
    failures.extend(parse_failures)
    active_tracks, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_ACTIVE_HEADING,
    )
    failures.extend(parse_failures)
    conditional_tracks, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_CONDITIONAL_HEADING,
    )
    failures.extend(parse_failures)
    deferred_tracks, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_DEFERRED_HEADING,
    )
    failures.extend(parse_failures)
    mandatory_baselines, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/baselines.md",
        BENCHMARK_BASELINES_MANDATORY_HEADING,
    )
    failures.extend(parse_failures)
    track_a_extra, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/baselines.md",
        BENCHMARK_BASELINES_TRACK_A_EXTRA_HEADING,
    )
    failures.extend(parse_failures)
    track_c_baselines, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/baselines.md",
        BENCHMARK_BASELINES_TRACK_C_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_task_family, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_TASK_FAMILY_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_CASES_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_artifact_posture, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_ARTIFACT_POSTURE_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_execution_posture, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_EXECUTION_POSTURE_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_disposition, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_DISPOSITION_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_retention, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_RETENTION_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_retirement, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_RETIREMENT_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_sample_sync, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_SAMPLE_SYNC_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_sample_redecision, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_SAMPLE_REDECISION_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_editorial_refreshes, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_EDITORIAL_REFRESH_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_provenance, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_TRACK_C_PROVENANCE_HEADING,
    )
    failures.extend(parse_failures)
    tracks_track_c_task_family, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_TRACK_C_TASK_FAMILY_HEADING,
    )
    failures.extend(parse_failures)
    tracks_track_c_execution_posture, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_TRACK_C_EXECUTION_POSTURE_HEADING,
    )
    failures.extend(parse_failures)
    tracks_track_c_disposition, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_TRACK_C_DISPOSITION_HEADING,
    )
    failures.extend(parse_failures)
    tracks_track_c_sample_sync, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_TRACK_C_SAMPLE_SYNC_HEADING,
    )
    failures.extend(parse_failures)
    tracks_track_c_sample_redecision, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_TRACK_C_SAMPLE_REDECISION_HEADING,
    )
    failures.extend(parse_failures)
    tracks_track_c_editorial_refreshes, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_TRACK_C_EDITORIAL_REFRESH_HEADING,
    )
    failures.extend(parse_failures)
    tracks_track_c_provenance, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        BENCHMARK_TRACKS_TRACK_C_PROVENANCE_HEADING,
    )
    failures.extend(parse_failures)
    corpora_track_c_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/corpora_policy.md",
        BENCHMARK_CORPORA_TRACK_C_CASES_HEADING,
    )
    failures.extend(parse_failures)
    track_a_success, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_TRACK_A_SUCCESS_HEADING,
    )
    failures.extend(parse_failures)
    track_a_kill, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_TRACK_A_KILL_HEADING,
    )
    failures.extend(parse_failures)
    track_b_success, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_TRACK_B_SUCCESS_HEADING,
    )
    failures.extend(parse_failures)
    track_b_kill, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_TRACK_B_KILL_HEADING,
    )
    failures.extend(parse_failures)
    conditional_gates, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_CONDITIONAL_HEADING,
    )
    failures.extend(parse_failures)
    track_c_success, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_TRACK_C_SUCCESS_HEADING,
    )
    failures.extend(parse_failures)
    track_c_kill, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_TRACK_C_KILL_HEADING,
    )
    failures.extend(parse_failures)
    track_c_retention, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_TRACK_C_RETENTION_HEADING,
    )
    failures.extend(parse_failures)
    track_c_retirement, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_TRACK_C_RETIREMENT_HEADING,
    )
    failures.extend(parse_failures)
    deferred_gates, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        BENCHMARK_GATES_DEFERRED_HEADING,
    )
    failures.extend(parse_failures)

    track_c_contract = benchmark_track_contract("C")

    if strategy_cases is not None and strategy_cases != BENCHMARK_CONTRACT_METADATA["benchmark_cases"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: active executable benchmark cases expected "
            + repr(BENCHMARK_CONTRACT_METADATA["benchmark_cases"])
        )
    if active_tracks is not None and active_tracks != BENCHMARK_CONTRACT_METADATA["active_tracks"]:
        failures.append(
            "benchmarks/tracks.md: active executable tracks expected "
            + repr(BENCHMARK_CONTRACT_METADATA["active_tracks"])
        )
    if conditional_tracks is not None and conditional_tracks != BENCHMARK_CONTRACT_METADATA["conditional_tracks"]:
        failures.append(
            "benchmarks/tracks.md: conditional tracks expected "
            + repr(BENCHMARK_CONTRACT_METADATA["conditional_tracks"])
        )
    if deferred_tracks is not None and deferred_tracks != BENCHMARK_CONTRACT_METADATA["deferred_tracks"]:
        failures.append(
            "benchmarks/tracks.md: deferred tracks expected "
            + repr(BENCHMARK_CONTRACT_METADATA["deferred_tracks"])
        )
    if mandatory_baselines is not None and mandatory_baselines != BENCHMARK_CONTRACT_METADATA["mandatory_baselines"]:
        failures.append(
            "benchmarks/baselines.md: mandatory active baselines expected "
            + repr(BENCHMARK_CONTRACT_METADATA["mandatory_baselines"])
        )
    expected_track_a_extra = BENCHMARK_CONTRACT_METADATA["track_specific_additional_baselines"]["A"]
    if track_a_extra is not None and track_a_extra != expected_track_a_extra:
        failures.append(
            "benchmarks/baselines.md: Track A additional executable baselines expected "
            + repr(expected_track_a_extra)
        )
    if track_c_baselines is not None and track_c_baselines != benchmark_track_baselines("C"):
        failures.append(
            "benchmarks/baselines.md: Track C pilot baselines expected "
            + repr(benchmark_track_baselines("C"))
        )
    if strategy_track_c_task_family is not None and strategy_track_c_task_family != [track_c_contract["task_family"]]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C pilot task family expected "
            + repr([track_c_contract["task_family"]])
        )
    if strategy_track_c_cases is not None and strategy_track_c_cases != track_c_contract["pilot_cases"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C pilot cases expected "
            + repr(track_c_contract["pilot_cases"])
        )
    if strategy_track_c_artifact_posture is not None and strategy_track_c_artifact_posture != track_c_contract["artifact_posture"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C artifact posture expected "
            + repr(track_c_contract["artifact_posture"])
        )
    if strategy_track_c_execution_posture is not None and strategy_track_c_execution_posture != track_c_contract["execution_posture"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C executable pilot posture expected "
            + repr(track_c_contract["execution_posture"])
        )
    if strategy_track_c_disposition is not None and strategy_track_c_disposition != track_c_contract["disposition"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C disposition expected "
            + repr(track_c_contract["disposition"])
        )
    if strategy_track_c_retention is not None and strategy_track_c_retention != track_c_contract["retention_criteria"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C retention criteria expected "
            + repr(track_c_contract["retention_criteria"])
        )
    if strategy_track_c_retirement is not None and strategy_track_c_retirement != track_c_contract["retirement_triggers"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C retirement triggers expected "
            + repr(track_c_contract["retirement_triggers"])
        )
    if strategy_track_c_sample_sync is not None and strategy_track_c_sample_sync != track_c_contract["sample_sync_requirements"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C sample synchronization expected "
            + repr(track_c_contract["sample_sync_requirements"])
        )
    if strategy_track_c_sample_redecision is not None and strategy_track_c_sample_redecision != track_c_contract["sample_posture_redecision_triggers"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C sample posture re-decision triggers expected "
            + repr(track_c_contract["sample_posture_redecision_triggers"])
        )
    if strategy_track_c_editorial_refreshes is not None and strategy_track_c_editorial_refreshes != track_c_contract["editorial_only_sample_refreshes"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C editorial-only sample refreshes expected "
            + repr(track_c_contract["editorial_only_sample_refreshes"])
        )
    if strategy_track_c_provenance is not None and strategy_track_c_provenance != track_c_contract["non_editorial_sample_refresh_provenance"]:
        failures.append(
            "BENCHMARK_STRATEGY.md: conditional Track C non-editorial sample refresh provenance expected "
            + repr(track_c_contract["non_editorial_sample_refresh_provenance"])
        )
    if tracks_track_c_task_family is not None and tracks_track_c_task_family != [track_c_contract["task_family"]]:
        failures.append(
            "benchmarks/tracks.md: Track C pilot task family expected "
            + repr([track_c_contract["task_family"]])
        )
    if tracks_track_c_execution_posture is not None and tracks_track_c_execution_posture != track_c_contract["execution_posture"]:
        failures.append(
            "benchmarks/tracks.md: Track C executable pilot posture expected "
            + repr(track_c_contract["execution_posture"])
        )
    if tracks_track_c_disposition is not None and tracks_track_c_disposition != track_c_contract["disposition"]:
        failures.append(
            "benchmarks/tracks.md: Track C disposition expected "
            + repr(track_c_contract["disposition"])
        )
    if tracks_track_c_sample_sync is not None and tracks_track_c_sample_sync != track_c_contract["sample_sync_requirements"]:
        failures.append(
            "benchmarks/tracks.md: Track C sample synchronization expected "
            + repr(track_c_contract["sample_sync_requirements"])
        )
    if tracks_track_c_sample_redecision is not None and tracks_track_c_sample_redecision != track_c_contract["sample_posture_redecision_triggers"]:
        failures.append(
            "benchmarks/tracks.md: Track C sample posture re-decision triggers expected "
            + repr(track_c_contract["sample_posture_redecision_triggers"])
        )
    if tracks_track_c_editorial_refreshes is not None and tracks_track_c_editorial_refreshes != track_c_contract["editorial_only_sample_refreshes"]:
        failures.append(
            "benchmarks/tracks.md: Track C editorial-only sample refreshes expected "
            + repr(track_c_contract["editorial_only_sample_refreshes"])
        )
    if tracks_track_c_provenance is not None and tracks_track_c_provenance != track_c_contract["non_editorial_sample_refresh_provenance"]:
        failures.append(
            "benchmarks/tracks.md: Track C non-editorial sample refresh provenance expected "
            + repr(track_c_contract["non_editorial_sample_refresh_provenance"])
        )
    if corpora_track_c_cases is not None and corpora_track_c_cases != track_c_contract["pilot_cases"]:
        failures.append(
            "benchmarks/corpora_policy.md: Track C pilot cases expected "
            + repr(track_c_contract["pilot_cases"])
        )
    if track_a_success is not None and track_a_success != benchmark_track_contract("A")["success_gates"]:
        failures.append(
            "benchmarks/success_failure_gates.md: Track A success gates expected "
            + repr(benchmark_track_contract("A")["success_gates"])
        )
    if track_a_kill is not None and track_a_kill != benchmark_track_contract("A")["kill_gates"]:
        failures.append(
            "benchmarks/success_failure_gates.md: Track A kill gates expected "
            + repr(benchmark_track_contract("A")["kill_gates"])
        )
    if track_b_success is not None and track_b_success != benchmark_track_contract("B")["success_gates"]:
        failures.append(
            "benchmarks/success_failure_gates.md: Track B success gates expected "
            + repr(benchmark_track_contract("B")["success_gates"])
        )
    if track_b_kill is not None and track_b_kill != benchmark_track_contract("B")["kill_gates"]:
        failures.append(
            "benchmarks/success_failure_gates.md: Track B kill gates expected "
            + repr(benchmark_track_contract("B")["kill_gates"])
        )
    if conditional_gates is not None and conditional_gates != BENCHMARK_CONTRACT_METADATA["conditional_success_gates"]:
        failures.append(
            "benchmarks/success_failure_gates.md: conditional benchmark gates expected "
            + repr(BENCHMARK_CONTRACT_METADATA["conditional_success_gates"])
        )
    if track_c_success is not None and track_c_success != track_c_contract["success_gates"]:
        failures.append(
            "benchmarks/success_failure_gates.md: Track C pilot success gates expected "
            + repr(track_c_contract["success_gates"])
        )
    if track_c_kill is not None and track_c_kill != track_c_contract["kill_gates"]:
        failures.append(
            "benchmarks/success_failure_gates.md: Track C pilot kill gates expected "
            + repr(track_c_contract["kill_gates"])
        )
    if track_c_retention is not None and track_c_retention != track_c_contract["retention_criteria"]:
        failures.append(
            "benchmarks/success_failure_gates.md: Track C retention criteria expected "
            + repr(track_c_contract["retention_criteria"])
        )
    if track_c_retirement is not None and track_c_retirement != track_c_contract["retirement_triggers"]:
        failures.append(
            "benchmarks/success_failure_gates.md: Track C retirement triggers expected "
            + repr(track_c_contract["retirement_triggers"])
        )
    if deferred_gates is not None and deferred_gates != BENCHMARK_CONTRACT_METADATA["deferred_kill_gates"]:
        failures.append(
            "benchmarks/success_failure_gates.md: deferred benchmark misuse gates expected "
            + repr(BENCHMARK_CONTRACT_METADATA["deferred_kill_gates"])
        )

    if "Python single-function repair" not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: Track C pilot summary must remain Python single-function repair")
    if "Track `C` is conditional." not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: Track C must remain explicitly conditional")
    if "Track `D` is deferred." not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: Track D must remain explicitly deferred")
    if "Track `C` may not become active" not in tracks_doc:
        failures.append("benchmarks/tracks.md: Track C activation rule must remain explicit")
    if "Always interpret results against the strongest relevant baseline first." not in baselines_doc:
        failures.append("benchmarks/baselines.md: strongest-baseline rule must remain explicit")
    if "run_baseline(baseline_name, corpus_manifest)" not in baselines_doc:
        failures.append("benchmarks/baselines.md: pluggable baseline adapter interface must remain explicit")
    if "not a new broad benchmark corpus" not in corpora_doc:
        failures.append("benchmarks/corpora_policy.md: Track C pilot corpus must remain non-broadening")
    if "immutable once a reporting run locks them" not in corpora_doc:
        failures.append("benchmarks/corpora_policy.md: manifest-lock immutability rule must remain explicit")
    if "train/dev/test" not in contamination_doc:
        failures.append("benchmarks/contamination_controls.md: split enforcement must remain explicit")
    if "`duplicates`" not in contamination_doc or "`near_duplicates`" not in contamination_doc:
        failures.append("benchmarks/contamination_controls.md: contamination report fields must remain explicit")
    if "`manifest_lock.json`" not in contamination_doc:
        failures.append("benchmarks/contamination_controls.md: manifest lock output must remain explicit")
    if "Track `A` and `B` are the only active executable benchmark gates in the MVP." not in gates_doc:
        failures.append("benchmarks/success_failure_gates.md: active executable benchmark gate rule must remain explicit")
    if "baseline results are missing" not in gates_doc:
        failures.append("benchmarks/success_failure_gates.md: missing-baseline claim gate must remain explicit")
    if "corpus hash mismatches" not in gates_doc:
        failures.append("benchmarks/success_failure_gates.md: corpus-hash claim gate must remain explicit")
    if "reproducibility block is missing" not in gates_doc:
        failures.append("benchmarks/success_failure_gates.md: reproducibility-block claim gate must remain explicit")
    if "contamination is detected" not in gates_doc:
        failures.append("benchmarks/success_failure_gates.md: contamination claim gate must remain explicit")
    if "illustrative only and stay outside the default executable benchmark gate" not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C sample-artifact default-gate boundary must remain explicit")
    if "`comparison_summary.json`" not in benchmarks_readme or "`contamination_report.json`" not in benchmarks_readme:
        failures.append("benchmarks/README.md: audit artifact outputs must remain explicit")
    if "`benchmark_report.json`" not in benchmarks_readme or "`benchmark_report.md`" not in benchmarks_readme:
        failures.append("benchmarks/README.md: claim-bound report outputs must remain explicit")
    if "`manifest_lock.json`" not in benchmarks_readme:
        failures.append("benchmarks/README.md: manifest lock output must remain explicit")
    if "opt-in only via `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`" not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C opt-in executable pilot command must remain explicit")
    if "retain that pilot as a bounded diagnostic slice" not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C retained diagnostic disposition must remain explicit")
    if "must stay identical to the current opt-in pilot outputs while continuing to satisfy the retained lock criteria" not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C sample synchronization rule must remain explicit")
    if "requires a new decision-register entry and queue update before the sample bundle may change" not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C sample posture re-decision rule must remain explicit")
    if "editorial-only Track `C` sample refreshes are limited to JSON-equivalent formatting changes" not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C editorial-only sample refresh rule must remain explicit")
    if "any non-editorial Track `C` sample refresh that remains within the retained pilot contract must cite" not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C non-editorial sample refresh provenance rule must remain explicit")
    if track_c_contract["opt_in_command"] not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C non-editorial sample refresh regeneration command must remain explicit")
    if track_c_contract["opt_in_validation_command"] not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C non-editorial sample refresh validation command must remain explicit")
    if "the regenerated corpus hash, and the regenerated `run_id` plus `system_under_test`" not in benchmarks_readme:
        failures.append("benchmarks/README.md: Track C non-editorial sample refresh provenance fields must remain explicit")
    if "illustrative only and do not belong to the default executable benchmark gate" not in reports_readme:
        failures.append("reports/README.md: Track C sample-artifact posture must remain explicit")
    if "non-default executable pilot" not in reports_readme:
        failures.append("reports/README.md: Track C non-default executable pilot posture must remain explicit")
    if "retained diagnostic posture" not in reports_readme:
        failures.append("reports/README.md: Track C retained diagnostic posture must remain explicit")
    if "Any non-editorial refresh to those Track `C` samples must cite the opt-in regeneration command, the matching opt-in validation command, the regenerated corpus hash, and the regenerated `run_id` plus `system_under_test`." not in reports_readme:
        failures.append("reports/README.md: Track C non-editorial sample refresh provenance rule must remain explicit")
    if "`benchmark_report.example.json`" not in reports_readme:
        failures.append("reports/README.md: benchmark report example must remain explicit")
    if "`comparison_summary.example.json`" not in reports_readme:
        failures.append("reports/README.md: comparison summary example must remain explicit")
    if "`contamination_report.example.json`" not in reports_readme:
        failures.append("reports/README.md: contamination report example must remain explicit")
    failures.extend(check_track_c_benchmark_examples(root))
    return failures


def check_track_c_benchmark_examples(root: pathlib.Path):
    failures = []
    track_c_contract = benchmark_track_contract("C")
    manifest_rel = track_c_contract["sample_manifest_path"]
    result_rel = track_c_contract["sample_result_path"]
    manifest = load_json_artifact(root, manifest_rel, failures)
    result = load_json_artifact(root, result_rel, failures)
    if manifest is None or result is None:
        return failures

    if manifest.get("benchmark_id") != track_c_contract["benchmark_id"]:
        failures.append(f"{manifest_rel}: expected benchmark_id {track_c_contract['benchmark_id']}")
    if manifest.get("track") != "C":
        failures.append(f"{manifest_rel}: expected track C")
    if manifest.get("task_family") != track_c_contract["task_family"]:
        failures.append(f"{manifest_rel}: expected task_family {track_c_contract['task_family']}")
    corpus = manifest.get("corpus", {})
    if corpus.get("name") != track_c_contract["corpus_name"]:
        failures.append(f"{manifest_rel}: expected corpus name {track_c_contract['corpus_name']}")
    if corpus.get("scope") != track_c_contract["corpus_scope"]:
        failures.append(f"{manifest_rel}: expected corpus scope {track_c_contract['corpus_scope']}")
    if corpus.get("hash") != track_c_contract["sample_manifest_hash"]:
        failures.append(f"{manifest_rel}: expected corpus hash {track_c_contract['sample_manifest_hash']}")
    if manifest.get("baselines") != benchmark_track_baselines("C"):
        failures.append(f"{manifest_rel}: expected baselines {benchmark_track_baselines('C')}")
    if manifest.get("profiles") != track_c_contract["profiles"]:
        failures.append(f"{manifest_rel}: expected profiles {track_c_contract['profiles']}")
    if manifest.get("success_gates") != track_c_contract["success_gates"]:
        failures.append(f"{manifest_rel}: expected success gates {track_c_contract['success_gates']}")
    if manifest.get("kill_gates") != track_c_contract["kill_gates"]:
        failures.append(f"{manifest_rel}: expected kill gates {track_c_contract['kill_gates']}")
    if manifest.get("contamination_controls") != BENCHMARK_CONTRACT_METADATA["contamination_controls"]:
        failures.append(
            f"{manifest_rel}: expected contamination controls {BENCHMARK_CONTRACT_METADATA['contamination_controls']}"
        )
    failures.extend(validate_track_c_sample_posture(track_c_contract, manifest, result, manifest_rel, result_rel))

    if result.get("benchmark_id") != track_c_contract["benchmark_id"]:
        failures.append(f"{result_rel}: expected benchmark_id {track_c_contract['benchmark_id']}")
    if result.get("run_id") != track_c_contract["sample_run_id"]:
        failures.append(f"{result_rel}: expected run_id {track_c_contract['sample_run_id']}")
    if result.get("system_under_test") != track_c_contract["sample_system_under_test"]:
        failures.append(f"{result_rel}: expected system_under_test {track_c_contract['sample_system_under_test']}")
    if result.get("track") != "C":
        failures.append(f"{result_rel}: expected track C")
    if result.get("profile") != track_c_contract["result_profile"]:
        failures.append(f"{result_rel}: expected profile {track_c_contract['result_profile']}")
    if result.get("status") != track_c_contract["sample_result_status"]:
        failures.append(f"{result_rel}: expected status {track_c_contract['sample_result_status']}")
    metrics = result.get("metrics", {})
    for metric in track_c_contract["required_metrics"]:
        if metric not in metrics:
            failures.append(f"{result_rel}: missing metric {metric}")
    if metrics.get("preservation_level_ceiling") != BENCHMARK_CONTRACT_METADATA["preservation_level_ceiling"]:
        failures.append(
            f"{result_rel}: expected preservation_level_ceiling {BENCHMARK_CONTRACT_METADATA['preservation_level_ceiling']}"
        )
    if list(result.get("baseline_comparison", {})) != benchmark_track_baselines("C"):
        failures.append(f"{result_rel}: expected baseline comparison keys {benchmark_track_baselines('C')}")
    if result.get("evidence") != track_c_contract["sample_evidence"]:
        failures.append(f"{result_rel}: expected evidence {track_c_contract['sample_evidence']}")
    failures.extend(validate_track_c_result_lock_criteria(track_c_contract, result, result_rel))
    return failures


def check_wasm_emitter_contract(root: pathlib.Path):
    """Reject Wasm contract drift that would imply broader ABI or preservation claims than the frozen subset supports."""

    failures = []
    wasm_readme = (root / "backends" / "wasm" / "README.md").read_text(encoding="utf-8")
    lowering_contract = (root / "LOWERING_CONTRACT.md").read_text(encoding="utf-8")
    validation_doc = (root / "VALIDATION.md").read_text(encoding="utf-8")
    validation_strategy = (root / "VALIDATION_STRATEGY.md").read_text(encoding="utf-8")
    example = load_json_artifact(root, "reports/examples/preservation_l_to_wasm.example.json", failures)

    for marker in [
        "helper-free",
        "backend-local slot assignment",
        "`field.addr`",
        "`async.resume`",
        "`opaque.call`",
    ]:
        if marker not in wasm_readme:
            failures.append(f"backends/wasm/README.md: missing helper-free Wasm boundary marker {marker}")
    if "module-owned linear memory" not in wasm_readme or "caller-visible mutation preserved only for callers that explicitly share the same record-cell ABI" not in wasm_readme:
        failures.append("backends/wasm/README.md: expected explicit bounded record-cell ABI markers")
    if "broader field-place shapes beyond the fixed record-cell case" not in wasm_readme:
        failures.append("backends/wasm/README.md: expected explicit non-candidate field-place blocker")

    if "helper-free Wasm emitter slice" not in validation_doc:
        failures.append("VALIDATION.md: canonical validation path must mention the helper-free Wasm emitter slice")

    expected_python_modules = [
        f"fixture.python_importer.{case_name}"
        for case_name in WASM_BACKEND_METADATA["emittable_python_cases"]
    ]
    expected_rust_modules = [
        f"fixture.rust_importer.{case_name}"
        for case_name in WASM_BACKEND_METADATA["emittable_rust_cases"]
    ]
    expected_module_ids = wasm_emittable_module_ids()
    expected_admitted_rules = list(WASM_BACKEND_METADATA["admitted_lowering_rules"])
    expected_non_emittable_rules = list(WASM_BACKEND_METADATA["non_emittable_lowering_rules"])

    python_modules, parse_failures = parse_markdown_bullet_list_section(
        root,
        "backends/wasm/README.md",
        WASM_README_PYTHON_HEADING,
    )
    failures.extend(parse_failures)
    rust_modules, parse_failures = parse_markdown_bullet_list_section(
        root,
        "backends/wasm/README.md",
        WASM_README_RUST_HEADING,
    )
    failures.extend(parse_failures)
    readme_admitted_rules, parse_failures = parse_markdown_bullet_list_section(
        root,
        "backends/wasm/README.md",
        WASM_README_ADMITTED_RULES_HEADING,
    )
    failures.extend(parse_failures)
    readme_non_emittable_rules, parse_failures = parse_markdown_bullet_list_section(
        root,
        "backends/wasm/README.md",
        WASM_README_NON_EMITTABLE_RULES_HEADING,
    )
    failures.extend(parse_failures)
    contract_admitted_rules, parse_failures = parse_markdown_bullet_list_section(
        root,
        "LOWERING_CONTRACT.md",
        LOWERING_CONTRACT_WASM_ADMITTED_HEADING,
    )
    failures.extend(parse_failures)
    contract_non_emittable_rules, parse_failures = parse_markdown_bullet_list_section(
        root,
        "LOWERING_CONTRACT.md",
        LOWERING_CONTRACT_WASM_NON_EMITTABLE_HEADING,
    )
    failures.extend(parse_failures)
    strategy_modules, parse_failures = parse_markdown_bullet_list_section(
        root,
        "VALIDATION_STRATEGY.md",
        VALIDATION_STRATEGY_WASM_MODULES_HEADING,
    )
    failures.extend(parse_failures)

    if python_modules is not None and python_modules != expected_python_modules:
        failures.append(
            "backends/wasm/README.md: admitted Python emitted modules expected "
            + repr(expected_python_modules)
        )
    if rust_modules is not None and rust_modules != expected_rust_modules:
        failures.append(
            "backends/wasm/README.md: admitted Rust emitted modules expected "
            + repr(expected_rust_modules)
        )
    if readme_admitted_rules is not None and readme_admitted_rules != expected_admitted_rules:
        failures.append(
            "backends/wasm/README.md: admitted Wasm lowering rules expected "
            + repr(expected_admitted_rules)
        )
    if readme_non_emittable_rules is not None and readme_non_emittable_rules != expected_non_emittable_rules:
        failures.append(
            "backends/wasm/README.md: non-emittable Wasm lowering rules expected "
            + repr(expected_non_emittable_rules)
        )
    if contract_admitted_rules is not None and contract_admitted_rules != expected_admitted_rules:
        failures.append(
            "LOWERING_CONTRACT.md: Wasm-admitted lowering rules expected "
            + repr(expected_admitted_rules)
        )
    if contract_non_emittable_rules is not None and contract_non_emittable_rules != expected_non_emittable_rules:
        failures.append(
            "LOWERING_CONTRACT.md: Wasm-non-emittable lowering rules expected "
            + repr(expected_non_emittable_rules)
        )
    if strategy_modules is not None and strategy_modules != expected_module_ids:
        failures.append(
            "VALIDATION_STRATEGY.md: admitted helper-free Wasm-emission modules expected "
            + repr(expected_module_ids)
        )

    if "profile `P`" not in wasm_readme or "`P2` ceiling" not in wasm_readme:
        failures.append("backends/wasm/README.md: expected explicit profile P and P2 ceiling markers")
    if "profile `P` with a `P2` contract ceiling" not in lowering_contract:
        failures.append("LOWERING_CONTRACT.md: expected explicit Wasm profile P and P2 ceiling marker")
    if "module-owned linear memory" not in lowering_contract or "shared-handle callers only" not in lowering_contract:
        failures.append("LOWERING_CONTRACT.md: expected explicit bounded record-cell ABI markers")
    if "path-qualified `l_to_wasm` evidence" not in validation_strategy:
        failures.append("VALIDATION_STRATEGY.md: Wasm validation must mention path-qualified l_to_wasm evidence")
    if "field-place lowering is normalized into imported memory, hidden host layout, or non-shared-handle callers" not in validation_strategy:
        failures.append("VALIDATION_STRATEGY.md: Wasm validation must reject non-candidate field-place normalization")

    if example is None:
        return failures

    if example.get("path") != WASM_BACKEND_METADATA["report_path"]:
        failures.append(
            "reports/examples/preservation_l_to_wasm.example.json: expected path "
            + WASM_BACKEND_METADATA["report_path"]
        )
    if example.get("profile") != WASM_BACKEND_METADATA["profile"]:
        failures.append(
            "reports/examples/preservation_l_to_wasm.example.json: expected profile "
            + WASM_BACKEND_METADATA["profile"]
        )
    if example.get("preservation_level") != WASM_BACKEND_METADATA["preservation_level"]:
        failures.append(
            "reports/examples/preservation_l_to_wasm.example.json: expected preservation_level "
            + WASM_BACKEND_METADATA["preservation_level"]
        )
    if example.get("status") != "pass":
        failures.append("reports/examples/preservation_l_to_wasm.example.json: expected status pass")

    downgrade_reasons = {item.get("reason") for item in example.get("downgrades", [])}
    required_reasons = {
        WASM_BACKEND_METADATA["local_slot_reason"],
        WASM_BACKEND_METADATA["cmp_reason"],
    }
    missing_reasons = sorted(reason for reason in required_reasons if reason not in downgrade_reasons)
    if missing_reasons:
        failures.append(
            "reports/examples/preservation_l_to_wasm.example.json: missing downgrade reasons "
            + ", ".join(missing_reasons)
        )

    normalized = example.get("observables", {}).get("normalized", [])
    if normalized != [WASM_BACKEND_METADATA["normalized_observable"]]:
        failures.append(
            "reports/examples/preservation_l_to_wasm.example.json: normalized observables expected "
            + repr([WASM_BACKEND_METADATA["normalized_observable"]])
        )
    contract_bounded = example.get("observables", {}).get("contract_bounded", [])
    if contract_bounded != [WASM_BACKEND_METADATA["contract_bounded_observable"]]:
        failures.append(
            "reports/examples/preservation_l_to_wasm.example.json: contract_bounded observables expected "
            + repr([WASM_BACKEND_METADATA["contract_bounded_observable"]])
        )

    required_evidence = set(WASM_BACKEND_METADATA["required_evidence"])
    missing_evidence = sorted(item for item in required_evidence if item not in example.get("evidence", []))
    if missing_evidence:
        failures.append(
            "reports/examples/preservation_l_to_wasm.example.json: missing evidence "
            + ", ".join(missing_evidence)
        )
    return failures


def run_checks(root: pathlib.Path):
    failures = []
    failures.extend(f"missing file: {rel}" for rel in check_required_files(root))
    failures.extend(check_json_files(root))
    failures.extend(check_nonempty_markdown(root))
    failures.extend(check_schema_metadata(root))
    failures.extend(check_example_artifacts(root))
    failures.extend(check_decision_register_export(root))
    failures.extend(check_open_questions_export(root))
    failures.extend(check_execution_queue_export(root))
    failures.extend(check_spec_completeness_checklist(root))
    failures.extend(check_scir_h_kernel_alignment(root))
    failures.extend(check_preservation_path_examples(root))
    failures.extend(check_active_corpora(root))
    failures.extend(check_corpus_manifest(root, "tests/corpora/python_preservation_negative_corpus.json"))
    failures.extend(check_invalid_scir_h_examples(root))
    failures.extend(check_invalid_scir_l_examples(root))
    failures.extend(check_identity_contract(root))
    failures.extend(check_python_proof_loop_contract(root))
    failures.extend(check_rust_importer_contract(root))
    failures.extend(check_benchmark_contract(root))
    failures.extend(check_sweep_contract(root))
    failures.extend(check_not_active_markers(root))
    failures.extend(check_active_surface_contract(root))
    failures.extend(check_wasm_emitter_contract(root))
    return failures


def mutate_remove_required_file(root: pathlib.Path):
    (root / "README.md").unlink()


def mutate_break_preservation_schema(root: pathlib.Path):
    path = root / "schemas" / "preservation_report.schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["required"].remove("path")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_break_checklist_row(root: pathlib.Path):
    path = root / "SPEC_COMPLETENESS_CHECKLIST.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("| `await` |", "| await-missing |", 1), encoding="utf-8")


def mutate_break_scir_h_spec_kernel_row(root: pathlib.Path):
    path = root / "specs" / "scir_h_spec.md"
    text = path.read_text(encoding="utf-8")
    old = "| `await` | yes | fully supported in MVP |"
    new = "| `await` | no | deferred |"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_identity_kernel_marker(root: pathlib.Path):
    path = root / "IDENTITY_MODEL.md"
    text = path.read_text(encoding="utf-8")
    old = "- revision-scoped node identity must vary when the revision tag changes"
    new = "- revision-scoped node identity may stay stable when the revision tag changes"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_decision_register_export(root: pathlib.Path):
    path = root / DECISION_REGISTER_EXPORT_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    data["decisions"][0]["decision"] = "drifted export"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mutate_break_open_questions_export(root: pathlib.Path):
    path = root / OPEN_QUESTIONS_EXPORT_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    data["open_questions"][0]["blocker"] = "yes"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mutate_break_execution_queue_export(root: pathlib.Path):
    path = root / EXECUTION_QUEUE_EXPORT_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    data["next_action"]["queue_id"] = "Q-00-999"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mutate_break_python_executable_case_list(root: pathlib.Path):
    path = root / "frontend" / "python" / "IMPORT_SCOPE.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- `a_async_await`", "- `b_if_else_return`", 1), encoding="utf-8")


def mutate_break_python_importer_only_case_list(root: pathlib.Path):
    path = root / "frontend" / "python" / "IMPORT_SCOPE.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- `d_try_except`", "- `d_exec_eval`", 1), encoding="utf-8")


def mutate_break_python_reconstruction_case_list(root: pathlib.Path):
    path = root / "docs" / "reconstruction_policy.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- `c_opaque_call`", "- `b_direct_call`", 1), encoding="utf-8")


def mutate_break_tier_a_corpus_hash(root: pathlib.Path):
    path = root / ACTIVE_TIER_A_CORPUS_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    data["fixtures"][0]["hash"] = "sha256:" + "0" * 64
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_break_sweep_manifest_corpus(root: pathlib.Path):
    path = root / SWEEP_SMOKE_REL
    data = json.loads(path.read_text(encoding="utf-8"))
    data["corpus_manifest"] = "tests/corpora/missing.json"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_break_rust_supported_case_list(root: pathlib.Path):
    path = root / "frontend" / "rust" / "IMPORT_SCOPE.md"
    text = path.read_text(encoding="utf-8")
    old = "### Importer-first evidence cases\n\n- `a_mut_local`\n- `a_struct_field_borrow_mut`\n- `a_async_await`\n- `c_unsafe_call`"
    new = "### Importer-first evidence cases\n\n- `a_mut_local`\n- `a_struct_field_borrow_mut`\n- `a_async_await`\n- `d_proc_macro`"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_rust_tier_a_case_list(root: pathlib.Path):
    path = root / "frontend" / "rust" / "IMPORT_SCOPE.md"
    text = path.read_text(encoding="utf-8")
    old = "### Tier A importer-evidence cases\n\n- `a_mut_local`\n- `a_struct_field_borrow_mut`\n- `a_async_await`"
    new = "### Tier A importer-evidence cases\n\n- `a_mut_local`\n- `a_struct_field_borrow_mut`\n- `c_unsafe_call`"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_rust_wasm_case_list(root: pathlib.Path):
    path = root / "frontend" / "rust" / "IMPORT_SCOPE.md"
    text = path.read_text(encoding="utf-8")
    old = "### Helper-free Wasm-emittable case\n\n- `a_mut_local`\n- `a_struct_field_borrow_mut`"
    new = "### Helper-free Wasm-emittable case\n\n- `a_mut_local`\n- `a_async_await`"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_benchmark_case_list(root: pathlib.Path):
    path = root / "BENCHMARK_STRATEGY.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- `c_opaque_call`", "- `b_direct_call`", 1), encoding="utf-8")


def mutate_break_benchmark_baseline_list(root: pathlib.Path):
    path = root / "benchmarks" / "baselines.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- `typed-AST`", "- `ssa-like IR`", 1), encoding="utf-8")


def mutate_break_benchmark_gate_list(root: pathlib.Path):
    path = root / "benchmarks" / "success_failure_gates.md"
    text = path.read_text(encoding="utf-8")
    old = "### Track B kill gates\n\n- `K3`\n- `K4`"
    new = "### Track B kill gates\n\n- `K3`\n- `K5`"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_task_family_list(root: pathlib.Path):
    path = root / "benchmarks" / "tracks.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- `python-single-function-repair`", "- `repository-scale-issue-repair`", 1), encoding="utf-8")


def mutate_break_track_c_baseline_list(root: pathlib.Path):
    path = root / "benchmarks" / "baselines.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "### Track C pilot baselines\n\n"
        "- `direct source`\n"
        "- `typed-AST`\n"
        "- `lightweight regularized core or s-expression`"
    )
    new = (
        "### Track C pilot baselines\n\n"
        "- `direct source`\n"
        "- `typed-AST`\n"
        "- `ssa-like IR`"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_gate_list(root: pathlib.Path):
    path = root / "benchmarks" / "success_failure_gates.md"
    text = path.read_text(encoding="utf-8")
    old = "### Track C pilot kill gates\n\n- `K1`"
    new = "### Track C pilot kill gates\n\n- `K2`"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_disposition_list(root: pathlib.Path):
    path = root / "benchmarks" / "tracks.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "## Track C disposition\n\n"
        "- `retain bounded diagnostic pilot`\n"
        "- `do not promote to default executable gate`\n"
        "- `keep c_opaque_call boundary-accounting-only`"
    )
    new = (
        "## Track C disposition\n\n"
        "- `retire pilot immediately`\n"
        "- `do not promote to default executable gate`\n"
        "- `keep c_opaque_call boundary-accounting-only`"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_retention_list(root: pathlib.Path):
    path = root / "benchmarks" / "success_failure_gates.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "### Track C retention criteria\n\n"
        "- `gate_S2_ready must remain true`\n"
        "- `gate_K1_hit must remain false`\n"
        "- `accepted_case_count must remain 3`\n"
        "- `boundary_only_case_count must remain 1`\n"
        "- `status must remain mixed or pass`"
    )
    new = (
        "### Track C retention criteria\n\n"
        "- `gate_S2_ready must remain true`\n"
        "- `gate_K1_hit must remain false`\n"
        "- `accepted_case_count must remain 1`\n"
        "- `boundary_only_case_count must remain 1`\n"
        "- `status must remain mixed or pass`"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_retirement_list(root: pathlib.Path):
    path = root / "benchmarks" / "success_failure_gates.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "### Track C retirement triggers\n\n"
        "- `retire if gate_S2_ready becomes false`\n"
        "- `retire if gate_K1_hit becomes true`\n"
        "- `retire if accepted_case_count drops below 3`\n"
        "- `retire if boundary_only_case_count differs from 1`\n"
        "- `retire if status becomes fail`"
    )
    new = (
        "### Track C retirement triggers\n\n"
        "- `retire if gate_S2_ready becomes false`\n"
        "- `retire if gate_K1_hit becomes true`\n"
        "- `retire if accepted_case_count drops below 1`\n"
        "- `retire if boundary_only_case_count differs from 1`\n"
        "- `retire if status becomes fail`"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_sample_sync_list(root: pathlib.Path):
    path = root / "benchmarks" / "tracks.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "## Track C sample synchronization\n\n"
        "- `checked-in sample manifest must equal the current opt-in pilot manifest`\n"
        "- `checked-in sample result must equal the current opt-in pilot result`\n"
        "- `checked-in sample result must keep accepted_case_count 3 and boundary_only_case_count 1`\n"
        "- `checked-in sample result must keep gate_S2_ready true, gate_K1_hit false, and status mixed or pass`"
    )
    new = (
        "## Track C sample synchronization\n\n"
        "- `checked-in sample manifest may differ from the current opt-in pilot manifest`\n"
        "- `checked-in sample result must equal the current opt-in pilot result`\n"
        "- `checked-in sample result must keep accepted_case_count 3 and boundary_only_case_count 1`\n"
        "- `checked-in sample result must keep gate_S2_ready true, gate_K1_hit false, and status mixed or pass`"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_sample_redecision_list(root: pathlib.Path):
    path = root / "benchmarks" / "tracks.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "## Track C sample posture re-decision triggers\n\n"
        "- `changing checked-in sample status from mixed requires a new decision-register entry and queue update`\n"
        "- `changing checked-in sample evidence or retained-diagnostic wording requires a new decision-register entry and queue update`\n"
        "- `changing checked-in sample task family, case set, or boundary-accounting posture requires a new decision-register entry and queue update`\n"
        "- `changing checked-in sample default-gate or promotion posture requires a new decision-register entry and queue update`"
    )
    new = (
        "## Track C sample posture re-decision triggers\n\n"
        "- `changing checked-in sample status from mixed is editorial only`\n"
        "- `changing checked-in sample evidence or retained-diagnostic wording requires a new decision-register entry and queue update`\n"
        "- `changing checked-in sample task family, case set, or boundary-accounting posture requires a new decision-register entry and queue update`\n"
        "- `changing checked-in sample default-gate or promotion posture requires a new decision-register entry and queue update`"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_editorial_refresh_list(root: pathlib.Path):
    path = root / "benchmarks" / "tracks.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "## Track C editorial-only sample refreshes\n\n"
        "- `json whitespace, indentation, and trailing-newline normalization that preserves parsed sample content`\n"
        "- `json key-order normalization that preserves parsed sample content`"
    )
    new = (
        "## Track C editorial-only sample refreshes\n\n"
        "- `status updates that preserve the retained diagnostic intent`\n"
        "- `json key-order normalization that preserves parsed sample content`"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_provenance_list(root: pathlib.Path):
    path = root / "benchmarks" / "tracks.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "## Track C non-editorial sample refresh provenance\n\n"
        "- `cite python scripts/benchmark_contract_dry_run.py --include-track-c-pilot as the regeneration command`\n"
        "- `cite python scripts/run_repo_validation.py --include-track-c-pilot as the confirming validation command`\n"
        "- `cite the regenerated manifest corpus hash`\n"
        "- `cite the regenerated result run_id and system_under_test`"
    )
    new = (
        "## Track C non-editorial sample refresh provenance\n\n"
        "- `cite python scripts/benchmark_contract_dry_run.py --include-track-c-pilot as the regeneration command`\n"
        "- `cite python scripts/run_repo_validation.py --include-track-c-pilot as the confirming validation command`\n"
        "- `cite any convenient corpus hash`\n"
        "- `cite the regenerated result run_id and system_under_test`"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_benchmark_readme_provenance(root: pathlib.Path):
    path = root / "benchmarks" / "README.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "- any non-editorial Track `C` sample refresh that remains within the retained pilot contract must cite "
        "`python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`, "
        "`python scripts/run_repo_validation.py --include-track-c-pilot`, the regenerated corpus hash, "
        "and the regenerated `run_id` plus `system_under_test`"
    )
    new = (
        "- any non-editorial Track `C` sample refresh may cite a local rerun note without recording the exact "
        "runner commands or regenerated provenance fields"
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_reports_readme_provenance(root: pathlib.Path):
    path = root / "reports" / "README.md"
    text = path.read_text(encoding="utf-8")
    old = (
        "Any non-editorial refresh to those Track `C` samples must cite the opt-in regeneration command, "
        "the matching opt-in validation command, the regenerated corpus hash, and the regenerated `run_id` "
        "plus `system_under_test`."
    )
    new = (
        "Any non-editorial refresh to those Track `C` samples may be summarized without recording the exact "
        "opt-in regeneration provenance."
    )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_track_c_sample_evidence(root: pathlib.Path):
    path = root / "reports" / "examples" / "benchmark_track_c_result.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["evidence"] = [
        "non-default executable pilot over fixed Python repair cases",
        "seeded single-edit repairs restore original behavior for executable non-opaque cases",
        "c_opaque_call remains boundary-accounting-only",
        "promotion-ready benchmark slice",
    ]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def mutate_break_track_c_sample_status(root: pathlib.Path):
    path = root / "reports" / "examples" / "benchmark_track_c_result.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["status"] = "pass"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def mutate_break_track_c_sample_lock_metric(root: pathlib.Path):
    path = root / "reports" / "examples" / "benchmark_track_c_result.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["metrics"]["accepted_case_count"] = 1
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def mutate_reenter_track_c_default_gate(root: pathlib.Path):
    path = root / "benchmarks" / "README.md"
    text = path.read_text(encoding="utf-8")
    old = "- Track `C` sample artifacts in `reports/examples/` are illustrative only and stay outside the default executable benchmark gate"
    new = "- Track `C` sample artifacts in `reports/examples/` are part of the default executable benchmark gate"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_makefile_reenter_track_c_default_gate(root: pathlib.Path):
    path = root / "Makefile"
    text = path.read_text(encoding="utf-8")
    old = "benchmark:\n\t$(PYTHON) scripts/benchmark_contract_dry_run.py\n"
    new = "benchmark:\n\t$(PYTHON) scripts/benchmark_contract_dry_run.py --include-track-c-pilot\n"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_validation_runner_reenter_track_c_default_gate(root: pathlib.Path):
    path = root / "scripts" / "run_repo_validation.py"
    text = path.read_text(encoding="utf-8")
    old = '    benchmark_command = [sys.executable, "scripts/benchmark_contract_dry_run.py"]\n'
    new = '    benchmark_command = [sys.executable, "scripts/benchmark_contract_dry_run.py", "--include-track-c-pilot"]\n'
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_remove_sync_command_from_readme(root: pathlib.Path):
    path = root / "README.md"
    text = path.read_text(encoding="utf-8")
    old = "python scripts/sync_python_proof_loop_artifacts.py --mode check\npython scripts/sync_python_proof_loop_artifacts.py --mode write\n"
    new = ""
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_wasm_python_module_list(root: pathlib.Path):
    path = root / "backends" / "wasm" / "README.md"
    text = path.read_text(encoding="utf-8")
    old = "### Admitted Python emitted modules\n\n- `fixture.python_importer.a_basic_function`\n- `fixture.python_importer.b_direct_call`"
    new = "### Admitted Python emitted modules\n\n- `fixture.python_importer.a_basic_function`\n- `fixture.python_importer.a_async_await`"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_wasm_non_emittable_rule_list(root: pathlib.Path):
    path = root / "LOWERING_CONTRACT.md"
    text = path.read_text(encoding="utf-8")
    old = "### Wasm-non-emittable lowering rules\n\n- `H_AWAIT_RESUME`\n- `H_OPAQUE_CALL`"
    new = "### Wasm-non-emittable lowering rules\n\n- `H_AWAIT_RESUME`\n- `H_BRANCH_JOIN`"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_remove_wasm_record_cell_marker(root: pathlib.Path):
    path = root / "backends" / "wasm" / "README.md"
    text = path.read_text(encoding="utf-8")
    old = "caller-visible mutation preserved only for callers that explicitly share the same record-cell ABI"
    new = "caller-visible mutation preserved for callers"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_break_wasm_validation_module_list(root: pathlib.Path):
    path = root / "VALIDATION_STRATEGY.md"
    text = path.read_text(encoding="utf-8")
    old = "### Admitted helper-free Wasm-emission modules\n\n- `fixture.python_importer.a_basic_function`\n- `fixture.python_importer.b_direct_call`\n- `fixture.rust_importer.a_mut_local`\n- `fixture.rust_importer.a_struct_field_borrow_mut`"
    new = "### Admitted helper-free Wasm-emission modules\n\n- `fixture.python_importer.a_basic_function`\n- `fixture.python_importer.a_async_await`\n- `fixture.rust_importer.a_mut_local`\n- `fixture.rust_importer.a_struct_field_borrow_mut`"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def mutate_reactivate_typescript(root: pathlib.Path):
    path = root / "Makefile"
    text = path.read_text(encoding="utf-8")
    text += "\n\t$(PYTHON) scripts/typescript_importer_conformance.py --mode validate-fixtures\n"
    path.write_text(text, encoding="utf-8")


def mutate_remove_not_active_marker(root: pathlib.Path):
    (root / "frontend" / "typescript" / "NOT_ACTIVE.md").unlink()


def mutate_remove_preservation_stage_behavior(root: pathlib.Path):
    path = root / ACTIVE_TIER_A_CORPUS_REL
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["fixtures"][0].pop("expected_preservation_stage_behavior", None)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def mutate_make_invalid_fixture_parseable(root: pathlib.Path):
    path = root / "tests" / "invalid_scir_h" / "legacy_brace_syntax.scirh"
    path.write_text("module valid.now\nfn ok -> int !\n  return 1\n", encoding="utf-8")


def run_negative_fixture(root: pathlib.Path, name: str, mutate, expected_markers):
    with tempfile.TemporaryDirectory(prefix="scir_repo_check_") as tmp:
        fixture_root = pathlib.Path(tmp) / "repo"
        shutil.copytree(
            root,
            fixture_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__"),
        )
        mutate(fixture_root)
        failures = run_checks(fixture_root)

    if not failures:
        return [f"self-test {name}: expected failure but validation passed"]

    missing_markers = [
        marker for marker in expected_markers if not any(marker in failure for failure in failures)
    ]
    if missing_markers:
        return [f"self-test {name}: missing expected failure markers {', '.join(missing_markers)}"]
    return []


def get_self_test_cases():
    return [
        ("missing required file", mutate_remove_required_file, ["missing file: README.md"]),
        (
            "preservation schema completeness",
            mutate_break_preservation_schema,
            ["schemas/preservation_report.schema.json: missing required fields path"],
        ),
        (
            "checklist drift",
            mutate_break_checklist_row,
            ["SPEC_COMPLETENESS_CHECKLIST.md: missing required rows `await`"],
        ),
        (
            "scir-h kernel spec drift",
            mutate_break_scir_h_spec_kernel_row,
            ["specs/scir_h_spec.md: kernel row `await` expected canonical parser/formatter 'yes'"],
        ),
        (
            "identity kernel marker drift",
            mutate_break_identity_kernel_marker,
            ["IDENTITY_MODEL.md: missing kernel identity marker"],
        ),
        (
            "decision register export drift",
            mutate_break_decision_register_export,
            [DECISION_REGISTER_EXPORT_REL, "decision"],
        ),
        (
            "open questions export drift",
            mutate_break_open_questions_export,
            [OPEN_QUESTIONS_EXPORT_REL, "blocker"],
        ),
        (
            "execution queue drift",
            mutate_break_execution_queue_export,
            [EXECUTION_QUEUE_EXPORT_REL, "synchronization check failed"],
        ),
        (
            "python executable proof-loop drift",
            mutate_break_python_executable_case_list,
            ["frontend/python/IMPORT_SCOPE.md: executable proof-loop cases expected"],
        ),
        (
            "python importer-only proof-loop drift",
            mutate_break_python_importer_only_case_list,
            ["frontend/python/IMPORT_SCOPE.md: importer-only proof-loop cases expected"],
        ),
        (
            "python reconstruction proof-loop drift",
            mutate_break_python_reconstruction_case_list,
            ["docs/reconstruction_policy.md: active reconstruction cases expected"],
        ),
        (
            "tier a corpus hash drift",
            mutate_break_tier_a_corpus_hash,
            [f"{ACTIVE_TIER_A_CORPUS_REL}: hash drift"],
        ),
        (
            "sweep manifest corpus drift",
            mutate_break_sweep_manifest_corpus,
            [f"{SWEEP_SMOKE_REL}: referenced corpus manifest missing"],
        ),
        (
            "rust supported importer drift",
            mutate_break_rust_supported_case_list,
            ["frontend/rust/IMPORT_SCOPE.md: importer-first Rust cases expected"],
        ),
        (
            "rust tier-a importer drift",
            mutate_break_rust_tier_a_case_list,
            ["frontend/rust/IMPORT_SCOPE.md: Tier A Rust importer cases expected"],
        ),
        (
            "rust wasm importer drift",
            mutate_break_rust_wasm_case_list,
            ["frontend/rust/IMPORT_SCOPE.md: Wasm-emittable Rust cases expected"],
        ),
        (
            "benchmark case drift",
            mutate_break_benchmark_case_list,
            ["BENCHMARK_STRATEGY.md: active executable benchmark cases expected"],
        ),
        (
            "benchmark baseline drift",
            mutate_break_benchmark_baseline_list,
            ["benchmarks/baselines.md: mandatory active baselines expected"],
        ),
        (
            "benchmark gate drift",
            mutate_break_benchmark_gate_list,
            ["benchmarks/success_failure_gates.md: Track B kill gates expected"],
        ),
        (
            "track c task family drift",
            mutate_break_track_c_task_family_list,
            ["benchmarks/tracks.md: Track C pilot task family expected"],
        ),
        (
            "track c baseline drift",
            mutate_break_track_c_baseline_list,
            ["benchmarks/baselines.md: Track C pilot baselines expected"],
        ),
        (
            "track c gate drift",
            mutate_break_track_c_gate_list,
            ["benchmarks/success_failure_gates.md: Track C pilot kill gates expected"],
        ),
        (
            "track c disposition drift",
            mutate_break_track_c_disposition_list,
            ["benchmarks/tracks.md: Track C disposition expected"],
        ),
        (
            "track c retention drift",
            mutate_break_track_c_retention_list,
            ["benchmarks/success_failure_gates.md: Track C retention criteria expected"],
        ),
        (
            "track c retirement drift",
            mutate_break_track_c_retirement_list,
            ["benchmarks/success_failure_gates.md: Track C retirement triggers expected"],
        ),
        (
            "track c sample synchronization drift",
            mutate_break_track_c_sample_sync_list,
            ["benchmarks/tracks.md: Track C sample synchronization expected"],
        ),
        (
            "track c sample posture re-decision drift",
            mutate_break_track_c_sample_redecision_list,
            ["benchmarks/tracks.md: Track C sample posture re-decision triggers expected"],
        ),
        (
            "track c editorial-only refresh drift",
            mutate_break_track_c_editorial_refresh_list,
            ["benchmarks/tracks.md: Track C editorial-only sample refreshes expected"],
        ),
        (
            "track c provenance drift",
            mutate_break_track_c_provenance_list,
            ["benchmarks/tracks.md: Track C non-editorial sample refresh provenance expected"],
        ),
        (
            "track c benchmark readme provenance drift",
            mutate_break_track_c_benchmark_readme_provenance,
            ["benchmarks/README.md: Track C non-editorial sample refresh provenance rule must remain explicit"],
        ),
        (
            "track c reports readme provenance drift",
            mutate_break_track_c_reports_readme_provenance,
            ["reports/README.md: Track C non-editorial sample refresh provenance rule must remain explicit"],
        ),
        (
            "track c sample status drift",
            mutate_break_track_c_sample_status,
            ["reports/examples/benchmark_track_c_result.example.json: sample status change requires explicit Track C re-decision"],
        ),
        (
            "track c sample evidence drift",
            mutate_break_track_c_sample_evidence,
            ["reports/examples/benchmark_track_c_result.example.json: sample evidence change requires explicit Track C re-decision"],
        ),
        (
            "track c sample lock-metric drift",
            mutate_break_track_c_sample_lock_metric,
            ["reports/examples/benchmark_track_c_result.example.json: sample case or boundary posture change requires explicit Track C re-decision"],
        ),
        (
            "track c sample artifact default-gate drift",
            mutate_reenter_track_c_default_gate,
            ["benchmarks/README.md: Track C sample-artifact default-gate boundary must remain explicit"],
        ),
        (
            "make benchmark re-enters track c default gate",
            mutate_makefile_reenter_track_c_default_gate,
            ["Makefile: default benchmark commands must not activate the non-default Track C pilot"],
        ),
        (
            "validation runner re-enters track c default gate",
            mutate_validation_runner_reenter_track_c_default_gate,
            ["scripts/run_repo_validation.py: default benchmark command must remain Track A/B only"],
        ),
        (
            "sync command doc drift",
            mutate_remove_sync_command_from_readme,
            ["README.md: Python proof-loop artifact sync check command must remain explicit"],
        ),
        (
            "wasm python emitted-module drift",
            mutate_break_wasm_python_module_list,
            ["backends/wasm/README.md: admitted Python emitted modules expected"],
        ),
        (
            "wasm non-emittable lowering-rule drift",
            mutate_break_wasm_non_emittable_rule_list,
            ["LOWERING_CONTRACT.md: Wasm-non-emittable lowering rules expected"],
        ),
        (
            "wasm record-cell ABI drift",
            mutate_remove_wasm_record_cell_marker,
            ["backends/wasm/README.md: expected explicit bounded record-cell ABI markers"],
        ),
        (
            "wasm validation emitted-module drift",
            mutate_break_wasm_validation_module_list,
            ["VALIDATION_STRATEGY.md: admitted helper-free Wasm-emission modules expected"],
        ),
        (
            "typescript reactivation",
            mutate_reactivate_typescript,
            ["Makefile: active commands must not invoke archived TypeScript conformance"],
        ),
        (
            "missing not-active marker",
            mutate_remove_not_active_marker,
            ["frontend/typescript/NOT_ACTIVE.md: missing NOT_ACTIVE marker"],
        ),
        (
            "missing preservation stage behavior",
            mutate_remove_preservation_stage_behavior,
            [f"{ACTIVE_TIER_A_CORPUS_REL}: fixture fixture.python_importer.a_basic_function must declare expected_preservation_stage_behavior"],
        ),
        (
            "invalid scirh fixture became valid",
            mutate_make_invalid_fixture_parseable,
            [f"{INVALID_SCIR_H_MANIFEST_REL}: hash drift for tests/invalid_scir_h/legacy_brace_syntax.scirh"],
        ),
    ]


def run_self_tests(root: pathlib.Path, cases):
    failures = []
    for name, mutate, expected_markers in cases:
        failures.extend(run_negative_fixture(root, name, mutate, expected_markers))
    return failures


def print_success(mode: str, *, self_test_case_count: int | None = None):
    print(f"[{mode}] repository contract validation passed")
    print(
        "Checked required files, JSON parseability, markdown non-emptiness, schema metadata, "
        "schema-valid examples, derived exports, SCIR-H kernel alignment, spec completeness, "
        "active and negative corpus manifests, sweep manifests, preservation-stage expectations, "
        "NOT_ACTIVE markers, identity stability, Python proof-loop drift, Rust importer drift, "
        "benchmark doctrine drift, Wasm backend drift, and active-surface command drift."
    )
    if mode == "test" and self_test_case_count is not None:
        print(f"Repository checker self-tests passed ({self_test_case_count} negative fixtures).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="validate")
    parser.add_argument("--root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve() if args.root else ROOT
    failures = run_checks(root)
    if failures:
        print(f"[{args.mode}] repository contract validation failed")
        for item in failures:
            print(f" - {item}")
        sys.exit(1)

    self_test_case_count = None
    if args.mode == "test":
        self_test_cases = get_self_test_cases()
        self_test_case_count = len(self_test_cases)
        self_test_failures = run_self_tests(root, self_test_cases)
        if self_test_failures:
            print("[test] repository contract self-tests failed")
            for item in self_test_failures:
                print(f" - {item}")
            sys.exit(1)

    print_success(args.mode, self_test_case_count=self_test_case_count)
    sys.exit(0)


if __name__ == "__main__":
    main()
