"""File: benchmarks/baselines/typed_ast/__init__.py
Purpose: Benchmark a typed-AST style baseline using Python's AST dump plus reconstructed source.
Role in system: This adapter is the strongest structural non-SCIR baseline in the repo's falsification doctrine.
Key dependencies: ast plus benchmark_audit_common row and token helpers.
Side effects: Reads fixture files, parses Python source into AST dumps, reconstructs source text, and emits per-stage audit rows.
"""
from __future__ import annotations

import ast

from benchmark_audit_common import (
    TYPED_AST_BASELINE_NAME,
    build_audit_row,
    case_name_from_artifact_id,
    token_count,
    token_edit_distance,
)


BASELINE_NAME = TYPED_AST_BASELINE_NAME
TYPED_AST_MARKERS = [
    "FunctionDef",
    "AsyncFunctionDef",
    "Assign",
    "Return",
    "If",
    "Call",
    "Await",
    "Attribute",
]


def representation_text(source_text: str) -> str:
    """Purpose: Render the baseline representation as a stable AST dump.

    Inputs:
      - source_text: str original fixture source.
    Outputs:
      - str AST dump without source-location noise.
    Side Effects:
      - Parses Python source into an AST.
    Assumptions:
      - Omitting attributes keeps the representation focused on structure rather than incidental coordinates.
    Failure Modes:
      - Raises SyntaxError if the source fixture is invalid Python.
    """
    return ast.dump(ast.parse(source_text), annotate_fields=True, include_attributes=False)


def reconstructed_text(source_text: str) -> str:
    """Purpose: Rebuild executable Python text from the parsed AST for round-trip comparison.

    Inputs:
      - source_text: str original fixture source.
    Outputs:
      - str reconstructed source with a trailing newline.
    Side Effects:
      - Parses and unparses Python source.
    Assumptions:
      - The typed-AST baseline's reconstruction surface is Python's own unparser.
    Failure Modes:
      - Raises SyntaxError if the source fixture is invalid Python.
    """
    return ast.unparse(ast.parse(source_text)).rstrip() + "\n"


def semantic_explicitness(text: str) -> float:
    """Purpose: Estimate how much structural information is visible in the AST-dump baseline.

    Inputs:
      - text: str typed-AST baseline representation.
    Outputs:
      - float normalized marker density for AST node names.
    Side Effects:
      - None.
    Assumptions:
      - Node-name density is a coarse structural-explicitness proxy for the typed-AST baseline.
    Failure Modes:
      - None.
    """
    token_total = max(token_count(text), 1)
    hits = sum(text.count(marker) for marker in TYPED_AST_MARKERS)
    return round(hits / token_total, 4)


def run(*, corpus_manifest: dict, root, stages: list[str], context: dict):
    """Purpose: Emit benchmark rows for the typed-AST baseline across the requested stage matrix.

    Inputs:
      - corpus_manifest: dict fixture manifest to iterate.
      - root: Path-like repository root used to resolve fixture paths.
      - stages: list[str] benchmark stages requested by the harness.
      - context: dict run metadata, callbacks, and row-construction dependencies.
    Outputs:
      - list[dict] audit rows for the typed-AST baseline.
    Side Effects:
      - Reads source fixtures from disk.
      - Builds AST-dump and reconstructed-source views.
      - Calls the benchmark evaluation callback for the reconstruction stage.
    Assumptions:
      - The typed-AST baseline participates meaningfully in `source_to_h` and `h_to_python` only.
    Failure Modes:
      - Propagates AST parse failures or evaluation callback failures.
    """
    rows = []
    for entry in corpus_manifest["fixtures"]:
        source_text = (root / entry["path"]).read_text(encoding="utf-8")
        case_name = case_name_from_artifact_id(entry["id"])
        baseline_text = representation_text(source_text)
        baseline_token_count = token_count(baseline_text)
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
                            "token_count": baseline_token_count,
                            "source_token_count": source_token_total,
                            "edit_distance": token_edit_distance(source_text, baseline_text),
                            "LCR": round(baseline_token_count / max(source_token_total, 1), 4),
                            "GR": 1.0,
                            "SE": semantic_explicitness(baseline_text),
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
                rebuilt_text = reconstructed_text(source_text)
                compile_pass, test_pass = context["evaluate_case"](case_name, rebuilt_text)
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
                            "token_count": token_count(rebuilt_text),
                            "source_token_count": source_token_total,
                            "edit_distance": token_edit_distance(source_text, rebuilt_text),
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
            # Keep the downstream aggregation shape stable by emitting skips for
            # stages that do not have a typed-AST analogue.
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
