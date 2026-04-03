"""Shared benchmark audit helpers for reproducible, claim-bounded reporting.

The utilities here normalize metric computation and manifest splitting so Track
A/B reports compare SCIR and baselines on the same contract surface. These
helpers are part of benchmark governance because downstream scripts rely on them
to keep descriptive, evaluative, and claim-grade evidence separated.
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
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_json_hash(payload: Any) -> str:
    return f"sha256:{hashlib.sha256(canonical_json_bytes(payload)).hexdigest()}"


def file_sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def environment_snapshot(root: Path) -> dict[str, str]:
    return {
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "cwd": str(root),
    }


def build_reproducibility_block(command: str, *, root: Path, seed: int = 0, timestamp: str) -> dict[str, Any]:
    return {
        "command": command,
        "environment": environment_snapshot(root),
        "seed": seed,
        "timestamp": timestamp,
    }


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text)


def token_count(text: str) -> int:
    return len(tokenize(text))


def token_edit_distance(left_text: str, right_text: str) -> int:
    left = tokenize(left_text)
    right = tokenize(right_text)
    if not left:
        return len(right)
    if not right:
        return len(left)
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
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return None
    return round(sum(usable) / len(usable), 4)


def resolve_baseline_name(name: str) -> str:
    key = name.strip()
    if key in BASELINE_DISPLAY_NAMES:
        return BASELINE_DISPLAY_NAMES[key]
    lowered = key.lower()
    if lowered in BASELINE_DISPLAY_NAMES:
        return BASELINE_DISPLAY_NAMES[lowered]
    raise KeyError(name)


def row_metric_value(row: dict, metric_name: str) -> float | None:
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
    active_rows = [row for row in rows if row.get("status") != "skip"]
    metric_keys = metric_keys or {}
    return {
        metric_name: safe_average(
            [row_metric_value(row, metric_keys.get(metric_name, metric_name)) for row in active_rows]
        )
        for metric_name in COMPARISON_METRICS
    }


def metric_delta(current: float | None, baseline: float | None) -> float | None:
    if current is None or baseline is None:
        return None
    return round(current - baseline, 4)


def split_contract(manifest: dict) -> dict[str, Any]:
    """Extract only the split metadata that is allowed to govern contamination and reproducibility checks."""

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
    return artifact_id.rsplit(".", 1)[-1]


def slice_axis_value(entry: dict, stage: str, profile: str, axis: str) -> str:
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
    """Build the canonical per-slice audit row used for SCIR and baseline comparisons alike."""

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
    if value is None:
        return "n/a"
    return str(value)
