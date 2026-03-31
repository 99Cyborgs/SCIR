#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import asyncio
import hashlib
import importlib
import json
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

from rust_toolchain import resolve_rust_toolchain, rust_toolchain_env
from scir_h_bootstrap_model import (
    AwaitExpr,
    CallExpr,
    FieldPlace,
    FunctionDecl,
    IfStmt,
    IntrinsicExpr,
    IntExpr,
    Module,
    NameExpr,
    PlaceExpr,
    RecordType,
    ReturnStmt,
    SetStmt,
    TypeDecl,
    VarDecl,
    format_place,
    format_module,
    parse_module,
    ScirHModelError,
)
from scir_python_bootstrap import (
    SCIRH_MODULES as PYTHON_SCIRH_MODULES,
    SOURCE_TEXTS as PYTHON_SOURCE_TEXTS,
    SPEC_VERSION,
    build_bundle as build_python_bundle,
)
from scir_rust_bootstrap import (
    SCIRH_MODULES as RUST_SCIRH_MODULES,
    SOURCE_TEXTS as RUST_SOURCE_TEXTS,
    TEST_TEXTS as RUST_TEST_TEXTS,
    build_bundle as build_rust_bundle,
)
from validate_repo_contracts import collect_instance_validation_errors


ALL_CASES = [
    "a_basic_function",
    "a_async_await",
    "b_if_else_return",
    "b_direct_call",
    "b_async_arg_await",
    "b_while_call_update",
    "b_while_break_continue",
    "b_class_init_method",
    "b_class_field_update",
    "c_opaque_call",
    "d_exec_eval",
    "d_try_except",
]
SUPPORTED_CASES = ["a_basic_function", "a_async_await", "c_opaque_call"]
SCIRH_ONLY_CASES = ["b_if_else_return", "b_direct_call", "b_async_arg_await", "b_while_call_update", "b_while_break_continue", "b_class_init_method", "b_class_field_update", "d_try_except"]
IMPORT_SUPPORTED_CASES = [*SUPPORTED_CASES, *SCIRH_ONLY_CASES]
REJECTED_CASES = ["d_exec_eval"]
BENCHMARK_CASES = [*SUPPORTED_CASES]
SCIRH_VALIDATOR_NAME = "scir-h-bootstrap-validator"
SCIRL_VALIDATOR_NAME = "scir-l-bootstrap-validator"
TRANSLATION_VALIDATOR_NAME = "translation-bootstrap-validator"
RECONSTRUCTION_VALIDATOR_NAME = "reconstruction-bootstrap-validator"

RECONSTRUCTION_EXPECTATIONS = {
    "a_basic_function": {"profile": "R", "preservation_level": "P1", "requires_opaque": False},
    "a_async_await": {"profile": "R", "preservation_level": "P1", "requires_opaque": False},
    "c_opaque_call": {"profile": "D-PY", "preservation_level": "P3", "requires_opaque": True},
}
RUST_ALL_CASES = [
    "a_mut_local",
    "a_struct_field_borrow_mut",
    "a_async_await",
    "c_unsafe_call",
    "d_proc_macro",
    "d_self_ref_pin",
]
RUST_SUPPORTED_CASES = ["a_mut_local", "a_struct_field_borrow_mut", "a_async_await", "c_unsafe_call"]
RUST_TIER_A_CASES = ["a_mut_local", "a_struct_field_borrow_mut", "a_async_await"]
RUST_REJECTED_CASES = ["d_proc_macro", "d_self_ref_pin"]
RUST_RECONSTRUCTION_EXPECTATIONS = {
    "a_mut_local": {"profile": "R", "preservation_level": "P1", "requires_opaque": False},
    "a_struct_field_borrow_mut": {"profile": "R", "preservation_level": "P1", "requires_opaque": False},
    "a_async_await": {"profile": "R", "preservation_level": "P1", "requires_opaque": False},
    "c_unsafe_call": {"profile": "N", "preservation_level": "P3", "requires_opaque": True},
}


class PipelineError(Exception):
    pass


def repo_root(root_arg: str | None) -> pathlib.Path:
    return pathlib.Path(root_arg).resolve() if root_arg else pathlib.Path(__file__).resolve().parents[1]


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_schema(root: pathlib.Path, schema_rel: str):
    return load_json(root / schema_rel)


def validate_instance(root: pathlib.Path, instance, schema_rel: str, label: str):
    failures = []
    schema = load_schema(root, schema_rel)
    for location, message in collect_instance_validation_errors(instance, schema):
        failures.append(f"{label} {location}: {message}")
    return failures


def slug(case_name: str) -> str:
    return case_name.replace("_", "-")


def fixture_source(root: pathlib.Path, case_name: str) -> pathlib.Path:
    return root / "tests" / "python_importer" / "cases" / case_name / "source.py"


def case_name_from_module(module: Module) -> str:
    return module.module_id.rsplit(".", 1)[-1]


def load_import_artifacts(root: pathlib.Path, case_name: str):
    bundle = build_python_bundle(root, fixture_source(root, case_name))
    parsed = {}
    for name, contents in bundle.files.items():
        if name.endswith(".json"):
            parsed[name] = json.loads(contents)
        else:
            parsed[name] = contents
    return parsed


def validate_import_bundle(root: pathlib.Path, case_name: str, artifacts: dict):
    failures = []
    failures.extend(
        validate_instance(
            root,
            artifacts["module_manifest.json"],
            "schemas/module_manifest.schema.json",
            f"{case_name} module_manifest",
        )
    )
    failures.extend(
        validate_instance(
            root,
            artifacts["feature_tier_report.json"],
            "schemas/feature_tier_report.schema.json",
            f"{case_name} feature_tier_report",
        )
    )
    failures.extend(
        validate_instance(
            root,
            artifacts["validation_report.json"],
            "schemas/validation_report.schema.json",
            f"{case_name} validation_report",
        )
    )
    if "opaque_boundary_contract.json" in artifacts:
        failures.extend(
            validate_instance(
                root,
                artifacts["opaque_boundary_contract.json"],
                "schemas/opaque_boundary_contract.schema.json",
                f"{case_name} opaque_boundary_contract",
            )
        )
    return failures


def validate_scirh_case(case_name: str, scirh_text: str):
    failures = []
    try:
        parsed = parse_module(scirh_text)
    except ScirHModelError as exc:
        failures.append(f"{case_name}: canonical SCIR-H parse failed: {exc}")
        parsed = None

    if parsed is not None:
        expected = PYTHON_SCIRH_MODULES[case_name]
        if parsed != expected:
            failures.append(
                f"{case_name}: parsed SCIR-H model drifted from the canonical bootstrap module model"
            )
        canonical_text = format_module(parsed)
        if scirh_text != canonical_text:
            failures.append(
                f"{case_name}: SCIR-H text is not canonical under parse-normalize-format"
            )

    report = {
        "report_id": f"scir-h-validation-{slug(case_name)}",
        "artifact": f"fixture.python_importer.{case_name}",
        "layer": "scir_h",
        "validator": SCIRH_VALIDATOR_NAME,
        "spec_version": SPEC_VERSION,
        "status": "pass" if not failures else "fail",
        "diagnostics": [
            {
                "code": "HBOOT001",
                "severity": "error",
                "message": message,
            }
            for message in failures
        ],
    }
    return failures, parsed, report


def is_local_place(value, expected: str) -> bool:
    return format_place(value) == expected


def lower_basic_function(module: Module):
    function = module.functions[0]
    body = list(function.body)
    if len(body) != 3:
        raise PipelineError("a_basic_function: expected var, if, return")
    var_stmt, if_stmt, return_stmt = body
    if not (
        isinstance(var_stmt, VarDecl)
        and var_stmt.name == "y"
        and isinstance(var_stmt.value, NameExpr)
        and var_stmt.value.name == "x"
        and isinstance(if_stmt, IfStmt)
        and isinstance(if_stmt.condition, IntrinsicExpr)
        and if_stmt.condition.op == "lt"
        and if_stmt.condition.args == (NameExpr("y"), IntExpr(0))
        and len(if_stmt.then_body) == 1
        and not if_stmt.else_body
        and isinstance(if_stmt.then_body[0], SetStmt)
        and is_local_place(if_stmt.then_body[0].target, "y")
        and if_stmt.then_body[0].value == IntExpr(0)
        and isinstance(return_stmt, ReturnStmt)
        and return_stmt.value == NameExpr("y")
    ):
        raise PipelineError("a_basic_function: unsupported compact SCIR-H shape for lowering")

    return {
        "module_id": module.module_id,
        "functions": [
            {
                "name": function.name,
                "returns": function.return_type,
                "params": [param.name for param in function.params],
                "blocks": [
                    {
                        "id": "entry",
                        "params": ["mem0"],
                        "instructions": [
                            {
                                "id": "cell0",
                                "op": "alloc",
                                "operands": ["mem0"],
                                "origin": f"{module.module_id}::var-y",
                            },
                            {
                                "id": "mem1",
                                "op": "store",
                                "operands": ["cell0", "x", "mem0"],
                                "origin": f"{module.module_id}::init-y",
                            },
                            {
                                "id": "load0",
                                "op": "load",
                                "operands": ["cell0", "mem1"],
                                "origin": f"{module.module_id}::lt-load-y",
                            },
                            {
                                "id": "cmp0",
                                "op": "cmp",
                                "operands": ["load0", 0],
                                "origin": f"{module.module_id}::lt-zero",
                            },
                        ],
                        "terminator": {
                            "kind": "cond_br",
                            "cond": "cmp0",
                            "true": "neg",
                            "true_args": ["cell0", "mem1"],
                            "false": "retread",
                            "false_args": ["cell0", "mem1"],
                            "origin": f"{module.module_id}::branch",
                        },
                    },
                    {
                        "id": "neg",
                        "params": ["cell1", "mem2"],
                        "instructions": [
                            {
                                "id": "mem3",
                                "op": "store",
                                "operands": ["cell1", 0, "mem2"],
                                "origin": f"{module.module_id}::set-y-zero",
                            }
                        ],
                        "terminator": {
                            "kind": "br",
                            "target": "retread",
                            "args": ["cell1", "mem3"],
                            "origin": f"{module.module_id}::join-return",
                        },
                    },
                    {
                        "id": "retread",
                        "params": ["cell2", "mem4"],
                        "instructions": [
                            {
                                "id": "load1",
                                "op": "load",
                                "operands": ["cell2", "mem4"],
                                "origin": f"{module.module_id}::return-load-y",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "load1",
                            "origin": f"{module.module_id}::return",
                        },
                    },
                ],
            }
        ],
    }


def lower_async_module(module: Module):
    fetch_value, load_once = module.functions
    if not (
        fetch_value.is_async
        and load_once.is_async
        and fetch_value.body == (ReturnStmt(IntExpr(1)),)
        and load_once.body == (ReturnStmt(AwaitExpr(CallExpr("fetch_value", ()))),)
    ):
        raise PipelineError("a_async_await: unsupported compact SCIR-H shape for lowering")

    return {
        "module_id": module.module_id,
        "functions": [
            {
                "name": "fetch_value",
                "returns": "int",
                "params": [],
                "blocks": [
                    {
                        "id": "entry",
                        "params": [],
                        "instructions": [
                            {
                                "id": "const0",
                                "op": "const",
                                "operands": [1],
                                "origin": f"{module.module_id}::fetch-value-return",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "const0",
                            "origin": f"{module.module_id}::fetch-value-ret",
                        },
                    }
                ],
            },
            {
                "name": "load_once",
                "returns": "int",
                "params": [],
                "blocks": [
                    {
                        "id": "entry",
                        "params": ["eff0"],
                        "instructions": [
                            {
                                "id": "call0",
                                "op": "call",
                                "operands": ["sym:fetch_value", "eff0"],
                                "origin": f"{module.module_id}::call-fetch-value",
                            },
                            {
                                "id": "await0",
                                "op": "async.resume",
                                "operands": ["call0", "eff0"],
                                "origin": f"{module.module_id}::await-fetch-value",
                            },
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "await0",
                            "origin": f"{module.module_id}::load-once-ret",
                        },
                    }
                ],
            },
        ],
    }


def lower_opaque_module(module: Module):
    function = module.functions[0]
    if not (
        len(module.imports) == 1
        and module.imports[0].local_id == "foreign_api_ping"
        and function.body == (ReturnStmt(CallExpr("foreign_api_ping", ())),)
    ):
        raise PipelineError("c_opaque_call: unsupported compact SCIR-H shape for lowering")

    return {
        "module_id": module.module_id,
        "functions": [
            {
                "name": "ping",
                "returns": "opaque<ForeignResult>",
                "params": [],
                "blocks": [
                    {
                        "id": "entry",
                        "params": ["eff0"],
                        "instructions": [
                            {
                                "id": "opaque0",
                                "op": "opaque.call",
                                "operands": ["sym:foreign_api_ping", "eff0"],
                                "origin": f"{module.module_id}::opaque-call",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "opaque0",
                            "origin": f"{module.module_id}::ret",
                        },
                    }
                ],
            }
        ],
    }


def lower_supported_module(module: Module):
    case_name = case_name_from_module(module)
    if case_name == "a_basic_function":
        return lower_basic_function(module)
    if case_name == "a_async_await":
        return lower_async_module(module)
    if case_name == "c_opaque_call":
        return lower_opaque_module(module)
    raise PipelineError(f"{case_name}: lowering is not defined for this case")


def validate_operand(operand, known_values: set[str]):
    if isinstance(operand, int):
        return []
    if not isinstance(operand, str):
        return [f"unexpected operand type {type(operand).__name__}"]
    if operand.startswith("sym:"):
        return []
    if operand not in known_values:
        return [f"unknown SSA/token operand {operand!r}"]
    return []


def token_prefix(value: str) -> str | None:
    if value.startswith("mem"):
        return "mem"
    if value.startswith("eff"):
        return "eff"
    return None


def validate_scirl_module(module: dict):
    failures = []
    allowed_ops = {
        "alloc",
        "store",
        "load",
        "field.addr",
        "cmp",
        "const",
        "call",
        "async.resume",
        "opaque.call",
    }
    function_names = set()
    for function in module["functions"]:
        name = function["name"]
        if name in function_names:
            failures.append(f"{module['module_id']}::{name}: duplicate function name")
        function_names.add(name)
        block_ids = {block["id"] for block in function["blocks"]}
        if "entry" not in block_ids:
            failures.append(f"{module['module_id']}::{name}: missing entry block")
        seen_ids = set(function["params"])
        block_param_lookup = {}
        for block in function["blocks"]:
            if block["id"] in block_param_lookup:
                failures.append(f"{module['module_id']}::{name}: duplicate block {block['id']}")
                continue
            block_param_lookup[block["id"]] = list(block["params"])

        for block in function["blocks"]:
            known_values = set(function["params"]) | set(block["params"])
            for instruction in block["instructions"]:
                if instruction["op"] not in allowed_ops:
                    failures.append(
                        f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: unsupported op {instruction['op']}"
                    )
                if not instruction.get("origin"):
                    failures.append(
                        f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: missing provenance origin"
                    )
                if instruction["id"] in seen_ids:
                    failures.append(
                        f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: duplicate SSA or token id"
                    )
                for operand in instruction["operands"]:
                    failures.extend(
                        f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: {item}"
                        for item in validate_operand(operand, known_values)
                    )
                seen_ids.add(instruction["id"])
                known_values.add(instruction["id"])

            terminator = block["terminator"]
            if not terminator.get("origin"):
                failures.append(
                    f"{module['module_id']}::{name}::{block['id']}::terminator: missing provenance origin"
                )
            if terminator["kind"] == "ret":
                failures.extend(
                    f"{module['module_id']}::{name}::{block['id']}::ret: {item}"
                    for item in validate_operand(terminator["value"], known_values)
                )
            elif terminator["kind"] == "br":
                target = terminator["target"]
                if target not in block_param_lookup:
                    failures.append(
                        f"{module['module_id']}::{name}::{block['id']}::br: unknown target block {target}"
                    )
                else:
                    target_params = block_param_lookup[target]
                    if len(target_params) != len(terminator["args"]):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::br: target arg count mismatch for {target}"
                        )
                    for index, arg in enumerate(terminator["args"]):
                        failures.extend(
                            f"{module['module_id']}::{name}::{block['id']}::br: {item}"
                            for item in validate_operand(arg, known_values)
                        )
                        if index < len(target_params):
                            source_prefix = token_prefix(arg) if isinstance(arg, str) else None
                            target_prefix = token_prefix(target_params[index])
                            if source_prefix != target_prefix and target_prefix in {"mem", "eff"}:
                                failures.append(
                                    f"{module['module_id']}::{name}::{block['id']}::br: token class mismatch for target {target}"
                                )
            elif terminator["kind"] == "cond_br":
                failures.extend(
                    f"{module['module_id']}::{name}::{block['id']}::cond_br: {item}"
                    for item in validate_operand(terminator["cond"], known_values)
                )
                for edge_name in ["true", "false"]:
                    target = terminator[edge_name]
                    args = terminator[f"{edge_name}_args"]
                    if target not in block_param_lookup:
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::cond_br: unknown target block {target}"
                        )
                        continue
                    target_params = block_param_lookup[target]
                    if len(target_params) != len(args):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::cond_br: target arg count mismatch for {target}"
                        )
                    for index, arg in enumerate(args):
                        failures.extend(
                            f"{module['module_id']}::{name}::{block['id']}::cond_br: {item}"
                            for item in validate_operand(arg, known_values)
                        )
                        if index < len(target_params):
                            source_prefix = token_prefix(arg) if isinstance(arg, str) else None
                            target_prefix = token_prefix(target_params[index])
                            if source_prefix != target_prefix and target_prefix in {"mem", "eff"}:
                                failures.append(
                                    f"{module['module_id']}::{name}::{block['id']}::cond_br: token class mismatch for target {target}"
                                )
            else:
                failures.append(
                    f"{module['module_id']}::{name}::{block['id']}::terminator: unsupported kind {terminator['kind']}"
                )

    report = {
        "report_id": f"scir-l-validation-{slug(module['module_id'].split('.')[-1])}",
        "artifact": module["module_id"],
        "layer": "scir_l",
        "validator": SCIRL_VALIDATOR_NAME,
        "spec_version": SPEC_VERSION,
        "status": "pass" if not failures else "fail",
        "diagnostics": [
            {
                "code": "LBOOT001",
                "severity": "error",
                "message": message,
            }
            for message in failures
        ],
    }
    return failures, report


