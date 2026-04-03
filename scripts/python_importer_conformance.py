#!/usr/bin/env python3
"""Conformance checker for checked-in Python importer bundles.

These checks enforce that the fixed Python fixture outputs still match the
importer contract, canonical `SCIR-H`, boundary accounting, and schema-backed
report surfaces. This is governance validation, not a generic golden-file diff.
"""
import argparse
import json
import pathlib
import shutil
import sys
import tempfile

from scir_h_bootstrap_model import ScirHModelError, format_module, parse_module
from scir_python_bootstrap import ImporterError, VALIDATOR_NAME, build_bundle
from validate_repo_contracts import (
    collect_instance_validation_errors,
    validate_boundary_capability_contract,
)


FIXTURE_ROOT = pathlib.Path("tests") / "python_importer" / "cases"

CASE_EXPECTATIONS = {
    "a_basic_function": {
        "tier": "A",
        "status": "pass",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["clamp_nonneg"],
        "opaque_boundary_count": 0,
        "summary": {"A": 3, "B": 0, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": [],
        "scirh_markers": [
            "module fixture.python_importer.a_basic_function",
            "fn clamp_nonneg x int -> int !write",
            "var y int x",
            "if lt y 0",
        ],
    },
    "a_async_await": {
        "tier": "A",
        "status": "pass",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["fetch_value", "load_once"],
        "opaque_boundary_count": 0,
        "summary": {"A": 2, "B": 0, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": [],
        "scirh_markers": [
            "module fixture.python_importer.a_async_await",
            "async fn fetch_value -> int !",
            "async fn load_once -> int !await",
            "return await fetch_value()",
        ],
    },
    "b_if_else_return": {
        "tier": "B",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["choose_zero_or_x"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 1, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.python_importer.b_if_else_return",
            "fn choose_zero_or_x x int -> int !",
            "if lt x 0",
            "else",
        ],
    },
    "b_direct_call": {
        "tier": "A",
        "status": "pass",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["identity", "call_identity"],
        "opaque_boundary_count": 0,
        "summary": {"A": 1, "B": 0, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": [],
        "scirh_markers": [
            "module fixture.python_importer.b_direct_call",
            "fn identity x int -> int !",
            "fn call_identity x int -> int !",
            "return identity(x)",
        ],
    },
    "b_async_arg_await": {
        "tier": "B",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["fetch_value", "load_value"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 1, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.python_importer.b_async_arg_await",
            "async fn fetch_value x int -> int !",
            "async fn load_value x int -> int !await",
            "return await fetch_value(x)",
        ],
    },
    "b_while_call_update": {
        "tier": "B",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["step_until_nonneg"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 2, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.python_importer.b_while_call_update",
            "fn step_until_nonneg step Callable x int -> int !write",
            "var current int x",
            "loop loop0",
            "set current step(current)",
            "return current",
            "break loop0",
        ],
    },
    "b_while_break_continue": {
        "tier": "B",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["step_with_escape"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 3, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.python_importer.b_while_break_continue",
            "fn step_with_escape step Callable x int -> int !write",
            "var current int x",
            "loop loop0",
            "if eq current -1",
            "break loop0",
            "set current step(current)",
            "continue loop0",
            "return current",
        ],
    },
    "b_class_init_method": {
        "tier": "B",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["Counter", "Counter__init__", "Counter__get"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 2, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.python_importer.b_class_init_method",
            "type Counter record { value int }",
            "fn Counter__init__ self Counter value int -> Counter !write",
            "set self.value value",
            "fn Counter__get self Counter -> int !",
            "return self.value",
        ],
    },
    "b_class_field_update": {
        "tier": "B",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["Counter", "Counter__init__", "Counter__bump"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 2, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.python_importer.b_class_field_update",
            "type Counter record { value int }",
            "fn Counter__init__ self Counter value int -> Counter !write",
            "fn Counter__bump self Counter step Callable -> int !write",
            "set self.value step(self.value)",
            "return self.value",
        ],
    },
    "c_opaque_call": {
        "tier": "C",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["D-PY"],
        "dependencies": ["python:foreign_api", "capability:foreign_api_ping"],
        "exports": ["ping"],
        "opaque_boundary_count": 1,
        "summary": {"A": 1, "B": 0, "C": 1, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": True,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.python_importer.c_opaque_call",
            "import sym foreign_api_ping",
            "opaque<ForeignResult>",
        ],
    },
    "d_exec_eval": {
        "tier": "D",
        "status": "fail",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["run"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 0, "C": 0, "D": 1},
        "require_scirh": False,
        "require_opaque_boundary": False,
        "diagnostic_severities": ["error"],
        "scirh_markers": [],
    },
    "d_try_except": {
        "tier": "B",
        "status": "warn",
        "validator": VALIDATOR_NAME,
        "profiles": ["R", "D-PY"],
        "dependencies": ["python:builtins"],
        "exports": ["guard"],
        "opaque_boundary_count": 0,
        "summary": {"A": 0, "B": 1, "C": 0, "D": 0},
        "require_scirh": True,
        "require_opaque_boundary": False,
        "diagnostic_severities": ["warn"],
        "scirh_markers": [
            "module fixture.python_importer.d_try_except",
            "fn guard may_fail Callable x int -> int !throw",
            "try",
            "catch err ValueError",
        ],
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


def check_case(root: pathlib.Path, case_name: str, expectation: dict):
    """Validate one fixture against the importer contract, tier expectations, and boundary doctrine."""

    failures = []
    case_dir = root / FIXTURE_ROOT / case_name
    if not case_dir.exists():
        return [f"missing fixture case directory: {case_dir.relative_to(root)}"]

    expected_files = {
        "source.py",
        "module_manifest.json",
        "feature_tier_report.json",
        "validation_report.json",
    }
    if expectation["require_scirh"]:
        expected_files.add(SCIRH_REL)
    if expectation["require_opaque_boundary"]:
        expected_files.add(OPAQUE_BOUNDARY_REL)

    actual_files = {
        path.name for path in case_dir.iterdir() if path.is_file()
    }

    missing_files = sorted(expected_files - actual_files)
    unexpected_files = sorted(actual_files - expected_files)
    for name in missing_files:
        failures.append(f"{case_dir.relative_to(root)}: missing required file {name}")
    for name in unexpected_files:
        failures.append(f"{case_dir.relative_to(root)}: unexpected file {name}")

    source_rel = FIXTURE_ROOT / case_name / "source.py"
    source_path = root / source_rel
    if source_path.exists() and not source_path.read_text(encoding="utf-8").strip():
        failures.append(f"{source_rel}: source fixture must not be empty")

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

    if manifest_instance is not None:
        expected_module_id = f"fixture.python_importer.{case_name}"
        if manifest_instance.get("module_id") != expected_module_id:
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected module_id {expected_module_id!r}"
            )
        if manifest_instance.get("layer") != "scir_h":
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected layer 'scir_h'"
            )
        if manifest_instance.get("source_language") != "python":
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected source_language 'python'"
            )
        if manifest_instance.get("source_path") != source_rel.as_posix():
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected source_path {source_rel.as_posix()!r}"
            )
        if manifest_instance.get("declared_profiles") != expectation["profiles"]:
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected declared_profiles {expectation['profiles']!r}"
            )
        if manifest_instance.get("declared_tier") != expectation["tier"]:
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected declared_tier {expectation['tier']!r}"
            )
        if manifest_instance.get("dependencies") != expectation["dependencies"]:
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected dependencies {expectation['dependencies']!r}"
            )
        if manifest_instance.get("exports") != expectation["exports"]:
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected exports {expectation['exports']!r}"
            )
        if manifest_instance.get("opaque_boundary_count") != expectation["opaque_boundary_count"]:
            failures.append(
                f"{source_rel.parent / 'module_manifest.json'}: expected opaque_boundary_count {expectation['opaque_boundary_count']}"
            )

    if feature_instance is not None:
        expected_module_id = f"fixture.python_importer.{case_name}"
        feature_path = source_rel.parent / "feature_tier_report.json"
        if feature_instance.get("subject") != expected_module_id:
            failures.append(f"{feature_path}: expected subject {expected_module_id!r}")
        if feature_instance.get("source_language") != "python":
            failures.append(f"{feature_path}: expected source_language 'python'")
        if feature_instance.get("summary") != expectation["summary"]:
            failures.append(
                f"{feature_path}: expected summary {expectation['summary']!r}"
            )
        derived_summary = summarize_item_tiers(feature_instance.get("items", []))
        if derived_summary != feature_instance.get("summary"):
            failures.append(
                f"{feature_path}: summary does not match the tiers present in items"
            )

    if validation_instance is not None:
        expected_module_id = f"fixture.python_importer.{case_name}"
        validation_path = source_rel.parent / "validation_report.json"
        if validation_instance.get("artifact") != expected_module_id:
            failures.append(f"{validation_path}: expected artifact {expected_module_id!r}")
        if validation_instance.get("layer") != "scir_h":
            failures.append(f"{validation_path}: expected layer 'scir_h'")
        if validation_instance.get("validator") != expectation["validator"]:
            failures.append(
                f"{validation_path}: expected validator {expectation['validator']!r}"
            )
        if validation_instance.get("status") != expectation["status"]:
            failures.append(
                f"{validation_path}: expected status {expectation['status']!r}"
            )
        actual_severities = [
            diagnostic.get("severity")
            for diagnostic in validation_instance.get("diagnostics", [])
        ]
        if actual_severities != expectation["diagnostic_severities"]:
            failures.append(
                f"{validation_path}: expected diagnostic severities {expectation['diagnostic_severities']!r}"
            )

    scirh_path = case_dir / SCIRH_REL
    if expectation["require_scirh"]:
        if scirh_path.exists():
            text = scirh_path.read_text(encoding="utf-8").strip()
            if not text:
                failures.append(f"{source_rel.parent / SCIRH_REL}: expected non-empty SCIR-H text")
            elif not text.startswith("module "):
                failures.append(
                    f"{source_rel.parent / SCIRH_REL}: expected SCIR-H text to begin with 'module '"
                )
            else:
                try:
                    parsed = parse_module(text + "\n")
                except ScirHModelError as exc:
                    failures.append(
                        f"{source_rel.parent / SCIRH_REL}: canonical SCIR-H parse failed: {exc}"
                    )
                else:
                    if format_module(parsed).strip() != text:
                        failures.append(
                            f"{source_rel.parent / SCIRH_REL}: SCIR-H text is not canonical under parse-normalize-format"
                        )
            for marker in expectation["scirh_markers"]:
                if marker not in text:
                    failures.append(
                        f"{source_rel.parent / SCIRH_REL}: missing marker {marker!r}"
                    )
    elif scirh_path.exists():
        failures.append(
            f"{source_rel.parent / SCIRH_REL}: Tier D fixtures must not include canonical SCIR-H"
        )

    opaque_contract_path = case_dir / OPAQUE_BOUNDARY_REL
    contract_instance = None
    if expectation["require_opaque_boundary"]:
        if opaque_contract_path.exists():
            contract_instance, contract_failures = validate_json_against_schema(
                root,
                opaque_contract_path,
                "schemas/opaque_boundary_contract.schema.json",
            )
            failures.extend(contract_failures)
            if contract_instance.get("kind") != "opaque_call":
                failures.append(
                    f"{source_rel.parent / OPAQUE_BOUNDARY_REL}: expected kind 'opaque_call'"
                )
            if "opaque" not in contract_instance.get("effects", []):
                failures.append(
                    f"{source_rel.parent / OPAQUE_BOUNDARY_REL}: expected effects to include 'opaque'"
                )
        else:
            failures.append(
                f"{source_rel.parent}: missing required file {OPAQUE_BOUNDARY_REL}"
            )
    elif opaque_contract_path.exists():
        failures.append(
            f"{source_rel.parent / OPAQUE_BOUNDARY_REL}: only Tier C fixtures may include opaque boundary contracts"
        )

    failures.extend(
        validate_boundary_capability_contract(
            manifest_instance,
            contract_instance,
            label=str(source_rel.parent),
            allow_capabilities=expectation["require_opaque_boundary"],
        )
    )

    return failures


