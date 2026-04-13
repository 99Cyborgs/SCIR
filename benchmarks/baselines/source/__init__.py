"""File: benchmarks/baselines/source/__init__.py
Purpose: Score the direct-source baseline against the benchmark row contract without adding an intermediate representation.
Role in system: This adapter provides the strongest non-SCIR baseline for lexical and round-trip comparisons.
Key dependencies: benchmark_audit_common row helpers and the benchmark evaluation callback supplied in context.
Side effects: Reads source fixtures from disk and emits per-stage audit rows.
"""
from __future__ import annotations

from benchmark_audit_common import (
    PIPELINE_STAGES,
    SOURCE_BASELINE_NAME,
    build_audit_row,
    case_name_from_artifact_id,
    token_count,
    token_edit_distance,
)


BASELINE_NAME = SOURCE_BASELINE_NAME
SOURCE_MARKERS = ["await", "return", "if", "import", "."]


def semantic_explicitness(text: str) -> float:
    """Purpose: Estimate how much semantic structure is directly visible in raw source text.

    Inputs:
      - text: str source representation under evaluation.
    Outputs:
      - float normalized marker density for the direct-source baseline.
    Side Effects:
      - None.
    Assumptions:
      - The selected source markers are a coarse readability proxy, not a semantic proof.
    Failure Modes:
      - None.
    """
    token_total = max(token_count(text), 1)
    hits = sum(text.count(marker) for marker in SOURCE_MARKERS)
    return round(hits / token_total, 4)


def run(*, corpus_manifest: dict, root, stages: list[str], context: dict):
    """Purpose: Emit direct-source benchmark rows for the requested benchmark stages.

    Inputs:
      - corpus_manifest: dict fixture manifest to iterate.
      - root: Path-like repository root used to resolve fixture paths.
      - stages: list[str] pipeline stages requested by the benchmark harness.
      - context: dict run metadata, callbacks, and row-construction dependencies.
    Outputs:
      - list[dict] audit rows for the direct-source baseline.
    Side Effects:
      - Reads source fixtures from disk.
      - Calls the benchmark evaluation callback for the reconstruction stage.
    Assumptions:
      - Only `source_to_h` and `h_to_python` have meaningful direct-source baseline behavior; later stages must stay explicit skips.
    Failure Modes:
      - Propagates filesystem or callback failures from fixture loading or evaluation.
    """
    rows = []
    for entry in corpus_manifest["fixtures"]:
        source_path = root / entry["path"]
        source_text = source_path.read_text(encoding="utf-8")
        case_name = case_name_from_artifact_id(entry["id"])
        for stage in stages:
            if stage == "source_to_h":
                metrics = {
                    "token_count": token_count(source_text),
                    "source_token_count": token_count(source_text),
                    "edit_distance": 0,
                    "LCR": 1.0,
                    "GR": 1.0,
                    "SE": semantic_explicitness(source_text),
                    "SCPR": None,
                    "round_trip": None,
                }
                rows.append(
                    build_audit_row(
                        entry=entry,
                        stage=stage,
                        run_id=context["run_id"],
                        commit_sha=context["commit_sha"],
                        spec_version=context["spec_version"],
                        tool_version=context["tool_version"],
                        baseline_name=BASELINE_NAME,
                        corpus_manifest_hash=context["corpus_manifest_hash"],
                        profile=context["profile_for_stage"](entry, stage),
                        status="pass",
                        diagnostic_codes=[],
                        preservation_requested=entry.get("expected_preservation_ceiling"),
                        preservation_observed=None,
                        compile_pass=None,
                        test_pass=None,
                        duration_ms=0,
                        metrics=metrics,
                        slice_axes=context["slice_axes"],
                        reproducibility_block=context["reproducibility_block"],
                        unsupported_tags=entry.get("unsupported_tags", []),
                    )
                )
                continue
            if stage == "h_to_python":
                compile_pass, test_pass = context["evaluate_case"](case_name, source_text)
                metrics = {
                    "token_count": token_count(source_text),
                    "source_token_count": token_count(source_text),
                    "edit_distance": 0,
                    "LCR": None,
                    "GR": 1.0 if compile_pass and test_pass else 0.0,
                    "SE": None,
                    "SCPR": 1.0 if compile_pass else 0.0,
                    "round_trip": 1.0 if compile_pass and test_pass else 0.0,
                }
                diagnostics = []
                if not compile_pass:
                    diagnostics.append("BASELINE_COMPILE_FAIL")
                elif not test_pass:
                    diagnostics.append("BASELINE_TEST_FAIL")
                rows.append(
                    build_audit_row(
                        entry=entry,
                        stage=stage,
                        run_id=context["run_id"],
                        commit_sha=context["commit_sha"],
                        spec_version=context["spec_version"],
                        tool_version=context["tool_version"],
                        baseline_name=BASELINE_NAME,
                        corpus_manifest_hash=context["corpus_manifest_hash"],
                        profile=context["profile_for_stage"](entry, stage),
                        status="pass" if compile_pass and test_pass else "fail",
                        diagnostic_codes=diagnostics,
                        preservation_requested=entry.get("expected_preservation_ceiling"),
                        preservation_observed=None,
                        compile_pass=compile_pass,
                        test_pass=test_pass,
                        duration_ms=0,
                        metrics=metrics,
                        slice_axes=context["slice_axes"],
                        reproducibility_block=context["reproducibility_block"],
                        unsupported_tags=entry.get("unsupported_tags", []),
                    )
                )
                continue
            # The direct-source baseline has no representation for derivative
            # stages, so preserve the stage matrix by emitting explicit skips.
            rows.append(
                build_audit_row(
                    entry=entry,
                    stage=stage,
                    run_id=context["run_id"],
                    commit_sha=context["commit_sha"],
                    spec_version=context["spec_version"],
                    tool_version=context["tool_version"],
                    baseline_name=BASELINE_NAME,
                    corpus_manifest_hash=context["corpus_manifest_hash"],
                    profile=context["profile_for_stage"](entry, stage),
                    status="skip",
                    diagnostic_codes=[],
                    preservation_requested=entry.get("expected_preservation_ceiling"),
                    preservation_observed=None,
                    compile_pass=None,
                    test_pass=None,
                    duration_ms=0,
                    metrics={
                        "token_count": None,
                        "source_token_count": token_count(source_text),
                        "edit_distance": None,
                        "LCR": None,
                        "GR": None,
                        "SE": None,
                        "SCPR": None,
                        "round_trip": None,
                    },
                    slice_axes=context["slice_axes"],
                    reproducibility_block=context["reproducibility_block"],
                    unsupported_tags=entry.get("unsupported_tags", []),
                )
            )
    return rows
