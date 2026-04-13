"""File: benchmarks/baselines/normalized/__init__.py
Purpose: Benchmark a lightweight normalized-Python baseline built from Python's own parsed and unparsed source.
Role in system: This adapter measures whether a simple regularized source form closes the gap with SCIR on the admitted corpus.
Key dependencies: ast plus benchmark_audit_common row and token helpers.
Side effects: Reads fixture files, reparses source with Python's AST, and emits per-stage audit rows.
"""
from __future__ import annotations

import ast

from benchmark_audit_common import (
    NORMALIZED_BASELINE_NAME,
    build_audit_row,
    case_name_from_artifact_id,
    token_count,
    token_edit_distance,
)


BASELINE_NAME = NORMALIZED_BASELINE_NAME
NORMALIZED_MARKERS = ["await", "return", "if", ".", "="]


def representation_text(source_text: str) -> str:
    """Purpose: Normalize source text through Python's parser and unparser.

    Inputs:
      - source_text: str original fixture source.
    Outputs:
      - str normalized source text with a trailing newline.
    Side Effects:
      - Parses Python source into an AST.
    Assumptions:
      - `ast.unparse(ast.parse(...))` is a fair baseline for lightweight regularization on the frozen Python corpus.
    Failure Modes:
      - Raises SyntaxError if the source fixture is invalid Python.
    """
    return ast.unparse(ast.parse(source_text)).rstrip() + "\n"


def semantic_explicitness(text: str) -> float:
    """Purpose: Estimate semantic marker density in the normalized-source baseline representation.

    Inputs:
      - text: str normalized baseline representation.
    Outputs:
      - float normalized marker density.
    Side Effects:
      - None.
    Assumptions:
      - The chosen markers approximate explicit structure in the regularized source view.
    Failure Modes:
      - None.
    """
    token_total = max(token_count(text), 1)
    hits = sum(text.count(marker) for marker in NORMALIZED_MARKERS)
    return round(hits / token_total, 4)


def run(*, corpus_manifest: dict, root, stages: list[str], context: dict):
    """Purpose: Emit benchmark rows for the normalized-source baseline across the requested stage matrix.

    Inputs:
      - corpus_manifest: dict fixture manifest to iterate.
      - root: Path-like repository root used to resolve fixture paths.
      - stages: list[str] benchmark stages requested by the harness.
      - context: dict run metadata, callbacks, and row-construction dependencies.
    Outputs:
      - list[dict] audit rows for the normalized baseline.
    Side Effects:
      - Reads source fixtures from disk.
      - Rebuilds normalized source text through Python's AST.
      - Calls the benchmark evaluation callback for the reconstruction stage.
    Assumptions:
      - The normalized baseline participates meaningfully in `source_to_h` and `h_to_python` only.
    Failure Modes:
      - Propagates AST parse failures or evaluation callback failures.
    """
    rows = []
    for entry in corpus_manifest["fixtures"]:
        source_text = (root / entry["path"]).read_text(encoding="utf-8")
        case_name = case_name_from_artifact_id(entry["id"])
        normalized_text = representation_text(source_text)
        normalized_token_count = token_count(normalized_text)
        source_token_total = token_count(source_text)
        for stage in stages:
            if stage == "source_to_h":
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
                        metrics={
                            "token_count": normalized_token_count,
                            "source_token_count": source_token_total,
                            "edit_distance": token_edit_distance(source_text, normalized_text),
                            "LCR": round(normalized_token_count / max(source_token_total, 1), 4),
                            "GR": 1.0,
                            "SE": semantic_explicitness(normalized_text),
                            "SCPR": None,
                            "round_trip": None,
                        },
                        slice_axes=context["slice_axes"],
                        reproducibility_block=context["reproducibility_block"],
                        unsupported_tags=entry.get("unsupported_tags", []),
                    )
                )
                continue
            if stage == "h_to_python":
                compile_pass, test_pass = context["evaluate_case"](case_name, normalized_text)
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
                        metrics={
                            "token_count": normalized_token_count,
                            "source_token_count": source_token_total,
                            "edit_distance": token_edit_distance(source_text, normalized_text),
                            "LCR": None,
                            "GR": 1.0 if compile_pass and test_pass else 0.0,
                            "SE": None,
                            "SCPR": 1.0 if compile_pass else 0.0,
                            "round_trip": 1.0 if compile_pass and test_pass else 0.0,
                        },
                        slice_axes=context["slice_axes"],
                        reproducibility_block=context["reproducibility_block"],
                        unsupported_tags=entry.get("unsupported_tags", []),
                    )
                )
                continue
            # Preserve the benchmark stage matrix even when this baseline has no
            # meaningful analogue for a later SCIR-specific stage.
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
                        "source_token_count": source_token_total,
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
