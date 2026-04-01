#!/usr/bin/env python3
import argparse
import json
import pathlib
import shutil
import sys
import tempfile

from scir_h_bootstrap_model import ScirHModelError, format_module, parse_module
from scir_rust_bootstrap import (
    CASE_CONFIG,
    CARGO_TOML,
    SOURCE_TEXTS,
    TEST_TEXTS,
    ImporterError,
    SCIRH_MODULES,
    VALIDATOR_NAME,
    build_bundle,
)
from validate_repo_contracts import collect_instance_validation_errors


FIXTURE_ROOT = pathlib.Path("tests") / "rust_importer" / "cases"

CASE_EXPECTATIONS = {
    "a_mut_local": {
        "tier": "A",
        "status": "pass",
        "validator": VALIDATOR_NAME,
        "profiles": ["R"],
        "dependencies": ["rust:std"],
        "exports": ["clamp_nonneg"],
        "opaque_boundary_count": 0,
        "summary": {"A": 3, "B": 0, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "require_smoke_test": True,
        "diagnostic_severities": [],
        "scirh_markers": [
            "module fixture.rust_importer.a_mut_local",
            "fn clamp_nonneg x int -> int !write",
            "var y int x",
            "if lt y 0",
        ],
    },
    "a_struct_field_borrow_mut": {
        "tier": "A",
        "status": "pass",
        "validator": VALIDATOR_NAME,
        "profiles": ["R"],
        "dependencies": ["rust:std"],
        "exports": ["Counter", "clamp_counter"],
        "opaque_boundary_count": 0,
        "summary": {"A": 3, "B": 0, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "require_smoke_test": True,
        "diagnostic_severities": [],
        "scirh_markers": [
            "module fixture.rust_importer.a_struct_field_borrow_mut",
            "type Counter record { value int }",
            "fn clamp_counter counter borrow_mut<Counter> -> int !write",
            "set counter.value 0",
        ],
    },
    "a_async_await": {
        "tier": "A",
        "status": "pass",
        "validator": VALIDATOR_NAME,
        "profiles": ["R"],
        "dependencies": ["rust:std"],
        "exports": ["load_once"],
        "opaque_boundary_count": 0,
        "summary": {"A": 2, "B": 0, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "require_smoke_test": True,
        "diagnostic_severities": [],
        "scirh_markers": [
            "module fixture.rust_importer.a_async_await",
            "async fn fetch_value -> int !",
            "async fn load_once -> int !await",
            "return await fetch_value()",
        ],
    },
    "c_unsafe_call": {
        "tier": "C",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["N"],
        "dependencies": ["rust:std"],
        "exports": ["call_unsafe_ping"],
        "opaque_boundary_count": 1,
        "summary": {"A": 1, "B": 0, "C": 1, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": True,
        "require_smoke_test": False,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.rust_importer.c_unsafe_call",
            "import sym unsafe_ping rust:unsafe_ping",
            "!opaque,unsafe",
        ],
    },
    "d_proc_macro": {
        "tier": "D",
        "status": "fail",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "N"],
        "dependencies": ["rust:std"],
        "exports": ["MacroDriven"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 0, "C": 0, "D": 1},
        "require_scirh": False,
        "require_opaque_boundary": False,
        "require_smoke_test": False,
        "diagnostic_severities": ["error"],
        "scirh_markers": [],
    },
    "d_self_ref_pin": {
        "tier": "D",
        "status": "fail",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "N"],
        "dependencies": ["rust:std"],
        "exports": ["SelfRef", "make_self_ref"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 0, "C": 0, "D": 1},
        "require_scirh": False,
        "require_opaque_boundary": False,
        "require_smoke_test": False,
        "diagnostic_severities": ["error"],
        "scirh_markers": [],
    },
}

COMMON_JSON_ARTIFACTS = {
    "module_manifest.json": "schemas/module_manifest.schema.json",
    "feature_tier_report.json": "schemas/feature_tier_report.schema.json",
    "validation_report.json": "schemas/validation_report.schema.json",
}

OPAQUE_BOUNDARY_REL = "opaque_boundary_contract.json"
SCIRH_REL = "expected.scirh"


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(root: pathlib.Path, relative_path: str):
    return load_json(root / relative_path)


def validate_json_against_schema(root: pathlib.Path, json_path: pathlib.Path, schema_rel: str):
    schema = load_schema(root, schema_rel)
    instance = load_json(json_path)
    failures = []
    for location, message in collect_instance_validation_errors(instance, schema):
        failures.append(f"{json_path.relative_to(root)} {location}: {message}")
    return instance, failures


def summarize_item_tiers(items):
    summary = {"A": 0, "B": 0, "C": 0, "D": 0}
    for item in items:
        tier = item.get("tier")
        if tier in summary:
            summary[tier] += 1
    return summary


def expected_cargo_text(case_name: str) -> str:
    return CARGO_TOML.format(crate_name=case_name)


def check_case(root: pathlib.Path, case_name: str, expectation: dict):
    failures = []
    case_dir = root / FIXTURE_ROOT / case_name
    if not case_dir.exists():
        return [f"missing fixture case directory: {case_dir.relative_to(root)}"]

    input_dir = case_dir / "input"
    expected_paths = {
        input_dir / "Cargo.toml",
        input_dir / "src" / "lib.rs",
        case_dir / "module_manifest.json",
        case_dir / "feature_tier_report.json",
        case_dir / "validation_report.json",
    }
    if expectation["require_scirh"]:
        expected_paths.add(case_dir / SCIRH_REL)
    if expectation["require_opaque_boundary"]:
        expected_paths.add(case_dir / OPAQUE_BOUNDARY_REL)
    if expectation["require_smoke_test"]:
        expected_paths.add(input_dir / "tests" / "smoke.rs")

    actual_files = {
        path for path in case_dir.rglob("*") if path.is_file()
    }
    missing_files = sorted(path.relative_to(case_dir).as_posix() for path in expected_paths - actual_files)
    unexpected_files = sorted(path.relative_to(case_dir).as_posix() for path in actual_files - expected_paths)
    for name in missing_files:
        failures.append(f"{case_dir.relative_to(root)}: missing required file {name}")
    for name in unexpected_files:
        failures.append(f"{case_dir.relative_to(root)}: unexpected file {name}")

    cargo_path = input_dir / "Cargo.toml"
    if cargo_path.exists() and cargo_path.read_text(encoding="utf-8") != expected_cargo_text(case_name):
        failures.append(f"{cargo_path.relative_to(root)}: unexpected Cargo.toml contents")

    source_path = input_dir / "src" / "lib.rs"
    if source_path.exists() and source_path.read_text(encoding="utf-8") != SOURCE_TEXTS[case_name]:
        failures.append(f"{source_path.relative_to(root)}: unexpected source fixture contents")

    test_path = input_dir / "tests" / "smoke.rs"
    if expectation["require_smoke_test"]:
        if test_path.exists() and test_path.read_text(encoding="utf-8") != TEST_TEXTS[case_name]:
            failures.append(f"{test_path.relative_to(root)}: unexpected smoke test contents")
    elif test_path.exists():
        failures.append(f"{test_path.relative_to(root)}: unexpected smoke test for non-round-trip case")

    manifest_instance = None
    feature_instance = None
    validation_instance = None

    for artifact_name, schema_rel in COMMON_JSON_ARTIFACTS.items():
        artifact_path = case_dir / artifact_name
        if artifact_path.exists():
            instance, artifact_failures = validate_json_against_schema(root, artifact_path, schema_rel)
            failures.extend(artifact_failures)
            if artifact_name == "module_manifest.json":
                manifest_instance = instance
            elif artifact_name == "feature_tier_report.json":
                feature_instance = instance
            elif artifact_name == "validation_report.json":
                validation_instance = instance

    source_rel = (FIXTURE_ROOT / case_name / "input" / "src" / "lib.rs").as_posix()
    expected_module_id = f"fixture.rust_importer.{case_name}"

    if manifest_instance is not None:
        if manifest_instance.get("module_id") != expected_module_id:
            failures.append(f"{case_name} module_manifest: expected module_id {expected_module_id!r}")
        if manifest_instance.get("layer") != "scir_h":
            failures.append(f"{case_name} module_manifest: expected layer 'scir_h'")
        if manifest_instance.get("source_language") != "rust":
            failures.append(f"{case_name} module_manifest: expected source_language 'rust'")
        if manifest_instance.get("source_path") != source_rel:
            failures.append(f"{case_name} module_manifest: expected source_path {source_rel!r}")
        if manifest_instance.get("declared_profiles") != expectation["profiles"]:
            failures.append(f"{case_name} module_manifest: expected declared_profiles {expectation['profiles']!r}")
        if manifest_instance.get("declared_tier") != expectation["tier"]:
            failures.append(f"{case_name} module_manifest: expected declared_tier {expectation['tier']!r}")
        if manifest_instance.get("dependencies") != expectation["dependencies"]:
            failures.append(f"{case_name} module_manifest: expected dependencies {expectation['dependencies']!r}")
        if manifest_instance.get("exports") != expectation["exports"]:
            failures.append(f"{case_name} module_manifest: expected exports {expectation['exports']!r}")
        if manifest_instance.get("opaque_boundary_count") != expectation["opaque_boundary_count"]:
            failures.append(
                f"{case_name} module_manifest: expected opaque_boundary_count {expectation['opaque_boundary_count']}"
            )

    if feature_instance is not None:
        if feature_instance.get("subject") != expected_module_id:
            failures.append(f"{case_name} feature_tier_report: expected subject {expected_module_id!r}")
        if feature_instance.get("source_language") != "rust":
            failures.append(f"{case_name} feature_tier_report: expected source_language 'rust'")
        if feature_instance.get("summary") != expectation["summary"]:
            failures.append(f"{case_name} feature_tier_report: expected summary {expectation['summary']!r}")
        derived_summary = summarize_item_tiers(feature_instance.get("items", []))
        if derived_summary != feature_instance.get("summary"):
            failures.append(f"{case_name} feature_tier_report: summary does not match tier items")

    if validation_instance is not None:
        if validation_instance.get("artifact") != expected_module_id:
            failures.append(f"{case_name} validation_report: expected artifact {expected_module_id!r}")
        if validation_instance.get("layer") != "scir_h":
            failures.append(f"{case_name} validation_report: expected layer 'scir_h'")
        if validation_instance.get("validator") != expectation["validator"]:
            failures.append(f"{case_name} validation_report: expected validator {expectation['validator']!r}")
        if validation_instance.get("status") != expectation["status"]:
            failures.append(f"{case_name} validation_report: expected status {expectation['status']!r}")
        actual_severities = [diagnostic.get("severity") for diagnostic in validation_instance.get("diagnostics", [])]
        if actual_severities != expectation["diagnostic_severities"]:
            failures.append(
                f"{case_name} validation_report: expected diagnostic severities {expectation['diagnostic_severities']!r}"
            )

    scirh_path = case_dir / SCIRH_REL
    if expectation["require_scirh"] and scirh_path.exists():
        scirh_text = scirh_path.read_text(encoding="utf-8")
        try:
            parsed = parse_module(scirh_text)
        except ScirHModelError as exc:
            failures.append(f"{scirh_path.relative_to(root)}: parse failure: {exc}")
        else:
            expected_model = SCIRH_MODULES[case_name]
            if parsed != expected_model:
                failures.append(f"{scirh_path.relative_to(root)}: parsed model drifted from canonical Rust bootstrap model")
            if format_module(parsed) != scirh_text:
                failures.append(f"{scirh_path.relative_to(root)}: text is not canonical under parse-normalize-format")
        for marker in expectation["scirh_markers"]:
            if marker not in scirh_text:
                failures.append(f"{scirh_path.relative_to(root)}: missing canonical marker {marker!r}")

    opaque_path = case_dir / OPAQUE_BOUNDARY_REL
    if expectation["require_opaque_boundary"] and opaque_path.exists():
        _, opaque_failures = validate_json_against_schema(root, opaque_path, "schemas/opaque_boundary_contract.schema.json")
        failures.extend(opaque_failures)
    if not expectation["require_opaque_boundary"] and opaque_path.exists():
        failures.append(f"{opaque_path.relative_to(root)}: unexpected opaque boundary contract")

    return failures


def validate_fixtures(root: pathlib.Path):
    failures = []
    expected_cases = set(CASE_EXPECTATIONS)
    actual_cases = {
        path.name
        for path in (root / FIXTURE_ROOT).iterdir()
        if path.is_dir()
    }
    for case_name in sorted(expected_cases - actual_cases):
        failures.append(f"{FIXTURE_ROOT.as_posix()}: missing fixture case {case_name}")
    for case_name in sorted(actual_cases - expected_cases):
        failures.append(f"{FIXTURE_ROOT.as_posix()}: unexpected fixture case {case_name}")
    for case_name in sorted(expected_cases & actual_cases):
        failures.extend(check_case(root, case_name, CASE_EXPECTATIONS[case_name]))
    return failures


def compare_generated_to_goldens(root: pathlib.Path):
    failures = []
    for case_name in sorted(CASE_EXPECTATIONS):
        source_path = root / FIXTURE_ROOT / case_name / "input" / "src" / "lib.rs"
        try:
            bundle = build_bundle(root, source_path)
        except ImporterError as exc:
            failures.append(f"{case_name}: importer failed for fixture source: {exc}")
            continue
        expected_files = {}
        for path in (root / FIXTURE_ROOT / case_name).iterdir():
            if path.is_file():
                expected_files[path.name] = path.read_text(encoding="utf-8")
        if bundle.files != expected_files:
            failures.append(f"{case_name}: generated bundle drifted from checked-in golden artifacts")
    return failures


def run_self_tests(root: pathlib.Path):
    failures = []
    source_path = root / FIXTURE_ROOT / "a_mut_local" / "input" / "src" / "lib.rs"
    original = source_path.read_text(encoding="utf-8")
    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="rust-importer-conformance-"))
    try:
        broken_source = temp_dir / "tests" / "rust_importer" / "cases" / "a_mut_local" / "input" / "src" / "lib.rs"
        broken_source.parent.mkdir(parents=True, exist_ok=True)
        broken_source.write_text(original.replace("y = 0;", "y = 1;"), encoding="utf-8")
        cargo_path = broken_source.parents[1] / "Cargo.toml"
        cargo_path.write_text(expected_cargo_text("a_mut_local"), encoding="utf-8")
        test_path = broken_source.parents[1] / "tests" / "smoke.rs"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(TEST_TEXTS["a_mut_local"], encoding="utf-8")
        try:
            build_bundle(temp_dir, broken_source)
            failures.append("self-test source drift: expected importer failure")
        except ImporterError as exc:
            if "checked-in bootstrap fixture text" not in str(exc):
                failures.append(f"self-test source drift: unexpected error {exc}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    bogus_scirh = "module fixture.rust_importer.a_mut_local\nfn clamp_nonneg x int -> int !write\n  set counter..value 0\n"
    try:
        parse_module(bogus_scirh)
        failures.append("self-test bogus scirh: expected parse failure")
    except ScirHModelError:
        pass
    return failures


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["validate-fixtures", "test"])
    parser.add_argument("--root")
    return parser.parse_args()


def main():
    args = parse_args()
    root = pathlib.Path(args.root).resolve() if args.root else pathlib.Path(__file__).resolve().parents[1]
    failures = []

    if not (root / FIXTURE_ROOT).exists():
        print(f"[{args.mode}] missing fixture root {(root / FIXTURE_ROOT)}")
        sys.exit(1)

    failures.extend(validate_fixtures(root))
    if args.mode == "test":
        failures.extend(compare_generated_to_goldens(root))
        failures.extend(run_self_tests(root))

    if failures:
        print(f"[{args.mode}] Rust importer conformance failed")
        for item in failures:
            print(f" - {item}")
        sys.exit(1)

    print(f"[{args.mode}] Rust importer conformance passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
