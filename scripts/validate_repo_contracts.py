#!/usr/bin/env python3
import argparse
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

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "SYSTEM_BOUNDARY.md",
    "REPO_MAP.md",
    "EXECUTION_QUEUE.md",
    "IMPLEMENTATION_PLAN.md",
    "VALIDATION_STRATEGY.md",
    "BENCHMARK_STRATEGY.md",
    "DECISION_REGISTER.md",
    "OPEN_QUESTIONS.md",
    "ASSUMPTIONS.md",
    "Makefile",
    "docs/project_overview.md",
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
    "specs/scir_l_spec.md",
    "specs/type_effect_capability_model.md",
    "specs/ownership_alias_model.md",
    "specs/concurrency_model.md",
    "specs/interop_and_opaque_boundary_spec.md",
    "specs/validator_invariants.md",
    "specs/provenance_and_stable_id_spec.md",
    "schemas/module_manifest.schema.json",
    "schemas/profile_claim.schema.json",
    "schemas/preservation_report.schema.json",
    "schemas/feature_tier_report.schema.json",
    "schemas/validation_report.schema.json",
    "schemas/benchmark_manifest.schema.json",
    "schemas/benchmark_result.schema.json",
    "schemas/reconstruction_report.schema.json",
    "schemas/opaque_boundary_contract.schema.json",
    "schemas/decision_register.schema.json",
    "schemas/open_questions.schema.json",
    "schemas/execution_queue.schema.json",
    "plans/PLANS.md",
    "plans/milestone_01_h_core.md",
    "plans/milestone_02_python_importer.md",
    "plans/milestone_03_l_lowering.md",
    "plans/milestone_04_reconstruction.md",
    "plans/milestone_05_benchmark_harness.md",
    "plans/milestone_06a_rust_subset.md",
    "plans/milestone_06b_dual_track_d_activation.md",
    "plans/milestone_07_typescript_witness_slice.md",
    "plans/2026-03-16-executable-bootstrap-path.md",
    "plans/2026-03-16-track-a-scirh-compaction.md",
    "plans/2026-03-24-post-6b-architecture-roadmap.md",
    "plans/2026-03-27-autonomous-execution-queue.md",
    "frontend/README.md",
    "frontend/python/AGENTS.md",
    "frontend/rust/AGENTS.md",
    "frontend/typescript/AGENTS.md",
    "frontend/python/IMPORT_SCOPE.md",
    "frontend/rust/IMPORT_SCOPE.md",
    "frontend/typescript/IMPORT_SCOPE.md",
    "validators/README.md",
    "validators/scir_h/AGENTS.md",
    "validators/scir_l/AGENTS.md",
    "validators/translation/AGENTS.md",
    "validators/validator_contracts.md",
    "benchmarks/README.md",
    "benchmarks/tracks.md",
    "benchmarks/baselines.md",
    "benchmarks/corpora_policy.md",
    "benchmarks/contamination_controls.md",
    "benchmarks/success_failure_gates.md",
    "tooling/README.md",
    "tooling/agent_api.md",
    "tooling/formatter_contract.md",
    "tooling/checker_contract.md",
    "tooling/explorer_contract.md",
    "ci/README.md",
    "ci/validation_pipeline.md",
    "ci/benchmark_pipeline.md",
    "ci/release_requirements.md",
    ".github/pull_request_template.md",
    ".github/workflows/validate.yml",
    ".github/workflows/benchmarks.yml",
    "scripts/validate_repo_contracts.py",
    "scripts/build_execution_queue.py",
    "scripts/scir_h_bootstrap_model.py",
    "scripts/scir_python_bootstrap.py",
    "scripts/scir_rust_bootstrap.py",
    "scripts/python_importer_conformance.py",
    "scripts/rust_importer_conformance.py",
    "scripts/scir_bootstrap_pipeline.py",
    "scripts/benchmark_contract_dry_run.py",
    "reports/README.md",
    "reports/examples/module_manifest.example.json",
    "reports/examples/feature_tier_report.example.json",
    "reports/examples/validation_report.example.json",
    "reports/examples/profile_claim.example.json",
    "reports/examples/preservation_report.example.json",
    "reports/examples/reconstruction_report.example.json",
    "reports/examples/opaque_boundary_contract.example.json",
    "reports/examples/benchmark_manifest.example.json",
    "reports/examples/benchmark_result.example.json",
    "reports/exports/decision_register.export.json",
    "reports/exports/open_questions.export.json",
    "reports/exports/execution_queue.export.json",
]

EXPECTED_INVARIANT_CODES = {
    "H": [f"H{i:03d}" for i in range(1, 13)],
    "L": [f"L{i:03d}" for i in range(1, 8)],
    "T": [f"T{i:03d}" for i in range(1, 5)],
}

REQUIRED_INVARIANT_SECTIONS = [
    "## `SCIR-H` invariants",
    "## `SCIR-L` invariants",
    "## Translation-validation invariants",
    "## Diagnostic contract",
]

REQUIRED_DIAGNOSTIC_MARKERS = [
    "code",
    "severity",
    "message",
    "artifact path or identifier",
    "stable node ID or block reference where available",
    "suggested downgrade or fix when applicable",
]

