#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.baselines import run_baseline
from benchmark_audit_common import (
    BASELINE_COMPARISON_METRIC_KEYS,
    BENCHMARK_TOOL_VERSION,
    CLAIM_COMPARISON_TOLERANCES,
    COMPARISON_METRICS,
    SCIR_SYSTEM_NAME,
    SOURCE_BASELINE_NAME,
    TYPED_AST_BASELINE_NAME,
    NORMALIZED_BASELINE_NAME,
    aggregate_comparison_metrics,
    build_audit_row,
    build_reproducibility_block,
    canonical_json_hash,
    case_name_from_artifact_id,
    metric_delta as comparison_metric_delta,
    slice_id_for_row as common_slice_id_for_row,
    token_count,
    token_edit_distance,
    tokenize,
)
from scir_bootstrap_pipeline import (
    evaluate_reconstruction,
    load_import_artifacts,
    preservation_expectation_status,
    run_pipeline,
)
from scir_python_bootstrap import SPEC_VERSION
from validate_repo_contracts import collect_instance_validation_errors


SWEEP_RESULT_SCHEMA = "schemas/sweep_result.schema.json"
SWEEP_SUMMARY_SCHEMA = "schemas/sweep_summary.schema.json"
REGRESSION_SUMMARY_SCHEMA = "schemas/regression_summary.schema.json"
COMPARISON_SUMMARY_SCHEMA = "schemas/comparison_summary.schema.json"
CONTAMINATION_REPORT_SCHEMA = "schemas/contamination_report.schema.json"
SWEEP_MANIFEST_SCHEMA = "schemas/sweep_manifest.schema.json"
CORPUS_MANIFEST_SCHEMA = "schemas/corpus_manifest.schema.json"
PRESERVATION_FAILURE_STATUSES = {
    "missing_observation",
    "overclaim",
    "status_mismatch",
    "unexplained_downgrade",
}
SCIR_MARKERS = ["await", "return", "if", "var ", "set ", ".", "opaque"]


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(root: pathlib.Path, relative_path: str):
    return load_json(root / relative_path)


def schema_failures(root: pathlib.Path, payload, schema_rel: str, label: str):
    schema = load_schema(root, schema_rel)
    return [
        f"{label} {location}: {message}"
        for location, message in collect_instance_validation_errors(payload, schema)
    ]


