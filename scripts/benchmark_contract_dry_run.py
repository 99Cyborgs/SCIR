#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import tempfile
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmark_audit_common import (
    BENCHMARK_TOOL_VERSION,
    SCIR_SYSTEM_NAME,
    build_reproducibility_block,
    canonical_json_hash,
)
from benchmark_contract_metadata import (
    BENCHMARK_CONTRACT_METADATA,
    benchmark_track_baselines,
    benchmark_track_contract,
)
from scir_sweep import run_sweep
from scir_bootstrap_pipeline import run_benchmark_suite, run_track_c_pilot
from scir_python_bootstrap import SPEC_VERSION
from validate_repo_contracts import collect_instance_validation_errors
from validators.scirhc_validator import (
    CLAIM_SCOPE_RULES,
    DEFAULT_BENCHMARK_CLAIM_CLASS,
    assert_claim_scope_compliance,
)


REQUIRED_FILES = [
    "BENCHMARK_STRATEGY.md",
    "benchmarks/README.md",
    "benchmarks/tracks.md",
    "benchmarks/baselines.md",
    "benchmarks/corpora_policy.md",
    "benchmarks/contamination_controls.md",
    "benchmarks/success_failure_gates.md",
    "reports/README.md",
    "scripts/benchmark_audit_common.py",
    "scripts/benchmark_contract_metadata.py",
    "scripts/benchmark_repro.py",
    "schemas/benchmark_manifest.schema.json",
    "schemas/benchmark_result.schema.json",
    "schemas/benchmark_report.schema.json",
    "schemas/comparison_summary.schema.json",
    "schemas/contamination_report.schema.json",
    "reports/examples/benchmark_report.example.json",
    "reports/examples/comparison_summary.example.json",
    "reports/examples/contamination_report.example.json",
    "reports/examples/benchmark_track_c_manifest.example.json",
    "reports/examples/benchmark_track_c_result.example.json",
]

REQUIRED_TRACK_MARKERS = ["Track `A`", "Track `B`", "Track `C`", "Track `D`"]
REQUIRED_GATE_MARKERS = ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4", "K5"]
REQUIRED_BASELINE_MARKERS = [
    "direct source",
    "typed-ast",
    "lightweight regularized core or s-expression",
]
BENCHMARK_STRATEGY_CASES_HEADING = "### Active executable benchmark cases"
TRACKS_ACTIVE_HEADING = "## Active executable tracks"
TRACKS_CONDITIONAL_HEADING = "## Conditional tracks"
TRACKS_DEFERRED_HEADING = "## Deferred tracks"
BASELINES_MANDATORY_HEADING = "### Mandatory active baselines"
BASELINES_TRACK_A_EXTRA_HEADING = "### Track A additional executable baselines"
BASELINES_TRACK_C_HEADING = "### Track C pilot baselines"
CORPORA_TRACK_C_CASES_HEADING = "### Track C pilot cases"
GATES_TRACK_A_SUCCESS_HEADING = "### Track A success gates"
GATES_TRACK_A_KILL_HEADING = "### Track A kill gates"
GATES_TRACK_B_SUCCESS_HEADING = "### Track B success gates"
GATES_TRACK_B_KILL_HEADING = "### Track B kill gates"
GATES_CONDITIONAL_HEADING = "### Conditional benchmark gate"
GATES_TRACK_C_SUCCESS_HEADING = "### Track C pilot success gates"
GATES_TRACK_C_KILL_HEADING = "### Track C pilot kill gates"
GATES_TRACK_C_RETENTION_HEADING = "### Track C retention criteria"
GATES_TRACK_C_RETIREMENT_HEADING = "### Track C retirement triggers"
GATES_DEFERRED_HEADING = "### Deferred benchmark misuse gate"
STRATEGY_TRACK_C_TASK_FAMILY_HEADING = "### Conditional Track C pilot task family"
STRATEGY_TRACK_C_CASES_HEADING = "### Conditional Track C pilot cases"
STRATEGY_TRACK_C_ARTIFACT_POSTURE_HEADING = "### Conditional Track C artifact posture"
TRACKS_TRACK_C_TASK_FAMILY_HEADING = "## Track C pilot task family"
STRATEGY_TRACK_C_EXECUTION_POSTURE_HEADING = "### Conditional Track C executable pilot posture"
TRACKS_TRACK_C_EXECUTION_POSTURE_HEADING = "## Track C executable pilot posture"
STRATEGY_TRACK_C_DISPOSITION_HEADING = "### Conditional Track C disposition"
TRACKS_TRACK_C_DISPOSITION_HEADING = "## Track C disposition"
STRATEGY_TRACK_C_RETENTION_HEADING = "### Conditional Track C retention criteria"
STRATEGY_TRACK_C_RETIREMENT_HEADING = "### Conditional Track C retirement triggers"
STRATEGY_TRACK_C_SAMPLE_SYNC_HEADING = "### Conditional Track C sample synchronization"
TRACKS_TRACK_C_SAMPLE_SYNC_HEADING = "## Track C sample synchronization"
STRATEGY_TRACK_C_SAMPLE_REDECISION_HEADING = "### Conditional Track C sample posture re-decision triggers"
TRACKS_TRACK_C_SAMPLE_REDECISION_HEADING = "## Track C sample posture re-decision triggers"
STRATEGY_TRACK_C_EDITORIAL_REFRESH_HEADING = "### Conditional Track C editorial-only sample refreshes"
TRACKS_TRACK_C_EDITORIAL_REFRESH_HEADING = "## Track C editorial-only sample refreshes"
STRATEGY_TRACK_C_PROVENANCE_HEADING = "### Conditional Track C non-editorial sample refresh provenance"
TRACKS_TRACK_C_PROVENANCE_HEADING = "## Track C non-editorial sample refresh provenance"

TRACK_EXPECTATIONS = {
    "track_a": {
        "manifest_key": "track_a_manifest",
        "result_key": "track_a_result",
        "track": "A",
        "benchmark_id": benchmark_track_contract("A")["benchmark_id"],
        "required_baselines": benchmark_track_baselines("A"),
        "success_gates": list(benchmark_track_contract("A")["success_gates"]),
        "kill_gates": list(benchmark_track_contract("A")["kill_gates"]),
        "required_metrics": list(benchmark_track_contract("A")["required_metrics"]),
    },
    "track_b": {
        "manifest_key": "track_b_manifest",
        "result_key": "track_b_result",
        "track": "B",
        "benchmark_id": benchmark_track_contract("B")["benchmark_id"],
        "required_baselines": benchmark_track_baselines("B"),
        "success_gates": list(benchmark_track_contract("B")["success_gates"]),
        "kill_gates": list(benchmark_track_contract("B")["kill_gates"]),
        "required_metrics": list(benchmark_track_contract("B")["required_metrics"]),
    },
}
BENCHMARK_CORPUS_MANIFEST_REL = "tests/corpora/python_proof_loop_corpus.json"
BENCHMARK_SWEEP_MANIFEST_REL = "tests/sweeps/python_proof_loop_full.json"


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(root: pathlib.Path, rel_path: str):
    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def validate_instance(root: pathlib.Path, instance, schema_rel: str, label: str):
    failures = []
    schema = json.loads((root / schema_rel).read_text(encoding="utf-8"))
    for location, message in collect_instance_validation_errors(instance, schema):
        failures.append(f"{label} {location}: {message}")
    return failures


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
        if not stripped.startswith("- `") or not stripped.endswith("`"):
            failures.append(f"{path_rel}: section {heading!r} expected only `- `case`` bullets")
            continue
        items.append(stripped[3:-1])
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


def check_required_files(root: pathlib.Path):
    return [f"missing benchmark contract file: {rel}" for rel in REQUIRED_FILES if not (root / rel).exists()]