SCHEMA_EXPECTATIONS = {
    "schemas/module_manifest.schema.json": {
        "required": [
            "module_id",
            "layer",
            "source_language",
            "source_path",
            "declared_profiles",
            "declared_tier",
            "dependencies",
        ],
        "properties": {
            "layer": {"enum": ["scir_h", "scir_l"]},
            "declared_profiles": {"type": "array"},
            "declared_tier": {"enum": ["A", "B", "C", "D"]},
            "dependencies": {"type": "array"},
        },
    },
    "schemas/profile_claim.schema.json": {
        "required": [
            "subject",
            "profile",
            "preservation_level",
            "equivalence_mode",
            "evidence",
        ],
        "properties": {
            "profile": {"enum": ["R", "N", "P", "D-PY", "D-JS"]},
            "preservation_level": {"enum": ["P0", "P1", "P2", "P3", "PX"]},
            "equivalence_mode": {
                "enum": [
                    "deterministic",
                    "trace",
                    "contract_bounded",
                    "boundary_only",
                    "none",
                ]
            },
            "evidence": {"type": "array"},
        },
    },
    "schemas/preservation_report.schema.json": {
        "required": [
            "report_id",
            "subject",
            "source_artifact",
            "target_artifact",
            "profile",
            "preservation_level",
            "status",
            "observables",
            "evidence",
        ],
        "properties": {
            "profile": {"enum": ["R", "N", "P", "D-PY", "D-JS"]},
            "preservation_level": {"enum": ["P0", "P1", "P2", "P3", "PX"]},
            "status": {"enum": ["pass", "mixed", "fail"]},
            "observables": {
                "type": "object",
                "required": [
                    "preserved",
                    "normalized",
                    "contract_bounded",
                    "opaque",
                    "unsupported",
                ],
            },
            "evidence": {"type": "array"},
        },
    },
    "schemas/feature_tier_report.schema.json": {
        "required": [
            "report_id",
            "subject",
            "source_language",
            "summary",
            "items",
        ],
        "properties": {
            "source_language": {
                "enum": [
                    "python",
                    "rust",
                    "typescript",
                    "go",
                    "c++",
                    "haskell",
                    "unknown",
                ]
            },
            "summary": {
                "type": "object",
                "required": ["A", "B", "C", "D"],
            },
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["feature", "tier", "rationale"],
                    "properties": {
                        "tier": {"enum": ["A", "B", "C", "D"]},
                    },
                },
            },
        },
    },
    "schemas/validation_report.schema.json": {
        "required": [
            "report_id",
            "artifact",
            "layer",
            "validator",
            "status",
            "diagnostics",
        ],
        "properties": {
            "layer": {"enum": ["repo", "scir_h", "scir_l", "translation", "benchmark"]},
            "status": {"enum": ["pass", "warn", "fail"]},
            "diagnostics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["code", "severity", "message"],
                    "properties": {
                        "severity": {"enum": ["info", "warn", "error"]},
                    },
                },
            },
        },
    },
    "schemas/benchmark_manifest.schema.json": {
        "required": [
            "benchmark_id",
            "track",
            "task_family",
            "corpus",
            "baselines",
            "success_gates",
            "kill_gates",
        ],
        "properties": {
            "track": {"enum": ["A", "B", "C", "D"]},
            "corpus": {
                "type": "object",
                "required": ["name", "scope"],
            },
            "baselines": {"type": "array"},
            "profiles": {
                "type": "array",
                "items": {"enum": ["R", "N", "P", "D-PY", "D-JS"]},
            },
            "success_gates": {"type": "array"},
            "kill_gates": {"type": "array"},
        },
    },
    "schemas/benchmark_result.schema.json": {
        "required": [
            "benchmark_id",
            "run_id",
            "system_under_test",
            "track",
            "metrics",
            "baseline_comparison",
            "status",
        ],
        "properties": {
            "track": {"enum": ["A", "B", "C", "D"]},
            "profile": {"enum": ["R", "N", "P", "D-PY", "D-JS"]},
            "metrics": {"type": "object"},
            "baseline_comparison": {"type": "object"},
            "status": {"enum": ["pass", "mixed", "fail"]},
        },
    },
    "schemas/reconstruction_report.schema.json": {
        "required": [
            "report_id",
            "subject",
            "source_language",
            "target_language",
            "profile",
            "preservation_level",
            "compile_pass",
            "test_pass",
            "provenance_complete",
        ],
        "properties": {
            "profile": {"enum": ["R", "N", "P", "D-PY", "D-JS"]},
            "preservation_level": {"enum": ["P0", "P1", "P2", "P3", "PX"]},
            "compile_pass": {"type": "boolean"},
            "test_pass": {"type": "boolean"},
            "provenance_complete": {"type": "boolean"},
        },
    },
    "schemas/opaque_boundary_contract.schema.json": {
        "required": [
            "boundary_id",
            "kind",
            "signature",
            "effects",
            "ownership_transfer",
            "capabilities",
            "determinism",
            "audit_note",
        ],
        "properties": {
            "kind": {
                "enum": [
                    "opaque_type",
                    "opaque_call",
                    "unsafe",
                    "foreign",
                    "host_stub",
                    "trusted_runtime",
                ]
            },
            "effects": {"type": "array"},
            "ownership_transfer": {
                "type": "object",
                "required": ["inbound", "outbound"],
            },
            "capabilities": {"type": "array"},
            "determinism": {"enum": ["deterministic", "nondeterministic", "unknown"]},
        },
    },
    "schemas/decision_register.schema.json": {
        "required": ["decisions"],
        "properties": {
            "decisions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "id",
                        "status",
                        "decision",
                        "constraint_imposed",
                        "reversible",
                        "first_validation",
                    ],
                    "properties": {
                        "status": {
                            "enum": ["accepted", "pending", "superseded", "rejected"],
                        },
                        "reversible": {"enum": ["yes", "no", "partly"]},
                    },
                },
            },
        },
    },
    "schemas/open_questions.schema.json": {
        "required": ["open_questions"],
        "properties": {
            "open_questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "id",
                        "question",
                        "impact",
                        "default_until_resolved",
                        "blocker",
                    ],
                    "properties": {
                        "blocker": {"enum": ["yes", "no"]},
                    },
                },
            },
        },
    },
    "schemas/execution_queue.schema.json": {
        "required": [
            "generation_timestamp",
            "active_milestone",
            "autonomy_mode",
            "source_documents",
            "queue_items",
            "blocking_open_questions",
            "next_action",
            "escalation_threshold",
        ],
        "properties": {
            "autonomy_mode": {"enum": ["high", "moderate", "conservative"]},
            "source_documents": {"type": "array"},
            "queue_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "queue_id",
                        "title",
                        "source_milestone_or_phase",
                        "status",
                        "why_now",
                        "prerequisites",
                        "work_instructions",
                        "touched_surfaces",
                        "validation",
                        "escalate_only_if",
                        "done_evidence",
                        "blocking_open_questions",
                    ],
                    "properties": {
                        "status": {
                            "enum": ["ready", "blocked", "in-progress", "done", "deferred"]
                        },
                        "prerequisites": {"type": "array"},
                        "touched_surfaces": {"type": "array"},
                        "validation": {"type": "array"},
                        "done_evidence": {"type": "array"},
                        "blocking_open_questions": {"type": "array"},
                    },
                },
            },
            "blocking_open_questions": {"type": "array"},
            "next_action": {
                "type": "object",
                "required": ["queue_id", "title"],
            },
        },
    },
}