def compare_generated_bundle(root: pathlib.Path, case_name: str, expectation: dict):
    """Regenerate one bundle and require byte-stable agreement with the checked-in contract artifacts."""

    failures = []
    case_dir = root / FIXTURE_ROOT / case_name
    try:
        bundle = build_bundle(root, case_dir / "source.py")
    except ImporterError as exc:
        return [f"{case_dir.relative_to(root)}: executable importer rejected fixture: {exc}"]

    expected_names = sorted(
        name for name in case_dir.iterdir()
        if name.is_file() and name.name != "source.py"
    )
    generated_names = sorted(bundle.files)
    expected_file_names = [path.name for path in expected_names]
    if generated_names != expected_file_names:
        failures.append(
            f"{case_dir.relative_to(root)}: generated artifact set {generated_names!r} "
            f"did not match checked-in artifacts {expected_file_names!r}"
        )
        return failures

    for path in expected_names:
        generated_text = bundle.files[path.name]
        if path.suffix == ".json":
            expected_json = load_json(path)
            generated_json = json.loads(generated_text)
            if expected_json != generated_json:
                failures.append(
                    f"{path.relative_to(root)}: generated JSON bundle did not match checked-in fixture"
                )
        else:
            expected_text = path.read_text(encoding="utf-8")
            if generated_text != expected_text:
                failures.append(
                    f"{path.relative_to(root)}: generated text bundle did not match checked-in fixture"
                )

    return failures


