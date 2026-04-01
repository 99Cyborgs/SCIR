#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
import tempfile

from benchmark_contract_dry_run import (
    run_checks as run_benchmark_doctrine_checks,
    validate_executable_benchmark_items,
)
from scir_bootstrap_pipeline import PipelineError, run_benchmark_suite


PHASE6B_PROFILE_SURFACE_REGISTRY = {
    "profile_schemas": [
    "schemas/module_manifest.schema.json",
    "schemas/profile_claim.schema.json",
    "schemas/preservation_report.schema.json",
    "schemas/reconstruction_report.schema.json",
    "schemas/benchmark_manifest.schema.json",
    "schemas/benchmark_result.schema.json",
    ],
    "profile_examples": [
    "reports/examples/module_manifest.example.json",
    "reports/examples/profile_claim.example.json",
    "reports/examples/preservation_report.example.json",
    "reports/examples/reconstruction_report.example.json",
    "reports/examples/benchmark_manifest.example.json",
    "reports/examples/benchmark_result.example.json",
    ],
    "governance_exports": [
    "reports/exports/decision_register.export.json",
    "reports/exports/open_questions.export.json",
    ],
    "phase6b_markdown": [
    "ARCHITECTURE.md",
    "SYSTEM_BOUNDARY.md",
    "IMPLEMENTATION_PLAN.md",
    "VALIDATION_STRATEGY.md",
    "BENCHMARK_STRATEGY.md",
    "DECISION_REGISTER.md",
    "OPEN_QUESTIONS.md",
    "docs/target_profiles.md",
    "docs/preservation_contract.md",
    "docs/runtime_doctrine.md",
    ],
    "python_importer_fixture_root": "tests/python_importer/cases",
    "python_importer_fixture_manifest": "module_manifest.json",
}

PROFILE_CONTEXT_KEYS = {"profile", "profiles", "declared_profiles"}
LEGACY_PROFILE_ROW = re.compile(r"^\|\s*`D`\s*\|")
LEGACY_PROFILE_CLAIM = re.compile(r"`?D/P[0-3X]`?")
BACKTICK_TOKEN = re.compile(r"`([^`]+)`")
PROFILE_WORD = re.compile(r"\bprofile(?:s)?\b", re.IGNORECASE)
TRACK_OR_TIER_D = re.compile(r"\b(?:Track|Tier)\s+`D`", re.IGNORECASE)
SUPPRESSED_LEGACY_WORDS = (
    "legacy",
    "monolithic",
    "supersed",
    "invalid",
    "reject",
    "replaced",
)
PYTHON_TRACK_D_METRICS = [
    "median_runtime_ratio",
    "async_overhead_ratio",
    "opaque_boundary_overhead_ratio",
]
RUST_TRACK_D_METRICS = [
    "median_runtime_ratio",
    "compile_time_ratio",
    "async_overhead_ratio",
]


def repo_root(root_arg: str | None) -> pathlib.Path:
    return pathlib.Path(root_arg).resolve() if root_arg else pathlib.Path(__file__).resolve().parents[1]


def relpath(root: pathlib.Path, path: pathlib.Path) -> str:
    return path.relative_to(root).as_posix()


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def format_json_path(segments: list[str]) -> str:
    if not segments:
        return "$"
    path = "$"
    for segment in segments:
        if segment.isdigit():
            path += f"[{segment}]"
        else:
            path += f".{segment}"
    return path


def is_suppressed_profile_line(text: str) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in SUPPRESSED_LEGACY_WORDS)


def scan_profile_text(text: str, rel: str, context: str) -> list[str]:
    findings = []
    if LEGACY_PROFILE_CLAIM.search(text):
        findings.append(f"{rel}: {context}: legacy profile preservation claim uses monolithic D")

    tokens = BACKTICK_TOKEN.findall(TRACK_OR_TIER_D.sub("", text))
    if PROFILE_WORD.search(text) and "D" in tokens and not is_suppressed_profile_line(text):
        findings.append(f"{rel}: {context}: profile claim uses legacy monolithic `D`")
    return findings