EXAMPLE_ARTIFACTS = [
    (
        "reports/examples/module_manifest.example.json",
        "schemas/module_manifest.schema.json",
    ),
    (
        "reports/examples/feature_tier_report.example.json",
        "schemas/feature_tier_report.schema.json",
    ),
    (
        "reports/examples/validation_report.example.json",
        "schemas/validation_report.schema.json",
    ),
    (
        "reports/examples/profile_claim.example.json",
        "schemas/profile_claim.schema.json",
    ),
    (
        "reports/examples/preservation_report.example.json",
        "schemas/preservation_report.schema.json",
    ),
    (
        "reports/examples/reconstruction_report.example.json",
        "schemas/reconstruction_report.schema.json",
    ),
    (
        "reports/examples/opaque_boundary_contract.example.json",
        "schemas/opaque_boundary_contract.schema.json",
    ),
    (
        "reports/examples/benchmark_manifest.example.json",
        "schemas/benchmark_manifest.schema.json",
    ),
    (
        "reports/examples/benchmark_result.example.json",
        "schemas/benchmark_result.schema.json",
    ),
]

DECISION_REGISTER_HEADER = [
    "ID",
    "Status",
    "Decision",
    "Constraint imposed",
    "Reversible",
    "First validation",
]

DECISION_REGISTER_EXPORT_REL = "reports/exports/decision_register.export.json"
DECISION_REGISTER_SCHEMA_REL = "schemas/decision_register.schema.json"
DECISION_REGISTER_REVERSIBLE_VALUES = ["yes", "no", "partly"]

OPEN_QUESTIONS_HEADER = [
    "ID",
    "Question",
    "Impact",
    "Default until resolved",
    "Blocker",
]

OPEN_QUESTIONS_EXPORT_REL = "reports/exports/open_questions.export.json"
OPEN_QUESTIONS_SCHEMA_REL = "schemas/open_questions.schema.json"
OPEN_QUESTIONS_BLOCKER_VALUES = ["yes", "no"]
EXECUTION_QUEUE_EXPORT_REL = "reports/exports/execution_queue.export.json"
EXECUTION_QUEUE_BUILD_SCRIPT_REL = "scripts/build_execution_queue.py"
TYPESCRIPT_PLACEHOLDER_CASES_ROOT_REL = pathlib.Path("tests") / "typescript_importer" / "cases"
TYPESCRIPT_ADMITTED_CASE_IDS = [
    "a_interface_decl",
    "a_interface_local_witness_use",
]
TYPESCRIPT_REJECTED_CASE_IDS = [
    "d_function_decl",
    "d_async_function",
    "d_class_implements_interface",
    "d_prototype_assignment",
    "d_decorator_class",
    "d_proxy_construct",
    "d_type_level_runtime_gate",
]
TYPESCRIPT_ADMITTED_FILE_SET = {
    "README.md",
    "source.ts",
    "expected.scirh",
    "module_manifest.json",
    "feature_tier_report.json",
    "validation_report.json",
}
TYPESCRIPT_REJECTED_FILE_SET = {
    "README.md",
    "source.ts",
    "module_manifest.json",
    "feature_tier_report.json",
    "validation_report.json",
}
TYPESCRIPT_DECLARED_PROFILES = ["R", "D-JS"]
TYPESCRIPT_PLACEHOLDER_VALIDATOR = "typescript-phase7-placeholder-bundle"
TYPESCRIPT_ADMITTED_SUMMARY = {"A": 1, "B": 0, "C": 0, "D": 0}
TYPESCRIPT_REJECTED_SUMMARY = {"A": 0, "B": 0, "C": 0, "D": 1}


def check_required_files(root: pathlib.Path):
    missing = []
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            missing.append(rel)
    return missing

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
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            failures.append(f"{path.relative_to(root)}: empty markdown file")
    return failures