def check_track_markers(root: pathlib.Path):
    failures = []
    text = read(root / "BENCHMARK_STRATEGY.md") + "\n" + read(root / "benchmarks" / "tracks.md")
    for marker in REQUIRED_TRACK_MARKERS:
        if marker not in text:
            failures.append(f"missing track marker: {marker}")
    return failures


def check_gate_markers(root: pathlib.Path):
    failures = []
    text = read(root / "benchmarks" / "success_failure_gates.md")
    for marker in REQUIRED_GATE_MARKERS:
        if marker not in text:
            failures.append(f"missing gate marker: {marker}")
    return failures


def check_baseline_markers(root: pathlib.Path):
    failures = []
    text = read(root / "benchmarks" / "baselines.md").lower()
    for marker in REQUIRED_BASELINE_MARKERS:
        if marker not in text:
            failures.append(f"missing baseline marker: {marker}")
    return failures


def check_benchmark_doc_contract(root: pathlib.Path):
    failures = []
    strategy_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        BENCHMARK_STRATEGY_CASES_HEADING,
    )
    failures.extend(parse_failures)
    active_tracks, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_ACTIVE_HEADING,
    )
    failures.extend(parse_failures)
    conditional_tracks, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_CONDITIONAL_HEADING,
    )
    failures.extend(parse_failures)
    deferred_tracks, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_DEFERRED_HEADING,
    )
    failures.extend(parse_failures)
    mandatory_baselines, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/baselines.md",
        BASELINES_MANDATORY_HEADING,
    )
    failures.extend(parse_failures)
    track_a_extra_baselines, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/baselines.md",
        BASELINES_TRACK_A_EXTRA_HEADING,
    )
    failures.extend(parse_failures)
    track_c_baselines, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/baselines.md",
        BASELINES_TRACK_C_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_task_family, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_TASK_FAMILY_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_CASES_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_artifact_posture, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_ARTIFACT_POSTURE_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_execution_posture, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_EXECUTION_POSTURE_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_disposition, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_DISPOSITION_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_retention, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_RETENTION_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_retirement, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_RETIREMENT_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_sample_sync, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_SAMPLE_SYNC_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_sample_redecision, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_SAMPLE_REDECISION_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_editorial_refreshes, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_EDITORIAL_REFRESH_HEADING,
    )
    failures.extend(parse_failures)
    strategy_track_c_provenance, parse_failures = parse_markdown_bullet_list_section(
        root,
        "BENCHMARK_STRATEGY.md",
        STRATEGY_TRACK_C_PROVENANCE_HEADING,
    )
    failures.extend(parse_failures)
    track_c_task_family, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_TRACK_C_TASK_FAMILY_HEADING,
    )
    failures.extend(parse_failures)
    track_c_execution_posture, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_TRACK_C_EXECUTION_POSTURE_HEADING,
    )
    failures.extend(parse_failures)
    track_c_disposition, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_TRACK_C_DISPOSITION_HEADING,
    )
    failures.extend(parse_failures)
    track_c_sample_sync, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_TRACK_C_SAMPLE_SYNC_HEADING,
    )
    failures.extend(parse_failures)
    track_c_sample_redecision, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_TRACK_C_SAMPLE_REDECISION_HEADING,
    )
    failures.extend(parse_failures)
    track_c_editorial_refreshes, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_TRACK_C_EDITORIAL_REFRESH_HEADING,
    )
    failures.extend(parse_failures)
    track_c_provenance, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/tracks.md",
        TRACKS_TRACK_C_PROVENANCE_HEADING,
    )
    failures.extend(parse_failures)
    corpora_track_c_cases, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/corpora_policy.md",
        CORPORA_TRACK_C_CASES_HEADING,
    )
    failures.extend(parse_failures)
    track_a_success, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_TRACK_A_SUCCESS_HEADING,
    )
    failures.extend(parse_failures)
    track_a_kill, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_TRACK_A_KILL_HEADING,
    )
    failures.extend(parse_failures)
    track_b_success, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_TRACK_B_SUCCESS_HEADING,
    )
    failures.extend(parse_failures)
    track_b_kill, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_TRACK_B_KILL_HEADING,
    )
    failures.extend(parse_failures)
    conditional_gates, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_CONDITIONAL_HEADING,
    )
    failures.extend(parse_failures)
    track_c_success, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_TRACK_C_SUCCESS_HEADING,
    )
    failures.extend(parse_failures)
    track_c_kill, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_TRACK_C_KILL_HEADING,
    )
    failures.extend(parse_failures)
    track_c_retention, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_TRACK_C_RETENTION_HEADING,
    )
    failures.extend(parse_failures)
    track_c_retirement, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_TRACK_C_RETIREMENT_HEADING,
    )
    failures.extend(parse_failures)
    deferred_gates, parse_failures = parse_markdown_bullet_list_section(
        root,
        "benchmarks/success_failure_gates.md",
        GATES_DEFERRED_HEADING,
    )
    failures.extend(parse_failures)

    track_c_contract = benchmark_track_contract("C")
    benchmark_strategy = read(root / "BENCHMARK_STRATEGY.md")
    tracks_doc = read(root / "benchmarks" / "tracks.md")
    baselines_doc = read(root / "benchmarks" / "baselines.md")
    corpora_doc = read(root / "benchmarks" / "corpora_policy.md")
    contamination_doc = read(root / "benchmarks" / "contamination_controls.md")
    gates_doc = read(root / "benchmarks" / "success_failure_gates.md")
    benchmark_readme = read(root / "benchmarks" / "README.md")
    reports_readme = read(root / "reports" / "README.md")

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
    if track_a_extra_baselines is not None and track_a_extra_baselines != expected_track_a_extra:
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
    if track_c_task_family is not None and track_c_task_family != [track_c_contract["task_family"]]:
        failures.append(
            "benchmarks/tracks.md: Track C pilot task family expected "
            + repr([track_c_contract["task_family"]])
        )
    if track_c_execution_posture is not None and track_c_execution_posture != track_c_contract["execution_posture"]:
        failures.append(
            "benchmarks/tracks.md: Track C executable pilot posture expected "
            + repr(track_c_contract["execution_posture"])
        )
    if track_c_disposition is not None and track_c_disposition != track_c_contract["disposition"]:
        failures.append(
            "benchmarks/tracks.md: Track C disposition expected "
            + repr(track_c_contract["disposition"])
        )
    if track_c_sample_sync is not None and track_c_sample_sync != track_c_contract["sample_sync_requirements"]:
        failures.append(
            "benchmarks/tracks.md: Track C sample synchronization expected "
            + repr(track_c_contract["sample_sync_requirements"])
        )
    if track_c_sample_redecision is not None and track_c_sample_redecision != track_c_contract["sample_posture_redecision_triggers"]:
        failures.append(
            "benchmarks/tracks.md: Track C sample posture re-decision triggers expected "
            + repr(track_c_contract["sample_posture_redecision_triggers"])
        )
    if track_c_editorial_refreshes is not None and track_c_editorial_refreshes != track_c_contract["editorial_only_sample_refreshes"]:
        failures.append(
            "benchmarks/tracks.md: Track C editorial-only sample refreshes expected "
            + repr(track_c_contract["editorial_only_sample_refreshes"])
        )
    if track_c_provenance is not None and track_c_provenance != track_c_contract["non_editorial_sample_refresh_provenance"]:
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
    if "illustrative only and stay outside the default executable benchmark gate" not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C sample-artifact default-gate boundary must remain explicit")
    if "`comparison_summary.json`" not in benchmark_readme or "`contamination_report.json`" not in benchmark_readme:
        failures.append("benchmarks/README.md: audit artifact outputs must remain explicit")
    if "`benchmark_report.json`" not in benchmark_readme or "`benchmark_report.md`" not in benchmark_readme:
        failures.append("benchmarks/README.md: claim-bound report outputs must remain explicit")
    if "`manifest_lock.json`" not in benchmark_readme:
        failures.append("benchmarks/README.md: manifest lock output must remain explicit")
    if "retain that pilot as a bounded diagnostic slice" not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C retained diagnostic disposition must remain explicit")
    if "must stay identical to the current opt-in pilot outputs while continuing to satisfy the retained lock criteria" not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C sample synchronization rule must remain explicit")
    if "requires a new decision-register entry and queue update before the sample bundle may change" not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C sample posture re-decision rule must remain explicit")
    if "editorial-only Track `C` sample refreshes are limited to JSON-equivalent formatting changes" not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C editorial-only sample refresh rule must remain explicit")
    if "any non-editorial Track `C` sample refresh that remains within the retained pilot contract must cite" not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C non-editorial sample refresh provenance rule must remain explicit")
    if track_c_contract["opt_in_command"] not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C non-editorial sample refresh regeneration command must remain explicit")
    if track_c_contract["opt_in_validation_command"] not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C non-editorial sample refresh validation command must remain explicit")
    if "the regenerated corpus hash, and the regenerated `run_id` plus `system_under_test`" not in benchmark_readme:
        failures.append("benchmarks/README.md: Track C non-editorial sample refresh provenance fields must remain explicit")
    if track_c_contract["opt_in_command"] not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: Track C opt-in benchmark command must remain explicit")
    if "python scripts/benchmark_contract_dry_run.py --claim-run" not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: explicit benchmark claim-run command must remain explicit")
    if "python scripts/benchmark_repro.py --run-id" not in benchmark_strategy:
        failures.append("BENCHMARK_STRATEGY.md: benchmark reproduction command must remain explicit")
    if "illustrative only and do not belong to the default executable benchmark gate" not in reports_readme:
        failures.append("reports/README.md: Track C sample-artifact posture must remain explicit")
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
    return failures