def format_value(value):
    if isinstance(value, int):
        return str(value)
    if value.startswith("sym:"):
        return value.split(":", 1)[1]
    return f"%{value}"


def render_scirl_module(module: dict):
    lines = [f"lmodule {module['module_id']} {{"]
    for function in module["functions"]:
        params = ", ".join(f"%{name}" for name in function["params"])
        lines.append(f"func {function['name']}({params}) -> {function['returns']} {{")
        for block in function["blocks"]:
            params_text = ", ".join(f"%{name}" for name in block["params"])
            lines.append(f"^{block['id']}({params_text}):")
            for instruction in block["instructions"]:
                operands = " ".join(format_value(item) for item in instruction["operands"])
                lines.append(f"  %{instruction['id']} = {instruction['op']} {operands};")
            terminator = block["terminator"]
            if terminator["kind"] == "ret":
                lines.append(f"  ret {format_value(terminator['value'])};")
            elif terminator["kind"] == "br":
                args = ", ".join(format_value(item) for item in terminator["args"])
                lines.append(f"  br ^{terminator['target']}({args});")
            else:
                true_args = ", ".join(format_value(item) for item in terminator["true_args"])
                false_args = ", ".join(format_value(item) for item in terminator["false_args"])
                lines.append(
                    "  cond_br "
                    f"{format_value(terminator['cond'])}, "
                    f"^{terminator['true']}({true_args}), "
                    f"^{terminator['false']}({false_args});"
                )
        lines.append("}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def validate_lowering_alignment(case_name: str, lowered: dict):
    failures = []
    if case_name == "a_basic_function":
        functions = lowered["functions"]
        if len(functions) != 1:
            return [f"{case_name}: expected exactly one lowered function"]
        function = functions[0]
        blocks = function["blocks"]
        if [block["id"] for block in blocks] != ["entry", "neg", "retread"]:
            failures.append(f"{case_name}: expected entry/neg/retread block layout")
        entry_ops = [item["op"] for item in blocks[0]["instructions"]]
        if entry_ops != ["alloc", "store", "load", "cmp"]:
            failures.append(f"{case_name}: expected alloc/store/load/cmp in entry block")
        if blocks[0]["terminator"]["kind"] != "cond_br":
            failures.append(f"{case_name}: expected cond_br entry terminator")
        if [item["op"] for item in blocks[1]["instructions"]] != ["store"]:
            failures.append(f"{case_name}: expected single store in neg block")
        if blocks[1]["terminator"]["kind"] != "br":
            failures.append(f"{case_name}: expected br terminator in neg block")
        if [item["op"] for item in blocks[2]["instructions"]] != ["load"]:
            failures.append(f"{case_name}: expected single load in retread block")
        if blocks[2]["terminator"]["kind"] != "ret":
            failures.append(f"{case_name}: expected ret terminator in retread block")
        return failures

    if case_name == "a_async_await":
        functions = lowered["functions"]
        if [function["name"] for function in functions] != ["fetch_value", "load_once"]:
            return [f"{case_name}: expected fetch_value/load_once lowered functions"]
        if [item["op"] for item in functions[0]["blocks"][0]["instructions"]] != ["const"]:
            failures.append(f"{case_name}: expected fetch_value to lower to const")
        if [item["op"] for item in functions[1]["blocks"][0]["instructions"]] != ["call", "async.resume"]:
            failures.append(f"{case_name}: expected load_once to lower to call + async.resume")
        if functions[1]["blocks"][0]["params"] != ["eff0"]:
            failures.append(f"{case_name}: expected load_once entry effect token parameter")
        return failures

    if case_name == "c_opaque_call":
        functions = lowered["functions"]
        if len(functions) != 1:
            return [f"{case_name}: expected exactly one lowered function"]
        function = functions[0]
        if function["blocks"][0]["params"] != ["eff0"]:
            failures.append(f"{case_name}: expected opaque entry effect token parameter")
        if [item["op"] for item in function["blocks"][0]["instructions"]] != ["opaque.call"]:
            failures.append(f"{case_name}: expected opaque.call lowering")
        return failures

    return [f"{case_name}: lowering alignment contract is not defined"]


def validate_translation_report(case_name: str, report: dict):
    failures = []
    expected = {
        "a_basic_function": ("R", "P1", False),
        "a_async_await": ("R", "P1", False),
        "c_opaque_call": ("D-PY", "P3", True),
    }
    profile, preservation_level, requires_opaque = expected[case_name]
    if report["profile"] != profile:
        failures.append(f"{case_name}: expected translation profile {profile}")
    if report["preservation_level"] != preservation_level:
        failures.append(f"{case_name}: expected translation preservation level {preservation_level}")
    opaque_items = report["observables"]["opaque"]
    if requires_opaque:
        if "foreign_api.ping boundary" not in opaque_items:
            failures.append(f"{case_name}: translation report must preserve opaque boundary accounting")
    elif opaque_items:
        failures.append(f"{case_name}: Tier A translation report must not introduce opaque accounting")
    return failures


def translation_report(case_name: str):
    if case_name == "c_opaque_call":
        return {
            "report_id": f"translation-preservation-{slug(case_name)}",
            "subject": f"fixture.python_importer.{case_name}",
            "source_artifact": f"scir_h:fixture.python_importer.{case_name}",
            "target_artifact": f"scir_l:fixture.python_importer.{case_name}",
            "profile": "D-PY",
            "preservation_level": "P3",
            "status": "pass",
            "observables": {
                "preserved": ["function boundary"],
                "normalized": ["direct foreign call lowered into explicit opaque.call op"],
                "contract_bounded": [],
                "opaque": ["foreign_api.ping boundary"],
                "unsupported": [],
            },
            "evidence": [
                TRANSLATION_VALIDATOR_NAME,
                "opaque boundary preserved in lowered form",
            ],
        }
    preserved = {
        "a_basic_function": ["function boundaries", "structured control", "explicit mutation"],
        "a_async_await": ["async function boundaries", "await suspension"],
    }
    return {
        "report_id": f"translation-preservation-{slug(case_name)}",
        "subject": f"fixture.python_importer.{case_name}",
        "source_artifact": f"scir_h:fixture.python_importer.{case_name}",
        "target_artifact": f"scir_l:fixture.python_importer.{case_name}",
        "profile": "R",
        "preservation_level": "P1",
        "status": "pass",
        "observables": {
            "preserved": preserved[case_name],
            "normalized": [],
            "contract_bounded": [],
            "opaque": [],
            "unsupported": [],
        },
        "evidence": [
            TRANSLATION_VALIDATOR_NAME,
            "lowered CFG and provenance validated",
        ],
    }


def reconstruction_profile(case_name: str):
    expected = RECONSTRUCTION_EXPECTATIONS[case_name]
    return expected["profile"], expected["preservation_level"]


def expected_provenance_map(scirh_text: str):
    return {
        str(index): line
        for index, line in enumerate(scirh_text.splitlines(), start=1)
        if line.strip()
    }


def build_provenance_map(scirh_text: str):
    return expected_provenance_map(scirh_text)


def provenance_map_matches_canonical_lines(scirh_text: str, provenance_map: dict[str, str]):
    expected = expected_provenance_map(scirh_text)
    return provenance_map == expected


def render_python_expr(expr, import_aliases: dict[str, str]):
    if isinstance(expr, NameExpr):
        return import_aliases.get(expr.name, expr.name)
    if isinstance(expr, PlaceExpr):
        place = format_place(expr.place)
        return import_aliases.get(place, place)
    if isinstance(expr, IntExpr):
        return str(expr.value)
    if isinstance(expr, CallExpr):
        args = ", ".join(render_python_expr(arg, import_aliases) for arg in expr.args)
        return f"{import_aliases.get(expr.callee, expr.callee)}({args})"
    if isinstance(expr, AwaitExpr):
        return f"await {render_python_expr(expr.value, import_aliases)}"
    if isinstance(expr, IntrinsicExpr):
        if expr.op == "lt":
            left = render_python_expr(expr.args[0], import_aliases)
            right = render_python_expr(expr.args[1], import_aliases)
            return f"{left} < {right}"
    raise PipelineError(f"unsupported Python reconstruction expression: {type(expr).__name__}")


def render_python_stmt(stmt, indent: int, import_aliases: dict[str, str]):
    prefix = " " * indent
    if isinstance(stmt, VarDecl):
        return [f"{prefix}{stmt.name} = {render_python_expr(stmt.value, import_aliases)}"]
    if isinstance(stmt, SetStmt):
        return [f"{prefix}{format_place(stmt.target)} = {render_python_expr(stmt.value, import_aliases)}"]
    if isinstance(stmt, ReturnStmt):
        return [f"{prefix}return {render_python_expr(stmt.value, import_aliases)}"]
    if isinstance(stmt, IfStmt):
        lines = [f"{prefix}if {render_python_expr(stmt.condition, import_aliases)}:"]
        for item in stmt.then_body:
            lines.extend(render_python_stmt(item, indent + 4, import_aliases))
        if stmt.else_body:
            lines.append(f"{prefix}else:")
            for item in stmt.else_body:
                lines.extend(render_python_stmt(item, indent + 4, import_aliases))
        return lines
    raise PipelineError(f"unsupported Python reconstruction statement: {type(stmt).__name__}")


def import_aliases(module: Module):
    aliases = {}
    for item in module.imports:
        if item.ref.startswith("python:"):
            aliases[item.local_id] = item.ref.split(":", 1)[1]
    return aliases


def reconstruct_python_source(module: Module):
    aliases = import_aliases(module)
    lines = []
    source_imports = sorted({value.split(".", 1)[0] for value in aliases.values()})
    for import_name in source_imports:
        lines.append(f"import {import_name}")
    if source_imports:
        lines.append("")
        lines.append("")

    for index, function in enumerate(module.functions):
        if index:
            lines.append("")
            lines.append("")
        params = ", ".join(param.name for param in function.params)
        header = f"async def {function.name}({params}):" if function.is_async else f"def {function.name}({params}):"
        lines.append(header)
        for stmt in function.body:
            lines.extend(render_python_stmt(stmt, 4, aliases))
    return "\n".join(lines) + "\n"


def execute_module(case_name: str, source_text: str):
    namespace = {"__builtins__": __builtins__}
    if case_name == "a_basic_function":
        exec(compile(source_text, f"<{case_name}>", "exec"), namespace)
        function = namespace["clamp_nonneg"]
        return [function(-4), function(0), function(7)]
    if case_name == "a_async_await":
        exec(compile(source_text, f"<{case_name}>", "exec"), namespace)
        return [
            asyncio.run(namespace["fetch_value"]()),
            asyncio.run(namespace["load_once"]()),
        ]
    if case_name == "c_opaque_call":
        with tempfile.TemporaryDirectory(prefix="scir_foreign_api_") as tmp:
            temp_dir = pathlib.Path(tmp)
            (temp_dir / "foreign_api.py").write_text(
                "def ping():\n    return {'status': 'ok', 'origin': 'stub'}\n",
                encoding="utf-8",
            )
            sys.path.insert(0, str(temp_dir))
            try:
                importlib.invalidate_caches()
                sys.modules.pop("foreign_api", None)
                exec(compile(source_text, f"<{case_name}>", "exec"), namespace)
                return namespace["ping"]()
            finally:
                sys.modules.pop("foreign_api", None)
                sys.path.pop(0)
    raise PipelineError(f"{case_name}: execution harness is not defined")


def evaluate_reconstruction(case_name: str, reconstructed_text: str):
    try:
        compile(reconstructed_text, f"<reconstructed:{case_name}>", "exec")
    except SyntaxError:
        return False, False
    try:
        expected = execute_module(case_name, PYTHON_SOURCE_TEXTS[case_name])
        actual = execute_module(case_name, reconstructed_text)
    except Exception:
        return True, False
    return True, expected == actual


def build_reconstruction_outputs(module: Module):
    case_name = case_name_from_module(module)
    reconstructed_text = reconstruct_python_source(module)
    scirh_text = format_module(module)
    provenance_map = build_provenance_map(scirh_text)
    provenance_complete = provenance_map_matches_canonical_lines(scirh_text, provenance_map)
    compile_pass, test_pass = evaluate_reconstruction(case_name, reconstructed_text)
    profile, preservation_level = reconstruction_profile(case_name)
    notes = [
        "Reconstructed from the fixed bootstrap SCIR-H slice.",
    ]
    if reconstructed_text == PYTHON_SOURCE_TEXTS[case_name]:
        notes.append("Reconstruction matched the checked-in source text exactly.")
    if case_name == "c_opaque_call":
        notes.append("Opaque boundary behavior remains bounded by the explicit contract.")
    if provenance_complete:
        notes.append("Line-granular provenance covers every non-empty canonical SCIR-H line.")

    reconstruction_report = {
        "report_id": f"reconstruction-report-{slug(case_name)}",
        "subject": f"fixture.python_importer.{case_name}",
        "source_language": "python",
        "target_language": "python",
        "profile": profile,
        "preservation_level": preservation_level,
        "compile_pass": compile_pass,
        "test_pass": test_pass,
        "idiomaticity_score": 5.0 if reconstructed_text == PYTHON_SOURCE_TEXTS[case_name] else 4.0,
        "provenance_complete": provenance_complete,
        "notes": notes,
    }
    preservation_report = {
        "report_id": f"reconstruction-preservation-{slug(case_name)}",
        "subject": f"fixture.python_importer.{case_name}",
        "source_artifact": f"scir_h:fixture.python_importer.{case_name}",
        "target_artifact": f"reconstructed/python/{case_name}.py",
        "profile": profile,
        "preservation_level": preservation_level,
        "status": "pass" if compile_pass and test_pass else "fail",
        "observables": {
            "preserved": ["function boundaries", "return behavior"],
            "normalized": [],
            "contract_bounded": [],
            "opaque": ["foreign_api.ping boundary"] if case_name == "c_opaque_call" else [],
            "unsupported": [],
        },
        "evidence": [
            f"compile:{'pass' if compile_pass else 'fail'}",
            f"test:{'pass' if test_pass else 'fail'}",
            f"provenance_map:{'complete' if provenance_complete else 'incomplete'}",
            RECONSTRUCTION_VALIDATOR_NAME,
        ],
    }
    return reconstructed_text, provenance_map, reconstruction_report, preservation_report


def validate_reconstruction_report(
    case_name: str,
    scirh_text: str,
    reconstructed_text: str,
    provenance_map: dict[str, str],
    report: dict,
):
    failures = []
    profile, preservation_level = reconstruction_profile(case_name)
    if report["source_language"] != "python":
        failures.append(f"{case_name}: expected reconstruction source_language python")
    if report["target_language"] != "python":
        failures.append(f"{case_name}: expected reconstruction target_language python")
    if report["profile"] != profile:
        failures.append(f"{case_name}: expected reconstruction profile {profile}")
    if report["preservation_level"] != preservation_level:
        failures.append(f"{case_name}: expected reconstruction preservation level {preservation_level}")

    actual_compile_pass, actual_test_pass = evaluate_reconstruction(case_name, reconstructed_text)
    if report["compile_pass"] != actual_compile_pass:
        failures.append(f"{case_name}: reconstruction report compile_pass disagreed with execution")
    if report["test_pass"] != actual_test_pass:
        failures.append(f"{case_name}: reconstruction report test_pass disagreed with execution")
    if not actual_compile_pass:
        failures.append(f"{case_name}: supported reconstruction must compile")
    if not actual_test_pass:
        failures.append(f"{case_name}: supported reconstruction must pass the bootstrap execution harness")

    expected_map = expected_provenance_map(scirh_text)
    missing_lines = [
        line_no
        for line_no, text in expected_map.items()
        if provenance_map.get(line_no) != text
    ]
    unexpected_lines = sorted(set(provenance_map) - set(expected_map))
    actual_provenance_complete = not missing_lines and not unexpected_lines
    if report["provenance_complete"] != actual_provenance_complete:
        failures.append(f"{case_name}: reconstruction report provenance_complete disagreed with canonical coverage")
    if missing_lines:
        failures.append(
            f"{case_name}: missing provenance lines for canonical SCIR-H lines {', '.join(missing_lines)}"
        )
    if unexpected_lines:
        failures.append(
            f"{case_name}: unexpected provenance entries for canonical SCIR-H lines {', '.join(unexpected_lines)}"
        )
    return failures


def validate_reconstruction_preservation_report(case_name: str, reconstruction_report: dict, report: dict):
    failures = []
    profile, preservation_level = reconstruction_profile(case_name)
    if report["profile"] != profile:
        failures.append(f"{case_name}: expected reconstruction preservation profile {profile}")
    if report["preservation_level"] != preservation_level:
        failures.append(
            f"{case_name}: expected reconstruction preservation level {preservation_level}"
        )

    expected_status = "pass" if reconstruction_report["compile_pass"] and reconstruction_report["test_pass"] else "fail"
    if report["status"] != expected_status:
        failures.append(f"{case_name}: reconstruction preservation status disagreed with compile/test evidence")

    opaque_items = report["observables"]["opaque"]
    if RECONSTRUCTION_EXPECTATIONS[case_name]["requires_opaque"]:
        if "foreign_api.ping boundary" not in opaque_items:
            failures.append(f"{case_name}: reconstruction preservation must retain opaque boundary accounting")
    elif opaque_items:
        failures.append(f"{case_name}: Tier A reconstruction must not introduce opaque accounting")

    if report["observables"]["unsupported"]:
        failures.append(f"{case_name}: supported reconstruction must not mark unsupported observables")

    required_evidence = [
        f"compile:{'pass' if reconstruction_report['compile_pass'] else 'fail'}",
        f"test:{'pass' if reconstruction_report['test_pass'] else 'fail'}",
        f"provenance_map:{'complete' if reconstruction_report['provenance_complete'] else 'incomplete'}",
    ]
    for item in required_evidence:
        if item not in report["evidence"]:
            failures.append(f"{case_name}: reconstruction preservation report missing evidence {item}")
    return failures


def validate_reconstruction_artifacts(
    case_name: str,
    scirh_text: str,
    reconstructed_text: str,
    provenance_map: dict[str, str],
    reconstruction_report: dict,
    preservation_report: dict,
):
    failures = []
    failures.extend(
        validate_reconstruction_report(
            case_name,
            scirh_text,
            reconstructed_text,
            provenance_map,
            reconstruction_report,
        )
    )
    failures.extend(
        validate_reconstruction_preservation_report(
            case_name,
            reconstruction_report,
            preservation_report,
        )
    )
    return failures


def validate_executable_output_set(outputs: dict):
    failures = []
    for case_name in SUPPORTED_CASES:
        if case_name not in outputs["scir_l_reports"]:
            failures.append(f"{case_name}: supported case must emit an SCIR-L output")
        if case_name not in outputs["translation_reports"]:
            failures.append(f"{case_name}: supported case must emit a translation output")
        if case_name not in outputs["reconstruction_reports"]:
            failures.append(f"{case_name}: supported case must emit a reconstruction output")
        if case_name not in outputs["reconstruction_preservation_reports"]:
            failures.append(f"{case_name}: supported case must emit a reconstruction preservation report")
    for case_name in [*SCIRH_ONLY_CASES, *REJECTED_CASES]:
        if case_name in outputs["scir_l_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit SCIR-L output")
        if case_name in outputs["translation_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit translation output")
        if case_name in outputs["reconstruction_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit reconstruction output")
        if case_name in outputs["reconstruction_preservation_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit reconstruction preservation report")
    return failures


def compare_imported_feature_totals(root: pathlib.Path):
    total = 0
    opaque = 0
    tier_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for case_name in SUPPORTED_CASES:
        report = load_import_artifacts(root, case_name)["feature_tier_report.json"]
        total += len(report["items"])
        for item in report["items"]:
            tier_counts[item["tier"]] += 1
            if item["tier"] == "C":
                opaque += 1
    return opaque, total, tier_counts


def count_tokens(text: str):
    return len(re.findall(r"[A-Za-z_]+|\d+|[^\s]", text))


def scirh_header_and_body_tokens(text: str):
    header = 0
    body = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        token_count = count_tokens(line)
        if line.startswith("module ") or line.startswith("import ") or line.startswith("fn ") or line.startswith("async fn "):
            header += token_count
        else:
            body += token_count
    return header, body


def source_body_tokens(text: str):
    total = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("def ") or stripped.startswith("async def ") or stripped.startswith("import "):
            continue
        total += count_tokens(stripped)
    return total


def corpus_hash(case_names: list[str]):
    digest = hashlib.sha256()
    for case_name in case_names:
        digest.update(PYTHON_SOURCE_TEXTS[case_name].encode("utf-8"))
    return f"sha256:{digest.hexdigest()}"


def run_track_a(root: pathlib.Path):
    scirh_texts = [load_import_artifacts(root, case_name)["expected.scirh"] for case_name in SUPPORTED_CASES]
    source_token_counts = [count_tokens(PYTHON_SOURCE_TEXTS[case_name]) for case_name in SUPPORTED_CASES]
    scirh_token_counts = [count_tokens(text) for text in scirh_texts]
    typed_ast_token_counts = [
        count_tokens(ast.dump(ast.parse(PYTHON_SOURCE_TEXTS[case_name]), annotate_fields=True))
        for case_name in SUPPORTED_CASES
    ]
    scirh_body_token_counts = [scirh_header_and_body_tokens(text)[1] for text in scirh_texts]
    source_body_token_counts = [source_body_tokens(PYTHON_SOURCE_TEXTS[case_name]) for case_name in SUPPORTED_CASES]
    scirh_header_token_counts = [scirh_header_and_body_tokens(text)[0] for text in scirh_texts]
    opaque_nodes, total_nodes, tier_counts = compare_imported_feature_totals(root)

    source_ratios = [
        scirh / source
        for scirh, source in zip(scirh_token_counts, source_token_counts)
    ]
    typed_ast_ratios = [
        scirh / typed
        for scirh, typed in zip(scirh_token_counts, typed_ast_token_counts)
    ]
    body_source_ratios = [
        scirh / source
        for scirh, source in zip(scirh_body_token_counts, source_body_token_counts)
    ]

    median_source_ratio = statistics.median(source_ratios)
    aggregate_source_ratio = sum(scirh_token_counts) / sum(source_token_counts)
    median_typed_ast_ratio = statistics.median(typed_ast_ratios)
    aggregate_typed_ast_ratio = sum(scirh_token_counts) / sum(typed_ast_token_counts)
    body_median_source_ratio = statistics.median(body_source_ratios)
    header_token_share = sum(scirh_header_token_counts) / sum(scirh_token_counts)
    opaque_fraction = opaque_nodes / total_nodes
    semantic_markers = sum(
        text.count("opaque") + text.count("await") + text.count("var ") + text.count("set ")
        for text in scirh_texts
    )
    source_markers = sum(
        PYTHON_SOURCE_TEXTS[case_name].count("await") + PYTHON_SOURCE_TEXTS[case_name].count("import ")
        for case_name in SUPPORTED_CASES
    )
    explicitness_gain = semantic_markers - source_markers

    gate_s3_source_pass = median_source_ratio <= 1.10
    gate_s3_ast_pass = median_typed_ast_ratio <= 0.75
    gate_s4_pass = opaque_fraction < 0.15
    gate_k2_hit = median_source_ratio > 1.50
    gate_k4_hit = opaque_fraction > 0.25
    success = (gate_s3_source_pass or gate_s3_ast_pass) and gate_s4_pass
    passed = success and not gate_k2_hit and not gate_k4_hit

    manifest = {
        "benchmark_id": "bootstrap-track-a-python-subset",
        "track": "A",
        "task_family": "scir-h-regularity-and-compression",
        "corpus": {
            "name": "python-bootstrap-fixtures",
            "scope": "Fixed executable Python bootstrap cases",
            "hash": corpus_hash(BENCHMARK_CASES),
        },
        "baselines": [
            "direct source",
            "typed-AST",
            "lightweight regularized core or s-expression",
        ],
        "profiles": ["R", "D-PY"],
        "success_gates": ["S3", "S4"],
        "kill_gates": ["K2", "K4", "K7"],
        "contamination_controls": [
            "hash every published corpus manifest",
            "separate development, tuning, and held-out evaluation slices",
            "record prompt templates and baseline adapters",
            "do not claim generalization from a contaminated or untracked dataset",
        ],
    }

    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": "bootstrap-track-a-run-2026-03-16",
        "system_under_test": "scir-bootstrap-executable-path",
        "track": "A",
        "profile": "R",
        "metrics": {
            "source_token_total": sum(source_token_counts),
            "scir_h_token_total": sum(scirh_token_counts),
            "typed_ast_token_total": sum(typed_ast_token_counts),
            "median_scir_to_source_ratio": round(median_source_ratio, 4),
            "aggregate_scir_to_source_ratio": round(aggregate_source_ratio, 4),
            "median_scir_to_typed_ast_ratio": round(median_typed_ast_ratio, 4),
            "aggregate_scir_to_typed_ast_ratio": round(aggregate_typed_ast_ratio, 4),
            "body_median_scir_to_source_ratio": round(body_median_source_ratio, 4),
            "header_token_share": round(header_token_share, 4),
            "gate_S3_source_pass": gate_s3_source_pass,
            "gate_S3_ast_pass": gate_s3_ast_pass,
            "gate_S4_pass": gate_s4_pass,
            "gate_K2_hit": gate_k2_hit,
            "gate_K4_hit": gate_k4_hit,
            "opaque_fraction": round(opaque_fraction, 4),
            "semantic_explicitness_gain": explicitness_gain,
            "preservation_level_ceiling": "P3",
            "tier_a_feature_count": tier_counts["A"],
            "tier_b_feature_count": tier_counts["B"],
            "tier_c_feature_count": tier_counts["C"],
            "tier_d_feature_count": tier_counts["D"],
        },
        "baseline_comparison": {
            "direct source": round(median_source_ratio - 1.0, 4),
            "typed-AST": round(1.0 - median_typed_ast_ratio, 4),
        },
        "status": "pass" if passed else "fail",
        "evidence": [
            "generated SCIR-H bundle corpus",
            "typed AST token baseline from Python ast.dump",
            "median gate evaluation follows benchmarks/success_failure_gates.md",
        ],
    }
    return manifest, result