def load_json_artifact(root: pathlib.Path, rel_path: pathlib.Path, failures: list[str]):
    try:
        return json.loads((root / rel_path).read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - bootstrap script
        failures.append(f"{rel_path}: {exc}")
        return None


def check_typescript_placeholder_case(
    root: pathlib.Path,
    case_id: str,
    *,
    expected_files: set[str],
    expected_tier: str,
    expected_summary: dict[str, int],
    expected_status: str,
    expected_severity: str,
    required_message_markers: list[str],
    require_reject_fallback: bool,
):
    failures = []
    case_rel = TYPESCRIPT_PLACEHOLDER_CASES_ROOT_REL / case_id
    case_path = root / case_rel
    if not case_path.is_dir():
        failures.append(f"{case_rel}: missing case directory")
        return failures

    actual_files = {item.name for item in case_path.iterdir()}
    missing_files = sorted(expected_files - actual_files)
    unexpected_files = sorted(actual_files - expected_files)

    if missing_files:
        failures.append(f"{case_rel}: missing files {', '.join(missing_files)}")
    if unexpected_files:
        failures.append(f"{case_rel}: unexpected files {', '.join(unexpected_files)}")

    subject = f"fixture.typescript_importer.{case_id}"
    source_rel = case_rel / "source.ts"

    manifest_rel = case_rel / "module_manifest.json"
    manifest = load_json_artifact(root, manifest_rel, failures)
    if manifest is not None:
        if manifest.get("module_id") != subject:
            failures.append(f"{manifest_rel}: expected module_id {subject!r}")
        if manifest.get("layer") != "scir_h":
            failures.append(f"{manifest_rel}: expected layer 'scir_h'")
        if manifest.get("source_language") != "typescript":
            failures.append(f"{manifest_rel}: expected source_language 'typescript'")
        if manifest.get("source_path") != source_rel.as_posix():
            failures.append(
                f"{manifest_rel}: expected source_path {source_rel.as_posix()!r}"
            )
        if manifest.get("declared_profiles") != TYPESCRIPT_DECLARED_PROFILES:
            failures.append(
                f"{manifest_rel}: expected declared_profiles {TYPESCRIPT_DECLARED_PROFILES!r}"
            )
        if manifest.get("declared_tier") != expected_tier:
            failures.append(f"{manifest_rel}: expected declared_tier {expected_tier!r}")

    feature_rel = case_rel / "feature_tier_report.json"
    feature_report = load_json_artifact(root, feature_rel, failures)
    if feature_report is not None:
        if feature_report.get("subject") != subject:
            failures.append(f"{feature_rel}: expected subject {subject!r}")
        if feature_report.get("source_language") != "typescript":
            failures.append(f"{feature_rel}: expected source_language 'typescript'")
        if feature_report.get("summary") != expected_summary:
            failures.append(f"{feature_rel}: expected summary {expected_summary!r}")
        items = feature_report.get("items")
        if not isinstance(items, list) or not items:
            failures.append(f"{feature_rel}: expected non-empty items list")
        else:
            first_item = items[0]
            if first_item.get("tier") != expected_tier:
                failures.append(f"{feature_rel}: expected first item tier {expected_tier!r}")
            if require_reject_fallback and first_item.get("fallback") != "reject":
                failures.append(f"{feature_rel}: expected first item fallback 'reject'")

    validation_rel = case_rel / "validation_report.json"
    validation_report = load_json_artifact(root, validation_rel, failures)
    if validation_report is not None:
        if validation_report.get("artifact") != subject:
            failures.append(f"{validation_rel}: expected artifact {subject!r}")
        if validation_report.get("layer") != "scir_h":
            failures.append(f"{validation_rel}: expected layer 'scir_h'")
        if validation_report.get("validator") != TYPESCRIPT_PLACEHOLDER_VALIDATOR:
            failures.append(
                f"{validation_rel}: expected validator {TYPESCRIPT_PLACEHOLDER_VALIDATOR!r}"
            )
        if validation_report.get("status") != expected_status:
            failures.append(f"{validation_rel}: expected status {expected_status!r}")
        diagnostics = validation_report.get("diagnostics")
        if not isinstance(diagnostics, list) or not diagnostics:
            failures.append(f"{validation_rel}: expected non-empty diagnostics list")
        else:
            first_diagnostic = diagnostics[0]
            if first_diagnostic.get("severity") != expected_severity:
                failures.append(
                    f"{validation_rel}: expected first diagnostic severity {expected_severity!r}"
                )
            message = first_diagnostic.get("message", "")
            message_lower = message.lower()
            for marker in required_message_markers:
                if marker.lower() not in message_lower:
                    failures.append(
                        f"{validation_rel}: expected first diagnostic message to mention {marker!r}"
                    )

    return failures


def check_typescript_placeholder_corpus(root: pathlib.Path):
    failures = []
    cases_root = root / TYPESCRIPT_PLACEHOLDER_CASES_ROOT_REL
    if not cases_root.is_dir():
        return [f"{TYPESCRIPT_PLACEHOLDER_CASES_ROOT_REL}: missing directory"]

    expected_case_ids = sorted(TYPESCRIPT_ADMITTED_CASE_IDS + TYPESCRIPT_REJECTED_CASE_IDS)
    actual_case_ids = sorted(path.name for path in cases_root.iterdir() if path.is_dir())
    missing_case_ids = [case_id for case_id in expected_case_ids if case_id not in actual_case_ids]
    unexpected_case_ids = [case_id for case_id in actual_case_ids if case_id not in expected_case_ids]

    if missing_case_ids:
        failures.append(
            f"{TYPESCRIPT_PLACEHOLDER_CASES_ROOT_REL}: missing case directories {', '.join(missing_case_ids)}"
        )
    if unexpected_case_ids:
        failures.append(
            f"{TYPESCRIPT_PLACEHOLDER_CASES_ROOT_REL}: unexpected case directories {', '.join(unexpected_case_ids)}"
        )

    for case_id in TYPESCRIPT_ADMITTED_CASE_IDS:
        failures.extend(
            check_typescript_placeholder_case(
                root,
                case_id,
                expected_files=TYPESCRIPT_ADMITTED_FILE_SET,
                expected_tier="A",
                expected_summary=TYPESCRIPT_ADMITTED_SUMMARY,
                expected_status="warn",
                expected_severity="warn",
                required_message_markers=["no live TypeScript importer"],
                require_reject_fallback=False,
            )
        )

    for case_id in TYPESCRIPT_REJECTED_CASE_IDS:
        failures.extend(
            check_typescript_placeholder_case(
                root,
                case_id,
                expected_files=TYPESCRIPT_REJECTED_FILE_SET,
                expected_tier="D",
                expected_summary=TYPESCRIPT_REJECTED_SUMMARY,
                expected_status="fail",
                expected_severity="error",
                required_message_markers=[
                    "canonical SCIR-H is intentionally absent",
                    "no live TypeScript importer",
                ],
                require_reject_fallback=True,
            )
        )

    return failures


def check_agents_contract(root: pathlib.Path):
    failures = []
    text = (root / "AGENTS.md").read_text(encoding="utf-8")
    required_substrings = [
        "IMPLEMENTATION_PLAN.md",
        "REPO_MAP.md",
        "plans/PLANS.md",
        "P0",
        "Tier A",
        "Do not invent unsupported semantics",
    ]
    for s in required_substrings:
        if s not in text:
            failures.append(f"AGENTS.md missing required text: {s}")
    return failures


def collect_invariant_codes(text: str, prefix: str):
    pattern = re.compile(rf"^\|\s*({prefix}\d{{3}})\s*\|", re.MULTILINE)
    return pattern.findall(text)


def check_validator_invariant_coverage(root: pathlib.Path):
    failures = []
    text = (root / "specs" / "validator_invariants.md").read_text(encoding="utf-8")

    for marker in REQUIRED_INVARIANT_SECTIONS:
        if marker not in text:
            failures.append(f"validator invariants missing section: {marker}")

    for marker in REQUIRED_DIAGNOSTIC_MARKERS:
        if marker not in text:
            failures.append(f"validator invariants missing diagnostic marker: {marker}")

    for prefix, expected_codes in EXPECTED_INVARIANT_CODES.items():
        found_codes = collect_invariant_codes(text, prefix)
        missing_codes = [code for code in expected_codes if code not in found_codes]
        unexpected_codes = [code for code in found_codes if code not in expected_codes]
        duplicate_codes = sorted({code for code in found_codes if found_codes.count(code) > 1})

        if missing_codes:
            failures.append(
                f"validator invariants missing {prefix}-codes: {', '.join(missing_codes)}"
            )
        if unexpected_codes:
            failures.append(
                f"validator invariants unexpected {prefix}-codes: {', '.join(unexpected_codes)}"
            )
        if duplicate_codes:
            failures.append(
                f"validator invariants duplicate {prefix}-codes: {', '.join(duplicate_codes)}"
            )

    return failures


def validate_schema_fragment(fragment, expectation, path):
    failures = []

    expected_type = expectation.get("type")
    if expected_type is not None and fragment.get("type") != expected_type:
        failures.append(f"{path}: expected type {expected_type!r}")

    if "additionalProperties" in expectation:
        expected_additional = expectation["additionalProperties"]
        if fragment.get("additionalProperties") != expected_additional:
            failures.append(
                f"{path}: expected additionalProperties={expected_additional!r}"
            )

    expected_required = expectation.get("required")
    if expected_required is not None:
        actual_required = fragment.get("required")
        if not isinstance(actual_required, list):
            failures.append(f"{path}: missing required list")
        else:
            missing_required = [name for name in expected_required if name not in actual_required]
            if missing_required:
                failures.append(
                    f"{path}: missing required fields {', '.join(missing_required)}"
                )

    expected_enum = expectation.get("enum")
    if expected_enum is not None:
        actual_enum = fragment.get("enum")
        if actual_enum != expected_enum:
            failures.append(f"{path}: expected enum {expected_enum!r}")

    expected_properties = expectation.get("properties")
    if expected_properties is not None:
        actual_properties = fragment.get("properties")
        if not isinstance(actual_properties, dict):
            failures.append(f"{path}: missing properties object")
        else:
            for key, child_expectation in expected_properties.items():
                if key not in actual_properties:
                    failures.append(f"{path}: missing property {key}")
                    continue
                failures.extend(
                    validate_schema_fragment(
                        actual_properties[key],
                        child_expectation,
                        f"{path}.properties.{key}",
                    )
                )

    expected_items = expectation.get("items")
    if expected_items is not None:
        actual_items = fragment.get("items")
        if actual_items is None:
            failures.append(f"{path}: missing items contract")
        else:
            failures.extend(
                validate_schema_fragment(actual_items, expected_items, f"{path}.items")
            )

    return failures


def check_schema_metadata(root: pathlib.Path):
    failures = []
    for path in sorted((root / "schemas").glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        rel = path.relative_to(root)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            failures.append(f"{rel}: expected Draft 2020-12 schema declaration")
        title = schema.get("title")
        if not isinstance(title, str) or not title.strip():
            failures.append(f"{rel}: missing non-empty title")
        if schema.get("type") != "object":
            failures.append(f"{rel}: expected top-level object schema")
        if schema.get("additionalProperties") is not False:
            failures.append(f"{rel}: expected top-level additionalProperties=false")
    return failures


def check_report_schema_completeness(root: pathlib.Path):
    failures = []
    for rel, expectation in SCHEMA_EXPECTATIONS.items():
        schema = json.loads((root / rel).read_text(encoding="utf-8"))
        failures.extend(validate_schema_fragment(schema, expectation, rel))
    return failures


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def matches_type(value, expected_type):
    if isinstance(expected_type, list):
        return any(matches_type(value, item) for item in expected_type)

    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": is_integer(value),
        "number": is_number(value),
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

    minimum = schema.get("minimum")
    if minimum is not None and is_number(instance) and instance < minimum:
        failures.append((path, f"expected value >= {minimum}"))

    maximum = schema.get("maximum")
    if maximum is not None and is_number(instance) and instance > maximum:
        failures.append((path, f"expected value <= {maximum}"))

    min_items = schema.get("minItems")
    if min_items is not None and isinstance(instance, list) and len(instance) < min_items:
        failures.append((path, f"expected at least {min_items} items"))

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

    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(instance),
        key=lambda error: ([str(part) for part in error.absolute_path], error.message),
    )
    return [(format_json_path(error.absolute_path), error.message) for error in errors]


def format_json_path(parts):
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def check_example_artifacts(root: pathlib.Path):
    failures = []
    for instance_rel, schema_rel in EXAMPLE_ARTIFACTS:
        instance = json.loads((root / instance_rel).read_text(encoding="utf-8"))
        schema = json.loads((root / schema_rel).read_text(encoding="utf-8"))
        errors = collect_instance_validation_errors(instance, schema)
        for location, message in errors:
            failures.append(f"{instance_rel} {location}: {message}")
    return failures


def split_markdown_table_row(line: str):
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip() for cell in stripped.split("|")[1:-1]]