def git_commit_sha(root: pathlib.Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def manifest_hash(root: pathlib.Path, manifest_rel: str) -> str:
    return canonical_json_hash(load_json(root / manifest_rel))


def scir_semantic_explicitness(text: str) -> float:
    total = max(token_count(text), 1)
    return round(sum(text.count(marker) for marker in SCIR_MARKERS) / total, 4)


def primary_profile(entry: dict, *, stage: str, observed_profile: str | None = None) -> str:
    if observed_profile:
        return observed_profile
    profiles = entry.get("profiles", [])
    if profiles:
        return profiles[0]
    if stage == "l_to_wasm":
        return "P"
    return "R"


def opaque_fraction_for_case(root: pathlib.Path, case_name: str) -> float:
    feature_report = load_import_artifacts(root, case_name)["feature_tier_report.json"]
    items = feature_report["items"]
    if not items:
        return 0.0
    opaque_items = sum(1 for item in items if item.get("tier") == "C")
    return round(opaque_items / len(items), 4)


def output_dir_for_run(root: pathlib.Path, commit_sha: str, timestamp: dt.datetime) -> pathlib.Path:
    run_label = f"{commit_sha[:12]}-{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    return root / "artifacts" / "sweeps" / run_label


def compare_payload_path(compare_path: pathlib.Path | None) -> pathlib.Path | None:
    if compare_path is None:
        return None
    if compare_path.is_file():
        return compare_path
    candidate = compare_path / "sweep_result.json"
    if candidate.exists():
        return candidate
    return None


def slice_id_for_row(entry: dict, stage: str, profile: str, slice_axes: list[str]) -> str:
    return common_slice_id_for_row(entry, stage, profile, slice_axes)


def stage_profile(entry: dict, case_name: str, stage: str, outputs: dict) -> str:
    if stage == "source_to_h":
        return outputs["source_to_h_reports"][case_name]["profile"]
    if stage == "scir_h_validation":
        return outputs["source_to_h_reports"][case_name]["profile"]
    if stage == "h_to_l":
        return outputs["translation_reports"][case_name]["profile"]
    if stage == "scir_l_validation":
        return outputs["translation_reports"][case_name]["profile"]
    if stage == "h_to_python":
        return outputs["reconstruction_preservation_reports"][case_name]["profile"]
    if stage == "l_to_wasm":
        return outputs["wasm_reports"][case_name]["preservation_report"]["profile"]
    return primary_profile(entry, stage=stage)


def scir_stage_metrics(
    *,
    root: pathlib.Path,
    entry: dict,
    case_name: str,
    stage: str,
    status: str,
    compile_pass,
    test_pass,
    outputs: dict,
):
    source_text = (root / entry["path"]).read_text(encoding="utf-8")
    source_tokens = token_count(source_text)
    scirhc_report = outputs.get("scir_hc_reports", {}).get(case_name, {})
    scirhc_text = scirhc_report.get("text")
    scirhc_valid = scirhc_report.get("validation_report", {}).get("status") == "pass"
    gr_scirhc = 1.0 if status == "pass" and scirhc_valid else 0.0
    if stage == "source_to_h":
        scirh_text = load_import_artifacts(root, case_name)["expected.scirh"]
        scirh_tokens = token_count(scirh_text)
        scirhc_tokens = token_count(scirhc_text) if isinstance(scirhc_text, str) else None
        return {
            "token_count": scirh_tokens,
            "token_count_scirhc": scirhc_tokens,
            "source_token_count": source_tokens,
            "edit_distance": token_edit_distance(source_text, scirh_text),
            "edit_distance_scirhc": (
                token_edit_distance(source_text, scirhc_text) if isinstance(scirhc_text, str) else None
            ),
            "LCR": round(scirh_tokens / max(source_tokens, 1), 4),
            "LCR_scirhc": round(scirhc_tokens / max(source_tokens, 1), 4) if scirhc_tokens is not None else None,
            "GR": 1.0 if status == "pass" else 0.0,
            "GR_scirhc": gr_scirhc,
            "SE": scir_semantic_explicitness(scirh_text),
            "SCPR": None,
            "SCPR_scirhc": None,
            "round_trip": None,
        }
    if stage == "h_to_python":
        reconstructed_text = outputs["reconstruction_reports"].get(case_name, {}).get("source")
        token_total = token_count(reconstructed_text) if isinstance(reconstructed_text, str) else None
        edit_distance = token_edit_distance(source_text, reconstructed_text) if isinstance(reconstructed_text, str) else None
        compile_score = None if compile_pass is None else (1.0 if compile_pass else 0.0)
        round_trip_score = None if compile_pass is None else (1.0 if compile_pass and test_pass else 0.0)
        return {
            "token_count": token_total,
            "source_token_count": source_tokens,
            "edit_distance": edit_distance,
            "LCR": None,
            "GR": 1.0 if status == "pass" else 0.0,
            "GR_scirhc": gr_scirhc,
            "SE": None,
            "SCPR": compile_score,
            "SCPR_scirhc": None if compile_score is None else (compile_score if scirhc_valid else 0.0),
            "round_trip": round_trip_score,
        }
    return {
        "token_count": None,
        "source_token_count": source_tokens,
        "edit_distance": None,
        "LCR": None,
        "GR": 1.0 if status == "pass" else 0.0,
        "GR_scirhc": gr_scirhc,
        "SE": None,
        "SCPR": None,
        "SCPR_scirhc": None,
        "round_trip": None,
    }


def build_stage_row(
    *,
    root: pathlib.Path,
    entry: dict,
    case_name: str,
    stage: str,
    run_id: str,
    commit_sha: str,
    corpus_manifest_hash: str,
    profile: str,
    observation: dict,
    expected_stage_behavior: dict | None,
    compile_pass,
    test_pass,
    opaque_fraction_value: float,
    duration_ms: int,
    slice_axes: list[str],
    reproducibility_block: dict,
    outputs: dict,
):
    preservation_expected = None
    if isinstance(expected_stage_behavior, dict):
        preservation_expected = expected_stage_behavior.get("preservation_level")
    expectation_status = preservation_expectation_status(observation, expected_stage_behavior)
    unsupported_tags = list(entry.get("unsupported_tags", []))
    return build_audit_row(
        entry=entry,
        stage=stage,
        run_id=run_id,
        commit_sha=commit_sha,
        spec_version=SPEC_VERSION,
        tool_version=BENCHMARK_TOOL_VERSION,
        baseline_name=SCIR_SYSTEM_NAME,
        corpus_manifest_hash=corpus_manifest_hash,
        profile=profile,
        status=observation["status"],
        diagnostic_codes=list(observation["diagnostic_codes"]),
        preservation_requested=entry["expected_preservation_ceiling"],
        preservation_expected=preservation_expected,
        preservation_observed=observation["preservation_level"],
        preservation_expectation_status=expectation_status,
        preservation_downgrade_count=observation["downgrade_count"],
        boundary_annotation_count=observation["boundary_annotation_count"],
        compile_pass=compile_pass,
        test_pass=test_pass,
        duration_ms=duration_ms,
        metrics=scir_stage_metrics(
            root=root,
            entry=entry,
            case_name=case_name,
            stage=stage,
            status=observation["status"],
            compile_pass=compile_pass,
            test_pass=test_pass,
            outputs=outputs,
        ),
        slice_axes=slice_axes,
        reproducibility_block=reproducibility_block,
        opaque_fraction=opaque_fraction_value,
        unsupported_tags=unsupported_tags,
    )


def stage_rows_for_entry(
    root: pathlib.Path,
    entry: dict,
    outputs: dict,
    sweep_manifest: dict,
    run_id: str,
    commit_sha: str,
    corpus_manifest_hash: str,
    reproducibility_block: dict,
):
    case_name = case_name_from_artifact_id(entry["id"])
    stage_observations = outputs["stage_observations"][case_name]
    stages = [
        stage
        for stage in sweep_manifest["stages"]
        if stage in entry.get("pipeline_stages", [])
    ]
    rows = []
    opaque_fraction_value = opaque_fraction_for_case(root, case_name)
    slice_axes = sweep_manifest["slice_axes"]
    reconstruction_report = outputs["reconstruction_reports"].get(case_name, {}).get("report", {})
    expected_stage_behavior = entry.get("expected_preservation_stage_behavior", {})

    for stage in stages:
        start = time.perf_counter()
        observation = stage_observations[stage]
        compile_pass = None
        test_pass = None
        if stage == "h_to_python":
            compile_pass = reconstruction_report.get("compile_pass")
            test_pass = reconstruction_report.get("test_pass")
        duration_ms = int((time.perf_counter() - start) * 1000)
        rows.append(
            build_stage_row(
                root=root,
                entry=entry,
                case_name=case_name,
                stage=stage,
                run_id=run_id,
                commit_sha=commit_sha,
                corpus_manifest_hash=corpus_manifest_hash,
                profile=stage_profile(entry, case_name, stage, outputs),
                observation=observation,
                expected_stage_behavior=expected_stage_behavior.get(stage),
                compile_pass=compile_pass,
                test_pass=test_pass,
                opaque_fraction_value=opaque_fraction_value,
                duration_ms=duration_ms,
                slice_axes=slice_axes,
                reproducibility_block=reproducibility_block,
                outputs=outputs,
            )
        )
    return rows


def baseline_stage_profile(entry: dict, stage: str) -> str:
    profiles = entry.get("profiles", [])
    if stage == "h_to_python" and "R" in profiles:
        return "R"
    if stage == "l_to_wasm" and "P" in profiles:
        return "P"
    return primary_profile(entry, stage=stage)


def baseline_rows_for_manifest(
    *,
    root: pathlib.Path,
    corpus_manifest: dict,
    sweep_manifest: dict,
    run_id: str,
    commit_sha: str,
    corpus_manifest_hash: str,
    reproducibility_block: dict,
):
    context = {
        "run_id": run_id,
        "commit_sha": commit_sha,
        "spec_version": SPEC_VERSION,
        "tool_version": BENCHMARK_TOOL_VERSION,
        "corpus_manifest_hash": corpus_manifest_hash,
        "slice_axes": sweep_manifest["slice_axes"],
        "reproducibility_block": reproducibility_block,
        "evaluate_case": evaluate_reconstruction,
        "profile_for_stage": baseline_stage_profile,
    }
    rows = []
    for baseline_name in [SOURCE_BASELINE_NAME, TYPED_AST_BASELINE_NAME, NORMALIZED_BASELINE_NAME]:
        rows.extend(
            run_baseline(
                baseline_name,
                corpus_manifest,
                root=root,
                stages=sweep_manifest["stages"],
                context=context,
            )
        )
    return rows


def fixture_text(root: pathlib.Path, entry: dict) -> str:
    return (root / entry["path"]).read_text(encoding="utf-8")


def near_duplicate_ratio(left_text: str, right_text: str) -> float:
    left = " ".join(token_count_token for token_count_token in fixture_tokens(left_text))
    right = " ".join(token_count_token for token_count_token in fixture_tokens(right_text))
    return round(difflib.SequenceMatcher(None, left, right).ratio(), 4)


def fixture_tokens(text: str) -> list[str]:
    return [token.lower() for token in tokenize(text)]


def build_contamination_report(
    *,
    root: pathlib.Path,
    manifest_rel: str,
    corpus_manifest: dict,
    corpus_manifest_hash: str,
    run_id: str,
    generated_at: str,
):
    duplicates = []
    near_duplicates = []
    leakage_flags = []
    fixtures = corpus_manifest["fixtures"]
    for index, left_entry in enumerate(fixtures):
        left_split = left_entry.get("split", "test")
        left_text = fixture_text(root, left_entry)
        left_hash = left_entry["hash"]
        for right_entry in fixtures[index + 1 :]:
            right_split = right_entry.get("split", "test")
            if left_split == right_split:
                continue
            if left_hash == right_entry["hash"]:
                duplicates.append(
                    {
                        "left_artifact_id": left_entry["id"],
                        "left_split": left_split,
                        "right_artifact_id": right_entry["id"],
                        "right_split": right_split,
                        "shared_hash": left_hash,
                    }
                )
                continue
            ratio = near_duplicate_ratio(left_text, fixture_text(root, right_entry))
            if ratio >= 0.9:
                near_duplicates.append(
                    {
                        "left_artifact_id": left_entry["id"],
                        "left_split": left_split,
                        "right_artifact_id": right_entry["id"],
                        "right_split": right_split,
                        "similarity": ratio,
                    }
                )
    if duplicates:
        leakage_flags.append("duplicate fixtures exist across train/dev/test splits")
    if near_duplicates:
        leakage_flags.append("near-duplicate fixtures exist across train/dev/test splits")
    split_mode = corpus_manifest.get("split_contract", {}).get("mode", "simulated_no_training")
    return {
        "run_id": run_id,
        "generated_at": generated_at,
        "corpus_manifest": manifest_rel,
        "corpus_manifest_hash": corpus_manifest_hash,
        "split_mode": split_mode,
        "duplicates": duplicates,
        "near_duplicates": near_duplicates,
        "leakage_flags": leakage_flags,
    }


def cluster_rows(rows: list[dict]):
    counts: dict[str, int] = {}
    for row in rows:
        if row["status"] not in {"fail", "warn"}:
            continue
        row_codes = row["diagnostic_codes"] or ["NO_CODE"]
        for code in row_codes:
            counts[code] = counts.get(code, 0) + 1
    return [{"code": code, "count": counts[code]} for code in sorted(counts)]


def safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def status_counts(rows: list[dict]) -> dict[str, int]:
    counts = {"pass": 0, "warn": 0, "fail": 0, "skip": 0}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return counts


def diagnostic_frequency(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        for code in row["diagnostic_codes"]:
            counts[code] = counts.get(code, 0) + 1
    return counts


def metric_snapshot(rows: list[dict]) -> dict:
    active_rows = [row for row in rows if row["status"] != "skip"]
    preservation_rows = [row for row in rows if row["preservation_observed"] is not None]
    opaque_values = [row["opaque_fraction"] for row in rows if row["opaque_fraction"] is not None]
    preservation_errors = [
        row
        for row in preservation_rows
        if row["preservation_expectation_status"] in PRESERVATION_FAILURE_STATUSES
    ]
    downgrade_rows = [row for row in preservation_rows if row["preservation_downgrade_count"] > 0]
    return {
        "validator_pass_rate": safe_ratio(sum(1 for row in active_rows if row["status"] == "pass"), len(active_rows)),
        "preservation_downgrade_rate": safe_ratio(len(downgrade_rows), len(preservation_rows)),
        "preservation_error_rate": safe_ratio(len(preservation_errors), len(preservation_rows)),
        "opaque_fraction": round(sum(opaque_values) / len(opaque_values), 4) if opaque_values else 0.0,
        "diagnostic_frequency_by_code": diagnostic_frequency(rows),
    }


def metric_delta(metric: str, baseline, current, *, key: str | None = None):
    payload = {
        "metric": metric,
        "baseline": baseline,
        "current": current,
    }
    if key is not None:
        payload["key"] = key
    if isinstance(baseline, (int, float)) and isinstance(current, (int, float)):
        payload["delta"] = round(current - baseline, 4)
    return payload


def compare_with_previous(current_payload: dict, previous_payload: dict):
    current_rows = current_payload["rows"]
    previous_rows = previous_payload.get("rows", [])
    previous_map = {(row["artifact_id"], row["stage"]): row for row in previous_rows}
    added_failures = []
    removed_failures = []
    for row in current_rows:
        key = (row["artifact_id"], row["stage"])
        previous = previous_map.get(key)
        if previous is None:
            continue
        if previous["status"] != "fail" and row["status"] == "fail":
            added_failures.append(
                {
                    "artifact_id": row["artifact_id"],
                    "stage": row["stage"],
                    "from_status": previous["status"],
                    "to_status": row["status"],
                }
            )
        if previous["status"] == "fail" and row["status"] != "fail":
            removed_failures.append(
                {
                    "artifact_id": row["artifact_id"],
                    "stage": row["stage"],
                    "from_status": previous["status"],
                    "to_status": row["status"],
                }
            )

    current_metrics = metric_snapshot(current_rows)
    previous_metrics = metric_snapshot(previous_rows)
    worsened_metrics = []
    improved_metrics = []
    for metric_name in ["validator_pass_rate", "preservation_downgrade_rate", "preservation_error_rate", "opaque_fraction"]:
        baseline = previous_metrics[metric_name]
        current = current_metrics[metric_name]
        delta = metric_delta(metric_name, baseline, current)
        if metric_name == "validator_pass_rate":
            if current < baseline:
                worsened_metrics.append(delta)
            elif current > baseline:
                improved_metrics.append(delta)
        else:
            if current > baseline:
                worsened_metrics.append(delta)
            elif current < baseline:
                improved_metrics.append(delta)

    unexpected_diagnostic_codes = []
    all_codes = sorted(
        set(previous_metrics["diagnostic_frequency_by_code"]) | set(current_metrics["diagnostic_frequency_by_code"])
    )
    for code in all_codes:
        baseline_count = previous_metrics["diagnostic_frequency_by_code"].get(code, 0)
        current_count = current_metrics["diagnostic_frequency_by_code"].get(code, 0)
        delta = metric_delta("diagnostic_frequency_by_code", baseline_count, current_count, key=code)
        if current_count > baseline_count:
            worsened_metrics.append(delta)
        elif current_count < baseline_count:
            improved_metrics.append(delta)
        if baseline_count == 0 and current_count > 0:
            unexpected_diagnostic_codes.append(code)

    return {
        "sweep_id": current_payload["sweep_id"],
        "run_id": current_payload["run_id"],
        "baseline_run_id": previous_payload.get("run_id", "unknown"),
        "baseline_commit_sha": previous_payload.get("commit_sha", "unknown"),
        "generated_at": current_payload["generated_at"],
        "added_failures": added_failures,
        "removed_failures": removed_failures,
        "worsened_metrics": worsened_metrics,
        "improved_metrics": improved_metrics,
        "unexpected_diagnostic_codes": unexpected_diagnostic_codes,
    }


def avg(rows: list[dict], key: str) -> float:
    values = [row[key] for row in rows if row.get(key) is not None]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def slice_score(rows: list[dict]) -> float:
    snapshot = metric_snapshot(rows)
    preservation_rows = [row for row in rows if row["preservation_observed"] is not None]
    preservation_correctness_rate = safe_ratio(
        sum(1 for row in preservation_rows if row["preservation_expectation_status"] not in PRESERVATION_FAILURE_STATUSES),
        len(preservation_rows),
    )
    unsupported_fraction = avg(rows, "unsupported_fraction")
    score = (
        0.4 * snapshot["validator_pass_rate"]
        + 0.3 * preservation_correctness_rate
        + 0.15 * (1.0 - snapshot["opaque_fraction"])
        + 0.15 * (1.0 - unsupported_fraction)
    )
    return round(score * 100.0, 2)


def summarize_group(rows: list[dict], *, name_key: str, name_value: str):
    counts = status_counts(rows)
    preservation_rows = [row for row in rows if row["preservation_observed"] is not None]
    return {
        name_key: name_value,
        "row_count": len(rows),
        "status_counts": counts,
        "validator_pass_rate": safe_ratio(counts["pass"], len([row for row in rows if row["status"] != "skip"])),
        "preservation_correctness_rate": safe_ratio(
            sum(1 for row in preservation_rows if row["preservation_expectation_status"] not in PRESERVATION_FAILURE_STATUSES),
            len(preservation_rows),
        ),
        "avg_opaque_fraction": avg(rows, "opaque_fraction"),
        "avg_unsupported_fraction": avg(rows, "unsupported_fraction"),
        "avg_duration_ms": avg(rows, "duration_ms"),
        "slice_score": slice_score(rows),
    }


def build_preservation_stage_breakdown(rows: list[dict]):
    breakdown = {}
    for row in rows:
        breakdown.setdefault(row["artifact_id"], {})
        breakdown[row["artifact_id"]][row["stage"]] = {
            "status": row["status"],
            "preservation_level": row["preservation_observed"],
            "expected_preservation_level": row["preservation_expected"],
            "expectation_status": row["preservation_expectation_status"],
        }
    return [{"artifact_id": artifact_id, "stages": stages} for artifact_id, stages in sorted(breakdown.items())]


def build_summary(result_payload: dict, regression_summary: dict | None = None) -> dict:
    rows = result_payload["rows"]
    stage_summary = [
        summarize_group(stage_rows, name_key="stage", name_value=stage)
        for stage, stage_rows in sorted(
            (
                (stage, [row for row in rows if row["stage"] == stage])
                for stage in sorted({row["stage"] for row in rows})
            ),
            key=lambda item: item[0],
        )
    ]
    construct_family_summary = [
        summarize_group(group_rows, name_key="construct_family", name_value=construct_family)
        for construct_family, group_rows in sorted(
            (
                (construct_family, [row for row in rows if row["construct_family"] == construct_family])
                for construct_family in sorted({row["construct_family"] for row in rows})
            ),
            key=lambda item: item[0],
        )
    ]
    diagnostic_code_summary = [{"code": code, "count": count} for code, count in sorted(diagnostic_frequency(rows).items())]
    slice_summary = [
        summarize_group(group_rows, name_key="slice_id", name_value=slice_id)
        for slice_id, group_rows in sorted(
            (
                (slice_id, [row for row in rows if row["slice_id"] == slice_id])
                for slice_id in sorted({row["slice_id"] for row in rows})
            ),
            key=lambda item: item[0],
        )
    ]
    failure_dense_slice = max(
        slice_summary,
        key=lambda item: (
            safe_ratio(item["status_counts"]["fail"] + item["status_counts"]["warn"], item["row_count"]),
            item["row_count"],
        ),
    )
    stable_slice = max(
        slice_summary,
        key=lambda item: (item["slice_score"], item["validator_pass_rate"], -item["avg_opaque_fraction"]),
    )
    fastest_improving_slice = None
    if regression_summary is not None:
        baseline_rows = result_payload.get("previous_rows", [])
        baseline_slice_scores = {
            item["slice_id"]: item["slice_score"]
            for item in [
                summarize_group(group_rows, name_key="slice_id", name_value=slice_id)
                for slice_id, group_rows in sorted(
                    (
                        (slice_id, [row for row in baseline_rows if row["slice_id"] == slice_id])
                        for slice_id in sorted({row["slice_id"] for row in baseline_rows})
                    ),
                    key=lambda item: item[0],
                )
            ]
        }
        improvements = []
        for item in slice_summary:
            baseline_score = baseline_slice_scores.get(item["slice_id"])
            if baseline_score is None:
                continue
            improvements.append(
                {
                    "slice_id": item["slice_id"],
                    "baseline_slice_score": baseline_score,
                    "current_slice_score": item["slice_score"],
                    "delta": round(item["slice_score"] - baseline_score, 2),
                }
            )
        if improvements:
            fastest_improving_slice = max(improvements, key=lambda item: item["delta"])

    return {
        "sweep_id": result_payload["sweep_id"],
        "run_id": result_payload["run_id"],
        "commit_sha": result_payload["commit_sha"],
        "spec_version": result_payload["spec_version"],
        "tool_version": result_payload["tool_version"],
        "corpus_id": result_payload["corpus_id"],
        "corpus_manifest_hash": result_payload["corpus_manifest_hash"],
        "generated_at": result_payload["generated_at"],
        "row_count": len(rows),
        "stage_summary": stage_summary,
        "construct_family_summary": construct_family_summary,
        "diagnostic_code_summary": diagnostic_code_summary,
        "slice_summary": slice_summary,
        "slice_rankings": {
            "most_stable_slice": {
                "slice_id": stable_slice["slice_id"],
                "slice_score": stable_slice["slice_score"],
            },
            "most_failure_dense_slice": {
                "slice_id": failure_dense_slice["slice_id"],
                "failure_density": safe_ratio(
                    failure_dense_slice["status_counts"]["fail"] + failure_dense_slice["status_counts"]["warn"],
                    failure_dense_slice["row_count"],
                ),
            },
            "fastest_improving_slice": fastest_improving_slice,
        },
        "preservation_stage_breakdown": build_preservation_stage_breakdown(rows),
    }


def comparison_key_for_baseline(baseline_name: str) -> str:
    if baseline_name == SOURCE_BASELINE_NAME:
        return "delta_vs_source"
    if baseline_name == TYPED_AST_BASELINE_NAME:
        return "delta_vs_ast"
    if baseline_name == NORMALIZED_BASELINE_NAME:
        return "delta_vs_normalized"
    raise KeyError(baseline_name)


def comparison_failure(metric_name: str, delta: float, tolerance: float | None) -> bool:
    if tolerance is None:
        return False
    if metric_name.startswith("LCR"):
        return delta > tolerance
    return delta < tolerance


def build_comparison_summary(result_payload: dict, baseline_rows: list[dict], contamination_report: dict) -> dict:
    scir_rows = result_payload["rows"]
    slice_ids = sorted({row["slice_id"] for row in scir_rows})
    baselines = [SOURCE_BASELINE_NAME, TYPED_AST_BASELINE_NAME, NORMALIZED_BASELINE_NAME]
    slice_summaries = []
    tolerance_failures = []
    for slice_id in slice_ids:
        scir_slice_rows = [row for row in scir_rows if row["slice_id"] == slice_id]
        scir_metrics = aggregate_comparison_metrics(scir_slice_rows)
        slice_payload = {
            "slice_id": slice_id,
            "scir_metrics": scir_metrics,
        }
        for baseline_name in baselines:
            baseline_slice_rows = [
                row
                for row in baseline_rows
                if row["baseline_name"] == baseline_name and row["slice_id"] == slice_id
            ]
            baseline_metrics = aggregate_comparison_metrics(
                baseline_slice_rows,
                metric_keys=BASELINE_COMPARISON_METRIC_KEYS,
            )
            delta_payload = {
                metric_name: comparison_metric_delta(scir_metrics[metric_name], baseline_metrics[metric_name])
                for metric_name in COMPARISON_METRICS
            }
            slice_payload[comparison_key_for_baseline(baseline_name)] = delta_payload
            tolerance_map = CLAIM_COMPARISON_TOLERANCES[baseline_name]
            for metric_name, delta in delta_payload.items():
                if delta is None:
                    continue
                if comparison_failure(metric_name, delta, tolerance_map.get(metric_name)):
                    tolerance_failures.append(
                        {
                            "slice_id": slice_id,
                            "baseline_name": baseline_name,
                            "metric": metric_name,
                            "delta": delta,
                            "tolerance": tolerance_map.get(metric_name),
                        }
                    )
        slice_summaries.append(slice_payload)

    aggregate = {
        "scir_metrics": aggregate_comparison_metrics(scir_rows),
    }
    for baseline_name in baselines:
        baseline_metrics = aggregate_comparison_metrics(
            [row for row in baseline_rows if row["baseline_name"] == baseline_name],
            metric_keys=BASELINE_COMPARISON_METRIC_KEYS,
        )
        aggregate[comparison_key_for_baseline(baseline_name)] = {
            metric_name: comparison_metric_delta(aggregate["scir_metrics"][metric_name], baseline_metrics[metric_name])
            for metric_name in COMPARISON_METRICS
        }

    return {
        "sweep_id": result_payload["sweep_id"],
        "run_id": result_payload["run_id"],
        "commit_sha": result_payload["commit_sha"],
        "spec_version": result_payload["spec_version"],
        "tool_version": result_payload["tool_version"],
        "corpus_id": result_payload["corpus_id"],
        "corpus_manifest_hash": result_payload["corpus_manifest_hash"],
        "generated_at": result_payload["generated_at"],
        "comparison_metrics": list(COMPARISON_METRICS),
        "aggregate": aggregate,
        "slices": slice_summaries,
        "tolerance_failures": tolerance_failures,
        "contamination_flags": list(contamination_report["leakage_flags"]),
    }


def build_summary_markdown(summary_payload: dict) -> str:
    lines = [
        f"# Sweep Summary: {summary_payload['sweep_id']}",
        "",
        f"- run_id: `{summary_payload['run_id']}`",
        f"- corpus_id: `{summary_payload['corpus_id']}`",
        f"- commit_sha: `{summary_payload['commit_sha']}`",
        f"- row_count: `{summary_payload['row_count']}`",
        "",
        "## Rankings",
        "",
        f"- most stable slice: `{summary_payload['slice_rankings']['most_stable_slice']['slice_id']}` "
        f"(score `{summary_payload['slice_rankings']['most_stable_slice']['slice_score']}`)",
        f"- most failure-dense slice: `{summary_payload['slice_rankings']['most_failure_dense_slice']['slice_id']}` "
        f"(density `{summary_payload['slice_rankings']['most_failure_dense_slice']['failure_density']}`)",
    ]
    improving = summary_payload["slice_rankings"]["fastest_improving_slice"]
    if improving:
        lines.append(f"- fastest improving slice: `{improving['slice_id']}` (delta `{improving['delta']}`)")

    lines.extend(["", "## Stage Summary", ""])
    for item in summary_payload["stage_summary"]:
        counts = ", ".join(f"{status}={count}" for status, count in item["status_counts"].items())
        lines.append(
            f"- `{item['stage']}`: {counts}; pass_rate=`{item['validator_pass_rate']}`; "
            f"preservation_correctness=`{item['preservation_correctness_rate']}`"
        )

    lines.extend(["", "## Diagnostic Codes", ""])
    if summary_payload["diagnostic_code_summary"]:
        for item in summary_payload["diagnostic_code_summary"]:
            lines.append(f"- `{item['code']}`: `{item['count']}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Preservation Breakdown", ""])
    for item in summary_payload["preservation_stage_breakdown"]:
        stage_fragments = []
        for stage, payload in sorted(item["stages"].items()):
            stage_fragments.append(f"{stage}={payload['preservation_level']} ({payload['expectation_status']})")
        lines.append(f"- `{item['artifact_id']}`: " + ", ".join(stage_fragments))
    return "\n".join(lines) + "\n"


def build_comparison_markdown(comparison_summary: dict) -> str:
    lines = [
        "# Comparison Summary",
        "",
        f"- run_id: `{comparison_summary['run_id']}`",
        f"- corpus_manifest_hash: `{comparison_summary['corpus_manifest_hash']}`",
        f"- metrics: `{', '.join(comparison_summary['comparison_metrics'])}`",
        "",
        "## Aggregate Deltas",
        "",
    ]
    for baseline_key in ["delta_vs_source", "delta_vs_ast", "delta_vs_normalized"]:
        lines.append(f"- `{baseline_key}`: `{comparison_summary['aggregate'][baseline_key]}`")
    lines.extend(["", "## Tolerance Failures", ""])
    if comparison_summary["tolerance_failures"]:
        for item in comparison_summary["tolerance_failures"]:
            lines.append(
                f"- `{item['slice_id']}` vs `{item['baseline_name']}` metric `{item['metric']}`: "
                f"delta `{item['delta']}` beyond tolerance `{item['tolerance']}`"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Contamination Flags", ""])
    if comparison_summary["contamination_flags"]:
        for item in comparison_summary["contamination_flags"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def build_regression_markdown(regression_summary: dict | None) -> str:
    if regression_summary is None:
        return "# Regression Summary\n\n- baseline unavailable\n"
    lines = [
        "# Regression Summary",
        "",
        f"- baseline_run_id: `{regression_summary['baseline_run_id']}`",
        f"- added_failures: `{len(regression_summary['added_failures'])}`",
        f"- removed_failures: `{len(regression_summary['removed_failures'])}`",
        "",
        "## Added Failures",
        "",
    ]
    if regression_summary["added_failures"]:
        for item in regression_summary["added_failures"]:
            lines.append(f"- `{item['artifact_id']}` / `{item['stage']}`: `{item['from_status']}` -> `{item['to_status']}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Removed Failures", ""])
    if regression_summary["removed_failures"]:
        for item in regression_summary["removed_failures"]:
            lines.append(f"- `{item['artifact_id']}` / `{item['stage']}`: `{item['from_status']}` -> `{item['to_status']}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Worsened Metrics", ""])
    if regression_summary["worsened_metrics"]:
        for item in regression_summary["worsened_metrics"]:
            suffix = f" `{item['key']}`" if "key" in item else ""
            lines.append(f"- `{item['metric']}`{suffix}: `{item['baseline']}` -> `{item['current']}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Improved Metrics", ""])
    if regression_summary["improved_metrics"]:
        for item in regression_summary["improved_metrics"]:
            suffix = f" `{item['key']}`" if "key" in item else ""
            lines.append(f"- `{item['metric']}`{suffix}: `{item['baseline']}` -> `{item['current']}`")
    else:
        lines.append("- none")
    if regression_summary["unexpected_diagnostic_codes"]:
        lines.extend(["", "## Unexpected Diagnostic Churn", ""])
        for code in regression_summary["unexpected_diagnostic_codes"]:
            lines.append(f"- `{code}`")
    return "\n".join(lines) + "\n"