def run_track_b(root: pathlib.Path, reconstruction_reports: dict[str, dict]):
    opaque_nodes, total_nodes, tier_counts = compare_imported_feature_totals(root)
    opaque_fraction = opaque_nodes / total_nodes
    tier_a_cases = ["a_basic_function", "a_async_await"]
    compile_rate = sum(
        1 for case_name in tier_a_cases if reconstruction_reports[case_name]["compile_pass"]
    ) / len(tier_a_cases)
    test_rate = sum(
        1 for case_name in tier_a_cases if reconstruction_reports[case_name]["test_pass"]
    ) / len(tier_a_cases)
    idiomaticity = sum(
        reconstruction_reports[case_name]["idiomaticity_score"] for case_name in SUPPORTED_CASES
    ) / len(SUPPORTED_CASES)
    gate_s1_pass = compile_rate >= 0.95 and test_rate >= 0.95
    gate_s4_pass = opaque_fraction < 0.15
    gate_k3_hit = compile_rate < 0.90 or test_rate < 0.90
    gate_k4_hit = opaque_fraction > 0.25
    passed = gate_s1_pass and gate_s4_pass and not gate_k3_hit and not gate_k4_hit
    manifest = {
        "benchmark_id": "bootstrap-track-b-python-subset",
        "track": "B",
        "task_family": "python-bootstrap-roundtrip",
        "corpus": {
            "name": "python-bootstrap-fixtures",
            "scope": "Tier A plus explicit Tier C bootstrap reconstruction subset",
            "hash": corpus_hash(BENCHMARK_CASES),
        },
        "baselines": ["direct source", "typed-AST"],
        "profiles": ["R", "D-PY"],
        "success_gates": ["S1", "S4"],
        "kill_gates": ["K3", "K4"],
        "contamination_controls": [
            "hash every published corpus manifest",
            "separate development, tuning, and held-out evaluation slices",
            "record prompt templates and baseline adapters",
            "do not claim generalization from a contaminated or untracked dataset",
        ],
    }
    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": "bootstrap-track-b-run-2026-03-16",
        "system_under_test": "scir-bootstrap-executable-path",
        "track": "B",
        "profile": "R",
        "metrics": {
            "supported_case_count": len(SUPPORTED_CASES),
            "tier_a_compile_pass_rate": round(compile_rate, 4),
            "tier_a_test_pass_rate": round(test_rate, 4),
            "idiomaticity_mean": round(idiomaticity, 4),
            "opaque_fraction": round(opaque_fraction, 4),
            "gate_S1_pass": gate_s1_pass,
            "gate_S4_pass": gate_s4_pass,
            "gate_K3_hit": gate_k3_hit,
            "gate_K4_hit": gate_k4_hit,
            "preservation_level_ceiling": "P3",
            "tier_a_feature_count": tier_counts["A"],
            "tier_b_feature_count": tier_counts["B"],
            "tier_c_feature_count": tier_counts["C"],
            "tier_d_feature_count": tier_counts["D"],
        },
        "baseline_comparison": {
            "direct source": "reference only",
            "typed-AST": 0.0,
        },
        "status": "pass" if passed else "fail",
        "evidence": [
            "validated importer outputs",
            "reconstruction compile/test harness",
        ],
    }
    return manifest, result


