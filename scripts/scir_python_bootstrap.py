#!/usr/bin/env python3
"""Python subset importer for the fixed SCIR proof-loop corpus.

This file does not attempt broad Python understanding. It validates and imports
only the checked-in bootstrap cases, emits canonical `SCIR-H`, and records the
case metadata that other validators and benchmark scripts treat as governance
inputs.
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys
from dataclasses import dataclass

from scir_h_bootstrap_model import (
    AwaitExpr,
    BreakStmt,
    CallExpr,
    ContinueStmt,
    FieldPlace,
    FieldType,
    FunctionDecl,
    IfStmt,
    ImportDecl,
    IntExpr,
    IntrinsicExpr,
    LoopStmt,
    Module,
    NameExpr,
    Param,
    PlaceExpr,
    RecordType,
    ReturnStmt,
    SetStmt,
    TypeDecl,
    TryStmt,
    VarDecl,
    format_module,
    normalize_module,
)


SPEC_VERSION = "v0.1-draft"
VALIDATOR_NAME = "python-bootstrap-importer"

SOURCE_TEXTS = {
    "a_basic_function": """def clamp_nonneg(x):
    y = x
    if y < 0:
        y = 0
    return y
""",
    "a_async_await": """async def fetch_value():
    return 1


async def load_once():
    return await fetch_value()
""",
    "b_if_else_return": """def choose_zero_or_x(x):
    if x < 0:
        return 0
    else:
        return x
""",
    "b_direct_call": """def identity(x):
    return x


def call_identity(x):
    return identity(x)
""",
    "b_async_arg_await": """async def fetch_value(x):
    return x


async def load_value(x):
    return await fetch_value(x)
""",
    "b_while_call_update": """def step_until_nonneg(step, x):
    while x < 0:
        x = step(x)
    return x
""",
    "b_while_break_continue": """def step_with_escape(step, x):
    while x < 0:
        if x == -1:
            break
        x = step(x)
        continue
    return x
""",
    "b_class_init_method": """class Counter:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value
""",
    "b_class_field_update": """class Counter:
    def __init__(self, value):
        self.value = value

    def bump(self, step):
        self.value = step(self.value)
        return self.value
""",
    "c_opaque_call": """import foreign_api


def ping():
    return foreign_api.ping()
""",
    "d_exec_eval": """def run(code):
    exec(code)
""",
    "d_try_except": """def guard(may_fail, x):
    try:
        return may_fail(x)
    except ValueError:
        return 0
