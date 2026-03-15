#!/usr/bin/env python3
import argparse
import json
import pathlib
import shutil
import tempfile
import sys

REQUIRED_FILES = [
    "BENCHMARK_STRATEGY.md",
    "benchmarks/README.md",
    "benchmarks/tracks.md",
    "benchmarks/baselines.md",
    "benchmarks/contamination_controls.md",
    "benchmarks/success_failure_gates.md",
    "schemas/benchmark_manifest.schema.json",
    "schemas/benchmark_result.schema.json",
]

REQUIRED_TRACK_MARKERS = ["Track `A`", "Track `B`", "Track `C`", "Track `D`"]
REQUIRED_GATE_MARKERS = ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4", "K5", "K6", "K7"]
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
                "items": {"enum": ["R", "N", "P", "D"]},
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
            "profile": {"enum": ["R", "N", "P", "D"]},
            "metrics": {"type": "object"},
            "baseline_comparison": {"type": "object"},
            "status": {"enum": ["pass", "mixed", "fail"]},
        },
    },
}


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


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
    failures.extend(check_contamination_markers(root))
    failures.extend(check_schema_expectations(root))
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
        failures.extend(run_negative_fixture(root, name, mutate, expected_markers))

    return failures


def print_success():
    print("[benchmark] doctrine dry run passed")
    print(
        "Tracks, baselines, contamination controls, benchmark schemas, "
        "and success/failure gates are present."
    )
    print("Benchmark checker self-tests passed (3 negative fixtures).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve() if args.root else pathlib.Path(__file__).resolve().parents[1]
    failures = run_checks(root)
    if failures:
        print("[benchmark] doctrine dry run failed")
        for item in failures:
            print(f" - {item}")
        sys.exit(1)

    self_test_failures = run_self_tests(root)
    if self_test_failures:
        print("[benchmark] doctrine self-tests failed")
        for item in self_test_failures:
            print(f" - {item}")
        sys.exit(1)

    print_success()
    sys.exit(0)


if __name__ == "__main__":
    main()
