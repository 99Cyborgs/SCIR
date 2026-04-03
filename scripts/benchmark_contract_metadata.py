#!/usr/bin/env python3
"""Central benchmark contract metadata shared by validation, execution, and reporting.

This file is authoritative for which tracks, cases, baselines, and Track C
pilot posture are active. Scripts import these constants to prevent docs, CI,
and executable benchmark logic from silently diverging.
"""
from __future__ import annotations

from scir_python_bootstrap import PYTHON_PROOF_LOOP_METADATA


TRACK_C_EXECUTABLE_CASES = [
    case_name
    for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items()
    if not contract["requires_opaque_boundary"]
]
TRACK_C_BOUNDARY_ONLY_CASES = [
    case_name
    for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items()
    if contract["requires_opaque_boundary"]
]
TRACK_C_SAMPLE_SYNC_REQUIREMENTS = [
    "checked-in sample manifest must equal the current opt-in pilot manifest",
    "checked-in sample result must equal the current opt-in pilot result",
    f"checked-in sample result must keep accepted_case_count {len(TRACK_C_EXECUTABLE_CASES)} and boundary_only_case_count {len(TRACK_C_BOUNDARY_ONLY_CASES)}",
    "checked-in sample result must keep gate_S2_ready true, gate_K1_hit false, and status mixed or pass",
]
TRACK_C_SAMPLE_POSTURE_REDECISION_TRIGGERS = [
    "changing checked-in sample status from mixed requires a new decision-register entry and queue update",
    "changing checked-in sample evidence or retained-diagnostic wording requires a new decision-register entry and queue update",
    "changing checked-in sample task family, case set, or boundary-accounting posture requires a new decision-register entry and queue update",
    "changing checked-in sample default-gate or promotion posture requires a new decision-register entry and queue update",
]
TRACK_C_EDITORIAL_ONLY_SAMPLE_REFRESHES = [
    "json whitespace, indentation, and trailing-newline normalization that preserves parsed sample content",
    "json key-order normalization that preserves parsed sample content",
]
TRACK_C_NON_EDITORIAL_SAMPLE_REFRESH_PROVENANCE = [
    "cite python scripts/benchmark_contract_dry_run.py --include-track-c-pilot as the regeneration command",
    "cite python scripts/run_repo_validation.py --include-track-c-pilot as the confirming validation command",
    "cite the regenerated manifest corpus hash",
    "cite the regenerated result run_id and system_under_test",
]