""",
}


class ImporterError(Exception):
    pass


@dataclass(frozen=True)
class Bundle:
    """Checked-in importer output bundle for one fixed Python corpus case."""

    case_name: str
    files: dict[str, str]


CASE_CONFIG = {
    "a_basic_function": {
        "profiles": ["R", "D-PY"],
        "tier": "A",
        "dependencies": ["python:builtins"],
        "exports": ["clamp_nonneg"],
        "status": "pass",
        "feature_items": [
            {
                "feature": "plain function definition",
                "tier": "A",
                "rationale": "A simple function lowers directly into the compact canonical SCIR-H function form.",
            },
            {
                "feature": "local reassignment",
                "tier": "A",
                "rationale": "Local mutation maps to an explicit mutable binder plus explicit set sites.",
            },
            {
                "feature": "scalar comparison branch",
                "tier": "A",
                "rationale": "The branch condition uses an explicit intrinsic comparison rather than a hidden host operator.",
            },
        ],
        "diagnostics": [],
        "opaque_boundary_contract": None,
    },
    "a_async_await": {
        "profiles": ["R", "D-PY"],
        "tier": "A",
        "dependencies": ["python:builtins"],
        "exports": ["fetch_value", "load_once"],
        "status": "pass",
        "feature_items": [
            {
                "feature": "async function definition",
                "tier": "A",
                "rationale": "Structured async definitions remain explicit in the compact canonical SCIR-H surface.",
            },
            {
                "feature": "simple await",
                "tier": "A",
                "rationale": "A single await point maps directly into the canonical await expression.",
            },
        ],
        "diagnostics": [],
        "opaque_boundary_contract": None,
    },
    "b_if_else_return": {
        "profiles": ["R", "D-PY"],
        "tier": "B",
        "dependencies": ["python:builtins"],
        "exports": ["choose_zero_or_x"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "explicit if/else return normalization",
                "tier": "B",
                "rationale": "A fixed-shape if/else that returns directly from both branches normalizes cleanly into canonical SCIR-H, but this follow-on slice remains importer-only with no executable lowering or reconstruction claim.",
            }
        ],
        "diagnostics": [
            {
                "code": "PY-B002",
                "severity": "warn",
                "message": "Explicit if/else return imports as Tier B canonical SCIR-H only; no executable lowering, translation, or reconstruction path is claimed for this follow-on case.",
                "location": "source.py:1",
            }
        ],
        "opaque_boundary_contract": None,
    },
    "b_direct_call": {
        "profiles": ["R", "D-PY"],
        "tier": "A",
        "dependencies": ["python:builtins"],
        "exports": ["identity", "call_identity"],
        "status": "pass",
        "feature_items": [
            {
                "feature": "direct local call preservation",
                "tier": "A",
                "rationale": "A fixed local direct call site now participates in the active Python proof loop with bounded lowering and reconstruction evidence.",
            }
        ],
        "diagnostics": [],
        "opaque_boundary_contract": None,
    },
    "b_async_arg_await": {
        "profiles": ["R", "D-PY"],
        "tier": "B",
        "dependencies": ["python:builtins"],
        "exports": ["fetch_value", "load_value"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "parameterized async await normalization",
                "tier": "B",
                "rationale": "A fixed-shape async function pair with an awaited local call preserves canonical await structure, but this follow-on slice remains importer-only and does not widen executable claims.",
            }
        ],
        "diagnostics": [
            {
                "code": "PY-B004",
                "severity": "warn",
                "message": "Parameterized async await imports as Tier B canonical SCIR-H only; no executable lowering, translation, or reconstruction path is claimed for this follow-on case.",
                "location": "source.py:1",
            }
        ],
        "opaque_boundary_contract": None,
    },
    "b_while_call_update": {
        "profiles": ["R", "D-PY"],
        "tier": "B",
        "dependencies": ["python:builtins"],
        "exports": ["step_until_nonneg"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "fixed-shape while-loop guard normalization",
                "tier": "B",
                "rationale": "A bounded while loop can normalize into canonical loop plus explicit guard-and-break structure, but this slice remains importer-only and adds no executable downstream claim.",
            },
            {
                "feature": "loop-carried mutation through a direct local call",
                "tier": "B",
                "rationale": "A loop body that updates a local through a direct local call is accepted only as canonical SCIR-H evidence and remains outside lowering, translation, and reconstruction.",
            },
        ],
        "diagnostics": [
            {
                "code": "PY-B005",
                "severity": "warn",
                "message": "Fixed-shape while-loop update imports as Tier B canonical SCIR-H only; no executable lowering, translation, or reconstruction path is claimed for this follow-on case.",
                "location": "source.py:1",
            }
        ],
        "opaque_boundary_contract": None,
    },
    "b_while_break_continue": {
        "profiles": ["R", "D-PY"],
        "tier": "B",
        "dependencies": ["python:builtins"],
        "exports": ["step_with_escape"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "fixed-shape while-loop guard normalization",
                "tier": "B",
                "rationale": "A bounded while loop can normalize into canonical loop plus explicit guard-and-break structure, but this slice remains importer-only and adds no executable downstream claim.",
            },
            {
                "feature": "explicit break normalization",
                "tier": "B",
                "rationale": "A fixed nested break site can normalize into canonical break syntax with a deterministic loop id, but this remains importer-only evidence.",
            },
            {
                "feature": "explicit continue normalization",
                "tier": "B",
                "rationale": "A fixed continue site can normalize into canonical continue syntax with a deterministic loop id, while executable lowering remains out of scope.",
            },
        ],
        "diagnostics": [
            {
                "code": "PY-B006",
                "severity": "warn",
                "message": "Fixed-shape while-loop break/continue imports as Tier B canonical SCIR-H only; no executable lowering, translation, or reconstruction path is claimed for this follow-on case.",
                "location": "source.py:1",
            }
        ],
        "opaque_boundary_contract": None,
    },
    "b_class_init_method": {
        "profiles": ["R", "D-PY"],
        "tier": "B",
        "dependencies": ["python:builtins"],
        "exports": ["Counter", "Counter__init__", "Counter__get"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "bounded record-like class import",
                "tier": "B",
                "rationale": "A single plain class with one explicit instance field can normalize into a canonical record declaration plus plain functions, but this slice remains importer-only and does not widen executable claims.",
            },
            {
                "feature": "explicit instance-field assignment and read normalization",
                "tier": "B",
                "rationale": "The fixed self.value assignment in __init__ and fixed field read in one method reuse canonical field-place syntax, while broader Python object semantics remain deferred.",
            },
        ],
        "diagnostics": [
            {
                "code": "PY-B007",
                "severity": "warn",
                "message": "Bounded class-field import remains Tier B canonical SCIR-H only; no executable lowering, translation, or reconstruction path is claimed for this follow-on case.",
                "location": "source.py:1",
            }
        ],
        "opaque_boundary_contract": None,
    },
    "b_class_field_update": {
        "profiles": ["R", "D-PY"],
        "tier": "B",
        "dependencies": ["python:builtins"],
        "exports": ["Counter", "Counter__init__", "Counter__bump"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "bounded record-like class import with field update method",
                "tier": "B",
                "rationale": "A single plain class with one explicit instance field and one fixed field-update method can normalize into a canonical record declaration plus plain functions, but this slice remains importer-only and does not widen executable claims.",
            },
            {
                "feature": "explicit instance-field read/write normalization through a direct local call",
                "tier": "B",
                "rationale": "The fixed self.value = step(self.value) method body reuses canonical field-place and direct-call syntax while broader Python object semantics remain deferred.",
            },
        ],
        "diagnostics": [
            {
                "code": "PY-B008",
                "severity": "warn",
                "message": "Bounded class field-update import remains Tier B canonical SCIR-H only; no executable lowering, translation, or reconstruction path is claimed for this follow-on case.",
                "location": "source.py:1",
            }
        ],
        "opaque_boundary_contract": None,
    },
    "c_opaque_call": {
        "profiles": ["D-PY"],
        "tier": "C",
        "dependencies": ["python:foreign_api", "capability:foreign_api_ping"],
        "exports": ["ping"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "modules and imports without import hooks",
                "tier": "A",
                "rationale": "The import itself is structured and does not use hook-driven semantics.",
            },
            {
                "feature": "opaque foreign module call",
                "tier": "C",
                "rationale": "The runtime behavior of foreign_api.ping is bounded only by an explicit opaque boundary contract.",
                "fallback": "opaque_call",
            },
        ],
        "diagnostics": [
            {
                "code": "PY-C001",
                "severity": "warn",
                "message": "foreign_api.ping remains an explicit opaque boundary in this bootstrap slice.",
                "location": "source.py:5",
            }
        ],
        "opaque_boundary_contract": {
            "boundary_id": "fixture.python_importer.c_opaque_call.boundary.foreign_api_ping",
            "kind": "opaque_call",
            "signature": "opaque.call foreign_api_ping() -> opaque<ForeignResult> !opaque",
            "effects": ["opaque"],
            "ownership_transfer": {
                "inbound": [],
                "outbound": ["opaque<ForeignResult>"],
            },
            "capabilities": ["capability:foreign_api_ping"],
            "determinism": "unknown",
            "audit_note": "The Python bootstrap slice treats foreign_api.ping as a Tier C opaque boundary rather than modeled semantics.",
        },
    },
    "d_exec_eval": {
        "profiles": ["R", "D-PY"],
        "tier": "D",
        "dependencies": ["python:builtins"],
        "exports": ["run"],
        "status": "fail",
        "feature_items": [
            {
                "feature": "exec/eval",
                "tier": "D",
                "rationale": "Ambient namespace execution is outside the credible Python bootstrap subset.",
                "fallback": "reject",
            }
        ],
        "diagnostics": [
            {
                "code": "PY-D001",
                "severity": "error",
                "message": "exec/eval is rejected in the Python bootstrap fixture subset.",
                "location": "source.py:2",
            }
        ],
        "opaque_boundary_contract": None,
    },
    "d_try_except": {
        "profiles": ["R", "D-PY"],
        "tier": "B",
        "dependencies": ["python:builtins"],
        "exports": ["guard"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "single-handler try/except normalization",
                "tier": "B",
                "rationale": "A minimal unnamed except ValueError block can normalize into canonical try/catch, but the importer synthesizes the catch binder and keeps callable and throw modeling coarse.",
            }
        ],
        "diagnostics": [
            {
                "code": "PY-B001",
                "severity": "warn",
                "message": "Minimal try/except imports as Tier B only; the catch binder is synthesized and no executable lowering or reconstruction path is claimed.",
                "location": "source.py:2",
            }
        ],
        "opaque_boundary_contract": None,
    },
}

PYTHON_PROOF_LOOP_METADATA = {
    "case_order": [
        "a_basic_function",
        "a_async_await",
        "b_direct_call",
        "c_opaque_call",
        "b_if_else_return",
        "b_async_arg_await",
        "b_while_call_update",
        "b_while_break_continue",
        "b_class_init_method",
        "b_class_field_update",
        "d_try_except",
        "d_exec_eval",
    ],
    "executable_cases": [
        "a_basic_function",
        "a_async_await",
        "b_direct_call",
        "c_opaque_call",
    ],
    "importer_only_cases": [
        "b_if_else_return",
        "b_async_arg_await",
        "b_while_call_update",
        "b_while_break_continue",
        "b_class_init_method",
        "b_class_field_update",
        "d_try_except",
    ],
    "rejected_cases": ["d_exec_eval"],
    "benchmark_cases": [
        "a_basic_function",
        "a_async_await",
        "b_direct_call",
        "c_opaque_call",
    ],
    "executable_case_contracts": {
        "a_basic_function": {
            "profile": "R",
            "preservation_level": "P1",
            "requires_opaque_boundary": False,
            "wasm_emittable": True,
        },
        "a_async_await": {
            "profile": "R",
            "preservation_level": "P1",
            "requires_opaque_boundary": False,
            "wasm_emittable": False,
        },
        "b_direct_call": {
            "profile": "R",
            "preservation_level": "P1",
            "requires_opaque_boundary": False,
            "wasm_emittable": True,
        },
        "c_opaque_call": {
            "profile": "D-PY",
            "preservation_level": "P3",
            "requires_opaque_boundary": True,
            "wasm_emittable": False,
        },
    },
}


def _validate_python_proof_loop_metadata():
    """Keep the executable Python proof loop locked to the declared fixed corpus."""

    case_order = PYTHON_PROOF_LOOP_METADATA["case_order"]
    executable_cases = PYTHON_PROOF_LOOP_METADATA["executable_cases"]
    importer_only_cases = PYTHON_PROOF_LOOP_METADATA["importer_only_cases"]
    rejected_cases = PYTHON_PROOF_LOOP_METADATA["rejected_cases"]
    benchmark_cases = PYTHON_PROOF_LOOP_METADATA["benchmark_cases"]
    executable_case_contracts = PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"]

    declared_cases = set(case_order)
    configured_cases = set(CASE_CONFIG)
    source_cases = set(SOURCE_TEXTS)
    if declared_cases != configured_cases or declared_cases != source_cases:
        raise ImporterError(
            "PYTHON_PROOF_LOOP_METADATA must cover exactly the fixed Python bootstrap corpus"
        )

    covered_cases = executable_cases + importer_only_cases + rejected_cases
    if covered_cases != case_order:
        raise ImporterError(
            "PYTHON_PROOF_LOOP_METADATA case classifications must preserve the fixed corpus order"
        )
    if len(set(covered_cases)) != len(covered_cases):
        raise ImporterError("PYTHON_PROOF_LOOP_METADATA case classifications must be disjoint")

    if benchmark_cases != executable_cases:
        raise ImporterError(
            "PYTHON_PROOF_LOOP_METADATA benchmark cases must stay locked to executable cases"
        )

    if set(executable_case_contracts) != set(executable_cases):
        raise ImporterError(
            "PYTHON_PROOF_LOOP_METADATA executable_case_contracts must cover executable cases exactly"
        )

    for case_name in executable_cases:
        config = CASE_CONFIG[case_name]
        if config["tier"] not in {"A", "C"}:
            raise ImporterError(
                f"{case_name}: executable Python proof-loop case must remain Tier A or Tier C"
            )
        contract = executable_case_contracts[case_name]
        if contract["requires_opaque_boundary"] != bool(config["opaque_boundary_contract"]):
            raise ImporterError(
                f"{case_name}: opaque-boundary requirement drifted from CASE_CONFIG"
            )
        if contract["profile"] not in config["profiles"]:
            raise ImporterError(
                f"{case_name}: executable proof-loop profile must remain declared by CASE_CONFIG"
            )

    for case_name in importer_only_cases:
        if CASE_CONFIG[case_name]["tier"] != "B":
            raise ImporterError(
                f"{case_name}: importer-only Python proof-loop case must remain Tier B"
            )

    for case_name in rejected_cases:
        if CASE_CONFIG[case_name]["tier"] != "D":
            raise ImporterError(f"{case_name}: rejected Python proof-loop case must remain Tier D")


_validate_python_proof_loop_metadata()


def build_supported_module(case_name: str) -> Module:
    """Return the canonical `SCIR-H` authority form for an admitted Python case."""

    module_id = f"fixture.python_importer.{case_name}"
    if case_name == "a_basic_function":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="clamp_nonneg",
                        params=(Param("x", "int"),),
                        return_type="int",
                        effects=("write",),
                        body=(
                            VarDecl("y", "int", NameExpr("x")),
                            IfStmt(
                                condition=IntrinsicExpr("lt", (NameExpr("y"), IntExpr(0))),
                                then_body=(SetStmt("y", IntExpr(0)),),
                                else_body=(),
                            ),
                            ReturnStmt(NameExpr("y")),
                        ),
                    ),
                ),
            )
        )
    if case_name == "a_async_await":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="fetch_value",
                        params=(),
                        return_type="int",
                        effects=(),
                        body=(ReturnStmt(IntExpr(1)),),
                        is_async=True,
                    ),
                    FunctionDecl(
                        name="load_once",
                        params=(),
                        return_type="int",
                        effects=("await",),
                        body=(
                            ReturnStmt(AwaitExpr(CallExpr("fetch_value", ()))),
                        ),
                        is_async=True,
                    ),
                ),
            )
        )
    if case_name == "b_if_else_return":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="choose_zero_or_x",
                        params=(Param("x", "int"),),
                        return_type="int",
                        effects=(),
                        body=(
                            IfStmt(
                                condition=IntrinsicExpr("lt", (NameExpr("x"), IntExpr(0))),
                                then_body=(ReturnStmt(IntExpr(0)),),
                                else_body=(ReturnStmt(NameExpr("x")),),
                            ),
                        ),
                    ),
                ),
            )
        )
    if case_name == "b_direct_call":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="identity",
                        params=(Param("x", "int"),),
                        return_type="int",
                        effects=(),
                        body=(ReturnStmt(NameExpr("x")),),
                    ),
                    FunctionDecl(
                        name="call_identity",
                        params=(Param("x", "int"),),
                        return_type="int",
                        effects=(),
                        body=(ReturnStmt(CallExpr("identity", (NameExpr("x"),))),),
                    ),
                ),
            )
        )
    if case_name == "b_async_arg_await":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="fetch_value",
                        params=(Param("x", "int"),),
                        return_type="int",
                        effects=(),
                        body=(ReturnStmt(NameExpr("x")),),
                        is_async=True,
                    ),
                    FunctionDecl(
                        name="load_value",
                        params=(Param("x", "int"),),
                        return_type="int",
                        effects=("await",),
                        body=(
                            ReturnStmt(AwaitExpr(CallExpr("fetch_value", (NameExpr("x"),)))),
                        ),
                        is_async=True,
                    ),
                ),
            )
        )
    if case_name == "b_while_call_update":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="step_until_nonneg",
                        params=(Param("step", "Callable"), Param("x", "int")),
                        return_type="int",
                        effects=("write",),
                        body=(
                            VarDecl("current", "int", NameExpr("x")),
                            LoopStmt(
                                "loop0",
                                (
                                    IfStmt(
                                        condition=IntrinsicExpr("lt", (NameExpr("current"), IntExpr(0))),
                                        then_body=(SetStmt("current", CallExpr("step", (NameExpr("current"),))),),
                                        else_body=(BreakStmt("loop0"),),
                                    ),
                                ),
                            ),
                            ReturnStmt(NameExpr("current")),
                        ),
                    ),
                ),
            )
        )
    if case_name == "b_while_break_continue":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="step_with_escape",
                        params=(Param("step", "Callable"), Param("x", "int")),
                        return_type="int",
                        effects=("write",),
                        body=(
                            VarDecl("current", "int", NameExpr("x")),
                            LoopStmt(
                                "loop0",
                                (
                                    IfStmt(
                                        condition=IntrinsicExpr("lt", (NameExpr("current"), IntExpr(0))),
                                        then_body=(
                                            IfStmt(
                                                condition=IntrinsicExpr("eq", (NameExpr("current"), IntExpr(-1))),
                                                then_body=(BreakStmt("loop0"),),
                                                else_body=(),
                                            ),
                                            SetStmt("current", CallExpr("step", (NameExpr("current"),))),
                                            ContinueStmt("loop0"),
                                        ),
                                        else_body=(BreakStmt("loop0"),),
                                    ),
                                ),
                            ),
                            ReturnStmt(NameExpr("current")),
                        ),
                    ),
                ),
            )
        )
    if case_name == "b_class_init_method":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(
                    TypeDecl("Counter", RecordType((FieldType("value", "int"),))),
                ),
                functions=(
                    FunctionDecl(
                        name="Counter__init__",
                        params=(Param("self", "Counter"), Param("value", "int")),
                        return_type="Counter",
                        effects=("write",),
                        body=(
                            SetStmt(FieldPlace("self", "value"), NameExpr("value")),
                            ReturnStmt(NameExpr("self")),
                        ),
                    ),
                    FunctionDecl(
                        name="Counter__get",
                        params=(Param("self", "Counter"),),
                        return_type="int",
                        effects=(),
                        body=(ReturnStmt(PlaceExpr(FieldPlace("self", "value"))),),
                    ),
                ),
            )
        )
    if case_name == "b_class_field_update":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(
                    TypeDecl("Counter", RecordType((FieldType("value", "int"),))),
                ),
                functions=(
                    FunctionDecl(
                        name="Counter__init__",
                        params=(Param("self", "Counter"), Param("value", "int")),
                        return_type="Counter",
                        effects=("write",),
                        body=(
                            SetStmt(FieldPlace("self", "value"), NameExpr("value")),
                            ReturnStmt(NameExpr("self")),
                        ),
                    ),
                    FunctionDecl(
                        name="Counter__bump",
                        params=(Param("self", "Counter"), Param("step", "Callable")),
                        return_type="int",
                        effects=("write",),
                        body=(
                            SetStmt(
                                FieldPlace("self", "value"),
                                CallExpr("step", (PlaceExpr(FieldPlace("self", "value")),)),
                            ),
                            ReturnStmt(PlaceExpr(FieldPlace("self", "value"))),
                        ),
                    ),
                ),
            )
        )
    if case_name == "c_opaque_call":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(ImportDecl("sym", "foreign_api_ping", "python:foreign_api.ping"),),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="ping",
                        params=(),
                        return_type="opaque<ForeignResult>",
                        effects=("opaque",),
                        body=(ReturnStmt(CallExpr("foreign_api_ping", ())),),
                    ),
                ),
            )
        )
    if case_name == "d_try_except":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="guard",
                        params=(Param("may_fail", "Callable"), Param("x", "int")),
                        return_type="int",
                        effects=("throw",),
                        body=(
                            TryStmt(
                                try_body=(ReturnStmt(CallExpr("may_fail", (NameExpr("x"),))),),
                                catch_name="err",
                                catch_type="ValueError",
                                catch_body=(ReturnStmt(IntExpr(0)),),
                            ),
                        ),
                    ),
                ),
            )
        )
    raise ImporterError(f"{case_name}: canonical SCIR-H is not defined for rejected cases")


SCIRH_MODULES = {
    case_name: build_supported_module(case_name)
    for case_name in (
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
        "d_try_except",
    )
}
SCIRH_TEXTS = {
    case_name: format_module(module)
    for case_name, module in SCIRH_MODULES.items()
}


def is_name(node: ast.AST, value: str) -> bool:
    return isinstance(node, ast.Name) and node.id == value


def is_const(node: ast.AST, value) -> bool:
    return isinstance(node, ast.Constant) and node.value == value


def is_signed_int(node: ast.AST, value: int) -> bool:
    if is_const(node, value):
        return True
    if (
        value < 0
        and isinstance(node, ast.UnaryOp)
        and isinstance(node.op, ast.USub)
        and is_const(node.operand, abs(value))
    ):
        return True
    return False


def is_self_attr(node: ast.AST, attr: str) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "self"
        and node.attr == attr
    )


def ensure_no_annotations(function: ast.FunctionDef | ast.AsyncFunctionDef):
    if function.returns is not None:
        raise ImporterError(f"{function.name}: return annotations are outside the bootstrap corpus")
    for arg in function.args.args:
        if arg.annotation is not None:
            raise ImporterError(f"{function.name}: parameter annotations are outside the bootstrap corpus")


def validate_basic_function(module: ast.Module):
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        raise ImporterError("a_basic_function: expected one plain function definition")

    function = module.body[0]
    ensure_no_annotations(function)
    if function.name != "clamp_nonneg":
        raise ImporterError("a_basic_function: expected function clamp_nonneg")
    if [arg.arg for arg in function.args.args] != ["x"]:
        raise ImporterError("a_basic_function: expected one parameter x")
    if function.decorator_list:
        raise ImporterError("a_basic_function: decorators are outside the bootstrap corpus")
    if len(function.body) != 3:
        raise ImporterError("a_basic_function: expected assignment, if, return")

    assign_stmt, if_stmt, return_stmt = function.body
    if not isinstance(assign_stmt, ast.Assign) or len(assign_stmt.targets) != 1:
        raise ImporterError("a_basic_function: expected y = x")
    if not is_name(assign_stmt.targets[0], "y") or not is_name(assign_stmt.value, "x"):
        raise ImporterError("a_basic_function: expected y = x")

    if not isinstance(if_stmt, ast.If):
        raise ImporterError("a_basic_function: expected if y < 0")
    if not isinstance(if_stmt.test, ast.Compare):
        raise ImporterError("a_basic_function: expected comparison in if")
    compare = if_stmt.test
    if not (
        is_name(compare.left, "y")
        and len(compare.ops) == 1
        and isinstance(compare.ops[0], ast.Lt)
        and len(compare.comparators) == 1
        and is_const(compare.comparators[0], 0)
    ):
        raise ImporterError("a_basic_function: expected if y < 0")
    if if_stmt.orelse:
        raise ImporterError("a_basic_function: explicit else is not part of the source fixture")
    if len(if_stmt.body) != 1:
        raise ImporterError("a_basic_function: expected one assignment in if body")
    inner_assign = if_stmt.body[0]
    if not isinstance(inner_assign, ast.Assign) or len(inner_assign.targets) != 1:
        raise ImporterError("a_basic_function: expected y = 0 in if body")
    if not is_name(inner_assign.targets[0], "y") or not is_const(inner_assign.value, 0):
        raise ImporterError("a_basic_function: expected y = 0 in if body")

    if not isinstance(return_stmt, ast.Return) or not is_name(return_stmt.value, "y"):
        raise ImporterError("a_basic_function: expected return y")


def validate_async_await(module: ast.Module):
    if len(module.body) != 2 or not all(isinstance(node, ast.AsyncFunctionDef) for node in module.body):
        raise ImporterError("a_async_await: expected two async function definitions")

    fetch_value, load_once = module.body
    ensure_no_annotations(fetch_value)
    ensure_no_annotations(load_once)
    if fetch_value.name != "fetch_value" or [arg.arg for arg in fetch_value.args.args] != []:
        raise ImporterError("a_async_await: expected async fn fetch_value()")
    if load_once.name != "load_once" or [arg.arg for arg in load_once.args.args] != []:
        raise ImporterError("a_async_await: expected async fn load_once()")
    if fetch_value.decorator_list or load_once.decorator_list:
        raise ImporterError("a_async_await: decorators are outside the bootstrap corpus")
    if len(fetch_value.body) != 1 or not isinstance(fetch_value.body[0], ast.Return) or not is_const(fetch_value.body[0].value, 1):
        raise ImporterError("a_async_await: expected return 1 in fetch_value")
    if len(load_once.body) != 1 or not isinstance(load_once.body[0], ast.Return):
        raise ImporterError("a_async_await: expected one return in load_once")
    await_expr = load_once.body[0].value
    if not isinstance(await_expr, ast.Await):
        raise ImporterError("a_async_await: expected await expression")
    if not isinstance(await_expr.value, ast.Call) or await_expr.value.keywords or len(await_expr.value.args) != 0:
        raise ImporterError("a_async_await: expected await fetch_value()")
    if not is_name(await_expr.value.func, "fetch_value"):
        raise ImporterError("a_async_await: expected await fetch_value()")


def validate_if_else_return(module: ast.Module):
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        raise ImporterError("b_if_else_return: expected one plain function definition")

    function = module.body[0]
    ensure_no_annotations(function)
    if function.name != "choose_zero_or_x" or [arg.arg for arg in function.args.args] != ["x"]:
        raise ImporterError("b_if_else_return: expected def choose_zero_or_x(x)")
    if function.decorator_list:
        raise ImporterError("b_if_else_return: decorators are outside the bootstrap corpus")
    if len(function.body) != 1 or not isinstance(function.body[0], ast.If):
        raise ImporterError("b_if_else_return: expected one if/else block")

    if_stmt = function.body[0]
    if not isinstance(if_stmt.test, ast.Compare):
        raise ImporterError("b_if_else_return: expected comparison in if")
    compare = if_stmt.test
    if not (
        is_name(compare.left, "x")
        and len(compare.ops) == 1
        and isinstance(compare.ops[0], ast.Lt)
        and len(compare.comparators) == 1
        and is_const(compare.comparators[0], 0)
    ):
        raise ImporterError("b_if_else_return: expected if x < 0")
    if len(if_stmt.body) != 1 or not isinstance(if_stmt.body[0], ast.Return) or not is_const(if_stmt.body[0].value, 0):
        raise ImporterError("b_if_else_return: expected return 0 in if body")
    if len(if_stmt.orelse) != 1 or not isinstance(if_stmt.orelse[0], ast.Return) or not is_name(if_stmt.orelse[0].value, "x"):
        raise ImporterError("b_if_else_return: expected explicit else with return x")


def validate_direct_call(module: ast.Module):
    if len(module.body) != 2 or not all(isinstance(node, ast.FunctionDef) for node in module.body):
        raise ImporterError("b_direct_call: expected two plain function definitions")

    identity, call_identity = module.body
    ensure_no_annotations(identity)
    ensure_no_annotations(call_identity)
    if identity.name != "identity" or [arg.arg for arg in identity.args.args] != ["x"]:
        raise ImporterError("b_direct_call: expected def identity(x)")
    if call_identity.name != "call_identity" or [arg.arg for arg in call_identity.args.args] != ["x"]:
        raise ImporterError("b_direct_call: expected def call_identity(x)")
    if identity.decorator_list or call_identity.decorator_list:
        raise ImporterError("b_direct_call: decorators are outside the bootstrap corpus")
    if len(identity.body) != 1 or not isinstance(identity.body[0], ast.Return) or not is_name(identity.body[0].value, "x"):
        raise ImporterError("b_direct_call: expected return x in identity")
    if len(call_identity.body) != 1 or not isinstance(call_identity.body[0], ast.Return):
        raise ImporterError("b_direct_call: expected one return in call_identity")
    call = call_identity.body[0].value
    if not isinstance(call, ast.Call) or call.keywords or len(call.args) != 1:
        raise ImporterError("b_direct_call: expected identity(x)")
    if not is_name(call.func, "identity") or not is_name(call.args[0], "x"):
        raise ImporterError("b_direct_call: expected direct local call identity(x)")


def validate_async_arg_await(module: ast.Module):
    if len(module.body) != 2 or not all(isinstance(node, ast.AsyncFunctionDef) for node in module.body):
        raise ImporterError("b_async_arg_await: expected two async function definitions")

    fetch_value, load_value = module.body
    ensure_no_annotations(fetch_value)
    ensure_no_annotations(load_value)
    if fetch_value.name != "fetch_value" or [arg.arg for arg in fetch_value.args.args] != ["x"]:
        raise ImporterError("b_async_arg_await: expected async fn fetch_value(x)")
    if load_value.name != "load_value" or [arg.arg for arg in load_value.args.args] != ["x"]:
        raise ImporterError("b_async_arg_await: expected async fn load_value(x)")
    if fetch_value.decorator_list or load_value.decorator_list:
        raise ImporterError("b_async_arg_await: decorators are outside the bootstrap corpus")
    if len(fetch_value.body) != 1 or not isinstance(fetch_value.body[0], ast.Return) or not is_name(fetch_value.body[0].value, "x"):
        raise ImporterError("b_async_arg_await: expected return x in fetch_value")
    if len(load_value.body) != 1 or not isinstance(load_value.body[0], ast.Return):
        raise ImporterError("b_async_arg_await: expected one return in load_value")
    await_expr = load_value.body[0].value
    if not isinstance(await_expr, ast.Await):
        raise ImporterError("b_async_arg_await: expected await expression")
    if not isinstance(await_expr.value, ast.Call) or await_expr.value.keywords or len(await_expr.value.args) != 1:
        raise ImporterError("b_async_arg_await: expected await fetch_value(x)")
    if not is_name(await_expr.value.func, "fetch_value") or not is_name(await_expr.value.args[0], "x"):
        raise ImporterError("b_async_arg_await: expected await fetch_value(x)")


def validate_while_call_update(module: ast.Module):
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        raise ImporterError("b_while_call_update: expected one plain function definition")

    function = module.body[0]
    ensure_no_annotations(function)
    if function.name != "step_until_nonneg" or [arg.arg for arg in function.args.args] != ["step", "x"]:
        raise ImporterError("b_while_call_update: expected def step_until_nonneg(step, x)")
    if function.decorator_list:
        raise ImporterError("b_while_call_update: decorators are outside the bootstrap corpus")
    if len(function.body) != 2 or not isinstance(function.body[0], ast.While):
        raise ImporterError("b_while_call_update: expected one while block followed by return")

    while_stmt, return_stmt = function.body
    if while_stmt.orelse:
        raise ImporterError("b_while_call_update: while-else is outside the bootstrap corpus")
    if not isinstance(while_stmt.test, ast.Compare):
        raise ImporterError("b_while_call_update: expected comparison in while")
    compare = while_stmt.test
    if not (
        is_name(compare.left, "x")
        and len(compare.ops) == 1
        and isinstance(compare.ops[0], ast.Lt)
        and len(compare.comparators) == 1
        and is_const(compare.comparators[0], 0)
    ):
        raise ImporterError("b_while_call_update: expected while x < 0")
    if len(while_stmt.body) != 1 or not isinstance(while_stmt.body[0], ast.Assign):
        raise ImporterError("b_while_call_update: expected one assignment in while body")
    assign_stmt = while_stmt.body[0]
    if len(assign_stmt.targets) != 1 or not is_name(assign_stmt.targets[0], "x"):
        raise ImporterError("b_while_call_update: expected x = step(x)")
    call = assign_stmt.value
    if not isinstance(call, ast.Call) or call.keywords or len(call.args) != 1:
        raise ImporterError("b_while_call_update: expected step(x)")
    if not is_name(call.func, "step") or not is_name(call.args[0], "x"):
        raise ImporterError("b_while_call_update: expected step(x)")
    if not isinstance(return_stmt, ast.Return) or not is_name(return_stmt.value, "x"):
        raise ImporterError("b_while_call_update: expected return x")


def validate_while_break_continue(module: ast.Module):
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        raise ImporterError("b_while_break_continue: expected one plain function definition")

    function = module.body[0]
    ensure_no_annotations(function)
    if function.name != "step_with_escape" or [arg.arg for arg in function.args.args] != ["step", "x"]:
        raise ImporterError("b_while_break_continue: expected def step_with_escape(step, x)")
    if function.decorator_list:
        raise ImporterError("b_while_break_continue: decorators are outside the bootstrap corpus")
    if len(function.body) != 2 or not isinstance(function.body[0], ast.While):
        raise ImporterError("b_while_break_continue: expected one while block followed by return")

    while_stmt, return_stmt = function.body
    if while_stmt.orelse:
        raise ImporterError("b_while_break_continue: while-else is outside the bootstrap corpus")
    if not isinstance(while_stmt.test, ast.Compare):
        raise ImporterError("b_while_break_continue: expected comparison in while")
    compare = while_stmt.test
    if not (
        is_name(compare.left, "x")
        and len(compare.ops) == 1
        and isinstance(compare.ops[0], ast.Lt)
        and len(compare.comparators) == 1
        and is_const(compare.comparators[0], 0)
    ):
        raise ImporterError("b_while_break_continue: expected while x < 0")
    if len(while_stmt.body) != 3:
        raise ImporterError("b_while_break_continue: expected if-break, assignment, continue in while body")
    if_stmt, assign_stmt, continue_stmt = while_stmt.body
    if not isinstance(if_stmt, ast.If):
        raise ImporterError("b_while_break_continue: expected nested if x == -1")
    if if_stmt.orelse:
        raise ImporterError("b_while_break_continue: nested if else is outside the bootstrap corpus")
    if not isinstance(if_stmt.test, ast.Compare):
        raise ImporterError("b_while_break_continue: expected comparison in nested if")
    nested_compare = if_stmt.test
    if not (
        is_name(nested_compare.left, "x")
        and len(nested_compare.ops) == 1
        and isinstance(nested_compare.ops[0], ast.Eq)
        and len(nested_compare.comparators) == 1
        and is_signed_int(nested_compare.comparators[0], -1)
    ):
        raise ImporterError("b_while_break_continue: expected if x == -1")
    if len(if_stmt.body) != 1 or not isinstance(if_stmt.body[0], ast.Break):
        raise ImporterError("b_while_break_continue: expected break in nested if body")
    if not isinstance(assign_stmt, ast.Assign) or len(assign_stmt.targets) != 1 or not is_name(assign_stmt.targets[0], "x"):
        raise ImporterError("b_while_break_continue: expected x = step(x)")
    call = assign_stmt.value
    if not isinstance(call, ast.Call) or call.keywords or len(call.args) != 1:
        raise ImporterError("b_while_break_continue: expected step(x)")
    if not is_name(call.func, "step") or not is_name(call.args[0], "x"):
        raise ImporterError("b_while_break_continue: expected step(x)")
    if not isinstance(continue_stmt, ast.Continue):
        raise ImporterError("b_while_break_continue: expected continue")
    if not isinstance(return_stmt, ast.Return) or not is_name(return_stmt.value, "x"):
        raise ImporterError("b_while_break_continue: expected return x")


def validate_class_init_method(module: ast.Module):
    if len(module.body) != 1 or not isinstance(module.body[0], ast.ClassDef):
        raise ImporterError("b_class_init_method: expected one plain class definition")

    class_def = module.body[0]
    if class_def.name != "Counter":
        raise ImporterError("b_class_init_method: expected class Counter")
    if class_def.bases or class_def.keywords:
        raise ImporterError("b_class_init_method: inheritance is outside the bootstrap corpus")
    if class_def.decorator_list:
        raise ImporterError("b_class_init_method: decorators are outside the bootstrap corpus")
    if len(class_def.body) != 2:
        raise ImporterError("b_class_init_method: expected exactly __init__ and get methods")
    if not all(isinstance(stmt, ast.FunctionDef) for stmt in class_def.body):
        raise ImporterError("b_class_init_method: expected only plain methods in class body")

    init_fn, get_fn = class_def.body
    if init_fn.name != "__init__":
        raise ImporterError("b_class_init_method: expected __init__ as the first method")
    if get_fn.name != "get":
        raise ImporterError("b_class_init_method: expected get as the second method")

    for function in (init_fn, get_fn):
        ensure_no_annotations(function)
        if function.decorator_list:
            raise ImporterError(
                f"b_class_init_method: {function.name} decorators are outside the bootstrap corpus"
            )
        args = function.args
        if args.posonlyargs or args.vararg or args.kwonlyargs or args.kwarg:
            raise ImporterError(f"b_class_init_method: {function.name} uses unsupported parameters")
        if args.defaults or args.kw_defaults:
            raise ImporterError(f"b_class_init_method: {function.name} defaults are outside the bootstrap corpus")

    if [arg.arg for arg in init_fn.args.args] != ["self", "value"]:
        raise ImporterError("b_class_init_method: expected def __init__(self, value)")
    if len(init_fn.body) != 1 or not isinstance(init_fn.body[0], ast.Assign):
        raise ImporterError("b_class_init_method: expected one assignment in __init__")
    init_assign = init_fn.body[0]
    if len(init_assign.targets) != 1 or not is_self_attr(init_assign.targets[0], "value"):
        raise ImporterError("b_class_init_method: expected self.value = value in __init__")
    if not is_name(init_assign.value, "value"):
        raise ImporterError("b_class_init_method: expected self.value = value in __init__")

    if [arg.arg for arg in get_fn.args.args] != ["self"]:
        raise ImporterError("b_class_init_method: expected def get(self)")
    if len(get_fn.body) != 1 or not isinstance(get_fn.body[0], ast.Return):
        raise ImporterError("b_class_init_method: expected one return in get")
    if not is_self_attr(get_fn.body[0].value, "value"):
        raise ImporterError("b_class_init_method: expected return self.value in get")


def validate_class_field_update(module: ast.Module):
    if len(module.body) != 1 or not isinstance(module.body[0], ast.ClassDef):
        raise ImporterError("b_class_field_update: expected one plain class definition")

    class_def = module.body[0]
    if class_def.name != "Counter":
        raise ImporterError("b_class_field_update: expected class Counter")
    if class_def.bases or class_def.keywords:
        raise ImporterError("b_class_field_update: inheritance is outside the bootstrap corpus")
    if class_def.decorator_list:
        raise ImporterError("b_class_field_update: decorators are outside the bootstrap corpus")
    if len(class_def.body) != 2:
        raise ImporterError("b_class_field_update: expected exactly __init__ and bump methods")
    if not all(isinstance(stmt, ast.FunctionDef) for stmt in class_def.body):
        raise ImporterError("b_class_field_update: expected only plain methods in class body")

    init_fn, bump_fn = class_def.body
    if init_fn.name != "__init__":
        raise ImporterError("b_class_field_update: expected __init__ as the first method")
    if bump_fn.name != "bump":
        raise ImporterError("b_class_field_update: expected bump as the second method")

    for function in (init_fn, bump_fn):
        ensure_no_annotations(function)
        if function.decorator_list:
            raise ImporterError(
                f"b_class_field_update: {function.name} decorators are outside the bootstrap corpus"
            )
        args = function.args
        if args.posonlyargs or args.vararg or args.kwonlyargs or args.kwarg:
            raise ImporterError(f"b_class_field_update: {function.name} uses unsupported parameters")
        if args.defaults or args.kw_defaults:
            raise ImporterError(f"b_class_field_update: {function.name} defaults are outside the bootstrap corpus")

    if [arg.arg for arg in init_fn.args.args] != ["self", "value"]:
        raise ImporterError("b_class_field_update: expected def __init__(self, value)")
    if len(init_fn.body) != 1 or not isinstance(init_fn.body[0], ast.Assign):
        raise ImporterError("b_class_field_update: expected one assignment in __init__")
    init_assign = init_fn.body[0]
    if len(init_assign.targets) != 1 or not is_self_attr(init_assign.targets[0], "value"):
        raise ImporterError("b_class_field_update: expected self.value = value in __init__")
    if not is_name(init_assign.value, "value"):
        raise ImporterError("b_class_field_update: expected self.value = value in __init__")

    if [arg.arg for arg in bump_fn.args.args] != ["self", "step"]:
        raise ImporterError("b_class_field_update: expected def bump(self, step)")
    if len(bump_fn.body) != 2:
        raise ImporterError("b_class_field_update: expected assignment and return in bump")
    assign_stmt, return_stmt = bump_fn.body
    if not isinstance(assign_stmt, ast.Assign) or len(assign_stmt.targets) != 1:
        raise ImporterError("b_class_field_update: expected self.value = step(self.value)")
    if not is_self_attr(assign_stmt.targets[0], "value"):
        raise ImporterError("b_class_field_update: expected self.value = step(self.value)")
    call = assign_stmt.value
    if not isinstance(call, ast.Call) or call.keywords or len(call.args) != 1:
        raise ImporterError("b_class_field_update: expected step(self.value)")
    if not is_name(call.func, "step") or not is_self_attr(call.args[0], "value"):
        raise ImporterError("b_class_field_update: expected step(self.value)")
    if not isinstance(return_stmt, ast.Return) or not is_self_attr(return_stmt.value, "value"):
        raise ImporterError("b_class_field_update: expected return self.value")


def validate_opaque_call(module: ast.Module):
    """Admit the Tier C opaque case only when the source stays an explicit boundary, not modeled semantics."""

    if len(module.body) != 2:
        raise ImporterError("c_opaque_call: expected one import and one function")
    import_stmt, function = module.body
    if not isinstance(import_stmt, ast.Import) or len(import_stmt.names) != 1:
        raise ImporterError("c_opaque_call: expected import foreign_api")
    alias = import_stmt.names[0]
    if alias.name != "foreign_api" or alias.asname is not None:
        raise ImporterError("c_opaque_call: expected import foreign_api")
    if not isinstance(function, ast.FunctionDef):
        raise ImporterError("c_opaque_call: expected plain function ping")
    ensure_no_annotations(function)
    if function.name != "ping" or [arg.arg for arg in function.args.args] != []:
        raise ImporterError("c_opaque_call: expected def ping()")
    if function.decorator_list:
        raise ImporterError("c_opaque_call: decorators are outside the bootstrap corpus")
    if len(function.body) != 1 or not isinstance(function.body[0], ast.Return):
        raise ImporterError("c_opaque_call: expected one return in ping")
    call = function.body[0].value
    if not isinstance(call, ast.Call) or call.args or call.keywords:
        raise ImporterError("c_opaque_call: expected foreign_api.ping()")
    if not isinstance(call.func, ast.Attribute):
        raise ImporterError("c_opaque_call: expected foreign_api.ping()")
    if not is_name(call.func.value, "foreign_api") or call.func.attr != "ping":
        raise ImporterError("c_opaque_call: expected foreign_api.ping()")


def validate_exec_eval(module: ast.Module):
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        raise ImporterError("d_exec_eval: expected one function")
    function = module.body[0]
    ensure_no_annotations(function)
    if function.name != "run" or [arg.arg for arg in function.args.args] != ["code"]:
        raise ImporterError("d_exec_eval: expected def run(code)")
    if function.decorator_list:
        raise ImporterError("d_exec_eval: decorators are outside the bootstrap corpus")
    if len(function.body) != 1 or not isinstance(function.body[0], ast.Expr):
        raise ImporterError("d_exec_eval: expected exec(code)")
    expr = function.body[0].value
    if not isinstance(expr, ast.Call) or expr.keywords or len(expr.args) != 1:
        raise ImporterError("d_exec_eval: expected exec(code)")
    if not isinstance(expr.func, ast.Name) or expr.func.id not in {"exec", "eval"}:
        raise ImporterError("d_exec_eval: expected exec(...) or eval(...)")
    if not is_name(expr.args[0], "code"):
        raise ImporterError("d_exec_eval: expected exec(code)")


def validate_try_except(module: ast.Module):
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        raise ImporterError("d_try_except: expected one function")
    function = module.body[0]
    ensure_no_annotations(function)
    if function.name != "guard" or [arg.arg for arg in function.args.args] != ["may_fail", "x"]:
        raise ImporterError("d_try_except: expected def guard(may_fail, x)")
    if function.decorator_list:
        raise ImporterError("d_try_except: decorators are outside the bootstrap corpus")
    if len(function.body) != 1 or not isinstance(function.body[0], ast.Try):
        raise ImporterError("d_try_except: expected one try/except block")
    try_stmt = function.body[0]
    if try_stmt.orelse or try_stmt.finalbody:
        raise ImporterError("d_try_except: else/finally are outside the bootstrap corpus")
    if len(try_stmt.body) != 1 or not isinstance(try_stmt.body[0], ast.Return):
        raise ImporterError("d_try_except: expected return may_fail(x) in try body")
    call = try_stmt.body[0].value
    if not isinstance(call, ast.Call) or call.keywords or len(call.args) != 1:
        raise ImporterError("d_try_except: expected may_fail(x)")
    if not is_name(call.func, "may_fail") or not is_name(call.args[0], "x"):
        raise ImporterError("d_try_except: expected may_fail(x)")
    if len(try_stmt.handlers) != 1:
        raise ImporterError("d_try_except: expected one except handler")
    handler = try_stmt.handlers[0]
    if handler.name is not None:
        raise ImporterError("d_try_except: named exception binding is outside the bootstrap corpus")
    if not is_name(handler.type, "ValueError"):
        raise ImporterError("d_try_except: expected except ValueError")
    if len(handler.body) != 1 or not isinstance(handler.body[0], ast.Return) or not is_const(handler.body[0].value, 0):
        raise ImporterError("d_try_except: expected return 0 in except body")


CASE_VALIDATORS = {
    "a_basic_function": validate_basic_function,
    "a_async_await": validate_async_await,
    "b_if_else_return": validate_if_else_return,
    "b_direct_call": validate_direct_call,
    "b_async_arg_await": validate_async_arg_await,
    "b_while_call_update": validate_while_call_update,
    "b_while_break_continue": validate_while_break_continue,
    "b_class_init_method": validate_class_init_method,
    "b_class_field_update": validate_class_field_update,
    "c_opaque_call": validate_opaque_call,
    "d_exec_eval": validate_exec_eval,
    "d_try_except": validate_try_except,
}


def make_summary(items: list[dict[str, str]]) -> dict[str, int]:
    summary = {"A": 0, "B": 0, "C": 0, "D": 0}
    for item in items:
        summary[item["tier"]] += 1
    return summary


def derive_case_name(source_path: pathlib.Path) -> str:
    case_name = source_path.parent.name
    if case_name not in CASE_CONFIG:
        raise ImporterError(
            f"{source_path}: not part of the fixed Python bootstrap corpus"
        )
    return case_name


def relative_source_path(root: pathlib.Path, source_path: pathlib.Path) -> str:
    try:
        return source_path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ImporterError(f"{source_path}: source must live under {root}") from exc


def build_bundle(root: pathlib.Path, source_path: pathlib.Path) -> Bundle:
    """Rebuild the canonical importer bundle and fail if any checked-in artifact drifts."""

    source_text = source_path.read_text(encoding="utf-8")
    case_name = derive_case_name(source_path)
    if source_text != SOURCE_TEXTS[case_name]:
        raise ImporterError(
            f"{source_path}: source does not match the checked-in bootstrap fixture text"
        )

    tree = ast.parse(source_text)
    CASE_VALIDATORS[case_name](tree)
    source_rel = relative_source_path(root, source_path)
    module_id = f"fixture.python_importer.{case_name}"
    config = CASE_CONFIG[case_name]
    summary = make_summary(config["feature_items"])
    validation_slug = case_name.replace("_", "-")

    module_manifest = {
        "module_id": module_id,
        "layer": "scir_h",
        "source_language": "python",
        "source_path": source_rel,
        "declared_profiles": config["profiles"],
        "declared_tier": config["tier"],
        "dependencies": config["dependencies"],
        "exports": config["exports"],
        "opaque_boundary_count": 1 if config["opaque_boundary_contract"] else 0,
    }
    feature_tier_report = {
        "report_id": f"fixture-feature-tier-{validation_slug}",
        "subject": module_id,
        "source_language": "python",
        "summary": summary,
        "items": config["feature_items"],
    }
    validation_report = {
        "report_id": f"fixture-validation-{validation_slug}",
        "artifact": module_id,
        "layer": "scir_h",
        "validator": VALIDATOR_NAME,
        "spec_version": SPEC_VERSION,
        "status": config["status"],
        "diagnostics": config["diagnostics"],
    }

    files = {
        "module_manifest.json": json.dumps(module_manifest, indent=2) + "\n",
        "feature_tier_report.json": json.dumps(feature_tier_report, indent=2) + "\n",
        "validation_report.json": json.dumps(validation_report, indent=2) + "\n",
    }
    if case_name in SCIRH_MODULES:
        files["expected.scirh"] = format_module(SCIRH_MODULES[case_name])
    opaque_contract = config["opaque_boundary_contract"]
    if opaque_contract is not None:
        files["opaque_boundary_contract.json"] = json.dumps(opaque_contract, indent=2) + "\n"
    return Bundle(case_name=case_name, files=files)


def write_bundle(bundle: Bundle, output_dir: pathlib.Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, contents in bundle.files.items():
        (output_dir / name).write_text(contents, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--root")
    return parser.parse_args()


def main():
    args = parse_args()
    root = pathlib.Path(args.root).resolve() if args.root else pathlib.Path(__file__).resolve().parents[1]
    source_path = pathlib.Path(args.source).resolve()
    output_dir = pathlib.Path(args.output_dir).resolve()

    try:
        bundle = build_bundle(root, source_path)
    except ImporterError as exc:
        print(f"[import] failed: {exc}")
        sys.exit(1)

    write_bundle(bundle, output_dir)
    print(
        f"[import] wrote {len(bundle.files)} artifact files for {bundle.case_name} "
        f"to {output_dir}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