def run_checks(root: pathlib.Path):
    """Run positive and negative conformance checks over the fixed Python importer corpus."""

    failures = []
    fixture_root = root / FIXTURE_ROOT
    if not fixture_root.exists():
        return [f"missing fixture root: {FIXTURE_ROOT.as_posix()}"]

    actual_case_names = sorted(
        path.name for path in fixture_root.iterdir() if path.is_dir()
    )
    expected_case_names = sorted(CASE_EXPECTATIONS)
    if actual_case_names != expected_case_names:
        failures.append(
            f"{FIXTURE_ROOT.as_posix()}: expected case directories {expected_case_names!r}"
        )

    for case_name, expectation in CASE_EXPECTATIONS.items():
        failures.extend(check_case(root, case_name, expectation))
        failures.extend(compare_generated_bundle(root, case_name, expectation))

    return failures


def mutate_remove_a_scirh(root: pathlib.Path):
    (root / FIXTURE_ROOT / "a_basic_function" / SCIRH_REL).unlink()


def mutate_remove_c_opaque_contract(root: pathlib.Path):
    (root / FIXTURE_ROOT / "c_opaque_call" / OPAQUE_BOUNDARY_REL).unlink()


def mutate_add_d_scirh(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "d_exec_eval" / SCIRH_REL
    path.write_text(
        "module fixture.python_importer.d_exec_eval {\n}\n",
        encoding="utf-8",
    )


def mutate_break_generated_golden(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "a_basic_function" / "validation_report.json"
    data = load_json(path)
    data["validator"] = "drifted-importer"
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_break_scirh_canonicality(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "a_basic_function" / SCIRH_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("var y int x", "var y: int = x"), encoding="utf-8")


def mutate_break_b_else_structure(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "b_if_else_return" / SCIRH_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("  else\n", ""), encoding="utf-8")


def mutate_break_b_direct_call_shape(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "b_direct_call" / SCIRH_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("return identity(x)", "return call identity(x)"), encoding="utf-8")


def mutate_break_b_async_await_shape(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "b_async_arg_await" / SCIRH_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("return await fetch_value(x)", "return fetch_value(x)"), encoding="utf-8")


def mutate_break_b_while_loop_shape(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "b_while_call_update" / SCIRH_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("loop loop0", "while loop0"), encoding="utf-8")


def mutate_break_b_while_continue_marker(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "b_while_break_continue" / SCIRH_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("continue loop0", "break loop0"), encoding="utf-8")


def mutate_break_b_class_field_place(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "b_class_init_method" / SCIRH_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("self.value", "self_value"), encoding="utf-8")


def mutate_break_b_class_update_call_shape(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "b_class_field_update" / SCIRH_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("step(self.value)", "call step(self.value)"), encoding="utf-8")


def mutate_remove_boundary_capability_import(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "c_opaque_call" / "module_manifest.json"
    data = load_json(path)
    data["dependencies"] = ["python:foreign_api"]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_add_unused_boundary_capability_import(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "c_opaque_call" / "module_manifest.json"
    data = load_json(path)
    data["dependencies"].append("capability:unused_boundary")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def mutate_add_illegal_capability_import_to_tier_a(root: pathlib.Path):
    path = root / FIXTURE_ROOT / "a_basic_function" / "module_manifest.json"
    data = load_json(path)
    data["dependencies"].append("capability:foreign_api_ping")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_negative_fixture(root: pathlib.Path, name: str, mutate, expected_markers):
    with tempfile.TemporaryDirectory(prefix="scir_python_fixture_") as tmp:
        fixture_root = pathlib.Path(tmp) / "repo"
        shutil.copytree(root, fixture_root, ignore=shutil.ignore_patterns("__pycache__"))
        mutate(fixture_root)
        failures = run_checks(fixture_root)

    if not failures:
        return [f"self-test {name}: expected failure but conformance passed"]

    missing_markers = [
        marker for marker in expected_markers if not any(marker in failure for failure in failures)
    ]
    if missing_markers:
        return [
            f"self-test {name}: missing expected failure markers {', '.join(missing_markers)}"
        ]

    return []


def run_self_tests(root: pathlib.Path):
    failures = []
    cases = [
        (
            "missing A-tier SCIR-H",
            mutate_remove_a_scirh,
            ["a_basic_function", "expected.scirh"],
        ),
        (
            "missing C-tier opaque contract",
            mutate_remove_c_opaque_contract,
            ["c_opaque_call", "opaque_boundary_contract.json"],
        ),
        (
            "unexpected D-tier SCIR-H",
            mutate_add_d_scirh,
            ["d_exec_eval", "Tier D fixtures must not include canonical SCIR-H"],
        ),
        (
            "generated bundle drift",
            mutate_break_generated_golden,
            ["a_basic_function", "generated JSON bundle did not match checked-in fixture"],
        ),
        (
            "non-canonical SCIR-H golden",
            mutate_break_scirh_canonicality,
            ["a_basic_function", "canonical SCIR-H parse failed"],
        ),
        (
            "if/else importer-only golden lost else structure",
            mutate_break_b_else_structure,
            ["b_if_else_return", "generated text bundle did not match checked-in fixture"],
        ),
        (
            "direct-call importer-only golden lost local call shape",
            mutate_break_b_direct_call_shape,
            ["b_direct_call", "canonical SCIR-H parse failed"],
        ),
        (
            "async importer-only golden lost await shape",
            mutate_break_b_async_await_shape,
            ["b_async_arg_await", "missing marker 'return await fetch_value(x)'"],
        ),
        (
            "while importer-only golden lost loop syntax",
            mutate_break_b_while_loop_shape,
            ["b_while_call_update", "canonical SCIR-H parse failed"],
        ),
        (
            "while importer-only golden lost continue marker",
            mutate_break_b_while_continue_marker,
            ["b_while_break_continue", "generated text bundle did not match checked-in fixture"],
        ),
        (
            "class importer-only golden lost field-place syntax",
            mutate_break_b_class_field_place,
            ["b_class_init_method", "missing marker 'set self.value value'"],
        ),
        (
            "class importer-only update golden lost local call shape",
            mutate_break_b_class_update_call_shape,
            ["b_class_field_update", "canonical SCIR-H parse failed"],
        ),
        (
            "boundary capability import missing",
            mutate_remove_boundary_capability_import,
            ["c_opaque_call", "missing capability imports for boundary requirements"],
        ),
        (
            "boundary capability import unused",
            mutate_add_unused_boundary_capability_import,
            ["c_opaque_call", "unused capability imports not referenced by the boundary contract"],
        ),
        (
            "illegal capability import on tier a fixture",
            mutate_add_illegal_capability_import_to_tier_a,
            ["a_basic_function", "non-boundary fixtures must not declare capability imports"],
        ),
    ]

    for name, mutate, expected_markers in cases:
        failures.extend(run_negative_fixture(root, name, mutate, expected_markers))

    return failures


def print_success(mode: str):
    print(f"[{mode}] python importer fixture conformance passed")
    print(
        "Checked fixture completeness, schema-valid bundle artifacts, "
        "tier-specific required files, generated-vs-golden bundle parity, "
        "capability-boundary alignment, parse-normalize-format canonical-SCIR-H expectations "
        f"for {len(CASE_EXPECTATIONS)} Python importer cases."
    )
    if mode == "test":
        print("Python importer conformance self-tests passed (15 negative fixtures).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="validate-fixtures")
    parser.add_argument("--root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve() if args.root else pathlib.Path(__file__).resolve().parents[1]
    failures = run_checks(root)

    if failures:
        print(f"[{args.mode}] python importer fixture conformance failed")
        for item in failures:
            print(f" - {item}")
        sys.exit(1)

    if args.mode == "test":
        self_test_failures = run_self_tests(root)
        if self_test_failures:
            print("[test] python importer fixture self-tests failed")
            for item in self_test_failures:
                print(f" - {item}")
            sys.exit(1)

    print_success(args.mode)
    sys.exit(0)


if __name__ == "__main__":
    main()