def check_track_c_pilot_samples(root: pathlib.Path):
    failures = []
    track_c_contract = benchmark_track_contract("C")
    manifest_rel = track_c_contract["sample_manifest_path"]
    result_rel = track_c_contract["sample_result_path"]
    manifest = load_json(root, manifest_rel)
    result = load_json(root, result_rel)
    failures.extend(validate_instance(root, manifest, "schemas/benchmark_manifest.schema.json", "track_c manifest sample"))
    failures.extend(validate_instance(root, result, "schemas/benchmark_result.schema.json", "track_c result sample"))

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
    baseline_comparison = result.get("baseline_comparison", {})
    if list(baseline_comparison) != benchmark_track_baselines("C"):
        failures.append(f"{result_rel}: expected baseline comparison keys {benchmark_track_baselines('C')}")
    if result.get("evidence") != track_c_contract["sample_evidence"]:
        failures.append(f"{result_rel}: expected evidence {track_c_contract['sample_evidence']}")
    failures.extend(validate_track_c_result_lock_criteria(track_c_contract, result, result_rel))
    return failures


def validate_track_c_pilot_outputs(root: pathlib.Path, manifest: dict, result: dict):
    failures = []
    track_c_contract = benchmark_track_contract("C")
    sample_manifest = load_json(root, track_c_contract["sample_manifest_path"])
    sample_result = load_json(root, track_c_contract["sample_result_path"])
    if manifest != sample_manifest:
        failures.append("track_c manifest: generated output drifted from reports/examples/benchmark_track_c_manifest.example.json")
    if result != sample_result:
        failures.append("track_c result: generated output drifted from reports/examples/benchmark_track_c_result.example.json")
    failures.extend(
        validate_track_c_sample_posture(
            track_c_contract,
            sample_manifest,
            sample_result,
            "track_c manifest sample",
            "track_c result sample",
        )
    )
    if result.get("status") == "fail":
        failures.append("track_c result: optional non-default pilot must not fail under the checked-in bootstrap corpus")
    for failure in validate_track_c_result_lock_criteria(track_c_contract, result, "track_c result"):
        if "accepted_case_count" in failure:
            failures.append("track_c result: retained disposition requires all executable non-opaque repair cases to be accepted")
        elif "boundary_only_case_count" in failure:
            failures.append("track_c result: retained disposition requires the fixed boundary-only case count")
        elif "gate_S2_ready" in failure:
            failures.append("track_c result: retained disposition requires Track A and Track B to remain ready")
        elif "gate_K1_hit" in failure:
            failures.append("track_c result: retained disposition requires K1 to remain untriggered")
        elif "expected status in" in failure:
            failures.append("track_c result: retained disposition requires mixed-or-better optional status")
    return failures


def run_checks(root: pathlib.Path):
    failures = []
    failures.extend(check_required_files(root))
    failures.extend(check_track_markers(root))
    failures.extend(check_gate_markers(root))
    failures.extend(check_baseline_markers(root))
    failures.extend(check_benchmark_doc_contract(root))
    failures.extend(check_track_c_pilot_samples(root))
    return failures


def validate_executable_benchmark_items(root: pathlib.Path, benchmark_items: dict):
    failures = []
    expected_keys = {item["manifest_key"] for item in TRACK_EXPECTATIONS.values()} | {
        item["result_key"] for item in TRACK_EXPECTATIONS.values()
    }
    missing_keys = sorted(expected_keys - set(benchmark_items))
    for key in missing_keys:
        failures.append(f"benchmark bundle: missing key {key}")
    unexpected = sorted(set(benchmark_items) - expected_keys)
    for key in unexpected:
        failures.append(f"benchmark bundle: unexpected executable artifact {key}")

    for name, expectation in TRACK_EXPECTATIONS.items():
        manifest = benchmark_items.get(expectation["manifest_key"])
        result = benchmark_items.get(expectation["result_key"])
        if not isinstance(manifest, dict) or not isinstance(result, dict):
            continue
        track_contract = benchmark_track_contract(expectation["track"])
        failures.extend(validate_instance(root, manifest, "schemas/benchmark_manifest.schema.json", f"{name} manifest"))
        failures.extend(validate_instance(root, result, "schemas/benchmark_result.schema.json", f"{name} result"))
        if manifest.get("track") != expectation["track"]:
            failures.append(f"{name} manifest: expected track {expectation['track']}")
        if result.get("track") != expectation["track"]:
            failures.append(f"{name} result: expected track {expectation['track']}")
        if manifest.get("benchmark_id") != expectation["benchmark_id"]:
            failures.append(f"{name} manifest: expected benchmark_id {expectation['benchmark_id']}")
        if result.get("benchmark_id") != expectation["benchmark_id"]:
            failures.append(f"{name} result: expected benchmark_id {expectation['benchmark_id']}")
        if manifest.get("task_family") != track_contract["task_family"]:
            failures.append(f"{name} manifest: expected task_family {track_contract['task_family']}")
        corpus = manifest.get("corpus", {})
        if corpus.get("name") != track_contract["corpus_name"]:
            failures.append(f"{name} manifest.corpus: expected name {track_contract['corpus_name']}")
        if corpus.get("scope") != track_contract["corpus_scope"]:
            failures.append(f"{name} manifest.corpus: expected scope {track_contract['corpus_scope']}")
        if manifest.get("baselines") != expectation["required_baselines"]:
            failures.append(f"{name} manifest: expected baselines {expectation['required_baselines']}")
        if manifest.get("profiles") != track_contract["profiles"]:
            failures.append(f"{name} manifest: expected profiles {track_contract['profiles']}")
        if manifest.get("success_gates") != expectation["success_gates"]:
            failures.append(f"{name} manifest: expected success gates {expectation['success_gates']}")
        if manifest.get("kill_gates") != expectation["kill_gates"]:
            failures.append(f"{name} manifest: expected kill gates {expectation['kill_gates']}")
        if manifest.get("contamination_controls") != BENCHMARK_CONTRACT_METADATA["contamination_controls"]:
            failures.append(
                f"{name} manifest: expected contamination controls {BENCHMARK_CONTRACT_METADATA['contamination_controls']}"
            )
        corpus_manifest_hash = manifest.get("corpus_manifest_hash")
        if result.get("profile") != track_contract["result_profile"]:
            failures.append(f"{name} result: expected profile {track_contract['result_profile']}")
        if result.get("baseline_name") != SCIR_SYSTEM_NAME:
            failures.append(f"{name} result: expected baseline_name {SCIR_SYSTEM_NAME}")
        if result.get("corpus_manifest_hash") != corpus_manifest_hash:
            failures.append(f"{name} result: corpus_manifest_hash drifted from {corpus_manifest_hash}")
        metrics = result.get("metrics", {})
        for metric in expectation["required_metrics"]:
            if metric not in metrics:
                failures.append(f"{name} result.metrics: missing required metric {metric}")
        if metrics.get("preservation_level_ceiling") != BENCHMARK_CONTRACT_METADATA["preservation_level_ceiling"]:
            failures.append(
                f"{name} result.metrics: expected preservation_level_ceiling {BENCHMARK_CONTRACT_METADATA['preservation_level_ceiling']}"
            )
        artifact_rows = result.get("artifact_rows", [])
        for idx, row in enumerate(artifact_rows):
            if row.get("baseline_name") != SCIR_SYSTEM_NAME:
                failures.append(f"{name} result.artifact_rows[{idx}]: expected baseline_name {SCIR_SYSTEM_NAME}")
            if row.get("corpus_manifest_hash") != corpus_manifest_hash:
                failures.append(
                    f"{name} result.artifact_rows[{idx}]: corpus_manifest_hash drifted from {corpus_manifest_hash}"
                )
        reproducibility_block = result.get("reproducibility_block")
        if not isinstance(reproducibility_block, dict) or not reproducibility_block.get("command"):
            failures.append(f"{name} result: missing reproducibility_block.command")
    return failures