def audit_json_profiles(value, rel: str, findings: list[str], segments: list[str] | None = None):
    if segments is None:
        segments = []

    if isinstance(value, dict):
        for key, child in value.items():
            audit_json_profiles(child, rel, findings, [*segments, key])
        return

    if isinstance(value, list):
        for index, child in enumerate(value):
            audit_json_profiles(child, rel, findings, [*segments, str(index)])
        return

    if not isinstance(value, str):
        return

    context_keys = set(segment for segment in segments if not segment.isdigit())
    path = format_json_path(segments)
    if value == "D" and PROFILE_CONTEXT_KEYS & context_keys:
        findings.append(f"{rel}: {path}: legacy monolithic profile `D` is not canonical")
    findings.extend(scan_profile_text(value, rel, path))


def audit_markdown_surface(root: pathlib.Path, rel: str) -> list[str]:
    findings = []
    path = root / rel
    if not path.exists():
        return [f"{rel}: missing canonical profile-bearing surface"]

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        context = f"line {line_no}"
        if LEGACY_PROFILE_ROW.match(stripped):
            findings.append(f"{rel}: {context}: profile table defines legacy monolithic `D`")
        findings.extend(scan_profile_text(line, rel, context))
    return findings


def build_surface_registry(root: pathlib.Path) -> tuple[dict[str, list[str]], list[str]]:
    registry = {
        "profile_schemas": list(PHASE6B_PROFILE_SURFACE_REGISTRY["profile_schemas"]),
        "profile_examples": list(PHASE6B_PROFILE_SURFACE_REGISTRY["profile_examples"]),
        "governance_exports": list(PHASE6B_PROFILE_SURFACE_REGISTRY["governance_exports"]),
        "phase6b_markdown": list(PHASE6B_PROFILE_SURFACE_REGISTRY["phase6b_markdown"]),
        "python_fixture_manifests": [],
    }
    findings = []

    case_root = root / PHASE6B_PROFILE_SURFACE_REGISTRY["python_importer_fixture_root"]
    manifest_name = PHASE6B_PROFILE_SURFACE_REGISTRY["python_importer_fixture_manifest"]
    if not case_root.exists():
        findings.append(f"{relpath(root, case_root)}: missing canonical profile-bearing surface")
        return registry, findings

    case_dirs = sorted(path for path in case_root.iterdir() if path.is_dir())
    if not case_dirs:
        findings.append(f"{relpath(root, case_root)}: no Python importer fixture cases found")
        return registry, findings

    for case_dir in case_dirs:
        registry["python_fixture_manifests"].append(relpath(root, case_dir / manifest_name))
    return registry, findings


def split_run_summaries(run_summaries: list[dict]) -> tuple[dict | None, dict | None]:
    first_successful_run = None
    first_failed_run = None
    for run_summary in run_summaries:
        if run_summary["status"] == "pass":
            if first_successful_run is None:
                first_successful_run = run_summary
            continue
        if first_failed_run is None:
            first_failed_run = run_summary
    return first_successful_run, first_failed_run


def run_legacy_profile_audit(root: pathlib.Path) -> dict:
    findings = []
    surfaces_checked = 0
    registry, registry_findings = build_surface_registry(root)
    findings.extend(registry_findings)

    for category in ("profile_schemas", "profile_examples", "governance_exports", "python_fixture_manifests"):
        for rel in registry[category]:
            surfaces_checked += 1
            path = root / rel
            if not path.exists():
                findings.append(f"{rel}: missing canonical profile-bearing surface")
                continue
            try:
                payload = load_json(path)
            except Exception as exc:  # pragma: no cover - bootstrap script
                findings.append(f"{rel}: could not parse JSON: {exc}")
                continue
            audit_json_profiles(payload, rel, findings)

    for rel in registry["phase6b_markdown"]:
        surfaces_checked += 1
        findings.extend(audit_markdown_surface(root, rel))

    return {
        "status": "pass" if not findings else "fail",
        "surfaces_checked": surfaces_checked,
        "findings": findings,
    }


def run_benchmark_once(root: pathlib.Path, run_number: int) -> dict:
    try:
        harness_failures, benchmark_items = run_benchmark_suite(root)
    except PipelineError as exc:
        return {
            "run": run_number,
            "status": "fail",
            "errors": [str(exc)],
        }

    if harness_failures or benchmark_items is None:
        return {
            "run": run_number,
            "status": "fail",
            "errors": list(harness_failures or ["benchmark harness returned no bundle"]),
        }

    bundle_failures = validate_executable_benchmark_items(root, benchmark_items)
    if bundle_failures:
        return {
            "run": run_number,
            "status": "fail",
            "errors": bundle_failures,
            "benchmark_items": benchmark_items,
        }

    python_metrics = benchmark_items["track_d_python_result"]["metrics"]
    rust_metrics = benchmark_items["track_d_rust_result"]["metrics"]
    return {
        "run": run_number,
        "status": "pass",
        "track_d_python_status": benchmark_items["track_d_python_result"]["status"],
        "track_d_rust_status": benchmark_items["track_d_rust_result"]["status"],
        "python_metrics": {name: python_metrics[name] for name in PYTHON_TRACK_D_METRICS},
        "rust_metrics": {name: rust_metrics[name] for name in RUST_TRACK_D_METRICS},
        "benchmark_items": benchmark_items,
    }


