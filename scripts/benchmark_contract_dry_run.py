#!/usr/bin/env python3
import argparse
import json
import pathlib
import shutil
import tempfile
import sys

from scir_bootstrap_pipeline import run_benchmark_suite
from rust_toolchain import resolve_rust_toolchain
from validate_repo_contracts import collect_instance_validation_errors

REQUIRED_FILES = [
    "BENCHMARK_STRATEGY.md",
    "benchmarks/README.md",
    "benchmarks/tracks.md",
    "benchmarks/baselines.md",
    "benchmarks/corpora_policy.md",
    "benchmarks/contamination_controls.md",
    "benchmarks/success_failure_gates.md",
    "schemas/benchmark_manifest.schema.json",
    "schemas/benchmark_result.schema.json",
]

REQUIRED_TRACK_MARKERS = ["Track `A`", "Track `B`", "Track `C`", "Track `D`"]
REQUIRED_GATE_MARKERS = ["S1", "S2", "S3", "S4", "S5", "K1", "K2", "K3", "K4", "K5", "K6", "K7", "K8"]
REQUIRED_BASELINE_MARKERS = {
    "direct source": ["direct source"],
    "typed-AST": ["typed-ast"],
    "SSA-like": ["ssa-like"],
    "MLIR": ["mlir"],
    "lightweight regularized core or s-expression": ["regularized core", "s-expression"],
}
REQUIRED_CONTAMINATION_MARKERS = [
    "hash every published corpus manifest",
    "separate development, tuning, and held-out evaluation slices",
    "record prompt templates and baseline adapters",
    "do not claim generalization from a contaminated or untracked dataset",
]
REQUIRED_CORPUS_MARKERS = [
    "record dataset name and hash in the benchmark manifest",
    "record language and tier mix",
    "do not use proprietary-only corpora for the primary evidence set",
]
EXECUTABLE_BUNDLE_KEYS = [
    "track_a_manifest",
    "track_a_result",
    "track_b_manifest",
    "track_b_result",
    "track_d_python_manifest",
    "track_d_python_result",
    "track_d_rust_manifest",
    "track_d_rust_result",
]
COMMON_RESULT_METRICS = [
    "opaque_fraction",
    "preservation_level_ceiling",
    "tier_a_feature_count",
    "tier_b_feature_count",
    "tier_c_feature_count",
    "tier_d_feature_count",
]
TRACK_EXPECTATIONS = {
    "track_a": {
        "manifest_key": "track_a_manifest",
        "result_key": "track_a_result",
        "track": "A",
        "benchmark_id": "bootstrap-track-a-python-subset",
        "corpus_name": "python-bootstrap-fixtures",
        "profiles": ["R", "D-PY"],
        "result_profile": "R",
        "required_manifest_baselines": [
            "direct source",
            "typed-AST",
            "lightweight regularized core or s-expression",
        ],
        "required_result_baselines": ["direct source", "typed-AST"],
        "success_gates": ["S3", "S4"],
        "kill_gates": ["K2", "K4", "K7"],
        "required_metrics": [
            "median_scir_to_source_ratio",
            "aggregate_scir_to_source_ratio",
            "median_scir_to_typed_ast_ratio",
            "aggregate_scir_to_typed_ast_ratio",
            "body_median_scir_to_source_ratio",
            "header_token_share",
            "gate_S3_source_pass",
            "gate_S3_ast_pass",
            "gate_S4_pass",
            "gate_K2_hit",
            "gate_K4_hit",
        ],
    },
    "track_b": {
        "manifest_key": "track_b_manifest",
        "result_key": "track_b_result",
        "track": "B",
        "benchmark_id": "bootstrap-track-b-python-subset",
        "corpus_name": "python-bootstrap-fixtures",
        "profiles": ["R", "D-PY"],
        "result_profile": "R",
        "required_manifest_baselines": ["direct source", "typed-AST"],
        "required_result_baselines": ["direct source", "typed-AST"],
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
    "track_d_python": {
        "manifest_key": "track_d_python_manifest",
        "result_key": "track_d_python_result",
        "track": "D",
        "benchmark_id": "bootstrap-track-d-python-dpy-subset",
        "corpus_name": "python-bootstrap-fixtures",
        "profiles": ["D-PY"],
        "result_profile": "D-PY",
        "required_manifest_baselines": ["direct source", "typed-AST"],
        "required_result_baselines": ["direct source", "typed-AST"],
        "success_gates": ["S5"],
        "kill_gates": ["K8"],
        "required_metrics": [
            "median_runtime_ratio",
            "async_overhead_ratio",
            "opaque_boundary_overhead_ratio",
            "observable_match",
            "gate_S5_pass",
            "gate_K8_hit",
        ],
    },
    "track_d_rust": {
        "manifest_key": "track_d_rust_manifest",
        "result_key": "track_d_rust_result",
        "track": "D",
        "benchmark_id": "bootstrap-track-d-rust-n-subset",
        "corpus_name": "rust-bootstrap-fixtures",
        "profiles": ["N"],
        "result_profile": "N",
        "required_manifest_baselines": ["direct source", "typed-AST", "SSA-like internal IR"],
        "required_result_baselines": ["direct source", "typed-AST", "SSA-like internal IR"],
        "success_gates": ["S5"],
        "kill_gates": ["K8"],
        "required_metrics": [
            "median_runtime_ratio",
            "compile_time_ratio",
            "artifact_size_ratio",
            "peak_memory_ratio",
            "async_overhead_ratio",
            "gate_S5_pass",
            "gate_K8_hit",
            "observable_match",
        ],
    },
}

SCHEMA_EXPECTATIONS = {
    "schemas/benchmark_manifest.schema.json": {
        "required": [
            "benchmark_id",
            "track",
            "task_family",
            "corpus",
            "baselines",
            "success_gates",
            "kill_gates",
        ],
        "properties": {
            "track": {"enum": ["A", "B", "C", "D"]},
            "corpus": {
                "type": "object",
                "required": ["name", "scope"],
            },
            "baselines": {"type": "array"},
            "profiles": {
                "type": "array",
                "items": {"enum": ["R", "N", "P", "D-PY", "D-JS"]},
            },
            "success_gates": {"type": "array"},
            "kill_gates": {"type": "array"},
        },
    },
    "schemas/benchmark_result.schema.json": {
        "required": [
            "benchmark_id",
            "run_id",
            "system_under_test",
            "track",
            "metrics",
            "baseline_comparison",
            "status",
        ],
        "properties": {
            "track": {"enum": ["A", "B", "C", "D"]},
            "profile": {"enum": ["R", "N", "P", "D-PY", "D-JS"]},
            "metrics": {"type": "object"},
            "baseline_comparison": {"type": "object"},
            "status": {"enum": ["pass", "mixed", "fail"]},
        },
    },
}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_instance(root: pathlib.Path, instance, schema_rel: str, label: str):
    failures = []
    schema = json.loads((root / schema_rel).read_text(encoding="utf-8"))
    for location, message in collect_instance_validation_errors(instance, schema):
        failures.append(f"{label} {location}: {message}")
    return failures


def check_required_files(root: pathlib.Path):
    failures = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing benchmark contract file: {rel}")
    return failures


def check_track_markers(root: pathlib.Path):
    failures = []
    tracks = read(root / "benchmarks" / "tracks.md")
    strategy = read(root / "BENCHMARK_STRATEGY.md")
    for marker in REQUIRED_TRACK_MARKERS:
        if marker not in tracks and marker not in strategy:
            failures.append(f"missing track marker: {marker}")
    return failures


def check_gate_markers(root: pathlib.Path):
    failures = []
    gates = read(root / "benchmarks" / "success_failure_gates.md")
    for marker in REQUIRED_GATE_MARKERS:
        if marker not in gates:
            failures.append(f"missing gate marker: {marker}")
    return failures


def check_baseline_markers(root: pathlib.Path):
    failures = []
    baselines = read(root / "benchmarks" / "baselines.md").lower()
    for label, alternatives in REQUIRED_BASELINE_MARKERS.items():
        if not any(marker in baselines for marker in alternatives):
            failures.append(f"missing baseline marker: {label}")
    return failures


def check_contamination_markers(root: pathlib.Path):
    failures = []
    contamination = read(root / "benchmarks" / "contamination_controls.md").lower()
    for marker in REQUIRED_CONTAMINATION_MARKERS:
        if marker not in contamination:
            failures.append(f"missing contamination marker: {marker}")
    return failures


def check_corpus_markers(root: pathlib.Path):
    failures = []
    corpora = read(root / "benchmarks" / "corpora_policy.md").lower()
    for marker in REQUIRED_CORPUS_MARKERS:
        if marker not in corpora:
            failures.append(f"missing corpus marker: {marker}")
    return failures


def validate_schema_fragment(fragment, expectation, path):
    failures = []

    expected_type = expectation.get("type")
    if expected_type is not None and fragment.get("type") != expected_type:
        failures.append(f"{path}: expected type {expected_type!r}")

    expected_required = expectation.get("required")
    if expected_required is not None:
        actual_required = fragment.get("required")
        if not isinstance(actual_required, list):
            failures.append(f"{path}: missing required list")
        else:
            missing_required = [name for name in expected_required if name not in actual_required]
            if missing_required:
                failures.append(
                    f"{path}: missing required fields {', '.join(missing_required)}"
                )

    expected_enum = expectation.get("enum")
    if expected_enum is not None and fragment.get("enum") != expected_enum:
        failures.append(f"{path}: expected enum {expected_enum!r}")

    expected_properties = expectation.get("properties")
    if expected_properties is not None:
        actual_properties = fragment.get("properties")
        if not isinstance(actual_properties, dict):
            failures.append(f"{path}: missing properties object")
        else:
            for key, child_expectation in expected_properties.items():
                if key not in actual_properties:
                    failures.append(f"{path}: missing property {key}")
                    continue
                failures.extend(
                    validate_schema_fragment(
                        actual_properties[key],
                        child_expectation,
                        f"{path}.properties.{key}",
                    )
                )

    expected_items = expectation.get("items")
    if expected_items is not None:
        actual_items = fragment.get("items")
        if actual_items is None:
            failures.append(f"{path}: missing items contract")
        else:
            failures.extend(
                validate_schema_fragment(actual_items, expected_items, f"{path}.items")
            )

    return failures


def check_schema_expectations(root: pathlib.Path):
    failures = []
    for rel, expectation in SCHEMA_EXPECTATIONS.items():
        schema = json.loads((root / rel).read_text(encoding="utf-8"))
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            failures.append(f"{rel}: expected Draft 2020-12 schema declaration")
        if schema.get("type") != "object":
            failures.append(f"{rel}: expected top-level object schema")
        if schema.get("additionalProperties") is not False:
            failures.append(f"{rel}: expected top-level additionalProperties=false")
        failures.extend(validate_schema_fragment(schema, expectation, rel))
    return failures


def run_checks(root: pathlib.Path):
    failures = []
    failures.extend(check_required_files(root))
    failures.extend(check_track_markers(root))
    failures.extend(check_gate_markers(root))
    failures.extend(check_baseline_markers(root))
    failures.extend(check_corpus_markers(root))
    failures.extend(check_contamination_markers(root))
    failures.extend(check_schema_expectations(root))
    return failures


def expect_keys(obj, keys, label):
    failures = []
    missing = [key for key in keys if key not in obj]
    for key in missing:
        failures.append(f"{label}: missing key {key}")
    return failures


def validate_executable_manifest(manifest: dict, label: str, expectation: dict):
    failures = []
    if manifest.get("track") != expectation["track"]:
        failures.append(f"{label}: expected track {expectation['track']}")
    if manifest.get("benchmark_id") != expectation["benchmark_id"]:
        failures.append(f"{label}: expected benchmark_id {expectation['benchmark_id']}")

    corpus = manifest.get("corpus")
    if not isinstance(corpus, dict):
        failures.append(f"{label}: expected corpus object")
    else:
        if corpus.get("name") != expectation["corpus_name"]:
            failures.append(
                f"{label}: expected fixed bootstrap corpus name {expectation['corpus_name']}"
            )
        if not corpus.get("hash"):
            failures.append(f"{label}: expected corpus hash for executable benchmark manifest")

    baselines = manifest.get("baselines")
    if not isinstance(baselines, list):
        failures.append(f"{label}: expected baselines list")
    else:
        for baseline in expectation["required_manifest_baselines"]:
            if baseline not in baselines:
                failures.append(f"{label}: missing executable baseline {baseline}")

    profiles = manifest.get("profiles")
    if not isinstance(profiles, list) or set(profiles) != set(expectation["profiles"]):
        failures.append(f"{label}: expected executable profiles {expectation['profiles']}")

    if manifest.get("success_gates") != expectation["success_gates"]:
        failures.append(f"{label}: expected success gates {expectation['success_gates']}")
    if manifest.get("kill_gates") != expectation["kill_gates"]:
        failures.append(f"{label}: expected kill gates {expectation['kill_gates']}")

    controls = manifest.get("contamination_controls")
    if not isinstance(controls, list) or not controls:
        failures.append(f"{label}: expected contamination_controls for executable manifest")

    return failures


def validate_common_result(result: dict, label: str, expectation: dict):
    failures = []
    if result.get("track") != expectation["track"]:
        failures.append(f"{label}: expected track {expectation['track']}")
    if result.get("benchmark_id") != expectation["benchmark_id"]:
        failures.append(f"{label}: expected benchmark_id {expectation['benchmark_id']}")
    if result.get("profile") != expectation["result_profile"]:
        failures.append(f"{label}: expected top-level profile {expectation['result_profile']}")

    metrics = result.get("metrics")
    if not isinstance(metrics, dict):
        return failures + [f"{label}: expected metrics object"], None, None

    baseline_comparison = result.get("baseline_comparison")
    if not isinstance(baseline_comparison, dict):
        failures.append(f"{label}: expected baseline_comparison object")
        baseline_comparison = {}
    for baseline in expectation["required_result_baselines"]:
        if baseline not in baseline_comparison:
            failures.append(f"{label}: missing baseline comparison for {baseline}")

    missing_metrics = [
        metric
        for metric in COMMON_RESULT_METRICS + expectation["required_metrics"]
        if metric not in metrics
    ]
    for metric in missing_metrics:
        failures.append(f"{label}.metrics: missing required metric {metric}")

    if missing_metrics:
        return failures, None, baseline_comparison

    return failures, metrics, baseline_comparison


def validate_track_a_result(result: dict):
    failures, metrics, _ = validate_common_result(result, "track_a result", TRACK_EXPECTATIONS["track_a"])
    if metrics is None:
        return failures

    derived_s3_source = metrics["median_scir_to_source_ratio"] <= 1.10
    derived_s3_ast = metrics["median_scir_to_typed_ast_ratio"] <= 0.75
    derived_k2 = metrics["median_scir_to_source_ratio"] > 1.50
    derived_s4 = metrics["opaque_fraction"] < 0.15
    derived_k4 = metrics["opaque_fraction"] > 0.25

    if metrics["gate_S3_source_pass"] != derived_s3_source:
        failures.append("track_a result: gate_S3_source_pass must be derived from median_scir_to_source_ratio")
    if metrics["gate_S3_ast_pass"] != derived_s3_ast:
        failures.append("track_a result: gate_S3_ast_pass must be derived from median_scir_to_typed_ast_ratio")
    if metrics["gate_S4_pass"] != derived_s4:
        failures.append("track_a result: gate_S4_pass must be derived from opaque_fraction")
    if metrics["gate_K2_hit"] != derived_k2:
        failures.append("track_a result: gate_K2_hit must be derived from median_scir_to_source_ratio")
    if metrics["gate_K4_hit"] != derived_k4:
        failures.append("track_a result: gate_K4_hit must be derived from opaque_fraction")

    expected_pass = (derived_s3_source or derived_s3_ast) and derived_s4 and not derived_k2 and not derived_k4
    if result.get("status") == "pass" and (derived_k2 or derived_k4):
        failures.append("track_a result: status pass despite automated kill gate")
    if result.get("status") != ("pass" if expected_pass else "fail"):
        failures.append(
            f"track_a result: expected status {'pass' if expected_pass else 'fail'} from executable gates"
        )

    if metrics["preservation_level_ceiling"] != "P3":
        failures.append("track_a result: expected preservation_level_ceiling P3")
    return failures


def validate_track_b_result(result: dict):
    failures, metrics, _ = validate_common_result(result, "track_b result", TRACK_EXPECTATIONS["track_b"])
    if metrics is None:
        return failures

    derived_s1 = metrics["tier_a_compile_pass_rate"] >= 0.95 and metrics["tier_a_test_pass_rate"] >= 0.95
    derived_k3 = metrics["tier_a_compile_pass_rate"] < 0.90 or metrics["tier_a_test_pass_rate"] < 0.90
    derived_s4 = metrics["opaque_fraction"] < 0.15
    derived_k4 = metrics["opaque_fraction"] > 0.25

    if metrics["gate_S1_pass"] != derived_s1:
        failures.append("track_b result: gate_S1_pass must be derived from Tier A compile/test rates")
    if metrics["gate_S4_pass"] != derived_s4:
        failures.append("track_b result: gate_S4_pass must be derived from opaque_fraction")
    if metrics["gate_K3_hit"] != derived_k3:
        failures.append("track_b result: gate_K3_hit must be derived from Tier A compile/test rates")
    if metrics["gate_K4_hit"] != derived_k4:
        failures.append("track_b result: gate_K4_hit must be derived from opaque_fraction")

    expected_pass = derived_s1 and derived_s4 and not derived_k3 and not derived_k4
    if result.get("status") == "pass" and not derived_s1:
        failures.append("track_b result: status pass despite Tier A compile/test gate failure")
    if result.get("status") == "pass" and (derived_k3 or derived_k4):
        failures.append("track_b result: status pass despite automated kill gate")
    if result.get("status") != ("pass" if expected_pass else "fail"):
        failures.append(
            f"track_b result: expected status {'pass' if expected_pass else 'fail'} from executable gates"
        )

    if metrics["preservation_level_ceiling"] != "P3":
        failures.append("track_b result: expected preservation_level_ceiling P3")
    return failures


def validate_track_d_python_result(result: dict):
    failures, metrics, _ = validate_common_result(
        result,
        "track_d_python result",
        TRACK_EXPECTATIONS["track_d_python"],
    )
    if metrics is None:
        return failures

    derived_s5 = (
        metrics["median_runtime_ratio"] <= 1.50
        and metrics["async_overhead_ratio"] <= 1.75
        and metrics["opaque_boundary_overhead_ratio"] <= 1.25
    )
    must_trigger_k8 = (
        metrics["median_runtime_ratio"] > 2.0
        or metrics["async_overhead_ratio"] > 2.0
        or metrics["opaque_boundary_overhead_ratio"] > 2.0
        or not metrics["observable_match"]
    )

    if metrics["gate_S5_pass"] != derived_s5:
        failures.append(
            "track_d_python result: gate_S5_pass must be derived from published Phase 6B ceilings"
        )
    if must_trigger_k8 and not metrics["gate_K8_hit"]:
        failures.append(
            "track_d_python result: gate_K8_hit must fire when a reported runtime exceeds 2.0x or observables diverge"
        )

    expected_status = "pass" if derived_s5 and not metrics["gate_K8_hit"] else "fail"
    if result.get("status") != expected_status:
        failures.append(
            f"track_d_python result: expected status {expected_status} from executable gates"
        )

    if metrics["preservation_level_ceiling"] != "P3":
        failures.append("track_d_python result: expected preservation_level_ceiling P3")
    return failures


def validate_track_d_rust_result(result: dict):
    failures, metrics, _ = validate_common_result(
        result,
        "track_d_rust result",
        TRACK_EXPECTATIONS["track_d_rust"],
    )
    if metrics is None:
        return failures

    derived_s5 = (
        metrics["median_runtime_ratio"] <= 1.25
        and metrics["compile_time_ratio"] <= 1.50
    )
    must_trigger_k8 = (
        metrics["median_runtime_ratio"] > 2.0
        or metrics["async_overhead_ratio"] > 2.0
        or not metrics["observable_match"]
    )

    if metrics["gate_S5_pass"] != derived_s5:
        failures.append(
            "track_d_rust result: gate_S5_pass must be derived from published Phase 6B ceilings"
        )
    if must_trigger_k8 and not metrics["gate_K8_hit"]:
        failures.append(
            "track_d_rust result: gate_K8_hit must fire when a reported runtime exceeds 2.0x or observables diverge"
        )

    expected_status = "pass" if derived_s5 and not metrics["gate_K8_hit"] else "fail"
    if result.get("status") != expected_status:
        failures.append(
            f"track_d_rust result: expected status {expected_status} from executable gates"
        )

    if metrics["preservation_level_ceiling"] != "P3":
        failures.append("track_d_rust result: expected preservation_level_ceiling P3")
    return failures


def validate_executable_benchmark_items(root: pathlib.Path, benchmark_items: dict):
    failures = []
    failures.extend(expect_keys(benchmark_items, EXECUTABLE_BUNDLE_KEYS, "benchmark bundle"))

    unexpected = sorted(key for key in benchmark_items if key not in EXECUTABLE_BUNDLE_KEYS)
    for key in unexpected:
        failures.append(f"benchmark bundle: unexpected executable artifact {key}")

    for name, expectation in TRACK_EXPECTATIONS.items():
        manifest_key = expectation["manifest_key"]
        result_key = expectation["result_key"]
        manifest = benchmark_items.get(manifest_key)
        result = benchmark_items.get(result_key)
        if not isinstance(manifest, dict) or not isinstance(result, dict):
            continue
        failures.extend(
            validate_instance(
                root,
                manifest,
                "schemas/benchmark_manifest.schema.json",
                f"{name} manifest",
            )
        )
        failures.extend(
            validate_instance(
                root,
                result,
                "schemas/benchmark_result.schema.json",
                f"{name} result",
            )
        )
        failures.extend(validate_executable_manifest(manifest, f"{name} manifest", expectation))

    if isinstance(benchmark_items.get("track_a_result"), dict):
        failures.extend(validate_track_a_result(benchmark_items["track_a_result"]))
    if isinstance(benchmark_items.get("track_b_result"), dict):
        failures.extend(validate_track_b_result(benchmark_items["track_b_result"]))
    if isinstance(benchmark_items.get("track_d_python_result"), dict):
        failures.extend(validate_track_d_python_result(benchmark_items["track_d_python_result"]))
    if isinstance(benchmark_items.get("track_d_rust_result"), dict):
        failures.extend(validate_track_d_rust_result(benchmark_items["track_d_rust_result"]))

    return failures


def mutate_remove_track_c(root: pathlib.Path):
    for rel in ["BENCHMARK_STRATEGY.md", "benchmarks/tracks.md"]:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        text = text.replace("Track `C`", "Track C")
        path.write_text(text, encoding="utf-8")


def mutate_remove_gate_k7(root: pathlib.Path):
    path = root / "benchmarks" / "success_failure_gates.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("| K7 | controlled human review finds `SCIR-H` materially less auditable than typed AST or source |\n", "", 1)
    path.write_text(text, encoding="utf-8")


def mutate_break_manifest_schema(root: pathlib.Path):
    path = root / "schemas" / "benchmark_manifest.schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["required"].remove("success_gates")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_negative_fixture(root: pathlib.Path, name: str, mutate, expected_markers):
    with tempfile.TemporaryDirectory(prefix="scir_benchmark_check_") as tmp:
        fixture_root = pathlib.Path(tmp) / "repo"
        shutil.copytree(root, fixture_root, ignore=shutil.ignore_patterns("__pycache__"))
        mutate(fixture_root)
        failures = run_checks(fixture_root)

    if not failures:
        return [f"benchmark self-test {name}: expected failure but dry run passed"]

    missing_markers = [
        marker for marker in expected_markers if not any(marker in failure for failure in failures)
    ]
    if missing_markers:
        return [
            f"benchmark self-test {name}: missing expected failure markers "
            f"{', '.join(missing_markers)}"
        ]

    return []


def run_self_tests(root: pathlib.Path):
    failures = []
    count = 0
    cases = [
        (
            "missing track marker",
            mutate_remove_track_c,
            ["missing track marker: Track `C`"],
        ),
        (
            "missing gate marker",
            mutate_remove_gate_k7,
            ["missing gate marker: K7"],
        ),
        (
            "benchmark manifest schema completeness",
            mutate_break_manifest_schema,
            [
                "schemas/benchmark_manifest.schema.json: missing required fields success_gates",
            ],
        ),
    ]

    for name, mutate, expected_markers in cases:
        count += 1
        failures.extend(run_negative_fixture(root, name, mutate, expected_markers))

    harness_failures, benchmark_items = run_benchmark_suite(root)
    if harness_failures or benchmark_items is None:
        return failures + ["benchmark self-test setup: executable benchmark harness must pass"], count
    baseline_failures = validate_executable_benchmark_items(root, benchmark_items)
    if baseline_failures:
        return failures + baseline_failures, count

    semantic_cases = [
        (
            "missing executable baselines",
            lambda items: items["track_b_manifest"].update({"baselines": ["SSA-like internal IR"]}),
            [
                "track_b manifest: missing executable baseline direct source",
                "track_b manifest: missing executable baseline typed-AST",
            ],
        ),
        (
            "track d rust baseline set",
            lambda items: items["track_d_rust_manifest"].update({"baselines": ["direct source", "typed-AST"]}),
            ["track_d_rust manifest: missing executable baseline SSA-like internal IR"],
        ),
        (
            "track a metric split",
            lambda items: items["track_a_result"]["metrics"].pop("aggregate_scir_to_source_ratio"),
            ["track_a result.metrics: missing required metric aggregate_scir_to_source_ratio"],
        ),
        (
            "track a kill gate",
            lambda items: items["track_a_result"]["metrics"].update({"median_scir_to_source_ratio": 1.6}),
            ["track_a result: status pass despite automated kill gate"],
        ),
        (
            "track b compile gate",
            lambda items: items["track_b_result"]["metrics"].update({"tier_a_compile_pass_rate": 0.5}),
            ["track_b result: status pass despite Tier A compile/test gate failure"],
        ),
        (
            "track d python s5 gate",
            lambda items: items["track_d_python_result"]["metrics"].update({"median_runtime_ratio": 1.6}),
            ["track_d_python result: gate_S5_pass must be derived from published Phase 6B ceilings"],
        ),
        (
            "track d rust observable gate",
            lambda items: items["track_d_rust_result"]["metrics"].update({"observable_match": False, "gate_K8_hit": False}),
            ["track_d_rust result: gate_K8_hit must fire when a reported runtime exceeds 2.0x or observables diverge"],
        ),
        (
            "unexpected track c artifact",
            lambda items: items.update({"track_c_result": {}}),
            ["benchmark bundle: unexpected executable artifact track_c_result"],
        ),
        (
            "unexpected d-js artifact",
            lambda items: items.update({"track_d_js_result": {}}),
            ["benchmark bundle: unexpected executable artifact track_d_js_result"],
        ),
    ]

    for name, mutate, expected_markers in semantic_cases:
        count += 1
        mutated_items = json.loads(json.dumps(benchmark_items))
        mutate(mutated_items)
        semantic_failures = validate_executable_benchmark_items(root, mutated_items)
        if not semantic_failures:
            failures.append(f"benchmark self-test {name}: expected failure but semantic validation passed")
            continue
        missing_markers = [
            marker for marker in expected_markers if not any(marker in failure for failure in semantic_failures)
        ]
        if missing_markers:
            failures.append(
                f"benchmark self-test {name}: missing expected failure markers "
                f"{', '.join(missing_markers)}"
            )

    return failures, count


def print_success(track_a_result, track_b_result, track_d_python_result, track_d_rust_result, self_test_count):
    print("[benchmark] benchmark harness passed")
    print(
        "Tracks, baselines, contamination controls, benchmark schemas, "
        "success/failure gates, and executable Track A/B/D benchmark runs are present."
    )
    print(
        "Track A status: "
        f"{track_a_result['status']} "
        f"(median SCIR/source ratio={track_a_result['metrics']['median_scir_to_source_ratio']}, "
        f"aggregate SCIR/source ratio={track_a_result['metrics']['aggregate_scir_to_source_ratio']}, "
        f"median SCIR/typed-AST ratio={track_a_result['metrics']['median_scir_to_typed_ast_ratio']})."
    )
    print(
        "Track B status: "
        f"{track_b_result['status']} "
        f"(Tier A compile={track_b_result['metrics']['tier_a_compile_pass_rate']}, "
        f"Tier A test={track_b_result['metrics']['tier_a_test_pass_rate']})."
    )
    print(
        "Track D Python status: "
        f"{track_d_python_result['status']} "
        f"(median runtime ratio={track_d_python_result['metrics']['median_runtime_ratio']}, "
        f"async overhead ratio={track_d_python_result['metrics']['async_overhead_ratio']})."
    )
    print(
        "Track D Rust status: "
        f"{track_d_rust_result['status']} "
        f"(median runtime ratio={track_d_rust_result['metrics']['median_runtime_ratio']}, "
        f"compile time ratio={track_d_rust_result['metrics']['compile_time_ratio']})."
    )
    print(f"Benchmark checker self-tests passed ({self_test_count} negative fixtures).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve() if args.root else pathlib.Path(__file__).resolve().parents[1]
    rust_resolution = resolve_rust_toolchain()
    failures = run_checks(root)
    if failures:
        print("[benchmark] doctrine dry run failed")
        for item in failures:
            print(f" - {item}")
        sys.exit(1)

    if not rust_resolution["available"]:
        print("[benchmark] executable benchmark harness unavailable")
        print(f" - Rust Track D requires a usable Rust toolchain: {rust_resolution['reason']}")
        sys.exit(1)

    self_test_failures, self_test_count = run_self_tests(root)
    if self_test_failures:
        print("[benchmark] doctrine self-tests failed")
        for item in self_test_failures:
            print(f" - {item}")
        sys.exit(1)

    harness_failures, benchmark_items = run_benchmark_suite(root)
    if harness_failures:
        print("[benchmark] executable benchmark harness failed")
        for item in harness_failures:
            print(f" - {item}")
        sys.exit(1)

    bundle_failures = validate_executable_benchmark_items(root, benchmark_items)
    if bundle_failures:
        print("[benchmark] executable benchmark bundle validation failed")
        for item in bundle_failures:
            print(f" - {item}")
        sys.exit(1)

    print_success(
        benchmark_items["track_a_result"],
        benchmark_items["track_b_result"],
        benchmark_items["track_d_python_result"],
        benchmark_items["track_d_rust_result"],
        self_test_count,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