def is_markdown_separator_row(cells):
    return bool(cells) and all(cell and set(cell) <= {"-", ":"} for cell in cells)


def parse_decision_register_markdown(root: pathlib.Path):
    failures = []
    lines = (root / "DECISION_REGISTER.md").read_text(encoding="utf-8").splitlines()
    start = None

    for idx, line in enumerate(lines):
        cells = split_markdown_table_row(line)
        if cells == DECISION_REGISTER_HEADER:
            start = idx + 1
            break

    if start is None:
        return None, ["DECISION_REGISTER.md: decision register table header not found"]

    decisions = []
    for line in lines[start:]:
        cells = split_markdown_table_row(line)
        if cells is None:
            if decisions:
                break
            continue
        if is_markdown_separator_row(cells):
            continue
        if len(cells) != len(DECISION_REGISTER_HEADER):
            failures.append(
                "DECISION_REGISTER.md: decision register row has "
                f"{len(cells)} columns, expected {len(DECISION_REGISTER_HEADER)}"
            )
            continue

        record = {
            "id": cells[0],
            "status": cells[1],
            "decision": cells[2],
            "constraint_imposed": cells[3],
            "reversible": cells[4],
            "first_validation": cells[5],
        }
        if record["reversible"] not in DECISION_REGISTER_REVERSIBLE_VALUES:
            failures.append(
                "DECISION_REGISTER.md: invalid reversible value "
                f"{record['reversible']!r} for {record['id']}"
            )
        decisions.append(record)

    if not decisions:
        failures.append("DECISION_REGISTER.md: no decision register rows found")

    return {"decisions": decisions}, failures