TRACK_D_CONTROLS = [
    "hash every published corpus manifest",
    "separate development, tuning, and held-out evaluation slices",
    "record prompt templates and baseline adapters",
    "do not claim generalization from a contaminated or untracked dataset",
]

PYTHON_TRACK_D_CASES = ["a_basic_function", "a_async_await", "c_opaque_call"]
RUST_TRACK_D_CASES = ["a_mut_local", "a_struct_field_borrow_mut", "a_async_await"]
PYTHON_TRACK_D_ITERATIONS = {
    "a_basic_function": 20000,
    "a_async_await": 1000,
    "c_opaque_call": 4000,
}
RUST_TRACK_D_ITERATIONS = {
    "a_mut_local": 200000,
    "a_struct_field_borrow_mut": 120000,
    "a_async_await": 30000,
}


def rust_corpus_hash():
    digest = hashlib.sha256()
    for case_name in RUST_ALL_CASES:
        digest.update(RUST_SOURCE_TEXTS[case_name].encode("utf-8"))
    return f"sha256:{digest.hexdigest()}"


def compare_rust_imported_feature_totals(root: pathlib.Path):
    total = 0
    opaque = 0
    tier_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for case_name in RUST_SUPPORTED_CASES:
        report = load_rust_import_artifacts(root, case_name)["feature_tier_report.json"]
        total += len(report["items"])
        for item in report["items"]:
            tier_counts[item["tier"]] += 1
            if item["tier"] == "C":
                opaque += 1
    return opaque, total, tier_counts


def scirl_instruction_count(module: dict):
    return sum(len(block["instructions"]) for function in module["functions"] for block in function["blocks"])