def regression_gate_failures(
    regression_summary: dict | None,
    comparison_summary: dict | None = None,
    contamination_report: dict | None = None,
) -> list[str]:
    failures = []
    if regression_summary is not None and regression_summary["added_failures"]:
        failures.append("added failing stage rows were introduced versus the baseline sweep")
        for item in regression_summary["worsened_metrics"]:
            if item["metric"] == "validator_pass_rate":
                failures.append("validator pass rate dropped versus the baseline sweep")
            if item["metric"] == "opaque_fraction":
                failures.append("opaque fraction increased versus the baseline sweep")
            if item["metric"] == "preservation_error_rate":
                failures.append("preservation expectation failures increased versus the baseline sweep")
        if regression_summary["unexpected_diagnostic_codes"]:
            failures.append("unexpected diagnostic churn detected: " + ", ".join(regression_summary["unexpected_diagnostic_codes"]))
    if comparison_summary is not None and comparison_summary["tolerance_failures"]:
        failures.append("SCIR lost to one or more baselines beyond tolerance")
    if contamination_report is not None and contamination_report["leakage_flags"]:
        failures.append("contamination detected in the benchmark corpus splits")
    return sorted(dict.fromkeys(failures))


def run_sweep(root: pathlib.Path, sweep_manifest_rel: str, *, compare_path: pathlib.Path | None = None):
    sweep_manifest = load_json(root / sweep_manifest_rel)
    manifest_failures = schema_failures(root, sweep_manifest, SWEEP_MANIFEST_SCHEMA, sweep_manifest_rel)
    if manifest_failures:
        return manifest_failures, None, None, None, None, None

    corpus_manifest = load_json(root / sweep_manifest["corpus_manifest"])
    corpus_failures = schema_failures(root, corpus_manifest, CORPUS_MANIFEST_SCHEMA, sweep_manifest["corpus_manifest"])
    if corpus_failures:
        return corpus_failures, None, None, None, None, None

    pipeline_failures, outputs = run_pipeline(root)
    if pipeline_failures:
        return pipeline_failures, None, None, None, None, None

    commit_sha = git_commit_sha(root)
    timestamp = dt.datetime.now(dt.timezone.utc)
    run_id = f"{sweep_manifest['sweep_id']}-{timestamp.strftime('%Y%m%dT%H%M%SZ')}"
    corpus_manifest_hash = manifest_hash(root, sweep_manifest["corpus_manifest"])
    reproducibility_block = build_reproducibility_block(
        f"python scripts/scir_sweep.py --manifest {sweep_manifest_rel}",
        root=root,
        timestamp=timestamp.isoformat(),
    )
    rows = []
    for entry in corpus_manifest["fixtures"]:
        rows.extend(
            stage_rows_for_entry(
                root,
                entry,
                outputs,
                sweep_manifest,
                run_id,
                commit_sha,
                corpus_manifest_hash,
                reproducibility_block,
            )
        )
    baseline_rows = baseline_rows_for_manifest(
        root=root,
        corpus_manifest=corpus_manifest,
        sweep_manifest=sweep_manifest,
        run_id=run_id,
        commit_sha=commit_sha,
        corpus_manifest_hash=corpus_manifest_hash,
        reproducibility_block=reproducibility_block,
    )
    contamination_report = build_contamination_report(
        root=root,
        manifest_rel=sweep_manifest["corpus_manifest"],
        corpus_manifest=corpus_manifest,
        corpus_manifest_hash=corpus_manifest_hash,
        run_id=run_id,
        generated_at=timestamp.isoformat(),
    )

    result_payload = {
        "sweep_id": sweep_manifest["sweep_id"],
        "run_id": run_id,
        "commit_sha": commit_sha,
        "spec_version": SPEC_VERSION,
        "tool_version": BENCHMARK_TOOL_VERSION,
        "corpus_id": corpus_manifest["corpus_id"],
        "corpus_manifest_hash": corpus_manifest_hash,
        "generated_at": timestamp.isoformat(),
        "rows": rows,
        "baseline_rows": baseline_rows,
        "clusters": cluster_rows(rows),
        "reproducibility_block": reproducibility_block,
    }
    regression_summary = None
    resolved_compare_path = compare_payload_path(compare_path)
    if resolved_compare_path is not None and resolved_compare_path.exists():
        previous_payload = load_json(resolved_compare_path)
        result_payload["previous_rows"] = previous_payload.get("rows", [])
        regression_summary = compare_with_previous(result_payload, previous_payload)

    sweep_summary = build_summary(result_payload, regression_summary)
    comparison_summary = build_comparison_summary(result_payload, baseline_rows, contamination_report)
    result_payload.pop("previous_rows", None)
    result_failures = schema_failures(root, result_payload, SWEEP_RESULT_SCHEMA, "sweep result")
    summary_failures = schema_failures(root, sweep_summary, SWEEP_SUMMARY_SCHEMA, "sweep summary")
    regression_failures = []
    if regression_summary is not None:
        regression_failures = schema_failures(root, regression_summary, REGRESSION_SUMMARY_SCHEMA, "regression summary")
    comparison_failures = schema_failures(
        root,
        comparison_summary,
        COMPARISON_SUMMARY_SCHEMA,
        "comparison summary",
    )
    contamination_failures = schema_failures(
        root,
        contamination_report,
        CONTAMINATION_REPORT_SCHEMA,
        "contamination report",
    )
    return (
        result_failures
        + summary_failures
        + regression_failures
        + comparison_failures
        + contamination_failures,
        result_payload,
        sweep_summary,
        regression_summary,
        comparison_summary,
        contamination_report,
    )