def build_track_d_contract_audit(
    root: pathlib.Path,
    first_successful_run: dict | None,
    first_failed_run: dict | None,
) -> dict:
    findings = list(run_benchmark_doctrine_checks(root))
    bundle_keys = []
    python_benchmark_id = None
    rust_benchmark_id = None

    if first_successful_run is None:
        if first_failed_run is None:
            findings.append("track_d contract audit: no benchmark run was executed")
        else:
            for item in first_failed_run.get("errors", []):
                findings.append(
                    f"track_d contract audit: run {first_failed_run['run']}: {item}"
                )
    else:
        benchmark_items = first_successful_run["benchmark_items"]
        bundle_keys = sorted(benchmark_items.keys())
        python_benchmark_id = benchmark_items["track_d_python_manifest"]["benchmark_id"]
        rust_benchmark_id = benchmark_items["track_d_rust_manifest"]["benchmark_id"]

    return {
        "status": "pass" if not findings else "fail",
        "bundle_keys": bundle_keys,
        "track_d_python_benchmark_id": python_benchmark_id,
        "track_d_rust_benchmark_id": rust_benchmark_id,
        "d_js_executable_bundle_present": any("track_d_js" in key for key in bundle_keys),
        "findings": findings,
    }


def build_benchmark_stability_audit(run_summaries: list[dict]) -> dict:
    findings = []
    for run_summary in run_summaries:
        if run_summary["status"] == "pass":
            continue
        errors = run_summary.get("errors", ["benchmark run failed"])
        for item in errors:
            findings.append(f"run {run_summary['run']}: {item}")

    return {
        "status": "pass" if not findings else "fail",
        "run_count": len(run_summaries),
        "standalone_acceptance_only": True,
        "out_of_scope": "overlapping benchmark-heavy commands are not part of this acceptance contract",
        "runs": [
            {
                key: value
                for key, value in run_summary.items()
                if key != "benchmark_items"
            }
            for run_summary in run_summaries
        ],
        "findings": findings,
    }


def perform_audit(root: pathlib.Path, runs: int) -> tuple[dict, dict | None]:
    legacy_profile_audit = run_legacy_profile_audit(root)

    run_summaries = [run_benchmark_once(root, run_number) for run_number in range(1, runs + 1)]
    first_successful_run, first_failed_run = split_run_summaries(run_summaries)
    track_d_contract_audit = build_track_d_contract_audit(
        root,
        first_successful_run,
        first_failed_run,
    )
    benchmark_stability_audit = build_benchmark_stability_audit(run_summaries)

    sections = [
        legacy_profile_audit,
        track_d_contract_audit,
        benchmark_stability_audit,
    ]
    report = {
        "status": "pass" if all(section["status"] == "pass" for section in sections) else "fail",
        "legacy_profile_audit": legacy_profile_audit,
        "track_d_contract_audit": track_d_contract_audit,
        "benchmark_stability_audit": benchmark_stability_audit,
    }
    first_successful_bundle = (
        first_successful_run["benchmark_items"] if first_successful_run is not None else None
    )
    return report, first_successful_bundle


def mutate_fixture_legacy_profile(root: pathlib.Path):
    path = root / "tests" / "python_importer" / "cases" / "a_basic_function" / "module_manifest.json"
    payload = load_json(path)
    payload["declared_profiles"] = ["R", "D"]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_negative_fixture(root: pathlib.Path, name: str, mutate, expected_marker: str) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="scir_phase6b_audit_") as tmp:
        fixture_root = pathlib.Path(tmp) / "repo"
        shutil.copytree(root, fixture_root, ignore=shutil.ignore_patterns("__pycache__"))
        mutate(fixture_root)
        findings = run_legacy_profile_audit(fixture_root)["findings"]

    if not findings:
        return [f"phase6b audit self-test {name}: expected failure but audit passed"]
    if not any(expected_marker in item for item in findings):
        return [f"phase6b audit self-test {name}: missing expected finding marker {expected_marker}"]
    return []