def optimize_local_cell_module(lowered: dict):
    function = lowered["functions"][0]
    entry, neg, retread = function["blocks"]
    if [item["op"] for item in entry["instructions"]] != ["alloc", "store", "load", "cmp"]:
        raise PipelineError(f"{lowered['module_id']}: expected local-cell lowering for optimization")
    if [item["op"] for item in neg["instructions"]] != ["store"]:
        raise PipelineError(f"{lowered['module_id']}: expected store-only negative block for optimization")
    if [item["op"] for item in retread["instructions"]] != ["load"]:
        raise PipelineError(f"{lowered['module_id']}: expected load-only return block for optimization")

    param = function["params"][0]
    module_id = lowered["module_id"]
    return {
        "module_id": module_id,
        "functions": [
            {
                "name": function["name"],
                "returns": function["returns"],
                "params": list(function["params"]),
                "blocks": [
                    {
                        "id": "entry",
                        "params": [],
                        "instructions": [
                            {
                                "id": "cmp0",
                                "op": "cmp",
                                "operands": [param, 0],
                                "origin": f"{module_id}::track-d-opt-cmp-param-zero",
                            }
                        ],
                        "terminator": {
                            "kind": "cond_br",
                            "cond": "cmp0",
                            "true": "neg",
                            "true_args": [],
                            "false": "retv",
                            "false_args": [param],
                            "origin": f"{module_id}::track-d-opt-branch",
                        },
                    },
                    {
                        "id": "neg",
                        "params": [],
                        "instructions": [
                            {
                                "id": "const0",
                                "op": "const",
                                "operands": [0],
                                "origin": f"{module_id}::track-d-opt-const-zero",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "const0",
                            "origin": f"{module_id}::track-d-opt-ret-zero",
                        },
                    },
                    {
                        "id": "retv",
                        "params": ["value0"],
                        "instructions": [],
                        "terminator": {
                            "kind": "ret",
                            "value": "value0",
                            "origin": f"{module_id}::track-d-opt-ret-value",
                        },
                    },
                ],
            }
        ],
    }


def optimize_field_borrow_module(lowered: dict):
    function = lowered["functions"][0]
    entry, neg, retread = function["blocks"]
    if [item["op"] for item in entry["instructions"]] != ["field.addr", "load", "cmp"]:
        raise PipelineError(f"{lowered['module_id']}: expected field borrow lowering for optimization")
    if [item["op"] for item in neg["instructions"]] != ["store"]:
        raise PipelineError(f"{lowered['module_id']}: expected field store block for optimization")
    if [item["op"] for item in retread["instructions"]] != ["load"]:
        raise PipelineError(f"{lowered['module_id']}: expected field reload block for optimization")

    module_id = lowered["module_id"]
    field_symbol = entry["instructions"][0]["operands"][1]
    param = function["params"][0]
    return {
        "module_id": module_id,
        "functions": [
            {
                "name": function["name"],
                "returns": function["returns"],
                "params": list(function["params"]),
                "blocks": [
                    {
                        "id": "entry",
                        "params": ["mem0"],
                        "instructions": [
                            {
                                "id": "field0",
                                "op": "field.addr",
                                "operands": [param, field_symbol],
                                "origin": f"{module_id}::track-d-opt-field",
                            },
                            {
                                "id": "load0",
                                "op": "load",
                                "operands": ["field0", "mem0"],
                                "origin": f"{module_id}::track-d-opt-load-field",
                            },
                            {
                                "id": "cmp0",
                                "op": "cmp",
                                "operands": ["load0", 0],
                                "origin": f"{module_id}::track-d-opt-cmp-zero",
                            },
                        ],
                        "terminator": {
                            "kind": "cond_br",
                            "cond": "cmp0",
                            "true": "neg",
                            "true_args": ["field0", "mem0"],
                            "false": "retv",
                            "false_args": ["load0"],
                            "origin": f"{module_id}::track-d-opt-branch",
                        },
                    },
                    {
                        "id": "neg",
                        "params": ["field1", "mem1"],
                        "instructions": [
                            {
                                "id": "const0",
                                "op": "const",
                                "operands": [0],
                                "origin": f"{module_id}::track-d-opt-const-zero",
                            },
                            {
                                "id": "mem2",
                                "op": "store",
                                "operands": ["field1", 0, "mem1"],
                                "origin": f"{module_id}::track-d-opt-store-zero",
                            },
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "const0",
                            "origin": f"{module_id}::track-d-opt-ret-zero",
                        },
                    },
                    {
                        "id": "retv",
                        "params": ["value0"],
                        "instructions": [],
                        "terminator": {
                            "kind": "ret",
                            "value": "value0",
                            "origin": f"{module_id}::track-d-opt-ret-value",
                        },
                    },
                ],
            }
        ],
    }


def optimize_python_track_d_module(case_name: str, lowered: dict):
    if case_name == "a_basic_function":
        return optimize_local_cell_module(lowered)
    if case_name in {"a_async_await", "c_opaque_call"}:
        return json.loads(json.dumps(lowered))
    raise PipelineError(f"{case_name}: Python Track D optimization contract is not defined")


def optimize_rust_track_d_module(case_name: str, lowered: dict):
    if case_name == "a_mut_local":
        return optimize_local_cell_module(lowered)
    if case_name == "a_struct_field_borrow_mut":
        return optimize_field_borrow_module(lowered)
    if case_name == "a_async_await":
        return json.loads(json.dumps(lowered))
    raise PipelineError(f"{case_name}: Rust Track D optimization contract is not defined")


def emit_python_track_d_source(case_name: str, optimized: bool):
    if case_name == "a_basic_function" and optimized:
        return (
            "def clamp_nonneg(x):\n"
            "    if x < 0:\n"
            "        return 0\n"
            "    return x\n"
        )
    return PYTHON_SOURCE_TEXTS[case_name]


def emit_rust_track_d_source(case_name: str, optimized: bool):
    if case_name == "a_mut_local" and optimized:
        return (
            "pub fn clamp_nonneg(x: i32) -> i32 {\n"
            "    if x < 0 {\n"
            "        return 0;\n"
            "    }\n"
            "    return x;\n"
            "}\n"
        )
    if case_name == "a_struct_field_borrow_mut" and optimized:
        return (
            "pub struct Counter {\n"
            "    pub value: i32,\n"
            "}\n"
            "\n"
            "pub fn clamp_counter(counter: &mut Counter) -> i32 {\n"
            "    if counter.value < 0 {\n"
            "        counter.value = 0;\n"
            "        return 0;\n"
            "    }\n"
            "    return counter.value;\n"
            "}\n"
        )
    return RUST_SOURCE_TEXTS[case_name]


def execute_python_track_d_case(case_name: str, source_text: str, iterations: int):
    namespace = {"__builtins__": __builtins__}
    compile(source_text, f"<track-d:{case_name}>", "exec")
    if case_name == "a_basic_function":
        exec(compile(source_text, f"<track-d:{case_name}>", "exec"), namespace)
        function = namespace["clamp_nonneg"]
        function(-3)
        start = time.perf_counter()
        checksum = 0
        for index in range(iterations):
            checksum += function(-3 if index % 2 == 0 else 4)
        return time.perf_counter() - start, checksum
    if case_name == "a_async_await":
        exec(compile(source_text, f"<track-d:{case_name}>", "exec"), namespace)

        async def run_many():
            checksum = 0
            for _ in range(iterations):
                checksum += await namespace["load_once"]()
            return checksum

        asyncio.run(run_many())
        start = time.perf_counter()
        checksum = asyncio.run(run_many())
        return time.perf_counter() - start, checksum
    if case_name == "c_opaque_call":
        with tempfile.TemporaryDirectory(prefix="scir-track-d-foreign-api-") as tmp:
            temp_dir = pathlib.Path(tmp)
            (temp_dir / "foreign_api.py").write_text(
                "def ping():\n    return {'status': 'ok', 'origin': 'stub'}\n",
                encoding="utf-8",
            )
            sys.path.insert(0, str(temp_dir))
            try:
                importlib.invalidate_caches()
                sys.modules.pop("foreign_api", None)
                exec(compile(source_text, f"<track-d:{case_name}>", "exec"), namespace)
                function = namespace["ping"]
                function()
                start = time.perf_counter()
                checksum = 0
                for _ in range(iterations):
                    checksum += len(function()["origin"])
                return time.perf_counter() - start, checksum
            finally:
                sys.modules.pop("foreign_api", None)
                sys.path.pop(0)
    raise PipelineError(f"{case_name}: Python Track D execution harness is not defined")


def rust_benchmark_harness(case_name: str, crate_name: str, iterations: int):
    if case_name == "a_mut_local":
        return (
            f"use {crate_name}::clamp_nonneg;\n\n"
            "fn main() {\n"
            "    let mut checksum: i64 = 0;\n"
            f"    for index in 0..{iterations} {{\n"
            "        checksum += clamp_nonneg(if index % 2 == 0 { -3 } else { 4 }) as i64;\n"
            "    }\n"
            "    println!(\"{}\", checksum);\n"
            "}\n"
        )
    if case_name == "a_struct_field_borrow_mut":
        return (
            f"use {crate_name}::{{clamp_counter, Counter}};\n\n"
            "fn main() {\n"
            "    let mut checksum: i64 = 0;\n"
            f"    for index in 0..{iterations} {{\n"
            "        let mut counter = Counter { value: if index % 2 == 0 { -5 } else { 4 } };\n"
            "        checksum += clamp_counter(&mut counter) as i64;\n"
            "        checksum += counter.value as i64;\n"
            "    }\n"
            "    println!(\"{}\", checksum);\n"
            "}\n"
        )
    if case_name == "a_async_await":
        return (
            f"use {crate_name}::load_once;\n"
            "use std::future::Future;\n"
            "use std::pin::Pin;\n"
            "use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};\n\n"
            "fn noop_raw_waker() -> RawWaker {\n"
            "    fn clone(_: *const ()) -> RawWaker { noop_raw_waker() }\n"
            "    fn wake(_: *const ()) {}\n"
            "    fn wake_by_ref(_: *const ()) {}\n"
            "    fn drop(_: *const ()) {}\n"
            "    RawWaker::new(std::ptr::null(), &RawWakerVTable::new(clone, wake, wake_by_ref, drop))\n"
            "}\n\n"
            "fn block_on<F: Future>(future: F) -> F::Output {\n"
            "    let waker = unsafe { Waker::from_raw(noop_raw_waker()) };\n"
            "    let mut future = Pin::from(Box::new(future));\n"
            "    loop {\n"
            "        let mut context = Context::from_waker(&waker);\n"
            "        match Future::poll(future.as_mut(), &mut context) {\n"
            "            Poll::Ready(value) => return value,\n"
            "            Poll::Pending => std::thread::yield_now(),\n"
            "        }\n"
            "    }\n"
            "}\n\n"
            "fn main() {\n"
            "    let mut checksum: i64 = 0;\n"
            f"    for _ in 0..{iterations} {{\n"
            "        checksum += block_on(load_once()) as i64;\n"
            "    }\n"
            "    println!(\"{}\", checksum);\n"
            "}\n"
        )
    raise PipelineError(f"{case_name}: Rust Track D benchmark harness is not defined")


def rust_binary_path(crate_root: pathlib.Path, crate_name: str):
    suffix = ".exe" if sys.platform.startswith("win") else ""
    return crate_root / "target" / "debug" / f"{crate_name}{suffix}"


def measure_rust_track_d_case(case_name: str, source_text: str, iterations: int):
    require_rust_toolchain()
    with tempfile.TemporaryDirectory(
        prefix=f"scir-track-d-rust-{case_name}-",
        ignore_cleanup_errors=True,
    ) as tmp:
        crate_root = pathlib.Path(tmp)
        crate_name = f"track_d_{slug(case_name).replace('-', '_')}"
        (crate_root / "src").mkdir(parents=True, exist_ok=True)
        (crate_root / "src" / "lib.rs").write_text(source_text, encoding="utf-8")
        (crate_root / "src" / "main.rs").write_text(
            rust_benchmark_harness(case_name, crate_name, iterations),
            encoding="utf-8",
        )
        (crate_root / "Cargo.toml").write_text(
            (
                f"[package]\nname = \"{crate_name}\"\nversion = \"0.1.0\"\nedition = \"2021\"\n\n"
                "[lib]\npath = \"src/lib.rs\"\n"
            ),
            encoding="utf-8",
        )

        compile_start = time.perf_counter()
        compile_result = run_rust_command(
            ["cargo", "build", "--quiet"],
            cwd=crate_root,
            capture_output=True,
            text=True,
        )
        compile_time = time.perf_counter() - compile_start
        if compile_result.returncode != 0:
            raise PipelineError(f"{case_name}: cargo build failed for Track D benchmark source")

        binary_path = rust_binary_path(crate_root, crate_name)
        if not binary_path.exists():
            raise PipelineError(f"{case_name}: expected Track D benchmark binary at {binary_path}")

        runtime_start = time.perf_counter()
        run_result = subprocess.run(
            [str(binary_path)],
            cwd=crate_root,
            capture_output=True,
            text=True,
            check=False,
        )
        runtime_time = time.perf_counter() - runtime_start
        if run_result.returncode != 0:
            raise PipelineError(f"{case_name}: Track D benchmark binary failed to execute")

        return {
            "compile_time": compile_time,
            "runtime_time": runtime_time,
            "artifact_size": binary_path.stat().st_size,
            "output": run_result.stdout.strip(),
        }


def run_python_track_d(root: pathlib.Path):
    opaque_nodes, total_nodes, tier_counts = compare_imported_feature_totals(root)
    opaque_fraction = opaque_nodes / total_nodes
    sync_ratios = []
    async_ratio = None
    opaque_ratio = None
    observable_match = True
    instruction_ratios = []

    for case_name in PYTHON_TRACK_D_CASES:
        lowered = lower_supported_module(PYTHON_SCIRH_MODULES[case_name])
        optimized = optimize_python_track_d_module(case_name, lowered)
        scirl_failures, _ = validate_scirl_module(optimized)
        if scirl_failures:
            raise PipelineError(f"{case_name}: optimized Python Track D SCIR-L failed validation")
        instruction_ratios.append(scirl_instruction_count(optimized) / scirl_instruction_count(lowered))

        direct_source = PYTHON_SOURCE_TEXTS[case_name]
        unoptimized_source = emit_python_track_d_source(case_name, optimized=False)
        optimized_source = emit_python_track_d_source(case_name, optimized=True)
        direct_elapsed, direct_value = execute_python_track_d_case(
            case_name,
            direct_source,
            PYTHON_TRACK_D_ITERATIONS[case_name],
        )
        if unoptimized_source == direct_source:
            unoptimized_elapsed, unoptimized_value = direct_elapsed, direct_value
        else:
            unoptimized_elapsed, unoptimized_value = execute_python_track_d_case(
                case_name,
                unoptimized_source,
                PYTHON_TRACK_D_ITERATIONS[case_name],
            )
        if optimized_source == direct_source:
            optimized_elapsed, optimized_value = direct_elapsed, direct_value
        else:
            optimized_elapsed, optimized_value = execute_python_track_d_case(
                case_name,
                optimized_source,
                PYTHON_TRACK_D_ITERATIONS[case_name],
            )
        observable_match = observable_match and direct_value == unoptimized_value == optimized_value
        ratio = optimized_elapsed / direct_elapsed
        if case_name == "a_async_await":
            async_ratio = ratio
        elif case_name == "c_opaque_call":
            opaque_ratio = ratio
            sync_ratios.append(ratio)
        else:
            sync_ratios.append(ratio)

    median_runtime_ratio = statistics.median(sync_ratios)
    gate_s5_pass = (
        median_runtime_ratio <= 1.50
        and async_ratio is not None
        and async_ratio <= 1.75
        and opaque_ratio is not None
        and opaque_ratio <= 1.25
    )
    gate_k8_hit = (
        any(ratio > 2.0 for ratio in sync_ratios)
        or (async_ratio is not None and async_ratio > 2.0)
        or (opaque_ratio is not None and opaque_ratio > 2.0)
        or not observable_match
    )

    manifest = {
        "benchmark_id": "bootstrap-track-d-python-dpy-subset",
        "track": "D",
        "task_family": "python-bootstrap-host-runtime",
        "corpus": {
            "name": "python-bootstrap-fixtures",
            "scope": "Fixed Python bootstrap cases emitted from optimized SCIR-L",
            "hash": corpus_hash(BENCHMARK_CASES),
        },
        "baselines": ["direct source", "typed-AST"],
        "profiles": ["D-PY"],
        "success_gates": ["S5"],
        "kill_gates": ["K8"],
        "contamination_controls": list(TRACK_D_CONTROLS),
    }
    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": "bootstrap-track-d-python-run-2026-03-17",
        "system_under_test": "scir-bootstrap-track-d-python-dpy",
        "track": "D",
        "profile": "D-PY",
        "metrics": {
            "median_runtime_ratio": round(median_runtime_ratio, 4),
            "async_overhead_ratio": round(async_ratio, 4),
            "opaque_boundary_overhead_ratio": round(opaque_ratio, 4),
            "observable_match": observable_match,
            "gate_S5_pass": gate_s5_pass,
            "gate_K8_hit": gate_k8_hit,
            "opaque_fraction": round(opaque_fraction, 4),
            "preservation_level_ceiling": "P3",
            "tier_a_feature_count": tier_counts["A"],
            "tier_b_feature_count": tier_counts["B"],
            "tier_c_feature_count": tier_counts["C"],
            "tier_d_feature_count": tier_counts["D"],
            "instruction_reduction_ratio": round(statistics.mean(instruction_ratios), 4),
        },
        "baseline_comparison": {
            "direct source": round(median_runtime_ratio - 1.0, 4),
            "typed-AST": "translation-only reference",
        },
        "status": "pass" if gate_s5_pass and not gate_k8_hit else "fail",
        "evidence": [
            "optimized Python D-PY source emitted from fixed SCIR-L bootstrap cases",
            "direct-source runtime baseline on the same harness",
            "observable matching checked across direct, unoptimized, and optimized emission",
        ],
    }
    return manifest, result


def run_rust_track_d(root: pathlib.Path):
    require_rust_toolchain()
    opaque_nodes, total_nodes, tier_counts = compare_rust_imported_feature_totals(root)
    opaque_fraction = opaque_nodes / total_nodes
    sync_ratios = []
    async_ratio = None
    compile_ratios = []
    size_ratios = []
    instruction_ratios = []
    observable_match = True

    for case_name in RUST_TRACK_D_CASES:
        lowered = lower_rust_supported_module(RUST_SCIRH_MODULES[case_name])
        optimized = optimize_rust_track_d_module(case_name, lowered)
        scirl_failures, _ = validate_scirl_module(optimized)
        if scirl_failures:
            raise PipelineError(f"{case_name}: optimized Rust Track D SCIR-L failed validation")
        instruction_ratios.append(scirl_instruction_count(optimized) / scirl_instruction_count(lowered))

        direct_source = RUST_SOURCE_TEXTS[case_name]
        unoptimized_source = emit_rust_track_d_source(case_name, optimized=False)
        optimized_source = emit_rust_track_d_source(case_name, optimized=True)
        direct_measure = measure_rust_track_d_case(
            case_name,
            direct_source,
            RUST_TRACK_D_ITERATIONS[case_name],
        )
        if unoptimized_source == direct_source:
            unoptimized_measure = dict(direct_measure)
        else:
            unoptimized_measure = measure_rust_track_d_case(
                case_name,
                unoptimized_source,
                RUST_TRACK_D_ITERATIONS[case_name],
            )
        if optimized_source == direct_source:
            optimized_measure = dict(direct_measure)
        else:
            optimized_measure = measure_rust_track_d_case(
                case_name,
                optimized_source,
                RUST_TRACK_D_ITERATIONS[case_name],
            )
        observable_match = (
            observable_match
            and direct_measure["output"] == unoptimized_measure["output"] == optimized_measure["output"]
        )

        runtime_ratio = optimized_measure["runtime_time"] / direct_measure["runtime_time"]
        compile_ratio = optimized_measure["compile_time"] / direct_measure["compile_time"]
        size_ratio = optimized_measure["artifact_size"] / direct_measure["artifact_size"]
        compile_ratios.append(compile_ratio)
        size_ratios.append(size_ratio)
        if case_name == "a_async_await":
            async_ratio = runtime_ratio
        else:
            sync_ratios.append(runtime_ratio)

    median_runtime_ratio = statistics.median(sync_ratios)
    compile_time_ratio = statistics.median(compile_ratios)
    artifact_size_ratio = statistics.median(size_ratios)
    gate_s5_pass = (
        median_runtime_ratio <= 1.25
        and compile_time_ratio <= 1.50
    )
    gate_k8_hit = (
        any(ratio > 2.0 for ratio in sync_ratios)
        or (async_ratio is not None and async_ratio > 2.0)
        or not observable_match
    )

    manifest = {
        "benchmark_id": "bootstrap-track-d-rust-n-subset",
        "track": "D",
        "task_family": "rust-bootstrap-native-runtime",
        "corpus": {
            "name": "rust-bootstrap-fixtures",
            "scope": "Fixed Rust bootstrap cases emitted from optimized SCIR-L",
            "hash": rust_corpus_hash(),
        },
        "baselines": ["direct source", "typed-AST", "SSA-like internal IR"],
        "profiles": ["N"],
        "success_gates": ["S5"],
        "kill_gates": ["K8"],
        "contamination_controls": list(TRACK_D_CONTROLS),
    }
    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": "bootstrap-track-d-rust-run-2026-03-17",
        "system_under_test": "scir-bootstrap-track-d-rust-n",
        "track": "D",
        "profile": "N",
        "metrics": {
            "median_runtime_ratio": round(median_runtime_ratio, 4),
            "compile_time_ratio": round(compile_time_ratio, 4),
            "artifact_size_ratio": round(artifact_size_ratio, 4),
            "peak_memory_ratio": None,
            "async_overhead_ratio": round(async_ratio, 4),
            "gate_S5_pass": gate_s5_pass,
            "gate_K8_hit": gate_k8_hit,
            "opaque_fraction": round(opaque_fraction, 4),
            "preservation_level_ceiling": "P3",
            "tier_a_feature_count": tier_counts["A"],
            "tier_b_feature_count": tier_counts["B"],
            "tier_c_feature_count": tier_counts["C"],
            "tier_d_feature_count": tier_counts["D"],
            "instruction_reduction_ratio": round(statistics.mean(instruction_ratios), 4),
            "observable_match": observable_match,
        },
        "baseline_comparison": {
            "direct source": round(median_runtime_ratio - 1.0, 4),
            "typed-AST": "translation-only reference",
            "SSA-like internal IR": "reference only",
        },
        "status": "pass" if gate_s5_pass and not gate_k8_hit else "fail",
        "evidence": [
            "optimized Rust N source emitted from fixed SCIR-L bootstrap cases",
            "direct-source runtime and compile-time baselines on the same harness",
            "observable matching checked across direct, unoptimized, and optimized emission",
        ],
    }
    return manifest, result


