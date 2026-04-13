"""File: scripts/benchmark_audit_common.py
Purpose: Provide shared helpers for reproducible benchmark auditing, metric aggregation, and claim-bounded reporting.
Role in system: This module is the common benchmark governance surface imported by sweep, reproduction, dry-run, and baseline scripts.
Key dependencies: hashlib, json, platform, regex tokenization, and report-manifest conventions defined elsewhere in the repo.
Side effects: Reads fixture bytes for hashing and captures process-environment metadata for reproducibility records.
"""
from __future__ import annotations

import hashlib
import json
import platform
import re
import sys
from pathlib import Path
from typing import Any


PIPELINE_STAGES = [
    "source_to_h",
    "scir_h_validation",
    "h_to_l",
    "scir_l_validation",
    "h_to_python",
    "l_to_wasm",
]

COMPARISON_METRICS = [
    "LCR",
    "GR",
    "SE",
    "SCPR",
    "round_trip",
    "LCR_scirhc",
    "GR_scirhc",
    "SCPR_scirhc",
]
BASELINE_COMPARISON_METRIC_KEYS = {
    "LCR_scirhc": "LCR",
    "GR_scirhc": "GR",
    "SCPR_scirhc": "SCPR",
}
BENCHMARK_TOOL_VERSION = "scir-benchmark-audit-v1"
SCIR_SYSTEM_NAME = "scir"
SOURCE_BASELINE_NAME = "direct source"
TYPED_AST_BASELINE_NAME = "typed-AST"
NORMALIZED_BASELINE_NAME = "lightweight regularized core or s-expression"
BASELINE_DISPLAY_NAMES = {
    "source": SOURCE_BASELINE_NAME,
    "direct source": SOURCE_BASELINE_NAME,
    "typed_ast": TYPED_AST_BASELINE_NAME,
    "typed-ast": TYPED_AST_BASELINE_NAME,
    "typed ast": TYPED_AST_BASELINE_NAME,
    "typed-AST": TYPED_AST_BASELINE_NAME,
    "normalized": NORMALIZED_BASELINE_NAME,
    "regularized core": NORMALIZED_BASELINE_NAME,
    "lightweight regularized core or s-expression": NORMALIZED_BASELINE_NAME,
}
CLAIM_COMPARISON_TOLERANCES = {
    SOURCE_BASELINE_NAME: {
        "LCR": 0.10,
        "GR": -0.05,
        "SE": 0.0,
        "SCPR": -0.05,
        "round_trip": -0.05,
        "LCR_scirhc": 0.10,
        "GR_scirhc": -0.05,
        "SCPR_scirhc": -0.05,
    },
    TYPED_AST_BASELINE_NAME: {
        "LCR": 0.0,
        "GR": -0.05,
        "SE": None,
        "SCPR": -0.05,
        "round_trip": -0.05,
        "LCR_scirhc": 0.0,
        "GR_scirhc": -0.05,
        "SCPR_scirhc": -0.05,
    },
    NORMALIZED_BASELINE_NAME: {
        "LCR": 0.10,
        "GR": -0.05,
        "SE": 0.0,
        "SCPR": -0.05,
        "round_trip": -0.05,
        "LCR_scirhc": 0.10,
        "GR_scirhc": -0.05,
        "SCPR_scirhc": -0.05,
    },
}
TOKEN_PATTERN = re.compile(r"[A-Za-z_]+|\d+|[^\s]")