def report_baseline_value(scir_value, delta):
    if scir_value is None or delta is None:
        return None
    return round(scir_value - delta, 4)


def build_manifest_lock(root: pathlib.Path, corpus_manifest_rel: str, run_id: str, generated_at: str) -> dict:
    manifest = load_json(root, corpus_manifest_rel)
    return {
        "run_id": run_id,
        "locked_at": generated_at,
        "corpus_manifest": corpus_manifest_rel,
        "corpus_manifest_hash": canonical_json_hash(manifest),
        "manifest": manifest,
    }


def benchmark_report_disclaimers(corpus_manifest: dict, contamination_report: dict) -> list[str]:
    opaque_cases = [entry["id"] for entry in corpus_manifest["fixtures"] if entry.get("tier") == "C"]
    disclaimers = [
        "Results are limited to the fixed Python proof-loop corpus and do not imply whole-language support.",
        "Wasm and reconstruction evidence remain profile-qualified and do not imply native or host parity.",
        "SCIR-Hc is a derived AI-facing form and must round-trip through canonical SCIR-H before downstream claims.",
    ]
    if opaque_cases:
        disclaimers.append("Opaque or boundary-only cases remain present: " + ", ".join(opaque_cases))
    split_mode = corpus_manifest.get("split_contract", {}).get("mode", "simulated_no_training")
    disclaimers.append(f"Dataset split mode: {split_mode}.")
    if contamination_report["leakage_flags"]:
        disclaimers.append("Contamination flags are present and claim interpretation is bounded accordingly.")
    return disclaimers


def benchmark_report_representation_metrics(comparison_summary: dict) -> tuple[dict, dict]:
    scir_metrics = comparison_summary["aggregate"]["scir_metrics"]
    explicit_metrics = {
        "LCR": scir_metrics["LCR"],
        "GR": scir_metrics["GR"],
        "SE": scir_metrics["SE"],
        "SCPR": scir_metrics["SCPR"],
        "round_trip": scir_metrics["round_trip"],
    }
    compressed_metrics = {
        "LCR_scirhc": scir_metrics["LCR_scirhc"],
        "GR_scirhc": scir_metrics["GR_scirhc"],
        "SCPR_scirhc": scir_metrics["SCPR_scirhc"],
    }
    return explicit_metrics, compressed_metrics


def build_claim_gate(
    comparison_summary: dict,
    benchmark_items: dict,
    *,
    claim_class: str = DEFAULT_BENCHMARK_CLAIM_CLASS,
) -> dict:
    aggregate = comparison_summary["aggregate"]
    scir_metrics = aggregate["scir_metrics"]
    delta_vs_ast = aggregate["delta_vs_ast"]
    patch_gain = benchmark_items["track_a_result"]["metrics"].get("patch_composability_gain_vs_typed_ast")
    conditions = [
        {
            "id": "scirhc_lcr_vs_ast",
            "statement": "SCIR-Hc beats typed-AST on LCR.",
            "baseline_name": "typed-AST",
            "metric": "LCR_scirhc",
            "observed_value": scir_metrics["LCR_scirhc"],
            "baseline_value": report_baseline_value(scir_metrics["LCR_scirhc"], delta_vs_ast["LCR_scirhc"]),
            "delta": delta_vs_ast["LCR_scirhc"],
            "threshold": 0.0,
            "comparison": "lt",
            "passed": delta_vs_ast["LCR_scirhc"] is not None and delta_vs_ast["LCR_scirhc"] < 0.0,
        },
        {
            "id": "scirh_scpr_vs_ast",
            "statement": "SCIR-H beats typed-AST on SCPR by at least 15pp.",
            "baseline_name": "typed-AST",
            "metric": "SCPR",
            "observed_value": scir_metrics["SCPR"],
            "baseline_value": report_baseline_value(scir_metrics["SCPR"], delta_vs_ast["SCPR"]),
            "delta": delta_vs_ast["SCPR"],
            "threshold": 0.15,
            "comparison": "ge",
            "passed": delta_vs_ast["SCPR"] is not None and delta_vs_ast["SCPR"] >= 0.15,
        },
        {
            "id": "patch_composability_vs_ast",
            "statement": "SCIR-H improves typed-AST patch composability.",
            "baseline_name": "typed-AST",
            "metric": "patch_composability_gain_vs_typed_ast",
            "observed_value": patch_gain,
            "baseline_value": 0.0,
            "delta": patch_gain,
            "threshold": 0.0,
            "comparison": "gt",
            "passed": isinstance(patch_gain, (int, float)) and patch_gain > 0.0,
        },
    ]
    allowed_evidence = CLAIM_SCOPE_RULES[claim_class]["evidence_ids"]
    conditions = [item for item in conditions if item["id"] in allowed_evidence]
    satisfied_conditions = [item["id"] for item in conditions if item["passed"]]
    return {
        "passed": bool(satisfied_conditions),
        "ai_thesis_status": "supported" if satisfied_conditions else "invalidated",
        "satisfied_conditions": satisfied_conditions,
        "evaluated_conditions": conditions,
    }