def describe_decision_register_mismatch(expected, actual):
    if not isinstance(actual, dict):
        return f"{DECISION_REGISTER_EXPORT_REL} $: expected object export"

    expected_decisions = expected.get("decisions", [])
    actual_decisions = actual.get("decisions")
    if not isinstance(actual_decisions, list):
        return f"{DECISION_REGISTER_EXPORT_REL} $.decisions: expected array export"
    if len(actual_decisions) != len(expected_decisions):
        return (
            f"{DECISION_REGISTER_EXPORT_REL} $.decisions: expected "
            f"{len(expected_decisions)} entries from DECISION_REGISTER.md"
        )

    for idx, expected_record in enumerate(expected_decisions):
        actual_record = actual_decisions[idx]
        if not isinstance(actual_record, dict):
            return (
                f"{DECISION_REGISTER_EXPORT_REL} $.decisions[{idx}]: "
                "expected object entry"
            )
        for key, expected_value in expected_record.items():
            actual_value = actual_record.get(key)
            if actual_value != expected_value:
                return (
                    f"{DECISION_REGISTER_EXPORT_REL} $.decisions[{idx}].{key}: "
                    f"expected {expected_value!r} from DECISION_REGISTER.md"
                )
        extra_keys = sorted(set(actual_record) - set(expected_record))
        if extra_keys:
            return (
                f"{DECISION_REGISTER_EXPORT_REL} $.decisions[{idx}]: "
                f"unexpected keys {', '.join(extra_keys)}"
            )

    extra_top_keys = sorted(set(actual) - {"decisions"})
    if extra_top_keys:
        return f"{DECISION_REGISTER_EXPORT_REL} $: unexpected keys {', '.join(extra_top_keys)}"

    return None