def canonical_json_bytes(payload: Any) -> bytes:
    """Purpose: Serialize JSON deterministically for hashing and lockfile comparisons.

    Inputs:
      - payload: Any JSON-serializable object.
    Outputs:
      - bytes UTF-8 canonical JSON encoding with sorted keys and no extra whitespace.
    Side Effects:
      - None.
    Assumptions:
      - Callers need byte-stable output across platforms for manifest and report integrity checks.
    Failure Modes:
      - Raises TypeError if payload is not JSON-serializable.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_json_hash(payload: Any) -> str:
    """Purpose: Compute the repository-standard SHA-256 digest for canonical JSON payloads.

    Inputs:
      - payload: Any JSON-serializable object.
    Outputs:
      - str `sha256:<hex>` digest over canonical_json_bytes(payload).
    Side Effects:
      - None.
    Assumptions:
      - Hash identity must be tied to canonicalized JSON rather than incidental formatting.
    Failure Modes:
      - Propagates serialization errors from canonical_json_bytes.
    """
    return f"sha256:{hashlib.sha256(canonical_json_bytes(payload)).hexdigest()}"


def file_sha256(path: Path) -> str:
    """Purpose: Hash tracked text fixtures in a way that survives Windows and Unix line-ending differences.

    Inputs:
      - path: Path to the fixture file being fingerprinted.
    Outputs:
      - str `sha256:<hex>` digest after CRLF normalization.
    Side Effects:
      - Reads file bytes from disk.
    Assumptions:
      - Benchmark fixture identity should not drift solely because a checkout rewrote line endings.
    Failure Modes:
      - Raises filesystem exceptions if the file cannot be read.
    """
    # Benchmark corpus fixtures are tracked as text and their manifest hashes are
    # line-ending-stable across Windows and Unix checkouts.
    return f"sha256:{hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()}"


def environment_snapshot(root: Path) -> dict[str, str]:
    """Purpose: Capture the minimal execution environment needed to reproduce a benchmark run.

    Inputs:
      - root: Path working directory used for the run.
    Outputs:
      - dict[str, str] environment metadata for audit records.
    Side Effects:
      - Reads interpreter and platform metadata from the current process.
    Assumptions:
      - Reproducibility reports only need lightweight environment facts, not a full process dump.
    Failure Modes:
      - None under normal runtime conditions.
    """
    return {
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": str(root),
    }


def build_reproducibility_block(command: str, *, root: Path, seed: int = 0, timestamp: str) -> dict[str, Any]:
    """Purpose: Package the reproducibility metadata carried on benchmark audit rows and reports.

    Inputs:
      - command: str user-facing command that generated the run.
      - root: Path repository root or working directory used by the run.
      - seed: int deterministic seed recorded for replay.
      - timestamp: str emission timestamp for the run artifact.
    Outputs:
      - dict[str, Any] reproducibility block suitable for report embedding.
    Side Effects:
      - Captures environment metadata through environment_snapshot.
    Assumptions:
      - Downstream reports require an explicit command, environment, seed, and timestamp tuple.
    Failure Modes:
      - None beyond environment_snapshot behavior.
    """
    return {
        "command": command,
        "environment": environment_snapshot(root),
        "seed": seed,
        "timestamp": timestamp,
    }


def tokenize(text: str) -> list[str]:
    """Purpose: Split text into stable comparison tokens for benchmark lexical metrics.

    Inputs:
      - text: str representation text to tokenize.
    Outputs:
      - list[str] regex-derived token sequence.
    Side Effects:
      - None.
    Assumptions:
      - The coarse token model is sufficient for repo-level comparison metrics and contamination checks.
    Failure Modes:
      - None.
    """
    return TOKEN_PATTERN.findall(text)


def token_count(text: str) -> int:
    """Purpose: Count benchmark tokens using the shared tokenization contract.

    Inputs:
      - text: str representation text to count.
    Outputs:
      - int number of tokens emitted by tokenize.
    Side Effects:
      - None.
    Assumptions:
      - All lexical count metrics must use the same tokenizer to stay comparable.
    Failure Modes:
      - None.
    """
    return len(tokenize(text))


def token_edit_distance(left_text: str, right_text: str) -> int:
    """Purpose: Measure token-level edit distance for representation and round-trip comparisons.

    Inputs:
      - left_text: str baseline token stream source.
      - right_text: str comparison token stream source.
    Outputs:
      - int Levenshtein distance over shared benchmark tokens.
    Side Effects:
      - None.
    Assumptions:
      - Token-level distance is a more stable comparison surface than raw character edits for these reports.
    Failure Modes:
      - None.
    """
    left = tokenize(left_text)
    right = tokenize(right_text)
    if not left:
        return len(right)
    if not right:
        return len(left)
    # Use dynamic programming so every caller shares the same deterministic edit
    # metric instead of open-coding slightly different token-diff behavior.
    previous = list(range(len(right) + 1))
    for left_index, left_token in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_token in enumerate(right, start=1):
            cost = 0 if left_token == right_token else 1
            current.append(
                min(
                    previous[right_index] + 1,
                    current[right_index - 1] + 1,
                    previous[right_index - 1] + cost,
                )
            )
        previous = current
    return previous[-1]


def safe_average(values: list[float | int | None]) -> float | None:
    """Purpose: Average optional numeric values while preserving `None` for fully missing data.

    Inputs:
      - values: list[float | int | None] metrics gathered from individual rows.
    Outputs:
      - float | None rounded average across present values, or None when nothing is usable.
    Side Effects:
      - None.
    Assumptions:
      - Missing metrics should not be treated as zero because that would distort benchmark summaries.
    Failure Modes:
      - None.
    """
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return None
    return round(sum(usable) / len(usable), 4)


def resolve_baseline_name(name: str) -> str:
    """Purpose: Normalize baseline aliases to the canonical display names used in reports.

    Inputs:
      - name: str baseline identifier or display alias from manifests or CLI inputs.
    Outputs:
      - str canonical display name for downstream report surfaces.
    Side Effects:
      - None.
    Assumptions:
      - Reports should not split the same baseline across multiple spellings.
    Failure Modes:
      - Raises KeyError when the alias is unknown.
    """
    key = name.strip()
    if key in BASELINE_DISPLAY_NAMES:
        return BASELINE_DISPLAY_NAMES[key]
    lowered = key.lower()
    if lowered in BASELINE_DISPLAY_NAMES:
        return BASELINE_DISPLAY_NAMES[lowered]
    raise KeyError(name)


def row_metric_value(row: dict, metric_name: str) -> float | None:
    """Purpose: Extract one metric from an audit row using the benchmark row contract.

    Inputs:
      - row: dict audit-row payload.
      - metric_name: str metric key to read from row["metrics"].
    Outputs:
      - float | None normalized numeric value, with booleans promoted to 1.0 or 0.0.
    Side Effects:
      - None.
    Assumptions:
      - Comparison summaries only aggregate numeric or boolean-valued metrics.
    Failure Modes:
      - Returns None for absent or non-numeric metric values.
    """
    metrics = row.get("metrics", {})
    value = metrics.get(metric_name)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return None


def aggregate_comparison_metrics(
    rows: list[dict],
    *,
    metric_keys: dict[str, str] | None = None,
) -> dict[str, float | None]:
    """Purpose: Produce the canonical aggregate metric bundle for a set of benchmark rows.

    Inputs:
      - rows: list[dict] audit rows for one SCIR or baseline slice.
      - metric_keys: dict[str, str] | None optional remapping from aggregate names to row metric keys.
    Outputs:
      - dict[str, float | None] averaged comparison metrics keyed by COMPARISON_METRICS.
    Side Effects:
      - None.
    Assumptions:
      - Rows with status `skip` should not affect aggregate metric comparisons.
    Failure Modes:
      - None; missing metrics surface as None in the aggregate output.
    """
    active_rows = [row for row in rows if row.get("status") != "skip"]
    metric_keys = metric_keys or {}
    return {
        metric_name: safe_average(
            [row_metric_value(row, metric_keys.get(metric_name, metric_name)) for row in active_rows]
        )
        for metric_name in COMPARISON_METRICS
    }


def metric_delta(current: float | None, baseline: float | None) -> float | None:
    """Purpose: Compute a rounded delta only when both sides of a comparison are present.

    Inputs:
      - current: float | None current-system aggregate metric.
      - baseline: float | None baseline aggregate metric.
    Outputs:
      - float | None rounded difference, or None when the comparison is incomplete.
    Side Effects:
      - None.
    Assumptions:
      - A missing metric should stay missing rather than be coerced into a numerical delta.
    Failure Modes:
      - None.
    """
    if current is None or baseline is None:
        return None
    return round(current - baseline, 4)


def split_contract(manifest: dict) -> dict[str, Any]:
    """Purpose: Extract the only manifest fields allowed to govern split-sensitive audit checks.

    Inputs:
      - manifest: dict benchmark manifest payload.
    Outputs:
      - dict[str, Any] split-contract surface, with a conservative default when the manifest omits it.
    Side Effects:
      - None.
    Assumptions:
      - Contamination and reproducibility logic must stay isolated from unrelated manifest metadata.
    Failure Modes:
      - Falls back to an all-test simulated contract when no explicit split contract is present.
    """

    # Default every fixture into the test split so legacy manifests remain
    # reproducible without silently inventing train or dev evidence.
    return manifest.get(
        "split_contract",
        {
            "mode": "simulated_no_training",
            "train": [],
            "dev": [],
            "test": [entry["id"] for entry in manifest.get("fixtures", [])],
        },
    )


def case_name_from_artifact_id(artifact_id: str) -> str:
    """Purpose: Recover the case name suffix from a namespaced artifact identifier.

    Inputs:
      - artifact_id: str artifact identifier containing a final case-name segment.
    Outputs:
      - str case name extracted from the suffix after the last dot.
    Side Effects:
      - None.
    Assumptions:
      - Artifact ids are dot-delimited and case names occupy the final segment.
    Failure Modes:
      - Returns the full string when no dot separator exists.
    """
    return artifact_id.rsplit(".", 1)[-1]


def slice_axis_value(entry: dict, stage: str, profile: str, axis: str) -> str:
    """Purpose: Resolve one audit slice axis using the row contract's fallback rules.

    Inputs:
      - entry: dict fixture or manifest entry backing the audit row.
      - stage: str pipeline stage for the row.
      - profile: str preservation profile for the row.
      - axis: str requested slice axis name.
    Outputs:
      - str normalized axis value.
    Side Effects:
      - None.
    Assumptions:
      - Unknown axes should degrade to entry metadata or `unknown` instead of failing the entire report build.
    Failure Modes:
      - None.
    """
    if axis == "pipeline_stage":
        return stage
    if axis == "profile":
        return profile
    if axis == "frontend":
        return entry.get("frontend", entry.get("language", "unknown"))
    if axis == "split":
        return entry.get("split", "test")
    return str(entry.get(axis, "unknown"))


def slice_id_for_row(entry: dict, stage: str, profile: str, slice_axes: list[str]) -> str:
    """Purpose: Build the stable slice identifier used to group comparable audit rows.

    Inputs:
      - entry: dict fixture or manifest entry.
      - stage: str pipeline stage for the row.
      - profile: str preservation profile for the row.
      - slice_axes: list[str] ordered axes that define grouping.
    Outputs:
      - str pipe-delimited slice identifier.
    Side Effects:
      - None.
    Assumptions:
      - Slice ids must be deterministic because downstream aggregation keys on them.
    Failure Modes:
      - None.
    """
    return "|".join(f"{axis}={slice_axis_value(entry, stage, profile, axis)}" for axis in slice_axes)


def build_audit_row(
    *,
    entry: dict,
    stage: str,
    run_id: str,
    commit_sha: str,
    spec_version: str,
    tool_version: str,
    baseline_name: str,
    corpus_manifest_hash: str,
    profile: str,
    status: str,
    diagnostic_codes: list[str],
    preservation_requested: str | None,
    preservation_observed: str | None,
    compile_pass: bool | None,
    test_pass: bool | None,
    duration_ms: int,
    metrics: dict[str, Any],
    slice_axes: list[str],
    reproducibility_block: dict[str, Any],
    preservation_expected: str | None = None,
    preservation_expectation_status: str = "not_applicable",
    preservation_downgrade_count: int = 0,
    boundary_annotation_count: int = 0,
    opaque_fraction: float | None = None,
    unsupported_fraction: float | None = None,
    unsupported_tags: list[str] | None = None,
) -> dict[str, Any]:
    """Purpose: Build the canonical audit row schema shared by SCIR and baseline benchmark outputs.

    Inputs:
      - entry: dict manifest entry for the evaluated fixture.
      - stage: str pipeline stage being recorded.
      - run_id: str logical benchmark run identifier.
      - commit_sha: str source revision captured for the run.
      - spec_version: str semantic or reporting contract version.
      - tool_version: str benchmark tool version recorded in the row.
      - baseline_name: str canonical baseline or system label for the row.
      - corpus_manifest_hash: str hash of the manifest governing the run.
      - profile: str active preservation profile for the row.
      - status: str row execution status.
      - diagnostic_codes: list[str] emitted diagnostics for the row.
      - preservation_requested: str | None requested preservation level.
      - preservation_observed: str | None observed preservation level.
      - compile_pass: bool | None compile result when applicable.
      - test_pass: bool | None test result when applicable.
      - duration_ms: int elapsed runtime for the row.
      - metrics: dict[str, Any] measured row metrics.
      - slice_axes: list[str] grouping axes used for rollups.
      - reproducibility_block: dict[str, Any] reproduction metadata bundle.
      - preservation_expected: str | None optional expected preservation level.
      - preservation_expectation_status: str expectation comparison status.
      - preservation_downgrade_count: int number of downgrades recorded for the row.
      - boundary_annotation_count: int number of explicit boundary annotations recorded for the row.
      - opaque_fraction: float | None fraction of the row explained by opaque boundaries.
      - unsupported_fraction: float | None fraction of the row outside admitted support.
      - unsupported_tags: list[str] | None explicit unsupported-case labels.
    Outputs:
      - dict[str, Any] canonical audit row ready for JSON emission.
    Side Effects:
      - None.
    Assumptions:
      - Missing opaque or unsupported fractions need deterministic defaults so aggregation does not guess.
    Failure Modes:
      - None; callers are responsible for schema validation after row construction.
    """

    unsupported_tags = list(unsupported_tags or [])
    if opaque_fraction is None:
        opaque_fraction = 0.0
    if unsupported_fraction is None:
        unsupported_fraction = 1.0 if unsupported_tags else 0.0
    return {
        "run_id": run_id,
        "commit_sha": commit_sha,
        "spec_version": spec_version,
        "tool_version": tool_version,
        "baseline_name": baseline_name,
        "corpus_manifest_hash": corpus_manifest_hash,
        "artifact_id": entry["id"],
        "frontend": entry.get("frontend", entry.get("language", "unknown")),
        "tier": entry["tier"],
        "split": entry.get("split", "test"),
        "origin": entry.get("origin", "unknown"),
        "sample_class": entry.get("sample_class", "unknown"),
        "profile": profile,
        "construct_family": entry.get("construct_family", "unknown"),
        "fixture_set": entry.get("fixture_set", "unknown"),
        "slice_id": slice_id_for_row(entry, stage, profile, slice_axes),
        "stage": stage,
        "status": status,
        "diagnostic_codes": list(diagnostic_codes),
        "metrics": metrics,
        "preservation_requested": preservation_requested,
        "preservation_expected": preservation_expected,
        "preservation_observed": preservation_observed,
        "preservation_expectation_status": preservation_expectation_status,
        "preservation_downgrade_count": preservation_downgrade_count,
        "boundary_annotation_count": boundary_annotation_count,
        "opaque_fraction": opaque_fraction,
        "unsupported_fraction": unsupported_fraction,
        "unsupported_tags": unsupported_tags,
        "compile_pass": compile_pass,
        "test_pass": test_pass,
        "duration_ms": duration_ms,
        "reproducibility_block": reproducibility_block,
    }


def markdown_bullet_value(value: float | int | bool | None) -> str:
    """Purpose: Render scalar summary values into markdown-safe bullet text.

    Inputs:
      - value: float | int | bool | None summary value to print.
    Outputs:
      - str markdown-friendly scalar, or `n/a` when the value is absent.
    Side Effects:
      - None.
    Assumptions:
      - Summary markdown should use a textual missing-value marker instead of JSON null.
    Failure Modes:
      - None.
    """
    if value is None:
        return "n/a"
    return str(value)
