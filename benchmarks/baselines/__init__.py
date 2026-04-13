"""File: benchmarks/baselines/__init__.py
Purpose: Resolve a requested benchmark baseline name to the corresponding adapter implementation.
Role in system: This module is the dispatch layer between benchmark orchestration code and individual baseline runners.
Key dependencies: the source, typed-AST, and normalized baseline packages plus benchmark_audit_common.resolve_baseline_name.
Side effects: None beyond delegating to the selected baseline runner.
"""
from __future__ import annotations

from .normalized import BASELINE_NAME as NORMALIZED_BASELINE_NAME, run as run_normalized
from .source import BASELINE_NAME as SOURCE_BASELINE_NAME, run as run_source
from .typed_ast import BASELINE_NAME as TYPED_AST_BASELINE_NAME, run as run_typed_ast
from benchmark_audit_common import resolve_baseline_name


BASELINE_ADAPTERS = {
    SOURCE_BASELINE_NAME: run_source,
    TYPED_AST_BASELINE_NAME: run_typed_ast,
    NORMALIZED_BASELINE_NAME: run_normalized,
}


def run_baseline(baseline_name: str, corpus_manifest: dict, **kwargs):
    """Purpose: Normalize a baseline label and dispatch to the matching benchmark adapter.

    Inputs:
      - baseline_name: str user-facing or manifest-sourced baseline label.
      - corpus_manifest: dict corpus manifest passed through to the baseline runner.
      - kwargs: per-run context forwarded unchanged to the selected adapter.
    Outputs:
      - Baseline-specific list of audit rows.
    Side Effects:
      - None in this wrapper; delegated runners perform file reads and row construction.
    Assumptions:
      - Baseline aliases must collapse to one canonical display name before dispatch so reports stay comparable.
    Failure Modes:
      - Raises KeyError when the baseline name cannot be resolved.
    """
    resolved = resolve_baseline_name(baseline_name)
    return BASELINE_ADAPTERS[resolved](corpus_manifest=corpus_manifest, **kwargs)