def write_outputs(
    output_dir: pathlib.Path,
    result_payload: dict,
    sweep_summary: dict,
    regression_summary: dict | None,
    comparison_summary: dict,
    contamination_report: dict,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "sweep_result.json").write_text(json.dumps(result_payload, indent=2) + "\n", encoding="utf-8")
    (output_dir / "sweep_summary.json").write_text(json.dumps(sweep_summary, indent=2) + "\n", encoding="utf-8")
    summary_markdown = build_summary_markdown(sweep_summary)
    (output_dir / "sweep_summary.md").write_text(summary_markdown, encoding="utf-8")
    (output_dir / "summary.md").write_text(summary_markdown, encoding="utf-8")
    (output_dir / "comparison_summary.json").write_text(json.dumps(comparison_summary, indent=2) + "\n", encoding="utf-8")
    (output_dir / "comparison_summary.md").write_text(build_comparison_markdown(comparison_summary), encoding="utf-8")
    (output_dir / "contamination_report.json").write_text(json.dumps(contamination_report, indent=2) + "\n", encoding="utf-8")
    regression_output = regression_summary
    if regression_output is None:
        regression_output = {
            "sweep_id": result_payload["sweep_id"],
            "run_id": result_payload["run_id"],
            "baseline_run_id": "unavailable",
            "generated_at": result_payload["generated_at"],
            "added_failures": [],
            "removed_failures": [],
            "worsened_metrics": [],
            "improved_metrics": [],
            "unexpected_diagnostic_codes": [],
        }
    (output_dir / "regression_summary.json").write_text(json.dumps(regression_output, indent=2) + "\n", encoding="utf-8")
    (output_dir / "regression_summary.md").write_text(build_regression_markdown(regression_output), encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Run a slice-based SCIR sweep over a fixed corpus manifest.")
    parser.add_argument("--manifest", required=True, help="Relative path to a sweep manifest.")
    parser.add_argument("--output-dir", help="Optional directory to write sweep artifacts. Defaults to artifacts/sweeps/<run>.")
    parser.add_argument("--compare", help="Optional prior sweep run directory or sweep_result.json path.")
    parser.add_argument("--enforce-regression-gates", action="store_true", help="Fail when comparison reveals blocked regressions.")
    parser.add_argument("--root")
    return parser.parse_args()


def main():
    args = parse_args()
    root = pathlib.Path(args.root).resolve() if args.root else ROOT
    compare_path = pathlib.Path(args.compare).resolve() if args.compare else None
    failures, result_payload, sweep_summary, regression_summary, comparison_summary, contamination_report = run_sweep(
        root,
        args.manifest,
        compare_path=compare_path,
    )
    if failures:
        print("[sweep] failed")
        for item in failures:
            print(f" - {item}")
        return 1

    generated_at = dt.datetime.fromisoformat(result_payload["generated_at"])
    output_dir = pathlib.Path(args.output_dir).resolve() if args.output_dir else output_dir_for_run(
        root,
        result_payload["commit_sha"],
        generated_at,
    )
    write_outputs(output_dir, result_payload, sweep_summary, regression_summary, comparison_summary, contamination_report)

    gate_failures = (
        regression_gate_failures(regression_summary, comparison_summary, contamination_report)
        if args.enforce_regression_gates
        else []
    )
    if gate_failures:
        print("[sweep] regression gates failed")
        for item in gate_failures:
            print(f" - {item}")
        print(f"[sweep] artifacts written to {output_dir}")
        return 1

    print("[sweep] passed")
    print(f"[sweep] artifacts written to {output_dir}")
    print(build_summary_markdown(sweep_summary).rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