def run_pipeline(root: pathlib.Path):
    failures = []
    outputs = {
        "scir_h_reports": {},
        "scir_l_reports": {},
        "translation_reports": {},
        "reconstruction_reports": {},
        "reconstruction_preservation_reports": {},
    }

    for case_name in ALL_CASES:
        artifacts = load_import_artifacts(root, case_name)
        failures.extend(validate_import_bundle(root, case_name, artifacts))
        if case_name in REJECTED_CASES:
            if "expected.scirh" in artifacts:
                failures.append(f"{case_name}: rejected case must not emit SCIR-H")
            continue

        scirh_failures, parsed_module, scir_h_report = validate_scirh_case(case_name, artifacts["expected.scirh"])
        failures.extend(scirh_failures)
        failures.extend(
            validate_instance(
                root,
                scir_h_report,
                "schemas/validation_report.schema.json",
                f"{case_name} scir_h_validation",
            )
        )
        outputs["scir_h_reports"][case_name] = scir_h_report
        if parsed_module is None:
            continue
        if case_name in SCIRH_ONLY_CASES:
            continue

        lowered = lower_supported_module(parsed_module)
        failures.extend(validate_lowering_alignment(case_name, lowered))
        scirl_failures, scir_l_report = validate_scirl_module(lowered)
        failures.extend(scirl_failures)
        failures.extend(
            validate_instance(
                root,
                scir_l_report,
                "schemas/validation_report.schema.json",
                f"{case_name} scir_l_validation",
            )
        )
        outputs["scir_l_reports"][case_name] = {
            "module": lowered,
            "text": render_scirl_module(lowered),
            "validation_report": scir_l_report,
        }

        trans_report = translation_report(case_name)
        failures.extend(validate_translation_report(case_name, trans_report))
        failures.extend(
            validate_instance(
                root,
                trans_report,
                "schemas/preservation_report.schema.json",
                f"{case_name} translation_preservation",
            )
        )
        outputs["translation_reports"][case_name] = trans_report

        reconstructed_text, provenance_map, reconstruction_report, preservation_report = build_reconstruction_outputs(
            parsed_module,
        )
        failures.extend(
            validate_instance(
                root,
                reconstruction_report,
                "schemas/reconstruction_report.schema.json",
                f"{case_name} reconstruction_report",
            )
        )
        failures.extend(
            validate_instance(
                root,
                preservation_report,
                "schemas/preservation_report.schema.json",
                f"{case_name} reconstruction_preservation",
            )
        )
        failures.extend(
            validate_reconstruction_artifacts(
                case_name,
                format_module(parsed_module),
                reconstructed_text,
                provenance_map,
                reconstruction_report,
                preservation_report,
            )
        )
        outputs["reconstruction_reports"][case_name] = {
            "source": reconstructed_text,
            "provenance_map": provenance_map,
            "report": reconstruction_report,
        }
        outputs["reconstruction_preservation_reports"][case_name] = preservation_report

    failures.extend(validate_executable_output_set(outputs))
    return failures, outputs


def run_benchmark_suite(root: pathlib.Path):
    failures, outputs = run_pipeline(root)
    try:
        rust_failures, _ = run_rust_pipeline(root)
    except PipelineError as exc:
        return [str(exc)], None
    failures.extend(rust_failures)
    if failures:
        return failures, None

    track_a_manifest, track_a_result = run_track_a(root)
    track_b_manifest, track_b_result = run_track_b(
        root,
        {name: item["report"] for name, item in outputs["reconstruction_reports"].items()},
    )
    track_d_python_manifest, track_d_python_result = run_python_track_d(root)
    try:
        track_d_rust_manifest, track_d_rust_result = run_rust_track_d(root)
    except PipelineError as exc:
        return [str(exc)], None
    benchmark_items = {
        "track_a_manifest": track_a_manifest,
        "track_a_result": track_a_result,
        "track_b_manifest": track_b_manifest,
        "track_b_result": track_b_result,
        "track_d_python_manifest": track_d_python_manifest,
        "track_d_python_result": track_d_python_result,
        "track_d_rust_manifest": track_d_rust_manifest,
        "track_d_rust_result": track_d_rust_result,
    }

    for label, manifest_key, result_key in [
        ("track_a", "track_a_manifest", "track_a_result"),
        ("track_b", "track_b_manifest", "track_b_result"),
        ("track_d_python", "track_d_python_manifest", "track_d_python_result"),
        ("track_d_rust", "track_d_rust_manifest", "track_d_rust_result"),
    ]:
        failures.extend(
            validate_instance(
                root,
                benchmark_items[manifest_key],
                "schemas/benchmark_manifest.schema.json",
                f"{label} manifest",
            )
        )
        failures.extend(
            validate_instance(
                root,
                benchmark_items[result_key],
                "schemas/benchmark_result.schema.json",
                f"{label} result",
            )
        )

    for label, result in [
        ("Track A", track_a_result),
        ("Track B", track_b_result),
        ("Track D Python", track_d_python_result),
        ("Track D Rust", track_d_rust_result),
    ]:
        if result["status"] != "pass":
            failures.append(f"{label}: benchmark status was {result['status']!r}")

    return failures, benchmark_items


def run_self_tests(root: pathlib.Path):
    failures = []
    old_syntax = (
        "module fixture.python_importer.a_basic_function {\n"
        "fn clamp_nonneg(x: int) -> int ! { write } {\n"
        "}\n"
        "}\n"
    )
    scirh_failures, _, _ = validate_scirh_case("a_basic_function", old_syntax)
    if not scirh_failures:
        failures.append("self-test legacy SCIR-H syntax: expected failure")

    base_lowered = lower_supported_module(PYTHON_SCIRH_MODULES["a_basic_function"])
    opaque_lowered = lower_supported_module(PYTHON_SCIRH_MODULES["c_opaque_call"])

    mutated = json.loads(json.dumps(opaque_lowered))
    mutated["functions"][0]["blocks"][0]["instructions"][0]["origin"] = ""
    scirl_failures, _ = validate_scirl_module(mutated)
    if not any("missing provenance origin" in item for item in scirl_failures):
        failures.append("self-test missing SCIR-L provenance: expected failure")

    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][0]["instructions"][0]["op"] = "add"
    scirl_failures, _ = validate_scirl_module(mutated)
    if not any("unsupported op" in item for item in scirl_failures):
        failures.append("self-test unsupported SCIR-L op: expected failure")

    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][0]["instructions"][1]["id"] = "cell0"
    scirl_failures, _ = validate_scirl_module(mutated)
    if not any("duplicate SSA or token id" in item for item in scirl_failures):
        failures.append("self-test duplicate SSA id: expected failure")

    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][1]["id"] = "entry"
    scirl_failures, _ = validate_scirl_module(mutated)
    if not any("duplicate block" in item for item in scirl_failures):
        failures.append("self-test duplicate block id: expected failure")

    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][0]["terminator"]["true"] = "missing"
    scirl_failures, _ = validate_scirl_module(mutated)
    if not any("unknown target block" in item for item in scirl_failures):
        failures.append("self-test bad branch target: expected failure")

    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][0]["terminator"]["true_args"] = ["cell0"]
    scirl_failures, _ = validate_scirl_module(mutated)
    if not any("target arg count mismatch" in item for item in scirl_failures):
        failures.append("self-test bad block arg count: expected failure")

    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][0]["terminator"]["true_args"] = ["cell0", "cell0"]
    scirl_failures, _ = validate_scirl_module(mutated)
    if not any("token class mismatch" in item for item in scirl_failures):
        failures.append("self-test token class mismatch: expected failure")

    mutated_report = translation_report("c_opaque_call")
    mutated_report["profile"] = "R"
    translation_failures = validate_translation_report("c_opaque_call", mutated_report)
    if not any("expected translation profile D-PY" in item for item in translation_failures):
        failures.append("self-test translation overclaim profile: expected failure")
    mutated_report = translation_report("c_opaque_call")
    mutated_report["observables"]["opaque"] = []
    translation_failures = validate_translation_report("c_opaque_call", mutated_report)
    if not any("preserve opaque boundary accounting" in item for item in translation_failures):
        failures.append("self-test translation opaque accounting: expected failure")

    base_scirh_text = format_module(PYTHON_SCIRH_MODULES["a_basic_function"])
    (
        base_reconstructed_text,
        base_provenance_map,
        base_reconstruction_report,
        base_preservation_report,
    ) = build_reconstruction_outputs(PYTHON_SCIRH_MODULES["a_basic_function"])

    reconstruction_failures = validate_reconstruction_artifacts(
        "a_basic_function",
        base_scirh_text,
        "def clamp_nonneg(:\n",
        base_provenance_map,
        base_reconstruction_report,
        base_preservation_report,
    )
    if not any("must compile" in item for item in reconstruction_failures):
        failures.append("self-test invalid reconstruction syntax: expected failure")

    mutated_reconstruction_report = json.loads(json.dumps(base_reconstruction_report))
    mutated_reconstruction_report["test_pass"] = False
    reconstruction_failures = validate_reconstruction_artifacts(
        "a_basic_function",
        base_scirh_text,
        base_reconstructed_text,
        base_provenance_map,
        mutated_reconstruction_report,
        base_preservation_report,
    )
    if not any("test_pass disagreed" in item for item in reconstruction_failures):
        failures.append("self-test reconstruction report/test mismatch: expected failure")

    mutated_preservation_report = json.loads(json.dumps(base_preservation_report))
    mutated_preservation_report["observables"]["opaque"] = ["foreign_api.ping boundary"]
    reconstruction_failures = validate_reconstruction_artifacts(
        "a_basic_function",
        base_scirh_text,
        base_reconstructed_text,
        base_provenance_map,
        base_reconstruction_report,
        mutated_preservation_report,
    )
    if not any("Tier A reconstruction must not introduce opaque accounting" in item for item in reconstruction_failures):
        failures.append("self-test Tier A opaque accounting: expected failure")

    opaque_scirh_text = format_module(PYTHON_SCIRH_MODULES["c_opaque_call"])
    (
        opaque_reconstructed_text,
        opaque_provenance_map,
        opaque_reconstruction_report,
        opaque_preservation_report,
    ) = build_reconstruction_outputs(PYTHON_SCIRH_MODULES["c_opaque_call"])

    mutated_reconstruction_report = json.loads(json.dumps(opaque_reconstruction_report))
    mutated_reconstruction_report["profile"] = "R"
    reconstruction_failures = validate_reconstruction_artifacts(
        "c_opaque_call",
        opaque_scirh_text,
        opaque_reconstructed_text,
        opaque_provenance_map,
        mutated_reconstruction_report,
        opaque_preservation_report,
    )
    if not any("expected reconstruction profile D-PY" in item for item in reconstruction_failures):
        failures.append("self-test opaque reconstruction overclaim profile: expected failure")

    mutated_preservation_report = json.loads(json.dumps(opaque_preservation_report))
    mutated_preservation_report["observables"]["opaque"] = []
    reconstruction_failures = validate_reconstruction_artifacts(
        "c_opaque_call",
        opaque_scirh_text,
        opaque_reconstructed_text,
        opaque_provenance_map,
        opaque_reconstruction_report,
        mutated_preservation_report,
    )
    if not any("retain opaque boundary accounting" in item for item in reconstruction_failures):
        failures.append("self-test opaque reconstruction accounting: expected failure")

    mutated_provenance_map = dict(base_provenance_map)
    mutated_provenance_map.pop(next(iter(mutated_provenance_map)))
    reconstruction_failures = validate_reconstruction_artifacts(
        "a_basic_function",
        base_scirh_text,
        base_reconstructed_text,
        mutated_provenance_map,
        base_reconstruction_report,
        base_preservation_report,
    )
    if not any("provenance_complete disagreed" in item or "missing provenance lines" in item for item in reconstruction_failures):
        failures.append("self-test reconstruction provenance completeness: expected failure")

    output_failures = validate_executable_output_set(
        {
            "scir_l_reports": {},
            "translation_reports": {},
            "reconstruction_reports": {"d_exec_eval": {}},
            "reconstruction_preservation_reports": {},
        }
    )
    if not any("d_exec_eval: non-executable case must not emit reconstruction output" in item for item in output_failures):
        failures.append("self-test rejected case reconstruction output: expected failure")

    importer_only_output_failures = validate_executable_output_set(
        {
            "scir_l_reports": {case_name: {} for case_name in SUPPORTED_CASES} | {"b_direct_call": {}},
            "translation_reports": {case_name: {} for case_name in SUPPORTED_CASES} | {"b_async_arg_await": {}},
            "reconstruction_reports": {case_name: {} for case_name in SUPPORTED_CASES} | {"b_if_else_return": {}},
            "reconstruction_preservation_reports": {case_name: {} for case_name in SUPPORTED_CASES},
        }
    )
    if not any("b_direct_call: non-executable case must not emit SCIR-L output" in item for item in importer_only_output_failures):
        failures.append("self-test importer-only SCIR-L output exclusion: expected failure")
    if not any("b_async_arg_await: non-executable case must not emit translation output" in item for item in importer_only_output_failures):
        failures.append("self-test importer-only translation output exclusion: expected failure")
    if not any("b_if_else_return: non-executable case must not emit reconstruction output" in item for item in importer_only_output_failures):
        failures.append("self-test importer-only reconstruction output exclusion: expected failure")

    for case_name in IMPORT_SUPPORTED_CASES:
        text = format_module(PYTHON_SCIRH_MODULES[case_name])
        parsed = parse_module(text)
        if format_module(parsed) != text:
            failures.append(f"self-test SCIR-H round-trip drifted for {case_name}")

    return failures


def rust_fixture_source(root: pathlib.Path, case_name: str) -> pathlib.Path:
    return root / "tests" / "rust_importer" / "cases" / case_name / "input" / "src" / "lib.rs"


def load_rust_import_artifacts(root: pathlib.Path, case_name: str):
    bundle = build_rust_bundle(root, rust_fixture_source(root, case_name))
    parsed = {}
    for name, contents in bundle.files.items():
        if name.endswith(".json"):
            parsed[name] = json.loads(contents)
        else:
            parsed[name] = contents
    return parsed


def require_rust_toolchain():
    resolution = resolve_rust_toolchain()
    if not resolution["available"]:
        raise PipelineError(f"Rust Phase 6A requires a usable Rust toolchain: {resolution['reason']}")


def run_rust_command(command: list[str], *, cwd: pathlib.Path, capture_output: bool = False, text: bool = False):
    require_rust_toolchain()
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=capture_output,
        text=text,
        check=False,
        env=rust_toolchain_env(),
    )