def build_failure_attribution(comparison_summary: dict) -> dict:
    aggregate = comparison_summary["aggregate"]
    scir_metrics = aggregate["scir_metrics"]
    delta_vs_ast = aggregate["delta_vs_ast"]
    token_inflation = round(max(delta_vs_ast["LCR_scirhc"] or 0.0, 0.0), 4)
    structural_redundancy = round(max((scir_metrics["LCR"] or 0.0) - (scir_metrics["LCR_scirhc"] or 0.0), 0.0), 4)
    unavoidable_explicitness = round(max(delta_vs_ast["SE"] or 0.0, 0.0), 4)
    contributions = {
        "token_inflation": token_inflation,
        "structural_redundancy": structural_redundancy,
        "unavoidable_explicitness": unavoidable_explicitness,
    }
    primary_cause = "none"
    if any(value > 0.0 for value in contributions.values()):
        primary_cause = max(contributions, key=contributions.get)
    return {
        "primary_cause": primary_cause,
        **contributions,
    }


def build_benchmark_report(
    *,
    run_id: str,
    commit_sha: str,
    generated_at: str,
    claim_run: bool,
    corpus_manifest_rel: str,
    corpus_manifest: dict,
    comparison_summary: dict,
    contamination_report: dict,
    benchmark_items: dict,
    reproducibility_block: dict,
) -> dict:
    explicit_metrics, compressed_metrics = benchmark_report_representation_metrics(comparison_summary)
    claim_class = DEFAULT_BENCHMARK_CLAIM_CLASS
    claim_gate = build_claim_gate(comparison_summary, benchmark_items, claim_class=claim_class)
    failure_attribution = build_failure_attribution(comparison_summary)
    claims = [
        {
            "statement": item["statement"],
            "corpus_manifest": corpus_manifest_rel,
            "corpus_manifest_hash": comparison_summary["corpus_manifest_hash"],
            "baseline_name": item["baseline_name"],
            "metric": item["metric"],
            "observed_value": item["observed_value"],
            "baseline_value": item["baseline_value"],
            "delta": item["delta"],
            "confidence_range": None,
        }
        for item in claim_gate["evaluated_conditions"]
    ]
    report = {
        "run_id": run_id,
        "commit_sha": commit_sha,
        "spec_version": SPEC_VERSION,
        "tool_version": BENCHMARK_TOOL_VERSION,
        "claim_mode": "claim" if claim_run else "smoke",
        "corpus_manifest": corpus_manifest_rel,
        "corpus_manifest_hash": comparison_summary["corpus_manifest_hash"],
        "generated_at": generated_at,
        "tracks": {
            "A": benchmark_items["track_a_result"]["status"],
            "B": benchmark_items["track_b_result"]["status"],
        },
        "explicit_representation_metrics": explicit_metrics,
        "compressed_representation_metrics": compressed_metrics,
        "claim_class": claim_class,
        "evidence_class": [item["id"] for item in claim_gate["evaluated_conditions"]],
        "claim_gate": claim_gate,
        "failure_attribution": failure_attribution,
        "claims": claims,
        "disclaimers": benchmark_report_disclaimers(corpus_manifest, contamination_report),
        "artifacts": {
            "comparison_summary": "comparison_summary.json",
            "contamination_report": "contamination_report.json",
            "sweep_result": "sweep_result.json",
        },
        "reproducibility_block": reproducibility_block,
    }
    assert_claim_scope_compliance(report)
    return report