def run_self_tests(root: pathlib.Path, baseline_bundle: dict) -> tuple[list[str], int]:
    failures = []
    count = 0

    count += 1
    failures.extend(
        run_negative_fixture(
            root,
            "legacy profile fixture",
            mutate_fixture_legacy_profile,
            "legacy monolithic profile `D` is not canonical",
        )
    )

    count += 1
    mutated_bundle = json.loads(json.dumps(baseline_bundle))
    mutated_bundle["track_d_js_result"] = {}
    bundle_failures = validate_executable_benchmark_items(root, mutated_bundle)
    if not any("unexpected executable artifact track_d_js_result" in item for item in bundle_failures):
        failures.append("phase6b audit self-test unexpected d-js artifact: missing expected executable-bundle failure")

    count += 1
    simulated = build_benchmark_stability_audit(
        [
            {"run": 1, "status": "pass", "python_metrics": {}, "rust_metrics": {}},
            {"run": 2, "status": "fail", "errors": ["simulated benchmark failure"]},
        ]
    )
    if simulated["status"] != "fail":
        failures.append("phase6b audit self-test repeated benchmark failure: expected fail status")
    elif not any("run 2: simulated benchmark failure" in item for item in simulated["findings"]):
        failures.append("phase6b audit self-test repeated benchmark failure: missing expected stability finding")

    return failures, count


def print_text_report(report: dict, mode: str, self_test_count: int | None = None):
    header = "[phase6b-audit] passed" if report["status"] == "pass" else "[phase6b-audit] failed"
    print(header)

    legacy = report["legacy_profile_audit"]
    print(
        "Legacy profile audit: "
        f"{legacy['status']} "
        f"({legacy['surfaces_checked']} canonical surfaces checked)."
    )
    if legacy["findings"]:
        for item in legacy["findings"]:
            print(f" - {item}")

    contract = report["track_d_contract_audit"]
    print(
        "Track D contract audit: "
        f"{contract['status']} "
        f"(Python={contract['track_d_python_benchmark_id']}, "
        f"Rust={contract['track_d_rust_benchmark_id']})."
    )
    if contract["findings"]:
        for item in contract["findings"]:
            print(f" - {item}")

    stability = report["benchmark_stability_audit"]
    print(
        "Benchmark stability audit: "
        f"{stability['status']} "
        f"({stability['run_count']} sequential standalone runs)."
    )
    for run_summary in stability["runs"]:
        if run_summary["status"] != "pass":
            print(f" - run {run_summary['run']}: fail")
            continue
        print(
            " - run "
            f"{run_summary['run']}: pass "
            f"(python median={run_summary['python_metrics']['median_runtime_ratio']}, "
            f"rust median={run_summary['rust_metrics']['median_runtime_ratio']})"
        )
    if stability["findings"]:
        for item in stability["findings"]:
            print(f" - {item}")
    print(
        "Acceptance scope: standalone sequential benchmark runs only; "
        "overlapping benchmark-heavy commands remain out of scope."
    )
    if mode == "test" and self_test_count is not None:
        print(f"Phase 6B audit self-tests passed ({self_test_count} negative checks).")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--mode", default="validate", choices=["validate", "test"])
    return parser.parse_args()


def main():
    args = parse_args()
    if args.runs < 1:
        print("--runs must be >= 1", file=sys.stderr)
        sys.exit(1)

    root = repo_root(args.root)
    report, first_successful_bundle = perform_audit(root, args.runs)

    if args.mode == "test":
        if first_successful_bundle is None:
            failure_message = "phase6b audit self-test setup: baseline executable benchmark bundle is required"
            report["status"] = "fail"
            report["self_tests"] = {"status": "fail", "findings": [failure_message], "count": 0}
        else:
            self_test_failures, self_test_count = run_self_tests(root, first_successful_bundle)
            report["self_tests"] = {
                "status": "pass" if not self_test_failures else "fail",
                "findings": self_test_failures,
                "count": self_test_count,
            }
            if self_test_failures:
                report["status"] = "fail"

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text_report(
            report,
            args.mode,
            report.get("self_tests", {}).get("count"),
        )
        if report.get("self_tests", {}).get("findings"):
            for item in report["self_tests"]["findings"]:
                print(f" - {item}")

    sys.exit(0 if report["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