def validate_rust_scirh_case(case_name: str, scirh_text: str):
    failures = []
    try:
        parsed = parse_module(scirh_text)
    except ScirHModelError as exc:
        failures.append(f"{case_name}: canonical Rust SCIR-H parse failed: {exc}")
        parsed = None

    if parsed is not None:
        expected = RUST_SCIRH_MODULES[case_name]
        if parsed != expected:
            failures.append(
                f"{case_name}: parsed Rust SCIR-H model drifted from the canonical bootstrap module model"
            )
        canonical_text = format_module(parsed)
        if scirh_text != canonical_text:
            failures.append(f"{case_name}: Rust SCIR-H text is not canonical under parse-normalize-format")

    report = {
        "report_id": f"scir-h-validation-{slug(case_name)}",
        "artifact": f"fixture.rust_importer.{case_name}",
        "layer": "scir_h",
        "validator": SCIRH_VALIDATOR_NAME,
        "spec_version": SPEC_VERSION,
        "status": "pass" if not failures else "fail",
        "diagnostics": [
            {
                "code": "HBOOT001",
                "severity": "error",
                "message": message,
            }
            for message in failures
        ],
    }
    return failures, parsed, report


def lower_rust_mut_local(module: Module):
    return lower_basic_function(module)


def lower_rust_struct_field_module(module: Module):
    function = module.functions[0]
    body = list(function.body)
    if len(body) != 2:
        raise PipelineError("a_struct_field_borrow_mut: expected if and return")
    if_stmt, return_stmt = body
    if not (
        len(module.type_decls) == 1
        and module.type_decls[0].name == "Counter"
        and isinstance(if_stmt, IfStmt)
        and isinstance(if_stmt.condition, IntrinsicExpr)
        and if_stmt.condition.op == "lt"
        and len(if_stmt.condition.args) == 2
        and isinstance(if_stmt.condition.args[0], PlaceExpr)
        and format_place(if_stmt.condition.args[0].place) == "counter.value"
        and if_stmt.condition.args[1] == IntExpr(0)
        and len(if_stmt.then_body) == 1
        and not if_stmt.else_body
        and isinstance(if_stmt.then_body[0], SetStmt)
        and format_place(if_stmt.then_body[0].target) == "counter.value"
        and if_stmt.then_body[0].value == IntExpr(0)
        and isinstance(return_stmt, ReturnStmt)
        and isinstance(return_stmt.value, PlaceExpr)
        and format_place(return_stmt.value.place) == "counter.value"
    ):
        raise PipelineError("a_struct_field_borrow_mut: unsupported compact SCIR-H shape for lowering")

    return {
        "module_id": module.module_id,
        "functions": [
            {
                "name": function.name,
                "returns": function.return_type,
                "params": [param.name for param in function.params],
                "blocks": [
                    {
                        "id": "entry",
                        "params": ["mem0"],
                        "instructions": [
                            {
                                "id": "field0",
                                "op": "field.addr",
                                "operands": ["counter", "sym:field:value"],
                                "origin": f"{module.module_id}::field-value",
                            },
                            {
                                "id": "load0",
                                "op": "load",
                                "operands": ["field0", "mem0"],
                                "origin": f"{module.module_id}::lt-load-value",
                            },
                            {
                                "id": "cmp0",
                                "op": "cmp",
                                "operands": ["load0", 0],
                                "origin": f"{module.module_id}::lt-zero",
                            },
                        ],
                        "terminator": {
                            "kind": "cond_br",
                            "cond": "cmp0",
                            "true": "neg",
                            "true_args": ["field0", "mem0"],
                            "false": "retread",
                            "false_args": ["field0", "mem0"],
                            "origin": f"{module.module_id}::branch",
                        },
                    },
                    {
                        "id": "neg",
                        "params": ["field1", "mem1"],
                        "instructions": [
                            {
                                "id": "mem2",
                                "op": "store",
                                "operands": ["field1", 0, "mem1"],
                                "origin": f"{module.module_id}::set-value",
                            },
                        ],
                        "terminator": {
                            "kind": "br",
                            "target": "retread",
                            "args": ["field1", "mem2"],
                            "origin": f"{module.module_id}::join",
                        },
                    },
                    {
                        "id": "retread",
                        "params": ["field2", "mem3"],
                        "instructions": [
                            {
                                "id": "load1",
                                "op": "load",
                                "operands": ["field2", "mem3"],
                                "origin": f"{module.module_id}::return-load-value",
                            },
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "load1",
                            "origin": f"{module.module_id}::return",
                        },
                    },
                ],
            }
        ],
    }


def lower_rust_async_module(module: Module):
    return lower_async_module(module)


def lower_rust_unsafe_module(module: Module):
    function = module.functions[0]
    if not (
        len(module.imports) == 1
        and module.imports[0].local_id == "unsafe_ping"
        and function.body == (ReturnStmt(CallExpr("unsafe_ping", ())),)
    ):
        raise PipelineError("c_unsafe_call: unsupported compact SCIR-H shape for lowering")
    return {
        "module_id": module.module_id,
        "functions": [
            {
                "name": function.name,
                "returns": function.return_type,
                "params": [],
                "blocks": [
                    {
                        "id": "entry",
                        "params": ["eff0"],
                        "instructions": [
                            {
                                "id": "result0",
                                "op": "opaque.call",
                                "operands": ["sym:unsafe_ping", "eff0"],
                                "origin": f"{module.module_id}::unsafe-boundary",
                            },
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "result0",
                            "origin": f"{module.module_id}::return",
                        },
                    }
                ],
            }
        ],
    }


def lower_rust_supported_module(module: Module):
    case_name = case_name_from_module(module)
    if case_name == "a_mut_local":
        return lower_rust_mut_local(module)
    if case_name == "a_struct_field_borrow_mut":
        return lower_rust_struct_field_module(module)
    if case_name == "a_async_await":
        return lower_rust_async_module(module)
    if case_name == "c_unsafe_call":
        return lower_rust_unsafe_module(module)
    raise PipelineError(f"{case_name}: Rust lowering is not defined for this case")


def validate_rust_lowering_alignment(case_name: str, lowered: dict):
    if case_name == "a_mut_local":
        return validate_lowering_alignment("a_basic_function", lowered)
    if case_name == "a_async_await":
        return validate_lowering_alignment("a_async_await", lowered)
    if case_name == "c_unsafe_call":
        function = lowered["functions"][0]
        failures = []
        if function["blocks"][0]["params"] != ["eff0"]:
            failures.append(f"{case_name}: expected unsafe entry effect token parameter")
        if [item["op"] for item in function["blocks"][0]["instructions"]] != ["opaque.call"]:
            failures.append(f"{case_name}: expected opaque.call lowering")
        return failures
    if case_name == "a_struct_field_borrow_mut":
        function = lowered["functions"][0]
        blocks = function["blocks"]
        failures = []
        if function["params"] != ["counter"]:
            failures.append(f"{case_name}: expected borrowed record parameter to remain a function input")
        if [block["id"] for block in blocks] != ["entry", "neg", "retread"]:
            failures.append(f"{case_name}: expected entry/neg/retread block layout")
        if [item["op"] for item in blocks[0]["instructions"]] != ["field.addr", "load", "cmp"]:
            failures.append(f"{case_name}: expected field.addr/load/cmp in entry block")
        if blocks[0]["terminator"]["kind"] != "cond_br":
            failures.append(f"{case_name}: expected cond_br entry terminator")
        if [item["op"] for item in blocks[1]["instructions"]] != ["store"]:
            failures.append(f"{case_name}: expected single store in neg block")
        if [item["op"] for item in blocks[2]["instructions"]] != ["load"]:
            failures.append(f"{case_name}: expected single load in retread block")
        return failures
    return [f"{case_name}: Rust lowering alignment contract is not defined"]


def rust_translation_report(case_name: str):
    preserved = {
        "a_mut_local": ["function boundaries", "mutable local semantics", "branch behavior"],
        "a_struct_field_borrow_mut": ["function boundaries", "borrowed field mutation semantics"],
        "a_async_await": ["function boundaries", "await boundary"],
        "c_unsafe_call": [],
    }
    profile, preservation_level = RUST_RECONSTRUCTION_EXPECTATIONS[case_name]["profile"], RUST_RECONSTRUCTION_EXPECTATIONS[case_name]["preservation_level"]
    return {
        "report_id": f"rust-lowering-preservation-{slug(case_name)}",
        "subject": f"fixture.rust_importer.{case_name}",
        "source_artifact": f"scir_h:fixture.rust_importer.{case_name}",
        "target_artifact": f"scir_l:fixture.rust_importer.{case_name}",
        "profile": profile,
        "preservation_level": preservation_level,
        "status": "pass",
        "observables": {
            "preserved": preserved[case_name],
            "normalized": [],
            "contract_bounded": [],
            "opaque": ["unsafe boundary"] if case_name == "c_unsafe_call" else [],
            "unsupported": [],
        },
        "evidence": [
            TRANSLATION_VALIDATOR_NAME,
            "Rust bootstrap lowering and provenance validated",
        ],
    }


def validate_rust_translation_report(case_name: str, report: dict):
    failures = []
    expected = RUST_RECONSTRUCTION_EXPECTATIONS[case_name]
    if report["profile"] != expected["profile"]:
        failures.append(f"{case_name}: expected translation profile {expected['profile']}")
    if report["preservation_level"] != expected["preservation_level"]:
        failures.append(
            f"{case_name}: expected translation preservation level {expected['preservation_level']}"
        )
    opaque_items = report["observables"]["opaque"]
    if expected["requires_opaque"]:
        if "unsafe boundary" not in opaque_items:
            failures.append(f"{case_name}: Rust translation must preserve unsafe boundary accounting")
    elif opaque_items:
        failures.append(f"{case_name}: Tier A Rust translation must not introduce opaque accounting")
    return failures


def rust_reconstruction_profile(case_name: str):
    expected = RUST_RECONSTRUCTION_EXPECTATIONS[case_name]
    return expected["profile"], expected["preservation_level"]


def rust_visibility(case_name: str, symbol_name: str) -> str:
    if case_name == "a_async_await" and symbol_name == "fetch_value":
        return ""
    return "pub "


def render_rust_type_name(type_name: str) -> str:
    return {
        "int": "i32",
        "borrow_mut<Counter>": "&mut Counter",
        "borrow<Counter>": "&Counter",
    }.get(type_name, type_name)


def render_rust_expr(expr):
    if isinstance(expr, NameExpr):
        return expr.name
    if isinstance(expr, PlaceExpr):
        return format_place(expr.place)
    if isinstance(expr, IntExpr):
        return str(expr.value)
    if isinstance(expr, CallExpr):
        args = ", ".join(render_rust_expr(arg) for arg in expr.args)
        return f"{expr.callee}({args})"
    if isinstance(expr, AwaitExpr):
        return f"{render_rust_expr(expr.value)}.await"
    if isinstance(expr, IntrinsicExpr) and expr.op == "lt":
        return f"{render_rust_expr(expr.args[0])} < {render_rust_expr(expr.args[1])}"
    raise PipelineError(f"unsupported Rust reconstruction expression: {type(expr).__name__}")


def render_rust_stmt(stmt, indent: int):
    prefix = " " * indent
    if isinstance(stmt, VarDecl):
        return [f"{prefix}let mut {stmt.name}: {render_rust_type_name(stmt.type_name)} = {render_rust_expr(stmt.value)};"]
    if isinstance(stmt, SetStmt):
        return [f"{prefix}{format_place(stmt.target)} = {render_rust_expr(stmt.value)};"]
    if isinstance(stmt, ReturnStmt):
        return [f"{prefix}return {render_rust_expr(stmt.value)};"]
    if isinstance(stmt, IfStmt):
        lines = [f"{prefix}if {render_rust_expr(stmt.condition)} {{"]
        for item in stmt.then_body:
            lines.extend(render_rust_stmt(item, indent + 4))
        lines.append(f"{prefix}}}")
        if stmt.else_body:
            lines.append(f"{prefix}else {{")
            for item in stmt.else_body:
                lines.extend(render_rust_stmt(item, indent + 4))
            lines.append(f"{prefix}}}")
        return lines
    raise PipelineError(f"unsupported Rust reconstruction statement: {type(stmt).__name__}")


def reconstruct_rust_source(case_name: str, module: Module):
    lines = []
    for type_decl in module.type_decls:
        if not isinstance(type_decl.type_expr, RecordType):
            raise PipelineError(f"{case_name}: only record type declarations are supported in Rust reconstruction")
        lines.append(f"{rust_visibility(case_name, type_decl.name)}struct {type_decl.name} {{")
        for field in type_decl.type_expr.fields:
            lines.append(f"    pub {field.name}: {render_rust_type_name(field.type_name)},")
        lines.append("}")
        lines.append("")

    for index, function in enumerate(module.functions):
        params = ", ".join(f"{param.name}: {render_rust_type_name(param.type_name)}" for param in function.params)
        if function.is_async:
            header = f"{rust_visibility(case_name, function.name)}async fn {function.name}({params}) -> {render_rust_type_name(function.return_type)}"
        else:
            header = f"{rust_visibility(case_name, function.name)}fn {function.name}({params}) -> {render_rust_type_name(function.return_type)}"
        lines.append(f"{header} {{")
        for stmt in function.body:
            lines.extend(render_rust_stmt(stmt, 4))
        lines.append("}")
        if index != len(module.functions) - 1:
            lines.append("")
    return "\n".join(lines) + "\n"


def evaluate_rust_reconstruction(case_name: str, reconstructed_text: str):
    require_rust_toolchain()
    # Windows can briefly retain Cargo-built executables after subprocess exit.
    with tempfile.TemporaryDirectory(
        prefix=f"scir-rust-reconstruction-{case_name}-",
        ignore_cleanup_errors=True,
    ) as tmp:
        crate_root = pathlib.Path(tmp)
        (crate_root / "src").mkdir(parents=True, exist_ok=True)
        (crate_root / "src" / "lib.rs").write_text(reconstructed_text, encoding="utf-8")
        (crate_root / "Cargo.toml").write_text(
            f"[package]\nname = \"{case_name}\"\nversion = \"0.1.0\"\nedition = \"2021\"\n\n[lib]\npath = \"src/lib.rs\"\n",
            encoding="utf-8",
        )
        tests_dir = crate_root / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "smoke.rs").write_text(RUST_TEST_TEXTS[case_name], encoding="utf-8")
        compile_result = run_rust_command(
            ["cargo", "test", "--quiet", "--no-run"],
            cwd=crate_root,
            capture_output=True,
            text=True,
        )
        if compile_result.returncode != 0:
            return False, False
        test_result = run_rust_command(
            ["cargo", "test", "--quiet"],
            cwd=crate_root,
            capture_output=True,
            text=True,
        )
        return True, test_result.returncode == 0