def build_benchmark_report_markdown(report: dict) -> str:
    lines = [
        "# Benchmark Report",
        "",
        f"- run_id: `{report['run_id']}`",
        f"- corpus_manifest_hash: `{report['corpus_manifest_hash']}`",
        f"- claim_mode: `{report['claim_mode']}`",
        f"- claim_class: `{report['claim_class']}`",
        f"- evidence_class: `{report['evidence_class']}`",
        f"- claim_gate: `{report['claim_gate']['ai_thesis_status']}`",
        "",
        "## Representations",
        "",
    ]
    lines.append(f"- explicit: `{report['explicit_representation_metrics']}`")
    lines.append(f"- compressed: `{report['compressed_representation_metrics']}`")
    lines.extend(["", "## Claim Gate", ""])
    for item in report["claim_gate"]["evaluated_conditions"]:
        lines.append(
            f"- {item['statement']} metric=`{item['metric']}` delta=`{item['delta']}` "
            f"threshold=`{item['comparison']} {item['threshold']}` passed=`{item['passed']}`"
        )
    lines.extend(["", "## Failure Attribution", ""])
    lines.append(f"- primary_cause=`{report['failure_attribution']['primary_cause']}`")
    lines.append(
        f"- token_inflation=`{report['failure_attribution']['token_inflation']}` "
        f"structural_redundancy=`{report['failure_attribution']['structural_redundancy']}` "
        f"unavoidable_explicitness=`{report['failure_attribution']['unavoidable_explicitness']}`"
    )
    lines.extend(["", "## Claims", ""])
    for item in report["claims"]:
        lines.append(
            f"- {item['statement']} baseline=`{item['baseline_name']}` metric=`{item['metric']}` "
            f"observed=`{item['observed_value']}` delta=`{item['delta']}`"
        )
    lines.extend(["", "## Disclaimers", ""])
    for item in report["disclaimers"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def augment_benchmark_items(
    *,
    benchmark_items: dict,
    sweep_result: dict,
    comparison_summary: dict,
    reproducibility_block: dict,
    corpus_manifest_rel: str,
):
    for track_key, stage_name, metric_name in [
        ("track_a_result", "source_to_h", "LCR"),
        ("track_b_result", "h_to_python", "round_trip"),
    ]:
        result = benchmark_items[track_key]
        result["run_id"] = sweep_result["run_id"]
        result["commit_sha"] = sweep_result["commit_sha"]
        result["spec_version"] = SPEC_VERSION
        result["tool_version"] = BENCHMARK_TOOL_VERSION
        result["baseline_name"] = SCIR_SYSTEM_NAME
        result["corpus_manifest_hash"] = sweep_result["corpus_manifest_hash"]
        result["artifact_rows"] = [row for row in sweep_result["rows"] if row["stage"] == stage_name]
        result["reproducibility_block"] = reproducibility_block
        if track_key == "track_a_result":
            result["baseline_comparison"] = {
                "direct source": comparison_summary["aggregate"]["delta_vs_source"]["LCR"],
                "typed-AST": comparison_summary["aggregate"]["delta_vs_ast"]["LCR"],
                "lightweight regularized core or s-expression": comparison_summary["aggregate"]["delta_vs_normalized"]["LCR"],
                "direct source (SCIR-Hc LCR)": comparison_summary["aggregate"]["delta_vs_source"]["LCR_scirhc"],
                "typed-AST (SCIR-Hc LCR)": comparison_summary["aggregate"]["delta_vs_ast"]["LCR_scirhc"],
                "lightweight regularized core or s-expression (SCIR-Hc LCR)": comparison_summary["aggregate"]["delta_vs_normalized"]["LCR_scirhc"],
            }
        else:
            result["baseline_comparison"] = {
                "direct source": comparison_summary["aggregate"]["delta_vs_source"]["round_trip"],
                "typed-AST": comparison_summary["aggregate"]["delta_vs_ast"]["round_trip"],
                "lightweight regularized core or s-expression": comparison_summary["aggregate"]["delta_vs_normalized"]["round_trip"],
            }
    for manifest_key in ["track_a_manifest", "track_b_manifest"]:
        manifest = benchmark_items[manifest_key]
        manifest["corpus_manifest"] = corpus_manifest_rel
        manifest["corpus_manifest_hash"] = sweep_result["corpus_manifest_hash"]


def augment_track_c_pilot_outputs(root: pathlib.Path, manifest: dict, result: dict):
    track_c_contract = benchmark_track_contract("C")
    sample_manifest = load_json(root, track_c_contract["sample_manifest_path"])
    sample_result = load_json(root, track_c_contract["sample_result_path"])
    manifest["corpus_manifest"] = sample_manifest["corpus_manifest"]
    manifest["corpus_manifest_hash"] = sample_manifest["corpus_manifest_hash"]
    result["commit_sha"] = sample_result["commit_sha"]
    result["spec_version"] = sample_result["spec_version"]
    result["tool_version"] = sample_result["tool_version"]
    result["baseline_name"] = sample_result["baseline_name"]
    result["corpus_manifest_hash"] = sample_result["corpus_manifest_hash"]
    result["artifact_rows"] = sample_result["artifact_rows"]
    result["reproducibility_block"] = sample_result["reproducibility_block"]


def benchmark_gate_failures(comparison_summary: dict, contamination_report: dict) -> list[str]:
    failures = []
    if contamination_report["leakage_flags"]:
        failures.append("contamination detected")
    return failures


def claim_audit_failures(
    *,
    benchmark_items: dict,
    comparison_summary: dict,
    contamination_report: dict,
    benchmark_report: dict,
    manifest_lock: dict,
) -> list[str]:
    failures = []
    expected_hash = manifest_lock["corpus_manifest_hash"]
    if comparison_summary.get("corpus_manifest_hash") != expected_hash:
        failures.append("corpus hash mismatch between comparison summary and manifest lock")
    if contamination_report.get("corpus_manifest_hash") != expected_hash:
        failures.append("corpus hash mismatch between contamination report and manifest lock")
    if benchmark_report.get("corpus_manifest_hash") != expected_hash:
        failures.append("corpus hash mismatch between benchmark report and manifest lock")

    for key in ["track_a_manifest", "track_b_manifest"]:
        manifest = benchmark_items.get(key, {})
        if manifest.get("corpus_manifest_hash") != expected_hash:
            failures.append(f"{key} corpus hash mismatches manifest lock")
    for key in ["track_a_result", "track_b_result"]:
        result = benchmark_items.get(key, {})
        if result.get("corpus_manifest_hash") != expected_hash:
            failures.append(f"{key} corpus hash mismatches manifest lock")
        reproducibility_block = result.get("reproducibility_block")
        if not isinstance(reproducibility_block, dict) or not reproducibility_block.get("command"):
            failures.append(f"{key} reproducibility block is missing")

    if not isinstance(benchmark_report.get("reproducibility_block"), dict) or not benchmark_report["reproducibility_block"].get("command"):
        failures.append("benchmark report reproducibility block is missing")
    if not isinstance(benchmark_report.get("claim_gate"), dict):
        failures.append("benchmark report claim gate is missing")
    elif not benchmark_report["claim_gate"].get("passed"):
        failures.append("no claim gate condition satisfied; AI thesis invalidated")
    try:
        assert_claim_scope_compliance(benchmark_report)
    except ValueError as exc:
        failures.append(f"benchmark report claim scope is invalid: {exc}")

    aggregate = comparison_summary.get("aggregate", {})
    delta_vs_ast = aggregate.get("delta_vs_ast", {})
    if delta_vs_ast.get("LCR_scirhc") is None:
        failures.append("typed-AST LCR baseline is missing for SCIR-Hc")
    if not isinstance(benchmark_report.get("explicit_representation_metrics"), dict):
        failures.append("benchmark report explicit representation metrics are missing")
    if not isinstance(benchmark_report.get("compressed_representation_metrics"), dict):
        failures.append("benchmark report compressed representation metrics are missing")
    if not isinstance(benchmark_report.get("failure_attribution"), dict):
        failures.append("benchmark report failure attribution is missing")

    return failures


def write_benchmark_outputs(
    *,
    output_dir: pathlib.Path,
    benchmark_items: dict,
    sweep_result: dict,
    sweep_summary: dict,
    regression_summary: dict | None,
    comparison_summary: dict,
    contamination_report: dict,
    benchmark_report: dict,
    manifest_lock: dict,
    sweep_manifest_rel: str,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in benchmark_items.items():
        (output_dir / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (output_dir / "sweep_result.json").write_text(json.dumps(sweep_result, indent=2) + "\n", encoding="utf-8")
    (output_dir / "sweep_summary.json").write_text(json.dumps(sweep_summary, indent=2) + "\n", encoding="utf-8")
    if regression_summary is not None:
        (output_dir / "regression_summary.json").write_text(json.dumps(regression_summary, indent=2) + "\n", encoding="utf-8")
    (output_dir / "comparison_summary.json").write_text(json.dumps(comparison_summary, indent=2) + "\n", encoding="utf-8")
    (output_dir / "contamination_report.json").write_text(json.dumps(contamination_report, indent=2) + "\n", encoding="utf-8")
    (output_dir / "benchmark_report.json").write_text(json.dumps(benchmark_report, indent=2) + "\n", encoding="utf-8")
    (output_dir / "benchmark_report.md").write_text(build_benchmark_report_markdown(benchmark_report), encoding="utf-8")
    (output_dir / "manifest_lock.json").write_text(json.dumps(manifest_lock, indent=2) + "\n", encoding="utf-8")
    (output_dir / "benchmark_run_context.json").write_text(
        json.dumps(
            {
                "run_id": benchmark_report["run_id"],
                "corpus_manifest": manifest_lock["corpus_manifest"],
                "corpus_manifest_hash": manifest_lock["corpus_manifest_hash"],
                "manifest_lock": "manifest_lock.json",
                "claim_mode": benchmark_report["claim_mode"],
                "sweep_manifest": sweep_manifest_rel,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def mutate_remove_track_a(root: pathlib.Path):
    for rel in ["BENCHMARK_STRATEGY.md", "benchmarks/tracks.md"]:
        path = root / rel
        path.write_text(
            path.read_text(encoding="utf-8").replace("Track `A`", "Track A"),
            encoding="utf-8",
        )


def mutate_remove_gate_s4(root: pathlib.Path):
    path = root / "benchmarks" / "success_failure_gates.md"
    path.write_text(path.read_text(encoding="utf-8").replace("S4", "SX"), encoding="utf-8")


def mutate_break_benchmark_case_list(root: pathlib.Path):
    path = root / "BENCHMARK_STRATEGY.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- `c_opaque_call`", "- `b_direct_call`", 1), encoding="utf-8")


def mutate_break_mandatory_baseline_list(root: pathlib.Path):
    path = root / "benchmarks" / "baselines.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("- `typed-AST`", "- `ssa-like IR`", 1), encoding="utf-8")


def mutate_break_track_b_gate_list(root: pathlib.Path):
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
        "- `checked-in sample manifest may differ from the opt-in pilot manifest`\n"
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


def mutate_add_track_d_result(benchmark_items: dict):
    benchmark_items["track_d_result"] = {}


def mutate_add_track_c_manifest(benchmark_items: dict):
    benchmark_items["track_c_manifest"] = {}


def mutate_remove_track_b_baseline(benchmark_items: dict):
    benchmark_items["track_b_manifest"]["baselines"] = ["direct source"]


def mutate_track_c_result_disposition(benchmark_items: dict):
    benchmark_items["track_c_result"]["metrics"]["gate_K1_hit"] = True


def mutate_track_c_sample_result_file(root: pathlib.Path):
    path = root / "reports" / "examples" / "benchmark_track_c_result.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["evidence"] = [
        "non-default executable pilot over fixed Python repair cases",
        "seeded single-edit repairs restore original behavior for executable non-opaque cases",
        "c_opaque_call remains boundary-accounting-only",
        "promotion-ready benchmark slice",
    ]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def mutate_track_c_sample_result_status_file(root: pathlib.Path):
    path = root / "reports" / "examples" / "benchmark_track_c_result.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["status"] = "pass"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def mutate_track_c_sample_result_lock_metric_file(root: pathlib.Path):
    path = root / "reports" / "examples" / "benchmark_track_c_result.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["metrics"]["accepted_case_count"] = 1
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_negative_fixture(root: pathlib.Path, name: str, mutate, expected_markers):
    with tempfile.TemporaryDirectory(prefix="scir_benchmark_check_") as tmp:
        fixture_root = pathlib.Path(tmp) / "repo"
        shutil.copytree(root, fixture_root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        mutate(fixture_root)
        failures = run_checks(fixture_root)

    if not failures:
        return [f"benchmark self-test {name}: expected failure but dry run passed"]
    missing_markers = [marker for marker in expected_markers if not any(marker in failure for failure in failures)]
    if missing_markers:
        return [f"benchmark self-test {name}: missing expected failure markers {', '.join(missing_markers)}"]
    return []


def run_negative_track_c_sample_sync_fixture(root: pathlib.Path, name: str, mutate, expected_markers):
    with tempfile.TemporaryDirectory(prefix="scir_track_c_sample_sync_") as tmp:
        fixture_root = pathlib.Path(tmp) / "repo"
        shutil.copytree(root, fixture_root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        mutate(fixture_root)
        failures, manifest, result = run_track_c_pilot(fixture_root)
        if failures or manifest is None or result is None:
            return [f"benchmark self-test {name}: Track C pilot setup failed unexpectedly"]
        sync_failures = validate_track_c_pilot_outputs(fixture_root, manifest, result)

    if not sync_failures:
        return [f"benchmark self-test {name}: expected failure but Track C sample synchronization passed"]
    missing_markers = [marker for marker in expected_markers if not any(marker in failure for failure in sync_failures)]
    if missing_markers:
        return [f"benchmark self-test {name}: missing expected failure markers {', '.join(missing_markers)}"]
    return []


def run_self_tests(root: pathlib.Path):
    failures = []
    count = 0
    for name, mutate, expected_markers in [
        ("missing track marker", mutate_remove_track_a, ["missing track marker: Track `A`"]),
        ("missing gate marker", mutate_remove_gate_s4, ["missing gate marker: S4"]),
        ("benchmark case drift", mutate_break_benchmark_case_list, ["BENCHMARK_STRATEGY.md: active executable benchmark cases expected"]),
        ("mandatory baseline drift", mutate_break_mandatory_baseline_list, ["benchmarks/baselines.md: mandatory active baselines expected"]),
        ("track b gate drift", mutate_break_track_b_gate_list, ["benchmarks/success_failure_gates.md: Track B kill gates expected"]),
        ("track c task family drift", mutate_break_track_c_task_family_list, ["benchmarks/tracks.md: Track C pilot task family expected"]),
        ("track c baseline drift", mutate_break_track_c_baseline_list, ["benchmarks/baselines.md: Track C pilot baselines expected"]),
        ("track c gate drift", mutate_break_track_c_gate_list, ["benchmarks/success_failure_gates.md: Track C pilot kill gates expected"]),
        ("track c disposition drift", mutate_break_track_c_disposition_list, ["benchmarks/tracks.md: Track C disposition expected"]),
        ("track c retention drift", mutate_break_track_c_retention_list, ["benchmarks/success_failure_gates.md: Track C retention criteria expected"]),
        ("track c retirement drift", mutate_break_track_c_retirement_list, ["benchmarks/success_failure_gates.md: Track C retirement triggers expected"]),
        ("track c sample synchronization drift", mutate_break_track_c_sample_sync_list, ["benchmarks/tracks.md: Track C sample synchronization expected"]),
        ("track c sample posture re-decision drift", mutate_break_track_c_sample_redecision_list, ["benchmarks/tracks.md: Track C sample posture re-decision triggers expected"]),
        ("track c editorial-only refresh drift", mutate_break_track_c_editorial_refresh_list, ["benchmarks/tracks.md: Track C editorial-only sample refreshes expected"]),
        ("track c provenance drift", mutate_break_track_c_provenance_list, ["benchmarks/tracks.md: Track C non-editorial sample refresh provenance expected"]),
        ("track c benchmark readme provenance drift", mutate_break_track_c_benchmark_readme_provenance, ["benchmarks/README.md: Track C non-editorial sample refresh provenance rule must remain explicit"]),
        ("track c reports readme provenance drift", mutate_break_track_c_reports_readme_provenance, ["reports/README.md: Track C non-editorial sample refresh provenance rule must remain explicit"]),
    ]:
        count += 1
        failures.extend(run_negative_fixture(root, name, mutate, expected_markers))

    harness_failures, benchmark_items = run_benchmark_suite(root)
    if harness_failures or benchmark_items is None:
        return failures + ["benchmark self-test setup: executable benchmark harness must pass"], count

    for name, mutate, expected_markers in [
        ("unexpected track d artifact", mutate_add_track_d_result, ["benchmark bundle: unexpected executable artifact track_d_result"]),
        ("track c sample re-enters executable bundle", mutate_add_track_c_manifest, ["benchmark bundle: unexpected executable artifact track_c_manifest"]),
        (
            "missing track b baseline",
            mutate_remove_track_b_baseline,
            ["track_b manifest: expected baselines ['direct source', 'typed-AST', 'lightweight regularized core or s-expression']"],
        ),
    ]:
        count += 1
        mutated_items = json.loads(json.dumps(benchmark_items))
        mutate(mutated_items)
        semantic_failures = validate_executable_benchmark_items(root, mutated_items)
        if not semantic_failures:
            failures.append(f"benchmark self-test {name}: expected failure but semantic validation passed")
            continue
        missing_markers = [marker for marker in expected_markers if not any(marker in failure for failure in semantic_failures)]
        if missing_markers:
            failures.append(f"benchmark self-test {name}: missing expected failure markers {', '.join(missing_markers)}")

    track_c_failures, track_c_manifest, track_c_result = run_track_c_pilot(root)
    if track_c_failures or track_c_manifest is None or track_c_result is None:
        return failures + ["benchmark self-test setup: Track C optional pilot must pass"], count
    augment_track_c_pilot_outputs(root, track_c_manifest, track_c_result)

    for name, mutate, expected_markers in [
        ("track c retained disposition drift", mutate_track_c_result_disposition, ["track_c result: retained disposition requires K1 to remain untriggered"]),
    ]:
        count += 1
        mutated_payload = {
            "track_c_manifest": json.loads(json.dumps(track_c_manifest)),
            "track_c_result": json.loads(json.dumps(track_c_result)),
        }
        mutate(mutated_payload)
        semantic_failures = validate_track_c_pilot_outputs(
            root,
            mutated_payload["track_c_manifest"],
            mutated_payload["track_c_result"],
        )
        if not semantic_failures:
            failures.append(f"benchmark self-test {name}: expected failure but Track C pilot validation passed")
            continue
        missing_markers = [marker for marker in expected_markers if not any(marker in failure for failure in semantic_failures)]
        if missing_markers:
            failures.append(f"benchmark self-test {name}: missing expected failure markers {', '.join(missing_markers)}")

    for name, mutate, expected_markers in [
        (
            "track c sample result status drift",
            mutate_track_c_sample_result_status_file,
            ["track_c result sample: sample status change requires explicit Track C re-decision"],
        ),
        (
            "track c sample result file drift",
            mutate_track_c_sample_result_file,
            ["track_c result sample: sample evidence change requires explicit Track C re-decision"],
        ),
        (
            "track c sample lock-metric drift",
            mutate_track_c_sample_result_lock_metric_file,
            ["track_c result sample: sample case or boundary posture change requires explicit Track C re-decision"],
        ),
    ]:
        count += 1
        failures.extend(run_negative_track_c_sample_sync_fixture(root, name, mutate, expected_markers))

    return failures, count


def print_success(track_a_result, track_b_result, self_test_count):
    print("[benchmark] benchmark harness passed")
    print("Tracks, baselines, contamination controls, and executable Track A/B runs are present.")
    print("Conditional Track C doctrine, retained disposition, and sample artifacts are synchronized and remain non-default.")
    print(
        "Track A status: "
        f"{track_a_result['status']} "
        f"(median SCIR/source ratio={track_a_result['metrics']['median_scir_to_source_ratio']}, "
        f"median SCIR-Hc/typed-AST ratio={track_a_result['metrics']['median_scirhc_to_typed_ast_ratio']})."
    )
    print(
        "Track B status: "
        f"{track_b_result['status']} "
        f"(Tier A compile={track_b_result['metrics']['tier_a_compile_pass_rate']}, "
        f"Tier A test={track_b_result['metrics']['tier_a_test_pass_rate']})."
    )
    print(f"Benchmark checker self-tests passed ({self_test_count} negative fixtures).")


def print_track_c_success(track_c_result):
    disposition = benchmark_track_contract("C")["disposition"][0]
    print(
        "Track C optional status: "
        f"{track_c_result['status']} "
        f"(accept={track_c_result['metrics']['repair_accept_rate']}, "
        f"test={track_c_result['metrics']['repair_test_pass_rate']}, "
        f"typed-AST delta={track_c_result['baseline_comparison']['typed-AST']}, "
        f"disposition={disposition})."
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--include-track-c-pilot", action="store_true")
    parser.add_argument("--output-dir")
    parser.add_argument("--claim-run", action="store_true")
    parser.add_argument("--corpus-manifest")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve() if args.root else pathlib.Path(__file__).resolve().parents[1]
    failures = run_checks(root)
    if failures:
        print("[benchmark] doctrine dry run failed")
        for item in failures:
            print(f" - {item}")
        sys.exit(1)

    self_test_failures, self_test_count = run_self_tests(root)
    if self_test_failures:
        print("[benchmark] doctrine self-tests failed")
        for item in self_test_failures:
            print(f" - {item}")
        sys.exit(1)

    corpus_manifest_rel = args.corpus_manifest or BENCHMARK_CORPUS_MANIFEST_REL
    sweep_manifest_rel = BENCHMARK_SWEEP_MANIFEST_REL
    temp_sweep_dir = None
    if corpus_manifest_rel != BENCHMARK_CORPUS_MANIFEST_REL:
        temp_sweep_dir = tempfile.TemporaryDirectory(prefix="scir_benchmark_sweep_", dir=root)
        sweep_manifest = load_json(root, BENCHMARK_SWEEP_MANIFEST_REL)
        sweep_manifest["corpus_manifest"] = corpus_manifest_rel
        temp_sweep_path = pathlib.Path(temp_sweep_dir.name) / "benchmark_sweep.json"
        temp_sweep_path.write_text(json.dumps(sweep_manifest, indent=2) + "\n", encoding="utf-8")
        sweep_manifest_rel = temp_sweep_path.relative_to(root).as_posix()

    sweep_failures, sweep_result, sweep_summary, regression_summary, comparison_summary, contamination_report = run_sweep(
        root,
        sweep_manifest_rel,
    )
    if sweep_failures:
        print("[benchmark] executable sweep audit failed")
        for item in sweep_failures:
            print(f" - {item}")
        sys.exit(1)

    harness_failures, benchmark_items = run_benchmark_suite(root)
    if harness_failures:
        print("[benchmark] executable benchmark harness failed")
        for item in harness_failures:
            print(f" - {item}")
        sys.exit(1)

    reproducibility_block = build_reproducibility_block(
        "python scripts/benchmark_contract_dry_run.py"
        + (" --include-track-c-pilot" if args.include_track_c_pilot else "")
        + (" --claim-run" if args.claim_run else ""),
        root=root,
        timestamp=sweep_result["generated_at"],
    )
    augment_benchmark_items(
        benchmark_items=benchmark_items,
        sweep_result=sweep_result,
        comparison_summary=comparison_summary,
        reproducibility_block=reproducibility_block,
        corpus_manifest_rel=corpus_manifest_rel,
    )

    bundle_failures = validate_executable_benchmark_items(root, benchmark_items)
    if bundle_failures:
        print("[benchmark] executable benchmark bundle validation failed")
        for item in bundle_failures:
            print(f" - {item}")
        sys.exit(1)

    corpus_manifest = load_json(root, corpus_manifest_rel)
    manifest_lock = build_manifest_lock(root, corpus_manifest_rel, sweep_result["run_id"], sweep_result["generated_at"])
    benchmark_report = build_benchmark_report(
        run_id=sweep_result["run_id"],
        commit_sha=sweep_result["commit_sha"],
        generated_at=sweep_result["generated_at"],
        claim_run=args.claim_run,
        corpus_manifest_rel=corpus_manifest_rel,
        corpus_manifest=corpus_manifest,
        comparison_summary=comparison_summary,
        contamination_report=contamination_report,
        benchmark_items=benchmark_items,
        reproducibility_block=reproducibility_block,
    )
    report_failures = []
    report_failures.extend(
        validate_instance(
            root,
            comparison_summary,
            "schemas/comparison_summary.schema.json",
            "comparison summary",
        )
    )
    report_failures.extend(
        validate_instance(
            root,
            contamination_report,
            "schemas/contamination_report.schema.json",
            "contamination report",
        )
    )
    report_failures.extend(
        validate_instance(
            root,
            benchmark_report,
            "schemas/benchmark_report.schema.json",
            "benchmark report",
        )
    )
    if report_failures:
        print("[benchmark] audit report schema validation failed")
        for item in report_failures:
            print(f" - {item}")
        sys.exit(1)
    output_dir = pathlib.Path(args.output_dir).resolve() if args.output_dir else (
        root / "artifacts" / "benchmark_runs" / sweep_result["run_id"]
    )
    write_benchmark_outputs(
        output_dir=output_dir,
        benchmark_items=benchmark_items,
        sweep_result=sweep_result,
        sweep_summary=sweep_summary,
        regression_summary=regression_summary,
        comparison_summary=comparison_summary,
        contamination_report=contamination_report,
        benchmark_report=benchmark_report,
        manifest_lock=manifest_lock,
        sweep_manifest_rel=sweep_manifest_rel,
    )

    claim_failures = (
        benchmark_gate_failures(comparison_summary, contamination_report)
        + claim_audit_failures(
            benchmark_items=benchmark_items,
            comparison_summary=comparison_summary,
            contamination_report=contamination_report,
            benchmark_report=benchmark_report,
            manifest_lock=manifest_lock,
        )
        if args.claim_run
        else []
    )
    if claim_failures:
        print("[benchmark] claim gates failed")
        for item in claim_failures:
            print(f" - {item}")
        print(f"[benchmark] artifacts written to {output_dir}")
        sys.exit(1)

    print_success(benchmark_items["track_a_result"], benchmark_items["track_b_result"], self_test_count)
    print(f"Benchmark artifacts written to {output_dir}")
    if args.include_track_c_pilot:
        track_c_failures, track_c_manifest, track_c_result = run_track_c_pilot(root)
        if track_c_failures:
            print("[benchmark] conditional Track C pilot failed")
            for item in track_c_failures:
                print(f" - {item}")
            sys.exit(1)
        augment_track_c_pilot_outputs(root, track_c_manifest, track_c_result)
        track_c_bundle_failures = validate_track_c_pilot_outputs(root, track_c_manifest, track_c_result)
        if track_c_bundle_failures:
            print("[benchmark] conditional Track C pilot bundle validation failed")
            for item in track_c_bundle_failures:
                print(f" - {item}")
            sys.exit(1)
        print_track_c_success(track_c_result)
    if temp_sweep_dir is not None:
        temp_sweep_dir.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    main()
