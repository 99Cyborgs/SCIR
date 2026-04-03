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
    resolved = resolve_baseline_name(baseline_name)
    return BASELINE_ADAPTERS[resolved](corpus_manifest=corpus_manifest, **kwargs)