BENCHMARK_CONTRACT_METADATA = {
    "active_tracks": ["A", "B"],
    "conditional_tracks": ["C"],
    "deferred_tracks": ["D"],
    "benchmark_cases": list(PYTHON_PROOF_LOOP_METADATA["benchmark_cases"]),
    "mandatory_baselines": [
        "direct source",
        "typed-AST",
    ],
    "track_specific_additional_baselines": {
        "A": ["lightweight regularized core or s-expression"],
        "B": ["lightweight regularized core or s-expression"],
        "C": ["lightweight regularized core or s-expression"],
    },
    "contamination_controls": [
        "hash every published corpus manifest",
        "separate development, tuning, and held-out evaluation slices",
        "record prompt templates and baseline adapters",
        "do not claim generalization from a contaminated or untracked dataset",
    ],
    "active_benchmark_case_heading": "fixed executable Python proof-loop cases",
    "track_contracts": {
        "A": {
            "benchmark_id": "bootstrap-track-a-python-subset",
            "task_family": "scir-h-regularity-and-compression",
            "corpus_name": "python-bootstrap-fixtures",
            "corpus_scope": "Fixed executable Python bootstrap cases",
            "profiles": ["R", "D-PY"],
            "result_profile": "R",
            "success_gates": ["S3", "S4"],
            "kill_gates": ["K2", "K4"],
            "required_metrics": [
                "median_scir_to_source_ratio",
                "aggregate_scir_to_source_ratio",
                "median_scirhc_to_source_ratio",
                "aggregate_scirhc_to_source_ratio",
                "median_scir_to_typed_ast_ratio",
                "aggregate_scir_to_typed_ast_ratio",
                "median_scirhc_to_typed_ast_ratio",
                "aggregate_scirhc_to_typed_ast_ratio",
                "aggregate_structural_redundancy_gain",
                "patch_composability_gain_vs_typed_ast",
                "gate_S3_source_pass",
                "gate_S3_ast_pass",
                "gate_S4_pass",
                "gate_K2_hit",
                "gate_K4_hit",
            ],
        },
        "B": {
            "benchmark_id": "bootstrap-track-b-python-subset",
            "task_family": "python-bootstrap-roundtrip",
            "corpus_name": "python-bootstrap-fixtures",
            "corpus_scope": "Tier A plus explicit Tier C bootstrap reconstruction subset",
            "profiles": ["R", "D-PY"],
            "result_profile": "R",
            "success_gates": ["S1", "S4"],
            "kill_gates": ["K3", "K4"],
            "required_metrics": [
                "tier_a_compile_pass_rate",
                "tier_a_test_pass_rate",
                "idiomaticity_mean",
                "gate_S1_pass",
                "gate_S4_pass",
                "gate_K3_hit",
                "gate_K4_hit",
            ],
        },
    },
    "conditional_track_contracts": {
        "C": {
            "benchmark_id": "example-benchmark-track-c-python-repair-001",
            "task_family": "python-single-function-repair",
            "corpus_name": "python-bootstrap-fixtures",
            "corpus_scope": "Fixed executable Python proof-loop cases reframed as single-function repair tasks",
            "pilot_cases": list(PYTHON_PROOF_LOOP_METADATA["benchmark_cases"]),
            "executable_cases": list(TRACK_C_EXECUTABLE_CASES),
            "boundary_only_cases": list(TRACK_C_BOUNDARY_ONLY_CASES),
            "profiles": ["R", "D-PY"],
            "result_profile": "R",
            "success_gates": ["S2"],
            "kill_gates": ["K1"],
            "required_metrics": [
                "repair_task_count",
                "accepted_case_count",
                "boundary_only_case_count",
                "repair_accept_rate",
                "repair_test_pass_rate",
                "median_scir_to_source_repair_ratio",
                "median_scir_to_typed_ast_repair_ratio",
                "median_scir_to_regularized_core_repair_ratio",
                "gate_S2_ready",
                "gate_K1_hit",
                "boundary_annotation_fraction",
                "preservation_level_ceiling",
            ],
            "artifact_posture": [
                "illustrative sample only",
                "outside default executable benchmark gate",
            ],
            "execution_posture": [
                "non-default executable pilot only",
                "opaque-boundary cases remain boundary-accounting-only",
            ],
            "disposition": [
                "retain bounded diagnostic pilot",
                "do not promote to default executable gate",
                "keep c_opaque_call boundary-accounting-only",
            ],
            "expected_accepted_case_count": len(TRACK_C_EXECUTABLE_CASES),
            "allowed_result_statuses": ["mixed", "pass"],
            "retention_criteria": [
                "gate_S2_ready must remain true",
                "gate_K1_hit must remain false",
                f"accepted_case_count must remain {len(TRACK_C_EXECUTABLE_CASES)}",
                f"boundary_only_case_count must remain {len(TRACK_C_BOUNDARY_ONLY_CASES)}",
                "status must remain mixed or pass",
            ],
            "retirement_triggers": [
                "retire if gate_S2_ready becomes false",
                "retire if gate_K1_hit becomes true",
                f"retire if accepted_case_count drops below {len(TRACK_C_EXECUTABLE_CASES)}",
                f"retire if boundary_only_case_count differs from {len(TRACK_C_BOUNDARY_ONLY_CASES)}",
                "retire if status becomes fail",
            ],
            "sample_sync_requirements": list(TRACK_C_SAMPLE_SYNC_REQUIREMENTS),
            "sample_posture_redecision_triggers": list(TRACK_C_SAMPLE_POSTURE_REDECISION_TRIGGERS),
            "editorial_only_sample_refreshes": list(TRACK_C_EDITORIAL_ONLY_SAMPLE_REFRESHES),
            "non_editorial_sample_refresh_provenance": list(TRACK_C_NON_EDITORIAL_SAMPLE_REFRESH_PROVENANCE),
            "opt_in_command": "python scripts/benchmark_contract_dry_run.py --include-track-c-pilot",
            "opt_in_validation_command": "python scripts/run_repo_validation.py --include-track-c-pilot",
            "sample_manifest_path": "reports/examples/benchmark_track_c_manifest.example.json",
            "sample_result_path": "reports/examples/benchmark_track_c_result.example.json",
            "sample_manifest_hash": "sha256:41592f102f5fd852200de007698774508f9ffeebd8fb5b4d9d01c85c812873e6",
            "sample_run_id": "example-track-c-pilot-run-2026-04-01",
            "sample_system_under_test": "scir-bootstrap-non-default-track-c-pilot",
            "sample_result_status": "mixed",
            "sample_evidence": [
                "non-default executable pilot over fixed Python repair cases",
                "seeded single-edit repairs restore original behavior for executable non-opaque cases",
                "c_opaque_call remains boundary-accounting-only",
                "retained as a bounded diagnostic pilot rather than a promotion claim",
            ],
        }
    },
    "conditional_success_gates": ["S2"],
    "deferred_kill_gates": ["K5"],
    "preservation_level_ceiling": "P3",
}