def build_rust_reconstruction_outputs(module: Module):
    case_name = case_name_from_module(module)
    reconstructed_text = reconstruct_rust_source(case_name, module)
    scirh_text = format_module(module)
    provenance_map = build_provenance_map(scirh_text)
    provenance_complete = provenance_map_matches_canonical_lines(scirh_text, provenance_map)
    compile_pass, test_pass = evaluate_rust_reconstruction(case_name, reconstructed_text)
    profile, preservation_level = rust_reconstruction_profile(case_name)
    notes = ["Reconstructed from the fixed Rust bootstrap SCIR-H slice."]
    if reconstructed_text == RUST_SOURCE_TEXTS[case_name]:
        notes.append("Reconstruction matched the checked-in Rust source text exactly.")
    if provenance_complete:
        notes.append("Line-granular provenance covers every non-empty canonical SCIR-H line.")
    reconstruction_report = {
        "report_id": f"rust-reconstruction-report-{slug(case_name)}",
        "subject": f"fixture.rust_importer.{case_name}",
        "source_language": "rust",
        "target_language": "rust",
        "profile": profile,
        "preservation_level": preservation_level,
        "compile_pass": compile_pass,
        "test_pass": test_pass,
        "idiomaticity_score": 5.0 if reconstructed_text == RUST_SOURCE_TEXTS[case_name] else 4.0,
        "provenance_complete": provenance_complete,
        "notes": notes,
    }
    preservation_report = {
        "report_id": f"rust-reconstruction-preservation-{slug(case_name)}",
        "subject": f"fixture.rust_importer.{case_name}",
        "source_artifact": f"scir_h:fixture.rust_importer.{case_name}",
        "target_artifact": f"reconstructed/rust/{case_name}/src/lib.rs",
        "profile": profile,
        "preservation_level": preservation_level,
        "status": "pass" if compile_pass and test_pass else "fail",
        "observables": {
            "preserved": ["function boundaries", "return behavior"],
            "normalized": [],
            "contract_bounded": [],
            "opaque": [],
            "unsupported": [],
        },
        "evidence": [
            f"compile:{'pass' if compile_pass else 'fail'}",
            f"test:{'pass' if test_pass else 'fail'}",
            f"provenance_map:{'complete' if provenance_complete else 'incomplete'}",
            RECONSTRUCTION_VALIDATOR_NAME,
        ],
    }
    return reconstructed_text, provenance_map, reconstruction_report, preservation_report


def validate_rust_reconstruction_report(case_name: str, scirh_text: str, reconstructed_text: str, provenance_map: dict[str, str], report: dict):
    failures = []
    profile, preservation_level = rust_reconstruction_profile(case_name)
    if report["source_language"] != "rust":
        failures.append(f"{case_name}: expected reconstruction source_language rust")
    if report["target_language"] != "rust":
        failures.append(f"{case_name}: expected reconstruction target_language rust")
    if report["profile"] != profile:
        failures.append(f"{case_name}: expected reconstruction profile {profile}")
    if report["preservation_level"] != preservation_level:
        failures.append(f"{case_name}: expected reconstruction preservation level {preservation_level}")
    actual_compile_pass, actual_test_pass = evaluate_rust_reconstruction(case_name, reconstructed_text)
    if report["compile_pass"] != actual_compile_pass:
        failures.append(f"{case_name}: reconstruction report compile_pass disagreed with execution")
    if report["test_pass"] != actual_test_pass:
        failures.append(f"{case_name}: reconstruction report test_pass disagreed with execution")
    if not actual_compile_pass:
        failures.append(f"{case_name}: supported Rust reconstruction must compile")
    if not actual_test_pass:
        failures.append(f"{case_name}: supported Rust reconstruction must pass fixture smoke tests")
    expected_map = expected_provenance_map(scirh_text)
    missing_lines = [line_no for line_no, text in expected_map.items() if provenance_map.get(line_no) != text]
    unexpected_lines = sorted(set(provenance_map) - set(expected_map))
    actual_complete = not missing_lines and not unexpected_lines
    if report["provenance_complete"] != actual_complete:
        failures.append(f"{case_name}: reconstruction report provenance_complete disagreed with canonical coverage")
    if missing_lines:
        failures.append(f"{case_name}: missing provenance lines for canonical SCIR-H lines {', '.join(missing_lines)}")
    if unexpected_lines:
        failures.append(f"{case_name}: unexpected provenance entries for canonical SCIR-H lines {', '.join(unexpected_lines)}")
    return failures


def validate_rust_reconstruction_preservation_report(case_name: str, reconstruction_report: dict, report: dict):
    failures = []
    profile, preservation_level = rust_reconstruction_profile(case_name)
    if report["profile"] != profile:
        failures.append(f"{case_name}: expected reconstruction preservation profile {profile}")
    if report["preservation_level"] != preservation_level:
        failures.append(f"{case_name}: expected reconstruction preservation level {preservation_level}")
    expected_status = "pass" if reconstruction_report["compile_pass"] and reconstruction_report["test_pass"] else "fail"
    if report["status"] != expected_status:
        failures.append(f"{case_name}: reconstruction preservation status disagreed with compile/test evidence")
    if report["observables"]["opaque"]:
        failures.append(f"{case_name}: Tier A Rust reconstruction must not introduce opaque accounting")
    required_evidence = [
        f"compile:{'pass' if reconstruction_report['compile_pass'] else 'fail'}",
        f"test:{'pass' if reconstruction_report['test_pass'] else 'fail'}",
        f"provenance_map:{'complete' if reconstruction_report['provenance_complete'] else 'incomplete'}",
    ]
    for item in required_evidence:
        if item not in report["evidence"]:
            failures.append(f"{case_name}: reconstruction preservation report missing evidence {item}")
    return failures


def validate_rust_reconstruction_artifacts(case_name: str, scirh_text: str, reconstructed_text: str, provenance_map: dict[str, str], reconstruction_report: dict, preservation_report: dict):
    failures = []
    failures.extend(
        validate_rust_reconstruction_report(case_name, scirh_text, reconstructed_text, provenance_map, reconstruction_report)
    )
    failures.extend(
        validate_rust_reconstruction_preservation_report(case_name, reconstruction_report, preservation_report)
    )
    return failures


def validate_rust_reconstruction_output_set(outputs: dict):
    failures = []
    for case_name in RUST_TIER_A_CASES:
        if case_name not in outputs["reconstruction_reports"]:
            failures.append(f"{case_name}: supported Rust Tier A case must emit a reconstruction output")
        if case_name not in outputs["reconstruction_preservation_reports"]:
            failures.append(f"{case_name}: supported Rust Tier A case must emit a reconstruction preservation report")
    for case_name in ["c_unsafe_call", *RUST_REJECTED_CASES]:
        if case_name in outputs["reconstruction_reports"]:
            failures.append(f"{case_name}: non-Tier-A Rust case must not emit reconstruction output")
        if case_name in outputs["reconstruction_preservation_reports"]:
            failures.append(f"{case_name}: non-Tier-A Rust case must not emit reconstruction preservation report")
    return failures


def run_rust_pipeline(root: pathlib.Path):
    require_rust_toolchain()
    failures = []
    outputs = {
        "scir_h_reports": {},
        "scir_l_reports": {},
        "translation_reports": {},
        "reconstruction_reports": {},
        "reconstruction_preservation_reports": {},
    }
    for case_name in RUST_ALL_CASES:
        artifacts = load_rust_import_artifacts(root, case_name)
        failures.extend(validate_import_bundle(root, case_name, artifacts))
        if case_name in RUST_REJECTED_CASES:
            if "expected.scirh" in artifacts:
                failures.append(f"{case_name}: rejected Rust case must not emit SCIR-H")
            continue
        scirh_failures, parsed_module, scir_h_report = validate_rust_scirh_case(case_name, artifacts["expected.scirh"])
        failures.extend(scirh_failures)
        failures.extend(validate_instance(root, scir_h_report, "schemas/validation_report.schema.json", f"{case_name} scir_h_validation"))
        outputs["scir_h_reports"][case_name] = scir_h_report
        if parsed_module is None:
            continue
        lowered = lower_rust_supported_module(parsed_module)
        failures.extend(validate_rust_lowering_alignment(case_name, lowered))
        scirl_failures, scir_l_report = validate_scirl_module(lowered)
        failures.extend(scirl_failures)
        failures.extend(validate_instance(root, scir_l_report, "schemas/validation_report.schema.json", f"{case_name} scir_l_validation"))
        outputs["scir_l_reports"][case_name] = {
            "module": lowered,
            "text": render_scirl_module(lowered),
            "validation_report": scir_l_report,
        }
        trans_report = rust_translation_report(case_name)
        failures.extend(validate_rust_translation_report(case_name, trans_report))
        failures.extend(validate_instance(root, trans_report, "schemas/preservation_report.schema.json", f"{case_name} translation_preservation"))
        outputs["translation_reports"][case_name] = trans_report

        if case_name in RUST_TIER_A_CASES:
            reconstructed_text, provenance_map, reconstruction_report, preservation_report = build_rust_reconstruction_outputs(parsed_module)
            failures.extend(validate_instance(root, reconstruction_report, "schemas/reconstruction_report.schema.json", f"{case_name} reconstruction_report"))
            failures.extend(validate_instance(root, preservation_report, "schemas/preservation_report.schema.json", f"{case_name} reconstruction_preservation"))
            failures.extend(
                validate_rust_reconstruction_artifacts(
                    case_name,
                    format_module(parsed_module),
                    reconstructed_text,
                    provenance_map,
                    reconstruction_report,
                    preservation_report,
                )
            )
            outputs["reconstruction_reports"][case_name] = {
                "source": reconstructed_text,
                "provenance_map": provenance_map,
                "report": reconstruction_report,
            }
            outputs["reconstruction_preservation_reports"][case_name] = preservation_report
    failures.extend(validate_rust_reconstruction_output_set(outputs))
    return failures, outputs


def run_rust_self_tests(root: pathlib.Path):
    failures = []
    old_syntax = (
        "module fixture.rust_importer.a_struct_field_borrow_mut {\n"
        "fn clamp_counter(counter: borrow_mut<Counter>) -> int !write {\n"
        "}\n"
        "}\n"
    )
    scirh_failures, _, _ = validate_rust_scirh_case("a_struct_field_borrow_mut", old_syntax)
    if not scirh_failures:
        failures.append("self-test Rust legacy SCIR-H syntax: expected failure")

    base_lowered = lower_rust_supported_module(RUST_SCIRH_MODULES["a_struct_field_borrow_mut"])
    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][0]["instructions"][0]["op"] = "load"
    alignment_failures = validate_rust_lowering_alignment("a_struct_field_borrow_mut", mutated)
    if not any("field.addr" in item for item in alignment_failures):
        failures.append("self-test Rust field.addr lowering: expected failure")

    mutated_report = rust_translation_report("c_unsafe_call")
    mutated_report["profile"] = "R"
    translation_failures = validate_rust_translation_report("c_unsafe_call", mutated_report)
    if not any("expected translation profile N" in item for item in translation_failures):
        failures.append("self-test Rust unsafe overclaim profile: expected failure")

    output_failures = validate_rust_reconstruction_output_set(
        {
            "reconstruction_reports": {"d_proc_macro": {}},
            "reconstruction_preservation_reports": {},
        }
    )
    if not any("d_proc_macro: non-Tier-A Rust case must not emit reconstruction output" in item for item in output_failures):
        failures.append("self-test Rust rejected reconstruction output: expected failure")

    for case_name in ["a_mut_local", "a_struct_field_borrow_mut", "a_async_await", "c_unsafe_call"]:
        text = format_module(RUST_SCIRH_MODULES[case_name])
        parsed = parse_module(text)
        if format_module(parsed) != text:
            failures.append(f"self-test Rust SCIR-H round-trip drifted for {case_name}")

    return failures


def print_validation_success():
    print("[pipeline] bootstrap validation passed")
    print(
        "Validated importer outputs, compact canonical SCIR-H parsing and formatting, "
        "SCIR-L lowering, translation preservation reports, reconstruction reports, "
        f"and compile/test evidence for {len(SUPPORTED_CASES)} supported bootstrap cases."
    )


def print_rust_validation_success():
    print("[pipeline] Rust Phase 6A validation passed")
    print(
        "Validated Rust importer outputs, compact canonical SCIR-H parsing and formatting, "
        "SCIR-L lowering with field.addr, translation preservation reports, and compile/test "
        f"evidence for {len(RUST_TIER_A_CASES)} supported Rust Tier A cases."
    )


def print_test_success():
    print("[pipeline] bootstrap self-tests passed")
    print(
        "Negative checks covered legacy SCIR-H syntax, unsupported SCIR-L ops, "
        "duplicate SSA and block ids, bad targets and arg counts, token-class mismatches, "
        "translation overclaims, reconstruction claim/accounting mismatches, invalid reconstruction syntax, "
        "non-executable output exclusion, and SCIR-H round-trips."
    )


def print_rust_test_success():
    print("[pipeline] Rust Phase 6A self-tests passed")
    print(
        "Negative checks covered legacy Rust SCIR-H syntax, field.addr alignment, unsafe-boundary "
        "translation overclaims, rejected-case output exclusion, and Rust SCIR-H round-trips."
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="validate")
    parser.add_argument("--language", default="python", choices=["python", "rust"])
    parser.add_argument("--root")
    return parser.parse_args()


def main():
    args = parse_args()
    root = repo_root(args.root)

    try:
        if args.language == "python":
            failures, _ = run_pipeline(root)
        else:
            failures, _ = run_rust_pipeline(root)
    except PipelineError as exc:
        print(f"[{args.mode}] {args.language} bootstrap pipeline failed")
        print(f" - {exc}")
        sys.exit(1)
    if failures:
        print(f"[{args.mode}] {args.language} bootstrap pipeline failed")
        for item in failures:
            print(f" - {item}")
        sys.exit(1)

    if args.mode == "test":
        self_test_failures = run_self_tests(root) if args.language == "python" else run_rust_self_tests(root)
        if self_test_failures:
            print(f"[test] {args.language} bootstrap pipeline self-tests failed")
            for item in self_test_failures:
                print(f" - {item}")
            sys.exit(1)
        if args.language == "python":
            print_validation_success()
            print_test_success()
        else:
            print_rust_validation_success()
            print_rust_test_success()
        sys.exit(0)

    if args.language == "python":
        print_validation_success()
    else:
        print_rust_validation_success()
    sys.exit(0)


if __name__ == "__main__":
    main()