def check_decision_register_export(root: pathlib.Path):
    failures = []
    derived_export, parse_failures = parse_decision_register_markdown(root)
    failures.extend(parse_failures)
    if derived_export is None:
        return failures

    try:
        schema = json.loads((root / DECISION_REGISTER_SCHEMA_REL).read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - bootstrap script
        return failures + [f"{DECISION_REGISTER_SCHEMA_REL}: {exc}"]

    try:
        checked_in_export = json.loads(
            (root / DECISION_REGISTER_EXPORT_REL).read_text(encoding="utf-8")
        )
    except Exception as exc:  # pragma: no cover - bootstrap script
        return failures + [f"{DECISION_REGISTER_EXPORT_REL}: {exc}"]

    for label, instance in [
        ("DECISION_REGISTER.md derived export", derived_export),
        (DECISION_REGISTER_EXPORT_REL, checked_in_export),
    ]:
        errors = collect_instance_validation_errors(instance, schema)
        for location, message in errors:
            failures.append(f"{label} {location}: {message}")

    mismatch = describe_decision_register_mismatch(derived_export, checked_in_export)
    if mismatch:
        failures.append(mismatch)

    return failures


def parse_open_questions_markdown(root: pathlib.Path):
    failures = []
    lines = (root / "OPEN_QUESTIONS.md").read_text(encoding="utf-8").splitlines()
    start = None

    for idx, line in enumerate(lines):
        cells = split_markdown_table_row(line)
        if cells == OPEN_QUESTIONS_HEADER:
            start = idx + 1
            break

    if start is None:
        return None, ["OPEN_QUESTIONS.md: open questions table header not found"]

    questions = []
    for line in lines[start:]:
        cells = split_markdown_table_row(line)
        if cells is None:
            if questions:
                break
            continue
        if is_markdown_separator_row(cells):
            continue
        if len(cells) != len(OPEN_QUESTIONS_HEADER):
            failures.append(
                "OPEN_QUESTIONS.md: open question row has "
                f"{len(cells)} columns, expected {len(OPEN_QUESTIONS_HEADER)}"
            )
            continue

        record = {
            "id": cells[0],
            "question": cells[1],
            "impact": cells[2],
            "default_until_resolved": cells[3],
            "blocker": cells[4],
        }
        if record["blocker"] not in OPEN_QUESTIONS_BLOCKER_VALUES:
            failures.append(
                "OPEN_QUESTIONS.md: invalid blocker value "
                f"{record['blocker']!r} for {record['id']}"
            )
        questions.append(record)

    if not questions:
        failures.append("OPEN_QUESTIONS.md: no open question rows found")

    return {"open_questions": questions}, failures


def describe_open_questions_mismatch(expected, actual):
    if not isinstance(actual, dict):
        return f"{OPEN_QUESTIONS_EXPORT_REL} $: expected object export"

    expected_questions = expected.get("open_questions", [])
    actual_questions = actual.get("open_questions")
    if not isinstance(actual_questions, list):
        return f"{OPEN_QUESTIONS_EXPORT_REL} $.open_questions: expected array export"
    if len(actual_questions) != len(expected_questions):
        return (
            f"{OPEN_QUESTIONS_EXPORT_REL} $.open_questions: expected "
            f"{len(expected_questions)} entries from OPEN_QUESTIONS.md"
        )

    for idx, expected_record in enumerate(expected_questions):
        actual_record = actual_questions[idx]
        if not isinstance(actual_record, dict):
            return (
                f"{OPEN_QUESTIONS_EXPORT_REL} $.open_questions[{idx}]: expected object entry"
            )
        for key, expected_value in expected_record.items():
            actual_value = actual_record.get(key)
            if actual_value != expected_value:
                return (
                    f"{OPEN_QUESTIONS_EXPORT_REL} $.open_questions[{idx}].{key}: "
                    f"expected {expected_value!r} from OPEN_QUESTIONS.md"
                )
        extra_keys = sorted(set(actual_record) - set(expected_record))
        if extra_keys:
            return (
                f"{OPEN_QUESTIONS_EXPORT_REL} $.open_questions[{idx}]: "
                f"unexpected keys {', '.join(extra_keys)}"
            )

    extra_top_keys = sorted(set(actual) - {"open_questions"})
    if extra_top_keys:
        return f"{OPEN_QUESTIONS_EXPORT_REL} $: unexpected keys {', '.join(extra_top_keys)}"

    return None


def check_open_questions_export(root: pathlib.Path):
    failures = []
    derived_export, parse_failures = parse_open_questions_markdown(root)
    failures.extend(parse_failures)
    if derived_export is None:
        return failures

    try:
        schema = json.loads((root / OPEN_QUESTIONS_SCHEMA_REL).read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - bootstrap script
        return failures + [f"{OPEN_QUESTIONS_SCHEMA_REL}: {exc}"]

    try:
        checked_in_export = json.loads(
            (root / OPEN_QUESTIONS_EXPORT_REL).read_text(encoding="utf-8")
        )
    except Exception as exc:  # pragma: no cover - bootstrap script
        return failures + [f"{OPEN_QUESTIONS_EXPORT_REL}: {exc}"]

    for label, instance in [
        ("OPEN_QUESTIONS.md derived export", derived_export),
        (OPEN_QUESTIONS_EXPORT_REL, checked_in_export),
    ]:
        errors = collect_instance_validation_errors(instance, schema)
        for location, message in errors:
            failures.append(f"{label} {location}: {message}")

    mismatch = describe_open_questions_mismatch(derived_export, checked_in_export)
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


def run_checks(root: pathlib.Path):
    failures = []
    failures.extend(f"missing file: {rel}" for rel in check_required_files(root))
    failures.extend(check_json_files(root))
    failures.extend(check_nonempty_markdown(root))
    failures.extend(check_typescript_placeholder_corpus(root))
    failures.extend(check_agents_contract(root))
    failures.extend(check_validator_invariant_coverage(root))
    failures.extend(check_schema_metadata(root))
    failures.extend(check_report_schema_completeness(root))
    failures.extend(check_example_artifacts(root))
    failures.extend(check_decision_register_export(root))
    failures.extend(check_open_questions_export(root))
    failures.extend(check_execution_queue_export(root))
    return failures


def mutate_remove_required_file(root: pathlib.Path):
    (root / "README.md").unlink()


def mutate_break_validation_report_required(root: pathlib.Path):
    path = root / "schemas" / "validation_report.schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["required"].remove("status")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_break_validator_invariants(root: pathlib.Path):
    path = root / "specs" / "validator_invariants.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("| H012 |", "| H099 |", 1)
    path.write_text(text, encoding="utf-8")


def mutate_break_example_module_manifest(root: pathlib.Path):
    path = root / "reports" / "examples" / "module_manifest.example.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["declared_tier"]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_break_decision_register_export(root: pathlib.Path):
    path = root / "reports" / "exports" / "decision_register.export.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["decisions"][0]["constraint_imposed"] = "Drifted export text."
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mutate_break_open_questions_export(root: pathlib.Path):
    path = root / "reports" / "exports" / "open_questions.export.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["open_questions"][0]["blocker"] = "yes"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mutate_break_execution_queue_export(root: pathlib.Path):
    path = root / "reports" / "exports" / "execution_queue.export.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["next_action"]["queue_id"] = "Q-07-001"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mutate_widen_execution_queue_scope(root: pathlib.Path):
    path = root / "EXECUTION_QUEUE.md"
    text = path.read_text(encoding="utf-8")
    target = (
        "- Work instructions: `Keep the first witness-bearing second-language item limited to a planning handoff for TypeScript "
        "interface-shaped witnesses; do not admit executable D-JS lowering, reconstruction, or benchmark work under the current roadmap.`"
    )
    replacement = (
        "- Work instructions: `Keep the first witness-bearing second-language item limited to a planning handoff for TypeScript "
        "interface-shaped witnesses; admit executable D-JS lowering, reconstruction, and benchmark work under the current roadmap.`"
    )
    path.write_text(text.replace(target, replacement, 1), encoding="utf-8")


def mutate_add_rejected_typescript_expected_scirh(root: pathlib.Path):
    path = root / TYPESCRIPT_PLACEHOLDER_CASES_ROOT_REL / "d_function_decl" / "expected.scirh"
    path.write_text("unexpected placeholder drift\n", encoding="utf-8")


def mutate_break_rejected_typescript_manifest_tier(root: pathlib.Path):
    path = root / TYPESCRIPT_PLACEHOLDER_CASES_ROOT_REL / "d_function_decl" / "module_manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["declared_tier"] = "A"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def get_self_test_cases():
    return [
        (
            "missing required file",
            mutate_remove_required_file,
            ["missing file: README.md"],
        ),
        (
            "validation report schema completeness",
            mutate_break_validation_report_required,
            [
                "schemas/validation_report.schema.json: missing required fields status",
            ],
        ),
        (
            "validator invariant drift",
            mutate_break_validator_invariants,
            [
                "validator invariants missing H-codes: H012",
                "validator invariants unexpected H-codes: H099",
            ],
        ),
        (
            "example artifact validation",
            mutate_break_example_module_manifest,
            [
                "reports/examples/module_manifest.example.json",
                "declared_tier",
            ],
        ),
        (
            "decision register export drift",
            mutate_break_decision_register_export,
            [
                DECISION_REGISTER_EXPORT_REL,
                "constraint_imposed",
            ],
        ),
        (
            "open questions export drift",
            mutate_break_open_questions_export,
            [
                OPEN_QUESTIONS_EXPORT_REL,
                "blocker",
            ],
        ),
        (
            "execution queue export drift",
            mutate_break_execution_queue_export,
            [
                EXECUTION_QUEUE_EXPORT_REL,
                "synchronization check failed",
            ],
        ),
        (
            "execution queue scope widening",
            mutate_widen_execution_queue_scope,
            [
                EXECUTION_QUEUE_BUILD_SCRIPT_REL,
                "cannot widen executable D-JS scope",
            ],
        ),
        (
            "typescript rejected expected.scirh drift",
            mutate_add_rejected_typescript_expected_scirh,
            [
                "d_function_decl",
                "expected.scirh",
            ],
        ),
        (
            "typescript rejected manifest tier drift",
            mutate_break_rejected_typescript_manifest_tier,
            [
                "d_function_decl",
                "declared_tier",
            ],
        ),
    ]


def run_negative_fixture(root: pathlib.Path, name: str, mutate, expected_markers):
    with tempfile.TemporaryDirectory(prefix="scir_repo_check_") as tmp:
        fixture_root = pathlib.Path(tmp) / "repo"
        shutil.copytree(root, fixture_root, ignore=shutil.ignore_patterns("__pycache__"))
        mutate(fixture_root)
        failures = run_checks(fixture_root)

    if not failures:
        return [f"self-test {name}: expected failure but validation passed"]

    missing_markers = [
        marker for marker in expected_markers if not any(marker in failure for failure in failures)
    ]
    if missing_markers:
        return [
            f"self-test {name}: missing expected failure markers "
            f"{', '.join(missing_markers)}"
        ]

    return []


def run_self_tests(root: pathlib.Path, cases):
    failures = []
    for name, mutate, expected_markers in cases:
        failures.extend(run_negative_fixture(root, name, mutate, expected_markers))

    return failures


def print_success(mode: str, *, self_test_case_count: int | None = None):
    print(f"[{mode}] repository contract validation passed")
    print(
        "Checked "
        f"{len(REQUIRED_FILES)} required files, markdown non-emptiness, JSON parseability, "
        "root AGENTS contract, validator invariant coverage, schema metadata, "
        "report-schema completeness, schema-valid example artifacts, "
        "and synchronized decision-register/open-questions/execution-queue exports."
    )
    if mode == "test" and self_test_case_count is not None:
        print(
            f"Repository checker self-tests passed ({self_test_case_count} negative fixtures)."
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="validate")
    parser.add_argument("--root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve() if args.root else pathlib.Path(__file__).resolve().parents[1]
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