def benchmark_track_contract(track: str) -> dict:
    """Return the canonical contract for one benchmark track."""

    if track in BENCHMARK_CONTRACT_METADATA["track_contracts"]:
        return BENCHMARK_CONTRACT_METADATA["track_contracts"][track]
    if track in BENCHMARK_CONTRACT_METADATA["conditional_track_contracts"]:
        return BENCHMARK_CONTRACT_METADATA["conditional_track_contracts"][track]
    raise KeyError(track)


def benchmark_track_baselines(track: str) -> list[str]:
    """Return the exact baseline set that a track must compare against."""

    return [
        *BENCHMARK_CONTRACT_METADATA["mandatory_baselines"],
        *BENCHMARK_CONTRACT_METADATA["track_specific_additional_baselines"][track],
    ]


def benchmark_track_compile_cases() -> list[str]:
    return list(TRACK_C_EXECUTABLE_CASES)


def _validate_benchmark_contract_metadata():
    """Fail fast if benchmark metadata would let executable logic drift from the frozen track doctrine."""

    expected_cases = list(PYTHON_PROOF_LOOP_METADATA["benchmark_cases"])
    if BENCHMARK_CONTRACT_METADATA["benchmark_cases"] != expected_cases:
        raise ValueError("BENCHMARK_CONTRACT_METADATA benchmark cases drifted from PYTHON_PROOF_LOOP_METADATA")

    expected_compile_cases = list(TRACK_C_EXECUTABLE_CASES)
    if benchmark_track_compile_cases() != expected_compile_cases:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track B compile cases drifted from PYTHON_PROOF_LOOP_METADATA")

    if BENCHMARK_CONTRACT_METADATA["active_tracks"] != ["A", "B"]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA active tracks must remain Track A and Track B")
    if BENCHMARK_CONTRACT_METADATA["conditional_tracks"] != ["C"]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA conditional tracks must remain Track C only")
    if BENCHMARK_CONTRACT_METADATA["deferred_tracks"] != ["D"]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA deferred tracks must remain Track D only")

    for track in BENCHMARK_CONTRACT_METADATA["active_tracks"]:
        contract = benchmark_track_contract(track)
        baselines = benchmark_track_baselines(track)
        if BENCHMARK_CONTRACT_METADATA["mandatory_baselines"][0] not in baselines:
            raise ValueError(f"BENCHMARK_CONTRACT_METADATA Track {track} must include direct source baseline")
        if BENCHMARK_CONTRACT_METADATA["mandatory_baselines"][1] not in baselines:
            raise ValueError(f"BENCHMARK_CONTRACT_METADATA Track {track} must include typed-AST baseline")
        if track == "A" and contract["success_gates"] != ["S3", "S4"]:
            raise ValueError("BENCHMARK_CONTRACT_METADATA Track A success gates must remain S3 and S4")
        if track == "A" and contract["kill_gates"] != ["K2", "K4"]:
            raise ValueError("BENCHMARK_CONTRACT_METADATA Track A kill gates must remain K2 and K4")
        if track == "B" and contract["success_gates"] != ["S1", "S4"]:
            raise ValueError("BENCHMARK_CONTRACT_METADATA Track B success gates must remain S1 and S4")
        if track == "B" and contract["kill_gates"] != ["K3", "K4"]:
            raise ValueError("BENCHMARK_CONTRACT_METADATA Track B kill gates must remain K3 and K4")

    track_c_contract = benchmark_track_contract("C")
    if BENCHMARK_CONTRACT_METADATA["track_specific_additional_baselines"]["C"] != [
        "lightweight regularized core or s-expression"
    ]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C pilot baseline must remain the regularized core comparison")
    if track_c_contract["task_family"] != "python-single-function-repair":
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C task family must remain python-single-function-repair")
    if track_c_contract["pilot_cases"] != expected_cases:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C pilot cases must remain the executable Python proof-loop cases")
    if track_c_contract["success_gates"] != ["S2"]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C success gates must remain S2")
    if track_c_contract["kill_gates"] != ["K1"]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C kill gates must remain K1")
    if track_c_contract["executable_cases"] != expected_compile_cases:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C executable cases must remain the non-opaque executable Python cases")
    if track_c_contract["boundary_only_cases"] != ["c_opaque_call"]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C boundary-only cases must remain c_opaque_call")
    if track_c_contract["profiles"] != ["R", "D-PY"]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C profiles must remain R and D-PY")
    if track_c_contract["sample_result_status"] != "mixed":
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C sample result status must remain mixed")
    if track_c_contract["artifact_posture"] != [
        "illustrative sample only",
        "outside default executable benchmark gate",
    ]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C artifact posture markers drifted")
    if track_c_contract["execution_posture"] != [
        "non-default executable pilot only",
        "opaque-boundary cases remain boundary-accounting-only",
    ]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C execution posture markers drifted")
    if track_c_contract["disposition"] != [
        "retain bounded diagnostic pilot",
        "do not promote to default executable gate",
        "keep c_opaque_call boundary-accounting-only",
    ]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C disposition markers drifted")
    if track_c_contract["expected_accepted_case_count"] != len(expected_compile_cases):
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C accepted-case expectation drifted")
    if track_c_contract["allowed_result_statuses"] != ["mixed", "pass"]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C allowed result statuses must remain mixed/pass")
    if track_c_contract["retention_criteria"] != [
        "gate_S2_ready must remain true",
        "gate_K1_hit must remain false",
        f"accepted_case_count must remain {len(expected_compile_cases)}",
        f"boundary_only_case_count must remain {len(track_c_contract['boundary_only_cases'])}",
        "status must remain mixed or pass",
    ]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C retention criteria drifted")
    if track_c_contract["retirement_triggers"] != [
        "retire if gate_S2_ready becomes false",
        "retire if gate_K1_hit becomes true",
        f"retire if accepted_case_count drops below {len(expected_compile_cases)}",
        f"retire if boundary_only_case_count differs from {len(track_c_contract['boundary_only_cases'])}",
        "retire if status becomes fail",
    ]:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C retirement triggers drifted")
    if track_c_contract["sample_sync_requirements"] != TRACK_C_SAMPLE_SYNC_REQUIREMENTS:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C sample synchronization requirements drifted")
    if track_c_contract["sample_posture_redecision_triggers"] != TRACK_C_SAMPLE_POSTURE_REDECISION_TRIGGERS:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C sample posture re-decision triggers drifted")
    if track_c_contract["editorial_only_sample_refreshes"] != TRACK_C_EDITORIAL_ONLY_SAMPLE_REFRESHES:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C editorial-only sample refresh allowances drifted")
    if track_c_contract["non_editorial_sample_refresh_provenance"] != TRACK_C_NON_EDITORIAL_SAMPLE_REFRESH_PROVENANCE:
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C non-editorial sample refresh provenance requirements drifted")
    if track_c_contract["opt_in_command"] != "python scripts/benchmark_contract_dry_run.py --include-track-c-pilot":
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C opt-in benchmark command drifted")
    if track_c_contract["opt_in_validation_command"] != "python scripts/run_repo_validation.py --include-track-c-pilot":
        raise ValueError("BENCHMARK_CONTRACT_METADATA Track C opt-in validation command drifted")


_validate_benchmark_contract_metadata()
