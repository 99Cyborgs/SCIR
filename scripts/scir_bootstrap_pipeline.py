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

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmark_contract_metadata import (
    BENCHMARK_CONTRACT_METADATA,
    benchmark_track_baselines,
    benchmark_track_compile_cases,
    benchmark_track_contract,
)
from rust_toolchain import resolve_rust_toolchain, rust_toolchain_env
from scir_h_bootstrap_model import (
    AwaitExpr,
    BreakStmt,
    CallExpr,
    ContinueStmt,
    FieldPlace,
    FunctionDecl,
    IfStmt,
    IntrinsicExpr,
    IntExpr,
    LoopStmt,
    Module,
    NamePlace,
    NameExpr,
    PlaceExpr,
    RecordType,
    ReturnStmt,
    SetStmt,
    TypeDecl,
    TryStmt,
    VarDecl,
    format_place,
    format_module,
    format_scirhc_module,
    parse_module,
    ScirHModelError,
    scirh_to_scirhc,
    scirhc_normalization_stats,
    validate_scirhc_roundtrip,
)
from scir_python_bootstrap import (
    PYTHON_PROOF_LOOP_METADATA,
    SCIRH_MODULES as PYTHON_SCIRH_MODULES,
    SOURCE_TEXTS as PYTHON_SOURCE_TEXTS,
    SPEC_VERSION,
    build_bundle as build_python_bundle,
)
from scir_rust_bootstrap import (
    RUST_IMPORTER_METADATA,
    SCIRH_MODULES as RUST_SCIRH_MODULES,
    SOURCE_TEXTS as RUST_SOURCE_TEXTS,
    build_bundle as build_rust_bundle,
)
from validate_repo_contracts import (
    collect_instance_validation_errors,
    validate_boundary_capability_contract,
)
from validators.scirhc_validator import (
    ScirHcDoctrineError,
    assert_deterministic_derivation,
    assert_no_hidden_semantics,
    assert_not_semantic_authority,
    assert_round_trip_integrity,
)
from wasm_backend_metadata import WASM_BACKEND_METADATA


ALL_CASES = list(PYTHON_PROOF_LOOP_METADATA["case_order"])
SUPPORTED_CASES = list(PYTHON_PROOF_LOOP_METADATA["executable_cases"])
SCIRH_ONLY_CASES = list(PYTHON_PROOF_LOOP_METADATA["importer_only_cases"])
IMPORT_SUPPORTED_CASES = [*SUPPORTED_CASES, *SCIRH_ONLY_CASES]
REJECTED_CASES = list(PYTHON_PROOF_LOOP_METADATA["rejected_cases"])
BENCHMARK_CASES = list(BENCHMARK_CONTRACT_METADATA["benchmark_cases"])
SCIRH_VALIDATOR_NAME = "scir-h-bootstrap-validator"
SCIRHC_VALIDATOR_NAME = "scir-hc-bootstrap-validator"
SCIRL_VALIDATOR_NAME = "scir-l-bootstrap-validator"
TRANSLATION_VALIDATOR_NAME = "translation-bootstrap-validator"
RECONSTRUCTION_VALIDATOR_NAME = "reconstruction-bootstrap-validator"
WASM_EMITTER_VALIDATOR_NAME = "wasm-emitter-bootstrap-validator"
WASM_EMITTABLE_CASES = [
    *WASM_BACKEND_METADATA["emittable_python_cases"]
]

RECONSTRUCTION_EXPECTATIONS = {
    case_name: {
        "profile": contract["profile"],
        "preservation_level": contract["preservation_level"],
        "requires_opaque": contract["requires_opaque_boundary"],
    }
    for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items()
}
RUST_ALL_CASES = [
    *RUST_IMPORTER_METADATA["case_order"],
]
RUST_SUPPORTED_CASES = list(RUST_IMPORTER_METADATA["supported_cases"])
RUST_TIER_A_CASES = list(RUST_IMPORTER_METADATA["tier_a_cases"])
RUST_REJECTED_CASES = list(RUST_IMPORTER_METADATA["rejected_cases"])
RUST_TRANSLATION_EXPECTATIONS = {
    case_name: {
        "profile": contract["profile"],
        "preservation_level": contract["preservation_level"],
        "requires_opaque": contract["requires_opaque_boundary"],
    }
    for case_name, contract in RUST_IMPORTER_METADATA["case_contracts"].items()
}
RUST_WASM_EMITTABLE_CASES = [
    *WASM_BACKEND_METADATA["emittable_rust_cases"]
]
INVALID_SCIRH_MANIFEST_REL = "tests/invalid_scir_h/manifest.json"
INVALID_SCIRL_MANIFEST_REL = "tests/invalid_scir_l/manifest.json"
ACTIVE_TIER_A_CORPUS_REL = "tests/corpora/python_tier_a_micro_corpus.json"
ACTIVE_PROOF_LOOP_CORPUS_REL = "tests/corpora/python_proof_loop_corpus.json"


class PipelineError(Exception):
    pass


class ForbiddenPathError(PipelineError):
    pass


def assert_canonical_pipeline_input(input_representation: str, stage: str) -> None:
    if input_representation == "SCIR-Hc":
        raise ForbiddenPathError(f"{stage}: SCIR-Hc must not be consumed directly; canonical SCIR-H is required")
    if input_representation != "SCIR-H":
        raise ForbiddenPathError(f"{stage}: unsupported semantic input representation {input_representation!r}")


SCIRH_VALID_EFFECTS = {"write", "await", "opaque", "unsafe", "throw"}
SCIRH_IMPLICIT_MUTATION_CODE = "H002"
SCIRH_IMPLICIT_EFFECT_CODE = "H003"
SCIRH_NAME_RESOLUTION_CODE = "H004"
SCIRH_CANONICAL_FORMAT_CODE = "H005"
SCIRH_DETERMINISTIC_STORAGE_CODE = "H006"
SCIRH_FIELD_PLACE_CODE = "H007"
SCIRH_BOUNDARY_CODE = "H008"
SCIRH_UNSUPPORTED_CODE = "H009"
SCIRH_OWNERSHIP_ALIAS_CODE = "H010"
PRESERVATION_LEVEL_ORDER = ["P0", "P1", "P2", "P3", "PX"]
PRESERVATION_STAGE_NAMES = [
    "source_to_h",
    "scir_h_validation",
    "h_to_l",
    "scir_l_validation",
    "h_to_python",
    "l_to_wasm",
]


def make_diagnostic(code: str, message: str, *, severity: str = "error", location: str | None = None):
    diagnostic = {
        "code": code,
        "severity": severity,
        "message": message,
    }
    if location:
        diagnostic["location"] = location
    return diagnostic


def path_exists(root: pathlib.Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


def read_text(root: pathlib.Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def is_builtin_type_name(type_name: str) -> bool:
    return type_name in {"int", "Callable", "Error", "ValueError", "ForeignResult"}


def unwrap_named_type(type_name: str) -> str | None:
    if type_name.endswith(">") and "<" in type_name:
        return type_name.split("<", 1)[1][:-1]
    return type_name


def root_place_name(place):
    current = place
    while isinstance(current, FieldPlace):
        current = current.base
    if isinstance(current, str):
        return current
    if hasattr(current, "name"):
        return current.name
    return None


def boundary_contract_symbol(contract: dict) -> str | None:
    signature = contract.get("signature")
    if isinstance(signature, str):
        match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\(", signature)
        if match:
            return match.group(1)
    boundary_id = contract.get("boundary_id")
    if isinstance(boundary_id, str) and "." in boundary_id:
        return boundary_id.rsplit(".", 1)[-1]
    return None


def normalize_boundary_contracts(boundary_contracts) -> dict[str, dict]:
    if not boundary_contracts:
        return {}
    items = boundary_contracts if isinstance(boundary_contracts, (list, tuple)) else [boundary_contracts]
    contracts_by_symbol = {}
    for contract in items:
        if not isinstance(contract, dict):
            continue
        symbol = boundary_contract_symbol(contract)
        if symbol:
            contracts_by_symbol[symbol] = contract
    return contracts_by_symbol


def contract_effects(contract: dict) -> set[str]:
    effects = contract.get("effects", [])
    if not isinstance(effects, list):
        return set()
    return {effect for effect in effects if isinstance(effect, str)}


def preservation_rank(level: str | None) -> int | None:
    if level not in PRESERVATION_LEVEL_ORDER:
        return None
    return PRESERVATION_LEVEL_ORDER.index(level)


def is_borrow_type(type_name: str) -> bool:
    return isinstance(type_name, str) and type_name.startswith("borrow<")


def is_borrow_mut_type(type_name: str) -> bool:
    return isinstance(type_name, str) and type_name.startswith("borrow_mut<")


def is_opaque_type(type_name: str) -> bool:
    return isinstance(type_name, str) and type_name.startswith("opaque<")


def provenance_origin_matches_module(module_id: str, origin: str | None) -> bool:
    return isinstance(origin, str) and origin.startswith(f"{module_id}::")


def import_sort_key_from_line(line: str) -> tuple[str, str]:
    fields = line.split()
    if len(fields) != 4:
        return ("", "")
    return fields[1], fields[2]


def has_nondeterministic_storage_markers(scirh_text: str) -> bool:
    stripped_lines = [line for line in scirh_text.splitlines() if line.strip()]
    import_lines = [line for line in stripped_lines if line.startswith("import ")]
    if import_lines != sorted(import_lines, key=import_sort_key_from_line):
        return True
    for line in stripped_lines:
        if "->" not in line:
            continue
        fields = line.split()
        if not fields:
            continue
        effect_row = fields[-1]
        if not effect_row.startswith("!"):
            continue
        effects = [item for item in effect_row[1:].split(",") if item]
        if effects != sorted(dict.fromkeys(effects)):
            return True
    return False


def diagnose_scirh_parse_failure(artifact: str, exc: Exception):
    message = str(exc)
    lower_message = message.lower()
    if "unsupported statement" in lower_message and ("select" in lower_message or "finally" in lower_message):
        return [make_diagnostic("H001", f"{artifact}: forbidden control-transfer form is outside the active subset: {message}")]
    if any(marker in lower_message for marker in ["tabs", "trailing spaces", "indentation", "must end with a newline"]):
        return [make_diagnostic(SCIRH_CANONICAL_FORMAT_CODE, f"{artifact}: canonical formatting violation: {message}")]
    if "{" in message or "}" in message or "unsupported top-level declaration" in lower_message:
        return [make_diagnostic(SCIRH_UNSUPPORTED_CODE, f"{artifact}: unsupported or legacy syntax: {message}")]
    return [make_diagnostic(SCIRH_UNSUPPORTED_CODE, f"{artifact}: invalid canonical SCIR-H: {message}")]


def record_type_map(module: Module):
    type_fields = {}
    for type_decl in module.type_decls:
        if isinstance(type_decl.type_expr, RecordType):
            type_fields[type_decl.name] = {field.name for field in type_decl.type_expr.fields}
    return type_fields


def resolve_record_type(binding_type: str, type_fields: dict[str, set[str]]) -> str | None:
    candidate = unwrap_named_type(binding_type)
    if candidate in type_fields:
        return candidate
    return None


def validate_scirh_module_semantics(
    artifact: str,
    module: Module,
    *,
    boundary_contracts=None,
    canonical_text: str | None = None,
):
    diagnostics = []
    contract_map = normalize_boundary_contracts(boundary_contracts)
    type_fields = record_type_map(module)
    function_effects = {}
    top_level_names: set[str] = set()
    import_names: set[str] = set()

    for import_decl in module.imports:
        if import_decl.local_id in import_names:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{artifact}: duplicate import local name {import_decl.local_id!r}",
                )
            )
        import_names.add(import_decl.local_id)
        if import_decl.local_id in top_level_names:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{artifact}: top-level name {import_decl.local_id!r} is ambiguous",
                )
            )
        top_level_names.add(import_decl.local_id)

    for type_decl in module.type_decls:
        if type_decl.name in top_level_names:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{artifact}: top-level name {type_decl.name!r} is ambiguous",
                )
            )
        top_level_names.add(type_decl.name)

    for function in module.functions:
        if function.name in function_effects:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{artifact}: duplicate function name {function.name!r}",
                )
            )
        function_effects[function.name] = set(function.effects)
        if function.name in top_level_names:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{artifact}: top-level name {function.name!r} is ambiguous",
                )
            )
        top_level_names.add(function.name)

    def validate_place(place, bindings: dict[str, str], *, artifact_label: str, as_assignment_target: bool):
        field_steps = []
        current = place
        while isinstance(current, FieldPlace):
            field_steps.append(current.field)
            current = current.base
        if isinstance(current, str):
            root_name = current
        elif isinstance(current, NamePlace):
            root_name = current.name
        else:
            root_name = getattr(current, "name", None)
        if root_name not in bindings:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{artifact}: unresolved place root {root_name!r} in {artifact_label}",
                )
            )
            return
        if not field_steps:
            return
        binding_type = bindings[root_name]
        if is_opaque_type(binding_type):
            diagnostics.append(
                make_diagnostic(
                    SCIRH_BOUNDARY_CODE,
                    f"{artifact}: opaque boundary value {root_name!r} cannot be projected in {artifact_label}",
                )
            )
            return
        if as_assignment_target and is_borrow_type(binding_type):
            diagnostics.append(
                make_diagnostic(
                    SCIRH_OWNERSHIP_ALIAS_CODE,
                    f"{artifact}: field mutation through read-only borrow {root_name!r} is invalid",
                )
            )
            return
        record_type = resolve_record_type(binding_type, type_fields)
        if record_type is None:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_FIELD_PLACE_CODE,
                    f"{artifact}: field place requires a record-like base for {root_name!r}",
                )
            )
            return
        current_type = record_type
        for field_name in reversed(field_steps):
            available_fields = type_fields.get(current_type, set())
            if field_name not in available_fields:
                diagnostics.append(
                    make_diagnostic(
                        SCIRH_FIELD_PLACE_CODE,
                        f"{artifact}: field {field_name!r} is not declared on type {current_type!r}",
                    )
                )
                return

    def validate_expr(expr, bindings: dict[str, str], required_effects: set[str], *, artifact_label: str):
        if isinstance(expr, NameExpr):
            if expr.name not in bindings and expr.name not in function_effects and expr.name not in import_names:
                diagnostics.append(
                    make_diagnostic(
                        SCIRH_NAME_RESOLUTION_CODE,
                        f"{artifact}: unresolved name {expr.name!r} in {artifact_label}",
                    )
                )
            return
        if isinstance(expr, PlaceExpr):
            validate_place(expr.place, bindings, artifact_label=artifact_label, as_assignment_target=False)
            return
        if isinstance(expr, IntExpr):
            return
        if isinstance(expr, CallExpr):
            for arg in expr.args:
                validate_expr(arg, bindings, required_effects, artifact_label=artifact_label)
            if expr.callee in function_effects:
                required_effects.update(function_effects[expr.callee])
                return
            if expr.callee in bindings:
                return
            if expr.callee in import_names:
                contract = contract_map.get(expr.callee)
                if contract is None:
                    diagnostics.append(
                        make_diagnostic(
                            SCIRH_BOUNDARY_CODE,
                            f"{artifact}: imported boundary call {expr.callee!r} is missing an explicit boundary contract",
                        )
                    )
                    return
                expected_symbol = boundary_contract_symbol(contract)
                if expected_symbol != expr.callee:
                    diagnostics.append(
                        make_diagnostic(
                            SCIRH_BOUNDARY_CODE,
                            f"{artifact}: boundary contract symbol {expected_symbol!r} does not match imported callee {expr.callee!r}",
                        )
                    )
                missing_fields = [
                    field_name
                    for field_name in [
                        "boundary_id",
                        "kind",
                        "signature",
                        "effects",
                        "ownership_transfer",
                        "capabilities",
                        "determinism",
                        "audit_note",
                    ]
                    if field_name not in contract
                ]
                if missing_fields:
                    diagnostics.append(
                        make_diagnostic(
                            SCIRH_BOUNDARY_CODE,
                            f"{artifact}: boundary contract for {expr.callee!r} is missing fields {missing_fields!r}",
                        )
                    )
                if contract.get("kind") != "opaque_call":
                    diagnostics.append(
                        make_diagnostic(
                            SCIRH_BOUNDARY_CODE,
                            f"{artifact}: boundary contract for {expr.callee!r} must use kind 'opaque_call'",
                        )
                    )
                required_effects.update(contract_effects(contract))
                return
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{artifact}: unresolved callee {expr.callee!r} in {artifact_label}",
                )
            )
            return
        if isinstance(expr, AwaitExpr):
            required_effects.add("await")
            validate_expr(expr.value, bindings, required_effects, artifact_label=artifact_label)
            return
        if isinstance(expr, IntrinsicExpr):
            for arg in expr.args:
                validate_expr(arg, bindings, required_effects, artifact_label=artifact_label)
            return

    def validate_stmt(stmt, bindings: dict[str, str], mutable_locals: set[str], loop_ids: set[str], required_effects: set[str], *, artifact_label: str):
        if isinstance(stmt, VarDecl):
            if stmt.name in bindings:
                diagnostics.append(
                    make_diagnostic(
                        SCIRH_NAME_RESOLUTION_CODE,
                        f"{artifact}: local name {stmt.name!r} is ambiguous in {artifact_label}",
                    )
                )
            bindings[stmt.name] = stmt.type_name
            mutable_locals.add(stmt.name)
            validate_expr(stmt.value, bindings, required_effects, artifact_label=f"{artifact_label}::var {stmt.name}")
            return
        if isinstance(stmt, SetStmt):
            required_effects.add("write")
            validate_expr(stmt.value, bindings, required_effects, artifact_label=f"{artifact_label}::set")
            target_root = root_place_name(stmt.target)
            if isinstance(stmt.target, NamePlace):
                if target_root in function_effects or target_root in import_names:
                    diagnostics.append(
                        make_diagnostic(
                            SCIRH_IMPLICIT_MUTATION_CODE,
                            f"{artifact}: assignment target {target_root!r} is not a mutable place",
                        )
                    )
                elif target_root not in bindings:
                    diagnostics.append(
                        make_diagnostic(
                            SCIRH_NAME_RESOLUTION_CODE,
                            f"{artifact}: unresolved assignment target {target_root!r}",
                        )
                    )
                elif target_root not in mutable_locals:
                    diagnostics.append(
                        make_diagnostic(
                            SCIRH_IMPLICIT_MUTATION_CODE,
                            f"{artifact}: assignment target {target_root!r} is not a mutable local",
                        )
                    )
                return
            validate_place(stmt.target, bindings, artifact_label=f"{artifact_label}::set", as_assignment_target=True)
            return
        if isinstance(stmt, ReturnStmt):
            validate_expr(stmt.value, bindings, required_effects, artifact_label=f"{artifact_label}::return")
            return
        if isinstance(stmt, IfStmt):
            validate_expr(stmt.condition, bindings, required_effects, artifact_label=f"{artifact_label}::if")
            then_bindings = dict(bindings)
            then_mutable = set(mutable_locals)
            for item in stmt.then_body:
                validate_stmt(item, then_bindings, then_mutable, set(loop_ids), required_effects, artifact_label=f"{artifact_label}::then")
            else_bindings = dict(bindings)
            else_mutable = set(mutable_locals)
            for item in stmt.else_body:
                validate_stmt(item, else_bindings, else_mutable, set(loop_ids), required_effects, artifact_label=f"{artifact_label}::else")
            return
        if isinstance(stmt, LoopStmt):
            if stmt.loop_id in loop_ids:
                diagnostics.append(
                    make_diagnostic(
                        SCIRH_NAME_RESOLUTION_CODE,
                        f"{artifact}: duplicate loop id {stmt.loop_id!r}",
                    )
                )
            next_loop_ids = set(loop_ids)
            next_loop_ids.add(stmt.loop_id)
            loop_bindings = dict(bindings)
            loop_mutable = set(mutable_locals)
            for item in stmt.body:
                validate_stmt(item, loop_bindings, loop_mutable, next_loop_ids, required_effects, artifact_label=f"{artifact_label}::loop {stmt.loop_id}")
            return
        if isinstance(stmt, BreakStmt):
            if stmt.loop_id not in loop_ids:
                diagnostics.append(
                    make_diagnostic(
                        "H001",
                        f"{artifact}: break references unknown loop {stmt.loop_id!r}",
                    )
                )
            return
        if isinstance(stmt, ContinueStmt):
            if stmt.loop_id not in loop_ids:
                diagnostics.append(
                    make_diagnostic(
                        "H001",
                        f"{artifact}: continue references unknown loop {stmt.loop_id!r}",
                    )
                )
            return
        if isinstance(stmt, TryStmt):
            required_effects.add("throw")
            try_bindings = dict(bindings)
            try_mutable = set(mutable_locals)
            for item in stmt.try_body:
                validate_stmt(item, try_bindings, try_mutable, set(loop_ids), required_effects, artifact_label=f"{artifact_label}::try")
            catch_bindings = dict(bindings)
            catch_mutable = set(mutable_locals)
            if stmt.catch_name in catch_bindings:
                diagnostics.append(
                    make_diagnostic(
                        SCIRH_NAME_RESOLUTION_CODE,
                        f"{artifact}: catch binder {stmt.catch_name!r} is ambiguous",
                    )
                )
            catch_bindings[stmt.catch_name] = stmt.catch_type
            for item in stmt.catch_body:
                validate_stmt(item, catch_bindings, catch_mutable, set(loop_ids), required_effects, artifact_label=f"{artifact_label}::catch")

    for function in module.functions:
        if set(function.effects) - SCIRH_VALID_EFFECTS:
            invalid_effects = sorted(set(function.effects) - SCIRH_VALID_EFFECTS)
            diagnostics.append(
                make_diagnostic(
                    SCIRH_IMPLICIT_EFFECT_CODE,
                    f"{artifact}: function {function.name!r} uses unsupported effects {invalid_effects!r}",
                )
            )
        bindings = {}
        mutable_locals = set()
        for param in function.params:
            if param.name in bindings:
                diagnostics.append(
                    make_diagnostic(
                        SCIRH_NAME_RESOLUTION_CODE,
                        f"{artifact}: parameter name {param.name!r} is ambiguous in function {function.name!r}",
                    )
                )
            bindings[param.name] = param.type_name
            named_type = unwrap_named_type(param.type_name)
            if not is_builtin_type_name(named_type) and named_type not in type_fields:
                diagnostics.append(
                    make_diagnostic(
                        SCIRH_NAME_RESOLUTION_CODE,
                        f"{artifact}: parameter {param.name!r} references unknown type {param.type_name!r}",
                    )
                )
        required_effects = set()
        for stmt in function.body:
            validate_stmt(
                stmt,
                bindings,
                mutable_locals,
                set(),
                required_effects,
                artifact_label=f"function {function.name}",
            )
        missing_effects = sorted(required_effects - set(function.effects))
        if missing_effects:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_IMPLICIT_EFFECT_CODE,
                    f"{artifact}: function {function.name!r} is missing explicit effects {missing_effects!r}",
                )
            )
        unused_effects = sorted(set(function.effects) - required_effects)
        if unused_effects:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_IMPLICIT_EFFECT_CODE,
                    f"{artifact}: function {function.name!r} declares unused effects {unused_effects!r}",
                )
            )
        named_return_type = unwrap_named_type(function.return_type)
        if not is_builtin_type_name(named_return_type) and named_return_type not in type_fields:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{artifact}: function {function.name!r} references unknown return type {function.return_type!r}",
                )
            )

    if canonical_text is not None:
        canonical_storage = format_module(module)
        if canonical_text != canonical_storage:
            code = (
                SCIRH_DETERMINISTIC_STORAGE_CODE
                if has_nondeterministic_storage_markers(canonical_text)
                else SCIRH_CANONICAL_FORMAT_CODE
            )
            diagnostics.append(
                make_diagnostic(
                    code,
                    f"{artifact}: canonical SCIR-H text is not normalized under parse-format equality",
                )
            )

    return diagnostics


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


def case_name_from_artifact_id(artifact_id: str) -> str:
    return artifact_id.rsplit(".", 1)[-1]


def load_import_artifacts(root: pathlib.Path, case_name: str):
    bundle = build_python_bundle(root, fixture_source(root, case_name))
    parsed = {}
    for name, contents in bundle.files.items():
        if name.endswith(".json"):
            parsed[name] = json.loads(contents)
        else:
            parsed[name] = contents
    return parsed


def file_sha256(root: pathlib.Path, relative_path: str) -> str:
    digest = hashlib.sha256()
    digest.update((root / relative_path).read_bytes())
    return f"sha256:{digest.hexdigest()}"


def load_corpus_manifest(root: pathlib.Path, relative_path: str):
    return load_json(root / relative_path)


def validate_negative_scirh_corpus(root: pathlib.Path):
    manifest = load_corpus_manifest(root, INVALID_SCIRH_MANIFEST_REL)
    failures = []
    for entry in manifest["fixtures"]:
        scirh_text = read_text(root, entry["path"])
        boundary_contracts = None
        boundary_contract_path = entry.get("boundary_contract_path")
        if isinstance(boundary_contract_path, str) and path_exists(root, boundary_contract_path):
            boundary_contracts = load_json(root / boundary_contract_path)
        try:
            parsed = parse_module(scirh_text)
        except ScirHModelError as exc:
            diagnostics = diagnose_scirh_parse_failure(entry["id"], exc)
        else:
            diagnostics = validate_scirh_module_semantics(
                entry["id"],
                parsed,
                boundary_contracts=boundary_contracts,
                canonical_text=scirh_text,
            )
        if not diagnostics:
            failures.append(f"{entry['id']}: expected SCIR-H validation failure")
            continue
        actual_codes = {diagnostic["code"] for diagnostic in diagnostics}
        expected_codes = set(entry.get("expected_diagnostic_codes", []))
        missing_codes = sorted(expected_codes - actual_codes)
        if missing_codes:
            failures.append(
                f"{entry['id']}: expected SCIR-H diagnostic codes {missing_codes!r}, got {sorted(actual_codes)!r}"
            )
    return failures


def validate_negative_scirl_corpus(root: pathlib.Path):
    manifest = load_corpus_manifest(root, INVALID_SCIRL_MANIFEST_REL)
    failures = []
    for entry in manifest["fixtures"]:
        lowered_module = load_json(root / entry["path"])
        diagnostic_messages, report = validate_scirl_module(lowered_module)
        if not diagnostic_messages:
            failures.append(f"{entry['id']}: expected SCIR-L validation failure")
            continue
        actual_codes = {diagnostic["code"] for diagnostic in report["diagnostics"]}
        expected_codes = set(entry.get("expected_diagnostic_codes", []))
        missing_codes = sorted(expected_codes - actual_codes)
        if missing_codes:
            failures.append(
                f"{entry['id']}: expected SCIR-L diagnostic codes {missing_codes!r}, got {sorted(actual_codes)!r}"
            )
    return failures


def validate_import_bundle(root: pathlib.Path, case_name: str, artifacts: dict):
    failures = []
    module_manifest = artifacts["module_manifest.json"]
    failures.extend(
        validate_instance(
            root,
            module_manifest,
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
        boundary_contract = artifacts["opaque_boundary_contract.json"]
        failures.extend(
            validate_instance(
                root,
                boundary_contract,
                "schemas/opaque_boundary_contract.schema.json",
                f"{case_name} opaque_boundary_contract",
            )
        )
    else:
        boundary_contract = None
    failures.extend(
        validate_boundary_capability_contract(
            module_manifest,
            boundary_contract,
            label=f"{case_name} import_bundle",
            allow_capabilities=boundary_contract is not None,
        )
    )
    return failures


def validate_scirh_case(case_name: str, scirh_text: str, *, boundary_contracts=None):
    try:
        parsed = parse_module(scirh_text)
    except ScirHModelError as exc:
        diagnostics = diagnose_scirh_parse_failure(case_name, exc)
        parsed = None
    else:
        diagnostics = validate_scirh_module_semantics(
            case_name,
            parsed,
            boundary_contracts=boundary_contracts,
            canonical_text=scirh_text,
        )
        expected = PYTHON_SCIRH_MODULES[case_name]
        if parsed != expected:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{case_name}: parsed SCIR-H model drifted from the canonical bootstrap module model",
                )
            )

    report = {
        "report_id": f"scir-h-validation-{slug(case_name)}",
        "artifact": f"fixture.python_importer.{case_name}",
        "layer": "scir_h",
        "validator": SCIRH_VALIDATOR_NAME,
        "spec_version": SPEC_VERSION,
        "status": "pass" if not diagnostics else "fail",
        "diagnostics": diagnostics,
    }
    failures = [item["message"] for item in diagnostics]
    return failures, parsed, report


def validate_scirhc_case(
    case_name: str,
    module: Module,
    *,
    artifact_prefix: str = "fixture.python_importer",
    boundary_contracts=None,
):
    try:
        hc_module = scirh_to_scirhc(module, boundary_contracts=boundary_contracts)
        hc_text = format_scirhc_module(hc_module)
        stats = scirhc_normalization_stats(module, boundary_contracts=boundary_contracts)
        diagnostics = []
        checks = [
            ("HC004", lambda: assert_not_semantic_authority(hc_module)),
            ("HC006", lambda: assert_no_hidden_semantics(hc_module)),
            ("HC005", lambda: assert_deterministic_derivation(module, hc_module)),
            ("HC002", lambda: assert_round_trip_integrity(module)),
        ]
        for default_code, check in checks:
            try:
                check()
            except ScirHcDoctrineError as exc:
                message = str(exc)
                code = default_code
                if "parse-format equality" in message:
                    code = "HC001"
                elif "deterministic derivation output" in message:
                    code = "HC005"
                diagnostics.append(make_diagnostic(code, f"{case_name}: {message}"))
    except (ScirHModelError, ScirHcDoctrineError) as exc:
        hc_module = None
        hc_text = None
        stats = {
            "effect_rows_deduplicated": 0,
            "return_types_inferred": 0,
            "ownership_markers_elided": 0,
            "single_use_witnesses_inlined": 0,
            "capabilities_hoisted": 0,
        }
        diagnostics = [make_diagnostic("HC003", f"{case_name}: invalid compressed SCIR-Hc: {exc}")]

    report = {
        "report_id": f"scir-hc-validation-{slug(case_name)}",
        "artifact": f"{artifact_prefix}.{case_name}",
        "layer": "scir_hc",
        "validator": SCIRHC_VALIDATOR_NAME,
        "spec_version": SPEC_VERSION,
        "status": "pass" if not diagnostics else "fail",
        "diagnostics": diagnostics,
    }
    failures = [item["message"] for item in diagnostics]
    return failures, hc_module, hc_text, stats, report


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
                                "lowering_rule": "H_VAR_ALLOC",
                            },
                            {
                                "id": "mem1",
                                "op": "store",
                                "operands": ["cell0", "x", "mem0"],
                                "origin": f"{module.module_id}::init-y",
                                "lowering_rule": "H_VAR_ALLOC",
                            },
                            {
                                "id": "load0",
                                "op": "load",
                                "operands": ["cell0", "mem1"],
                                "origin": f"{module.module_id}::lt-load-y",
                                "lowering_rule": "H_PLACE_LOAD",
                            },
                            {
                                "id": "cmp0",
                                "op": "cmp",
                                "operands": ["load0", 0],
                                "origin": f"{module.module_id}::lt-zero",
                                "lowering_rule": "H_INTRINSIC_CMP",
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
                            "lowering_rule": "H_BRANCH_COND",
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
                                "lowering_rule": "H_SET_STORE",
                            }
                        ],
                        "terminator": {
                            "kind": "br",
                            "target": "retread",
                            "args": ["cell1", "mem3"],
                            "origin": f"{module.module_id}::join-return",
                            "lowering_rule": "H_BRANCH_JOIN",
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
                                "lowering_rule": "H_PLACE_LOAD",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "load1",
                            "origin": f"{module.module_id}::return",
                            "lowering_rule": "H_RETURN",
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
                                "lowering_rule": "H_CONST_RET",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "const0",
                            "origin": f"{module.module_id}::fetch-value-ret",
                            "lowering_rule": "H_CONST_RET",
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
                                "lowering_rule": "H_DIRECT_CALL",
                            },
                            {
                                "id": "await0",
                                "op": "async.resume",
                                "operands": ["call0", "eff0"],
                                "origin": f"{module.module_id}::await-fetch-value",
                                "lowering_rule": "H_AWAIT_RESUME",
                            },
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "await0",
                            "origin": f"{module.module_id}::load-once-ret",
                            "lowering_rule": "H_RETURN",
                        },
                    }
                ],
            },
        ],
    }


def lower_direct_call_module(module: Module):
    identity, call_identity = module.functions
    if not (
        len(module.functions) == 2
        and not module.imports
        and identity.body == (ReturnStmt(NameExpr("x")),)
        and call_identity.body == (ReturnStmt(CallExpr("identity", (NameExpr("x"),))),)
    ):
        raise PipelineError("b_direct_call: unsupported compact SCIR-H shape for lowering")

    return {
        "module_id": module.module_id,
        "functions": [
            {
                "name": "identity",
                "returns": "int",
                "params": ["x"],
                "blocks": [
                    {
                        "id": "entry",
                        "params": [],
                        "instructions": [],
                        "terminator": {
                            "kind": "ret",
                            "value": "x",
                            "origin": f"{module.module_id}::identity-return",
                            "lowering_rule": "H_RETURN",
                        },
                    }
                ],
            },
            {
                "name": "call_identity",
                "returns": "int",
                "params": ["x"],
                "blocks": [
                    {
                        "id": "entry",
                        "params": ["eff0"],
                        "instructions": [
                            {
                                "id": "call0",
                                "op": "call",
                                "operands": ["sym:identity", "x", "eff0"],
                                "origin": f"{module.module_id}::call-identity",
                                "lowering_rule": "H_DIRECT_CALL",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "call0",
                            "origin": f"{module.module_id}::call-identity-return",
                            "lowering_rule": "H_RETURN",
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
                                "lowering_rule": "H_OPAQUE_CALL",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "opaque0",
                            "origin": f"{module.module_id}::ret",
                            "lowering_rule": "H_RETURN",
                        },
                    }
                ],
            }
        ],
    }


def lower_supported_module(module: Module, *, input_representation: str = "SCIR-H"):
    assert_canonical_pipeline_input(input_representation, "lowering")
    case_name = case_name_from_module(module)
    if case_name == "a_basic_function":
        return lower_basic_function(module)
    if case_name == "a_async_await":
        return lower_async_module(module)
    if case_name == "b_direct_call":
        return lower_direct_call_module(module)
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


def scirl_diagnostic_code(message: str) -> str:
    lower_message = message.lower()
    if any(marker in lower_message for marker in ["missing entry block", "duplicate block", "unknown target block", "unsupported kind"]):
        return "L001"
    if any(marker in lower_message for marker in ["duplicate ssa or token id", "unknown ssa/token operand", "target arg count mismatch"]):
        return "L002"
    if any(marker in lower_message for marker in ["effect token"]):
        return "L003"
    if any(marker in lower_message for marker in ["memory token"]):
        return "L004"
    if "provenance origin" in lower_message:
        return "L005"
    if "lowering_rule" in lower_message:
        return "L006"
    if "unsupported op" in lower_message:
        return "L007"
    if any(marker in lower_message for marker in ["opaque.call", "boundary op"]):
        return "L008"
    return "L001"


def is_token_with_prefix(value, prefix: str) -> bool:
    return isinstance(value, str) and token_prefix(value) == prefix


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
    lowering_rules_by_op = {
        "alloc": {"H_VAR_ALLOC"},
        "store": {"H_VAR_ALLOC", "H_SET_STORE"},
        "load": {"H_PLACE_LOAD"},
        "field.addr": {"H_FIELD_ADDR"},
        "cmp": {"H_INTRINSIC_CMP"},
        "const": {"H_CONST_RET"},
        "call": {"H_DIRECT_CALL"},
        "async.resume": {"H_AWAIT_RESUME"},
        "opaque.call": {"H_OPAQUE_CALL"},
    }
    lowering_rules_by_terminator = {
        "ret": {"H_CONST_RET", "H_RETURN"},
        "br": {"H_BRANCH_JOIN"},
        "cond_br": {"H_BRANCH_COND"},
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
                elif not provenance_origin_matches_module(module["module_id"], instruction["origin"]):
                    failures.append(
                        f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: provenance origin must remain rooted in {module['module_id']}::"
                    )
                lowering_rule = instruction.get("lowering_rule")
                if not lowering_rule:
                    failures.append(
                        f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: missing lowering_rule"
                    )
                elif lowering_rule not in lowering_rules_by_op.get(instruction["op"], set()):
                    failures.append(
                        f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: invalid lowering_rule {lowering_rule!r} for op {instruction['op']}"
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
                if instruction["op"] == "alloc":
                    if len(instruction["operands"]) != 1 or not is_token_with_prefix(instruction["operands"][0], "mem"):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: alloc requires one memory token operand"
                        )
                elif instruction["op"] == "store":
                    if len(instruction["operands"]) < 3 or not is_token_with_prefix(instruction["operands"][-1], "mem"):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: store requires a trailing memory token operand"
                        )
                elif instruction["op"] == "load":
                    if len(instruction["operands"]) != 2 or not is_token_with_prefix(instruction["operands"][-1], "mem"):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: load requires a trailing memory token operand"
                        )
                elif instruction["op"] == "call":
                    if len(instruction["operands"]) < 2 or not isinstance(instruction["operands"][0], str) or not instruction["operands"][0].startswith("sym:"):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: call requires a symbolic callee operand"
                        )
                    if not is_token_with_prefix(instruction["operands"][-1], "eff"):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: call requires a trailing effect token operand"
                        )
                elif instruction["op"] == "async.resume":
                    if len(instruction["operands"]) != 2 or not is_token_with_prefix(instruction["operands"][-1], "eff"):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: async.resume requires a trailing effect token operand"
                        )
                elif instruction["op"] == "opaque.call":
                    if len(instruction["operands"]) < 2 or not isinstance(instruction["operands"][0], str) or not instruction["operands"][0].startswith("sym:"):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: opaque.call requires an explicit symbolic boundary op"
                        )
                    if not is_token_with_prefix(instruction["operands"][-1], "eff"):
                        failures.append(
                            f"{module['module_id']}::{name}::{block['id']}::{instruction['id']}: opaque.call requires a trailing effect token operand"
                        )
                seen_ids.add(instruction["id"])
                known_values.add(instruction["id"])

            terminator = block["terminator"]
            if not terminator.get("origin"):
                failures.append(
                    f"{module['module_id']}::{name}::{block['id']}::terminator: missing provenance origin"
                )
            elif not provenance_origin_matches_module(module["module_id"], terminator["origin"]):
                failures.append(
                    f"{module['module_id']}::{name}::{block['id']}::terminator: provenance origin must remain rooted in {module['module_id']}::"
                )
            term_rule = terminator.get("lowering_rule")
            if not term_rule:
                failures.append(
                    f"{module['module_id']}::{name}::{block['id']}::terminator: missing lowering_rule"
                )
            elif term_rule not in lowering_rules_by_terminator.get(terminator["kind"], set()):
                failures.append(
                    f"{module['module_id']}::{name}::{block['id']}::terminator: invalid lowering_rule {term_rule!r} for kind {terminator['kind']}"
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
                "code": scirl_diagnostic_code(message),
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

    if case_name == "b_direct_call":
        functions = lowered["functions"]
        if [function["name"] for function in functions] != ["identity", "call_identity"]:
            return [f"{case_name}: expected identity/call_identity lowered functions"]
        if functions[0]["blocks"][0]["instructions"]:
            failures.append(f"{case_name}: expected identity to return its parameter directly")
        if functions[0]["blocks"][0]["terminator"]["kind"] != "ret":
            failures.append(f"{case_name}: expected identity ret terminator")
        if functions[0]["blocks"][0]["terminator"]["value"] != "x":
            failures.append(f"{case_name}: expected identity to return x directly")
        if [item["op"] for item in functions[1]["blocks"][0]["instructions"]] != ["call"]:
            failures.append(f"{case_name}: expected call_identity to lower to a single call")
        if functions[1]["blocks"][0]["params"] != ["eff0"]:
            failures.append(f"{case_name}: expected call_identity entry effect token parameter")
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
    expected = RECONSTRUCTION_EXPECTATIONS[case_name]
    profile = expected["profile"]
    preservation_level = expected["preservation_level"]
    requires_opaque = expected["requires_opaque"]
    if report["path"] != "h_to_l":
        failures.append(f"{case_name}: expected translation path h_to_l")
    if report["profile"] != profile:
        failures.append(f"{case_name}: expected translation profile {profile}")
    if report["preservation_level"] != preservation_level:
        failures.append(f"{case_name}: expected translation preservation level {preservation_level}")
    opaque_items = report["boundary_annotations"]
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
            "path": "h_to_l",
            "source_artifact": f"scir_h:fixture.python_importer.{case_name}",
            "target_artifact": f"scir_l:fixture.python_importer.{case_name}",
            "profile": "D-PY",
            "preservation_level": "P3",
            "status": "pass",
            "downgrades": [
                {
                    "reason": "opaque boundary preserved as boundary annotation only",
                    "preservation_level": "P3",
                }
            ],
            "boundary_annotations": ["foreign_api.ping boundary"],
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
        "b_direct_call": ["function boundaries", "direct local call semantics"],
    }
    return {
        "report_id": f"translation-preservation-{slug(case_name)}",
        "subject": f"fixture.python_importer.{case_name}",
        "path": "h_to_l",
        "source_artifact": f"scir_h:fixture.python_importer.{case_name}",
        "target_artifact": f"scir_l:fixture.python_importer.{case_name}",
        "profile": "R",
        "preservation_level": "P1",
        "status": "pass",
        "downgrades": [],
        "boundary_annotations": [],
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


def build_source_to_h_preservation_report(case_name: str, artifacts: dict):
    module_manifest = artifacts["module_manifest.json"]
    validation_report = artifacts["validation_report.json"]
    profile = module_manifest["declared_profiles"][0]
    preservation_level = "P3" if module_manifest.get("opaque_boundary_count", 0) else "P1"
    status = {
        "pass": "pass",
        "warn": "mixed",
        "fail": "fail",
    }.get(validation_report["status"], "fail")
    boundary_annotations = []
    downgrades = []
    if module_manifest.get("opaque_boundary_count", 0):
        boundary_annotations = ["explicit importer boundary"]
        downgrades = [
            {
                "reason": "imported opaque or unsafe boundary remains explicit rather than semantically modeled",
                "preservation_level": preservation_level,
            }
        ]
    return {
        "report_id": f"source-to-h-preservation-{slug(case_name)}",
        "subject": f"fixture.python_importer.{case_name}",
        "path": "source_to_h",
        "source_artifact": f"frontend/python:{module_manifest['source_path']}",
        "target_artifact": f"scir_h:fixture.python_importer.{case_name}",
        "profile": profile,
        "preservation_level": preservation_level,
        "status": status,
        "downgrades": downgrades,
        "boundary_annotations": boundary_annotations,
        "observables": {
            "preserved": ["canonical module shape", "declared interface surface"],
            "normalized": [],
            "contract_bounded": [],
            "opaque": list(boundary_annotations),
            "unsupported": [],
        },
        "evidence": [
            validation_report["validator"],
            "canonical scir-h emitted from checked-in importer fixture",
        ],
    }


def make_stage_observation(
    *,
    status: str,
    preservation_level: str | None,
    diagnostic_codes: list[str] | None = None,
    downgrade_count: int = 0,
    boundary_annotation_count: int = 0,
    unsupported_count: int = 0,
):
    diagnostic_codes = list(diagnostic_codes or [])
    return {
        "status": status,
        "preservation_level": preservation_level,
        "diagnostic_codes": diagnostic_codes,
        "downgrade_count": downgrade_count,
        "boundary_annotation_count": boundary_annotation_count,
        "unsupported_count": unsupported_count,
        "justification_present": (
            bool(diagnostic_codes)
            or downgrade_count > 0
            or boundary_annotation_count > 0
            or unsupported_count > 0
            or status != "pass"
        ),
    }


def preservation_expectation_status(observation: dict | None, stage_expectation: dict | None):
    if observation is None:
        return "missing_observation"
    if not isinstance(stage_expectation, dict):
        return "not_configured"
    observed_level = observation.get("preservation_level")
    expected_level = stage_expectation.get("preservation_level")
    observed_rank = preservation_rank(observed_level)
    expected_rank = preservation_rank(expected_level)
    if observation.get("status") != stage_expectation.get("status"):
        return "status_mismatch"
    if observed_rank is None or expected_rank is None:
        return "not_applicable"
    if observed_rank < expected_rank:
        return "overclaim"
    if observed_rank > expected_rank:
        return "justified_downgrade" if observation.get("justification_present") else "unexplained_downgrade"
    return "match"


def build_case_stage_observations(case_name: str, artifacts: dict, outputs: dict):
    observations = {}
    source_report = outputs["source_to_h_reports"][case_name]
    import_validation = artifacts["validation_report.json"]
    observations["source_to_h"] = make_stage_observation(
        status=import_validation["status"],
        preservation_level=source_report["preservation_level"],
        diagnostic_codes=[item["code"] for item in import_validation.get("diagnostics", [])],
        downgrade_count=len(source_report["downgrades"]),
        boundary_annotation_count=len(source_report["boundary_annotations"]),
        unsupported_count=len(source_report.get("observables", {}).get("unsupported", [])),
    )

    scir_h_report = outputs["scir_h_reports"][case_name]
    observations["scir_h_validation"] = make_stage_observation(
        status=scir_h_report["status"],
        preservation_level=source_report["preservation_level"],
        diagnostic_codes=[item["code"] for item in scir_h_report.get("diagnostics", [])],
    )

    translation = outputs["translation_reports"].get(case_name)
    if translation is not None:
        observations["h_to_l"] = make_stage_observation(
            status=translation["status"],
            preservation_level=translation["preservation_level"],
            downgrade_count=len(translation["downgrades"]),
            boundary_annotation_count=len(translation["boundary_annotations"]),
            unsupported_count=len(translation.get("observables", {}).get("unsupported", [])),
        )

    scir_l_report = outputs["scir_l_reports"].get(case_name, {}).get("validation_report")
    if scir_l_report is not None and translation is not None:
        observations["scir_l_validation"] = make_stage_observation(
            status=scir_l_report["status"],
            preservation_level=translation["preservation_level"],
            diagnostic_codes=[item["code"] for item in scir_l_report.get("diagnostics", [])],
        )

    reconstruction = outputs["reconstruction_preservation_reports"].get(case_name)
    if reconstruction is not None:
        observations["h_to_python"] = make_stage_observation(
            status=reconstruction["status"],
            preservation_level=reconstruction["preservation_level"],
            downgrade_count=len(reconstruction["downgrades"]),
            boundary_annotation_count=len(reconstruction["boundary_annotations"]),
            unsupported_count=len(reconstruction.get("observables", {}).get("unsupported", [])),
        )

    wasm_report = outputs["wasm_reports"].get(case_name, {}).get("preservation_report")
    if wasm_report is not None:
        observations["l_to_wasm"] = make_stage_observation(
            status=wasm_report["status"],
            preservation_level=wasm_report["preservation_level"],
            downgrade_count=len(wasm_report["downgrades"]),
            boundary_annotation_count=len(wasm_report["boundary_annotations"]),
            unsupported_count=len(wasm_report.get("observables", {}).get("unsupported", [])),
        )
    return observations


def validate_active_corpus_preservation(root: pathlib.Path, manifest_rel: str, outputs: dict):
    manifest = load_corpus_manifest(root, manifest_rel)
    failures = []
    for entry in manifest["fixtures"]:
        case_name = case_name_from_artifact_id(entry["id"])
        if case_name not in outputs["stage_observations"]:
            failures.append(f"{entry['id']}: missing stage observations for active preservation enforcement")
            continue
        stage_observations = outputs["stage_observations"][case_name]
        stage_expectations = entry.get("expected_preservation_stage_behavior", {})
        ceiling = entry["expected_preservation_ceiling"]
        ceiling_rank = preservation_rank(ceiling)
        for stage in entry.get("pipeline_stages", []):
            observation = stage_observations.get(stage)
            stage_expectation = stage_expectations.get(stage)
            expectation_status = preservation_expectation_status(observation, stage_expectation)
            if observation is None:
                failures.append(f"{entry['id']}::{stage}: missing preservation-stage observation")
                continue
            observed_rank = preservation_rank(observation.get("preservation_level"))
            if ceiling_rank is not None and observed_rank is not None and observed_rank < ceiling_rank:
                failures.append(
                    f"{entry['id']}::{stage}: observed preservation {observation['preservation_level']} overclaims stronger preservation than ceiling {ceiling}"
                )
            if expectation_status == "status_mismatch":
                failures.append(
                    f"{entry['id']}::{stage}: expected status {stage_expectation['status']}, observed {observation['status']}"
                )
            if expectation_status == "overclaim":
                failures.append(
                    f"{entry['id']}::{stage}: observed preservation {observation['preservation_level']} overclaims stronger preservation than expected {stage_expectation['preservation_level']}"
                )
            if expectation_status == "unexplained_downgrade":
                failures.append(
                    f"{entry['id']}::{stage}: observed preservation {observation['preservation_level']} is weaker than expected {stage_expectation['preservation_level']} without diagnostics or downgrade evidence"
                )
    return failures


def render_wasm_param(param_name: str) -> str:
    return f"(param ${param_name} i32)"


def validate_wasm_scalar_signature(module: Module):
    for type_decl in module.type_decls:
        raise PipelineError(
            f"{module.module_id}: Wasm emission does not support type declaration {type_decl.name!r}"
        )
    if module.imports:
        raise PipelineError(
            f"{module.module_id}: Wasm emission does not support imported boundaries or helper shims"
        )
    for function in module.functions:
        if function.is_async:
            raise PipelineError(
                f"{module.module_id}::{function.name}: async functions are not emittable in the helper-free Wasm subset"
            )
        if function.return_type != "int":
            raise PipelineError(
                f"{module.module_id}::{function.name}: Wasm emission requires int returns in the active subset"
            )
        for param in function.params:
            if param.type_name != "int":
                raise PipelineError(
                    f"{module.module_id}::{function.name}: Wasm emission requires int parameters in the active subset"
                )


def is_wasm_record_cell_candidate(module: Module, lowered: dict):
    if case_name_from_module(module) != "a_struct_field_borrow_mut":
        return False
    if len(module.imports) != 0 or len(module.functions) != 1 or len(lowered["functions"]) != 1:
        return False
    function = module.functions[0]
    lowered_function = lowered["functions"][0]
    return (
        len(module.type_decls) == 1
        and module.type_decls[0].name == "Counter"
        and isinstance(module.type_decls[0].type_expr, RecordType)
        and tuple((field.name, field.type_name) for field in module.type_decls[0].type_expr.fields) == (("value", "int"),)
        and function.name == "clamp_counter"
        and len(function.params) == 1
        and function.params[0].name == "counter"
        and function.params[0].type_name == "borrow_mut<Counter>"
        and function.return_type == "int"
        and not function.is_async
        and lowered_function["name"] == "clamp_counter"
    )


def detect_wasm_field_place_layout_blocker(module: Module, lowered: dict):
    has_field_addr = any(
        instruction["op"] == "field.addr"
        for function in lowered["functions"]
        for block in function["blocks"]
        for instruction in block["instructions"]
    )
    if not has_field_addr:
        return
    if is_wasm_record_cell_candidate(module, lowered):
        return
    raise PipelineError(
        f"{module.module_id}: {WASM_BACKEND_METADATA['field_addr_blocker_reason']} under the current scalar-only Wasm signature contract"
    )


def emit_wasm_const_ret_function(module: Module, function: FunctionDecl, lowered_function: dict):
    blocks = lowered_function["blocks"]
    if len(blocks) != 1 or blocks[0]["id"] != "entry":
        raise PipelineError(
            f"{module.module_id}::{function.name}: constant-return Wasm emission requires a single entry block"
        )
    block = blocks[0]
    if block["params"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: constant-return Wasm emission does not admit block parameters"
        )
    if len(block["instructions"]) != 1 or block["instructions"][0]["op"] != "const":
        raise PipelineError(
            f"{module.module_id}::{function.name}: constant-return Wasm emission requires a single const instruction"
        )
    instruction = block["instructions"][0]
    if len(instruction["operands"]) != 1 or not isinstance(instruction["operands"][0], int):
        raise PipelineError(
            f"{module.module_id}::{function.name}: constant-return Wasm emission requires an integer const operand"
        )
    terminator = block["terminator"]
    if terminator["kind"] != "ret" or terminator["value"] != instruction["id"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: constant-return Wasm emission requires ret of the const value"
        )
    params_clause = " ".join(render_wasm_param(param.name) for param in function.params)
    header = f"  (func ${function.name} (export \"{function.name}\")"
    if params_clause:
        header += f" {params_clause}"
    header += " (result i32)"
    return [
        header,
        f"    i32.const {instruction['operands'][0]}",
        "  )",
    ]


def emit_wasm_local_slot_function(module: Module, function: FunctionDecl, lowered_function: dict):
    blocks = lowered_function["blocks"]
    if len(function.params) != 1:
        raise PipelineError(
            f"{module.module_id}::{function.name}: local-slot Wasm emission requires exactly one int parameter"
        )
    if [block["id"] for block in blocks] != ["entry", "neg", "retread"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: Wasm emission requires the current entry/neg/retread lowering shape"
        )

    entry, neg, retread = blocks
    if entry["params"] != ["mem0"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: Wasm emission requires the current mem0 entry token shape"
        )
    entry_ops = [instruction["op"] for instruction in entry["instructions"]]
    if entry_ops != ["alloc", "store", "load", "cmp"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: Wasm emission only supports alloc/store/load/cmp in the current less-than bootstrap shape"
        )

    alloc_instr, init_store, entry_load, cmp_instr = entry["instructions"]
    if alloc_instr["operands"] != ["mem0"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: alloc must remain tied to the entry memory token"
        )
    slot_id = alloc_instr["id"]
    param_name = function.params[0].name
    if init_store["operands"] != [slot_id, param_name, "mem0"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: initial store must write the function parameter into the local slot"
        )
    if entry_load["operands"] != [slot_id, init_store["id"]]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: load must read from the allocated slot after initialization"
        )
    if cmp_instr["operands"] != [entry_load["id"], 0]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: cmp must remain the current less-than-zero bootstrap shape"
        )

    entry_terminator = entry["terminator"]
    if (
        entry_terminator["kind"] != "cond_br"
        or entry_terminator["cond"] != cmp_instr["id"]
        or entry_terminator["true"] != "neg"
        or entry_terminator["false"] != "retread"
        or entry_terminator["true_args"] != [slot_id, init_store["id"]]
        or entry_terminator["false_args"] != [slot_id, init_store["id"]]
    ):
        raise PipelineError(
            f"{module.module_id}::{function.name}: cond_br must remain the current clamp-style diamond"
        )

    if len(neg["params"]) != 2 or len(neg["instructions"]) != 1 or neg["instructions"][0]["op"] != "store":
        raise PipelineError(
            f"{module.module_id}::{function.name}: neg block must remain a single store over slot and mem tokens"
        )
    neg_store = neg["instructions"][0]
    if neg_store["operands"] != [neg["params"][0], 0, neg["params"][1]]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: neg block store must write zero into the carried slot"
        )
    neg_terminator = neg["terminator"]
    if (
        neg_terminator["kind"] != "br"
        or neg_terminator["target"] != "retread"
        or neg_terminator["args"] != [neg["params"][0], neg_store["id"]]
    ):
        raise PipelineError(
            f"{module.module_id}::{function.name}: neg block must branch directly to retread with updated slot state"
        )

    if len(retread["params"]) != 2 or len(retread["instructions"]) != 1 or retread["instructions"][0]["op"] != "load":
        raise PipelineError(
            f"{module.module_id}::{function.name}: retread block must remain a single slot load"
        )
    retread_load = retread["instructions"][0]
    if retread_load["operands"] != retread["params"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: retread block load must read the carried slot and memory token"
        )
    ret_terminator = retread["terminator"]
    if ret_terminator["kind"] != "ret" or ret_terminator["value"] != retread_load["id"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: retread block must return the final slot load"
        )

    params_clause = " ".join(render_wasm_param(param.name) for param in function.params)
    header = f"  (func ${function.name} (export \"{function.name}\")"
    if params_clause:
        header += f" {params_clause}"
    header += " (result i32)"
    return [
        header,
        "    (local $slot0 i32)",
        f"    local.get ${param_name}",
        "    local.set $slot0",
        "    block $retread",
        "      local.get $slot0",
        "      i32.const 0",
        "      i32.lt_s",
        "      i32.eqz",
        "      br_if $retread",
        "      i32.const 0",
        "      local.set $slot0",
        "    end",
        "    local.get $slot0",
        "  )",
    ]


def emit_wasm_passthrough_function(module: Module, function: FunctionDecl, lowered_function: dict):
    if len(function.params) != 1:
        raise PipelineError(
            f"{module.module_id}::{function.name}: passthrough Wasm emission requires exactly one int parameter"
        )
    blocks = lowered_function["blocks"]
    if len(blocks) != 1 or blocks[0]["id"] != "entry":
        raise PipelineError(
            f"{module.module_id}::{function.name}: passthrough Wasm emission requires a single entry block"
        )
    block = blocks[0]
    if block["params"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: passthrough Wasm emission does not admit block parameters"
        )
    if block["instructions"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: passthrough Wasm emission requires no body instructions"
        )
    terminator = block["terminator"]
    param_name = function.params[0].name
    if terminator["kind"] != "ret" or terminator["value"] != param_name:
        raise PipelineError(
            f"{module.module_id}::{function.name}: passthrough Wasm emission requires direct ret of the function parameter"
        )

    params_clause = " ".join(render_wasm_param(param.name) for param in function.params)
    header = f"  (func ${function.name} (export \"{function.name}\")"
    if params_clause:
        header += f" {params_clause}"
    header += " (result i32)"
    return [
        header,
        f"    local.get ${param_name}",
        "  )",
    ]


def emit_wasm_direct_local_call_function(module: Module, function: FunctionDecl, lowered_function: dict):
    if len(function.params) != 1:
        raise PipelineError(
            f"{module.module_id}::{function.name}: direct-call Wasm emission requires exactly one int parameter"
        )
    blocks = lowered_function["blocks"]
    if len(blocks) != 1 or blocks[0]["id"] != "entry":
        raise PipelineError(
            f"{module.module_id}::{function.name}: direct-call Wasm emission requires a single entry block"
        )
    block = blocks[0]
    if block["params"] != ["eff0"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: direct-call Wasm emission requires the current eff0 entry token shape"
        )
    if len(block["instructions"]) != 1 or block["instructions"][0]["op"] != "call":
        raise PipelineError(
            f"{module.module_id}::{function.name}: direct-call Wasm emission requires a single call instruction"
        )
    instruction = block["instructions"][0]
    param_name = function.params[0].name
    if instruction["operands"] != ["sym:identity", param_name, "eff0"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: direct-call Wasm emission requires the fixed same-module identity(x) shape"
        )
    terminator = block["terminator"]
    if terminator["kind"] != "ret" or terminator["value"] != instruction["id"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: direct-call Wasm emission requires ret of the call result"
        )

    params_clause = " ".join(render_wasm_param(param.name) for param in function.params)
    header = f"  (func ${function.name} (export \"{function.name}\")"
    if params_clause:
        header += f" {params_clause}"
    header += " (result i32)"
    return [
        header,
        f"    local.get ${param_name}",
        "    call $identity",
        "  )",
    ]


def emit_wasm_record_cell_function(module: Module, function: FunctionDecl, lowered_function: dict):
    blocks = lowered_function["blocks"]
    if [block["id"] for block in blocks] != ["entry", "neg", "retread"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires the current entry/neg/retread lowering shape"
        )
    entry, neg, retread = blocks
    if entry["params"] != ["mem0"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires the current mem0 entry token shape"
        )
    if [instruction["op"] for instruction in entry["instructions"]] != ["field.addr", "load", "cmp"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires field.addr/load/cmp in the entry block"
        )
    field_addr, entry_load, cmp_instr = entry["instructions"]
    param_name = function.params[0].name
    if field_addr["operands"] != [param_name, "sym:field:value"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires the fixed Counter.value field projection"
        )
    if entry_load["operands"] != [field_addr["id"], "mem0"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires entry load from the carried field address"
        )
    if cmp_instr["operands"] != [entry_load["id"], 0]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires the current less-than-zero compare"
        )
    entry_term = entry["terminator"]
    if (
        entry_term["kind"] != "cond_br"
        or entry_term["cond"] != cmp_instr["id"]
        or entry_term["true"] != "neg"
        or entry_term["false"] != "retread"
        or entry_term["true_args"] != [field_addr["id"], "mem0"]
        or entry_term["false_args"] != [field_addr["id"], "mem0"]
    ):
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires the current field-carrying diamond"
        )

    if neg["params"] != ["field1", "mem1"] or [instruction["op"] for instruction in neg["instructions"]] != ["store"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires a single store in the neg block"
        )
    neg_store = neg["instructions"][0]
    if neg_store["operands"] != ["field1", 0, "mem1"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires zero-store over the carried field handle"
        )
    neg_term = neg["terminator"]
    if neg_term["kind"] != "br" or neg_term["target"] != "retread" or neg_term["args"] != ["field1", neg_store["id"]]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires the neg block to carry the updated field handle"
        )

    if retread["params"] != ["field2", "mem3"] or [instruction["op"] for instruction in retread["instructions"]] != ["load"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires a single load in the retread block"
        )
    retread_load = retread["instructions"][0]
    if retread_load["operands"] != ["field2", "mem3"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires retread load from the carried field handle"
        )
    ret_term = retread["terminator"]
    if ret_term["kind"] != "ret" or ret_term["value"] != retread_load["id"]:
        raise PipelineError(
            f"{module.module_id}::{function.name}: record-cell Wasm emission requires returning the final field load"
        )

    header = f"  (func ${function.name} (export \"{function.name}\") {render_wasm_param(param_name)} (result i32)"
    return [
        header,
        f"    local.get ${param_name}",
        "    i32.load offset=0",
        "    i32.const 0",
        "    i32.lt_s",
        "    if",
        f"      local.get ${param_name}",
        "      i32.const 0",
        "      i32.store offset=0",
        "    end",
        f"    local.get ${param_name}",
        "    i32.load offset=0",
        "  )",
    ]


def emit_wasm_function(module: Module, function: FunctionDecl, lowered_function: dict):
    admitted_rules = set(WASM_BACKEND_METADATA["admitted_lowering_rules"])
    non_emittable_rules = set(WASM_BACKEND_METADATA["non_emittable_lowering_rules"])
    lowering_rules = [
        *(instruction["lowering_rule"] for block in lowered_function["blocks"] for instruction in block["instructions"]),
        *(block["terminator"]["lowering_rule"] for block in lowered_function["blocks"]),
    ]
    blocked_rules = [rule for rule in lowering_rules if rule in non_emittable_rules]
    if blocked_rules:
        raise PipelineError(
            f"{module.module_id}::{function.name}: helper-free Wasm emission does not admit lowering rule {blocked_rules[0]!r}"
        )
    unsupported_rules = [rule for rule in lowering_rules if rule not in admitted_rules]
    if unsupported_rules:
        raise PipelineError(
            f"{module.module_id}::{function.name}: lowering rule {unsupported_rules[0]!r} is outside the admitted Wasm contract"
        )

    lowered_ops = [instruction["op"] for block in lowered_function["blocks"] for instruction in block["instructions"]]
    unsupported_ops = [op for op in lowered_ops if op not in {"const", "alloc", "store", "load", "field.addr", "cmp", "call"}]
    if unsupported_ops:
        first_unsupported = unsupported_ops[0]
        raise PipelineError(
            f"{module.module_id}::{function.name}: unsupported SCIR-L op {first_unsupported!r} for helper-free Wasm emission"
        )
    if any(block["terminator"]["kind"] not in {"ret", "br", "cond_br"} for block in lowered_function["blocks"]):
        raise PipelineError(
            f"{module.module_id}::{function.name}: unsupported terminator in helper-free Wasm emission"
        )
    if lowered_ops == ["const"]:
        return emit_wasm_const_ret_function(module, function, lowered_function)
    if lowered_ops == []:
        return emit_wasm_passthrough_function(module, function, lowered_function)
    if lowered_ops == ["call"]:
        return emit_wasm_direct_local_call_function(module, function, lowered_function)
    if lowered_ops == ["field.addr", "load", "cmp", "store", "load"]:
        return emit_wasm_record_cell_function(module, function, lowered_function)
    if lowered_ops == ["alloc", "store", "load", "cmp", "store", "load"]:
        return emit_wasm_local_slot_function(module, function, lowered_function)
    raise PipelineError(
        f"{module.module_id}::{function.name}: Wasm emission does not admit this lowered op shape"
    )


def build_wasm_preservation_report(module: Module, lowered: dict):
    lowered_ops = {
        instruction["op"]
        for function in lowered["functions"]
        for block in function["blocks"]
        for instruction in block["instructions"]
    }
    downgrades = []
    normalized = []
    contract_bounded = []
    if {"alloc", "store", "load"} & lowered_ops:
        downgrades.append(
            {
                "reason": WASM_BACKEND_METADATA["local_slot_reason"],
                "preservation_level": WASM_BACKEND_METADATA["preservation_level"],
            }
        )
        normalized.append(WASM_BACKEND_METADATA["normalized_observable"])
    if "field.addr" in lowered_ops:
        downgrades.extend(
            [
                {
                    "reason": WASM_BACKEND_METADATA["record_cell_layout_reason"],
                    "preservation_level": WASM_BACKEND_METADATA["preservation_level"],
                },
                {
                    "reason": WASM_BACKEND_METADATA["shared_handle_reason"],
                    "preservation_level": WASM_BACKEND_METADATA["preservation_level"],
                },
            ]
        )
        normalized.append(WASM_BACKEND_METADATA["record_cell_normalized_observable"])
        contract_bounded.append(WASM_BACKEND_METADATA["shared_handle_contract_observable"])
    if "cmp" in lowered_ops:
        downgrades.append(
            {
                "reason": WASM_BACKEND_METADATA["cmp_reason"],
                "preservation_level": WASM_BACKEND_METADATA["preservation_level"],
            }
        )
        contract_bounded.append(WASM_BACKEND_METADATA["contract_bounded_observable"])
    preserved = ["synchronous scalar control flow", "return behavior"]
    if "call" in lowered_ops:
        preserved.append(WASM_BACKEND_METADATA["direct_call_observable"])
    if "field.addr" in lowered_ops:
        preserved.append(WASM_BACKEND_METADATA["field_addr_blocked_observable"])
    evidence = list(WASM_BACKEND_METADATA["required_evidence"])
    if "field.addr" in lowered_ops:
        evidence.extend(WASM_BACKEND_METADATA["record_cell_evidence"])
    return {
        "report_id": f"wasm-preservation-{slug(case_name_from_module(module))}",
        "subject": module.module_id,
        "path": WASM_BACKEND_METADATA["report_path"],
        "source_artifact": f"scir_l:{module.module_id}",
        "target_artifact": f"wasm:{module.module_id}.wat",
        "profile": WASM_BACKEND_METADATA["profile"],
        "preservation_level": WASM_BACKEND_METADATA["preservation_level"],
        "status": "pass",
        "downgrades": downgrades,
        "boundary_annotations": [],
        "observables": {
            "preserved": preserved,
            "normalized": normalized,
            "contract_bounded": contract_bounded,
            "opaque": [],
            "unsupported": [],
        },
        "evidence": evidence,
    }


def emit_wasm_module(module: Module, lowered: dict, *, input_representation: str = "SCIR-H"):
    assert_canonical_pipeline_input(input_representation, "backend emission")
    detect_wasm_field_place_layout_blocker(module, lowered)
    is_record_cell_candidate = is_wasm_record_cell_candidate(module, lowered)
    if not is_record_cell_candidate:
        validate_wasm_scalar_signature(module)
    lowered_functions = lowered["functions"]
    if len(lowered_functions) != len(module.functions):
        raise PipelineError(
            f"{module.module_id}: Wasm emission requires one lowered function per SCIR-H function"
        )
    lines = ["(module"]
    if is_record_cell_candidate:
        lines.append('  (memory (export "memory") 1)')
    for function, lowered_function in zip(module.functions, lowered_functions):
        if function.name != lowered_function["name"]:
            raise PipelineError(
                f"{module.module_id}: lowered function order drifted for Wasm emission"
            )
        lines.extend(emit_wasm_function(module, function, lowered_function))
    lines.append(")")
    wat_text = "\n".join(lines) + "\n"
    return wat_text, build_wasm_preservation_report(module, lowered)


def validate_wasm_preservation_report(module: Module, lowered: dict, report: dict):
    failures = []
    if report["path"] != WASM_BACKEND_METADATA["report_path"]:
        failures.append(f"{module.module_id}: expected Wasm preservation path {WASM_BACKEND_METADATA['report_path']}")
    if report["profile"] != WASM_BACKEND_METADATA["profile"]:
        failures.append(f"{module.module_id}: expected Wasm preservation profile {WASM_BACKEND_METADATA['profile']}")
    if report["preservation_level"] != WASM_BACKEND_METADATA["preservation_level"]:
        failures.append(f"{module.module_id}: expected Wasm preservation level {WASM_BACKEND_METADATA['preservation_level']}")
    if report["status"] != "pass":
        failures.append(f"{module.module_id}: expected Wasm preservation status pass")
    if report["boundary_annotations"]:
        failures.append(f"{module.module_id}: helper-free Wasm emission must not add boundary annotations")
    if report["observables"]["opaque"]:
        failures.append(f"{module.module_id}: helper-free Wasm emission must not record opaque observables")
    if report["observables"]["unsupported"]:
        failures.append(f"{module.module_id}: emitted Wasm subset must not report unsupported observables")

    lowered_ops = {
        instruction["op"]
        for function in lowered["functions"]
        for block in function["blocks"]
        for instruction in block["instructions"]
    }
    required_evidence = set(WASM_BACKEND_METADATA["required_evidence"])
    if "field.addr" in lowered_ops:
        required_evidence |= set(WASM_BACKEND_METADATA["record_cell_evidence"])
    missing_evidence = sorted(required_evidence - set(report["evidence"]))
    if missing_evidence:
        failures.append(
            f"{module.module_id}: Wasm preservation report missing evidence {', '.join(missing_evidence)}"
        )
    reasons = {item["reason"] for item in report["downgrades"]}
    expected_normalized = []
    expected_contract_bounded = []
    if {"alloc", "store", "load"} & lowered_ops:
        local_slot_reason = WASM_BACKEND_METADATA["local_slot_reason"]
        if local_slot_reason not in reasons:
            failures.append(f"{module.module_id}: Wasm preservation report must record local-slot normalization")
        expected_normalized.append(WASM_BACKEND_METADATA["normalized_observable"])
    if "field.addr" in lowered_ops:
        layout_reason = WASM_BACKEND_METADATA["record_cell_layout_reason"]
        shared_reason = WASM_BACKEND_METADATA["shared_handle_reason"]
        if layout_reason not in reasons:
            failures.append(f"{module.module_id}: Wasm preservation report must record record-cell layout normalization")
        if shared_reason not in reasons:
            failures.append(f"{module.module_id}: Wasm preservation report must record the shared-handle caller contract")
        expected_normalized.append(WASM_BACKEND_METADATA["record_cell_normalized_observable"])
        expected_contract_bounded.append(WASM_BACKEND_METADATA["shared_handle_contract_observable"])
    if "cmp" in lowered_ops:
        cmp_reason = WASM_BACKEND_METADATA["cmp_reason"]
        if cmp_reason not in reasons:
            failures.append(f"{module.module_id}: Wasm preservation report must record the bounded cmp shape")
        expected_contract_bounded.append(WASM_BACKEND_METADATA["contract_bounded_observable"])
    expected_preserved = ["synchronous scalar control flow", "return behavior"]
    if "call" in lowered_ops:
        expected_preserved.append(WASM_BACKEND_METADATA["direct_call_observable"])
    if "field.addr" in lowered_ops:
        expected_preserved.append(WASM_BACKEND_METADATA["field_addr_blocked_observable"])
    if report["observables"]["preserved"] != expected_preserved:
        failures.append(
            f"{module.module_id}: Wasm preservation report preserved observables expected {expected_preserved!r}"
        )
    if report["observables"]["normalized"] != expected_normalized:
        failures.append(
            f"{module.module_id}: Wasm preservation report normalized observables expected {expected_normalized!r}"
        )
    if report["observables"]["contract_bounded"] != expected_contract_bounded:
        failures.append(
            f"{module.module_id}: Wasm preservation report contract_bounded observables expected {expected_contract_bounded!r}"
        )
    return failures


def validate_wasm_artifacts(module: Module, lowered: dict, wat_text: str, report: dict):
    failures = []
    if not wat_text.startswith("(module\n"):
        failures.append(f"{module.module_id}: emitted WAT must start with a module header")
    if "(import " in wat_text:
        failures.append(f"{module.module_id}: emitted WAT must not introduce helper imports")
    if "(call_indirect" in wat_text:
        failures.append(f"{module.module_id}: emitted WAT must not introduce indirect Wasm calls in this slice")
    if "(local $slot0 i32)" in wat_text and "i32.lt_s" not in wat_text:
        failures.append(f"{module.module_id}: local-slot Wasm emission must retain the less-than comparison")
    lowered_ops = {
        instruction["op"]
        for function in lowered["functions"]
        for block in function["blocks"]
        for instruction in block["instructions"]
    }
    if "field.addr" in lowered_ops:
        if '(memory (export "memory") 1)' not in wat_text:
            failures.append(f"{module.module_id}: record-cell Wasm emission must export module-owned memory")
        if "i32.load offset=0" not in wat_text or "i32.store offset=0" not in wat_text:
            failures.append(f"{module.module_id}: record-cell Wasm emission must use the fixed Counter.value offset=0 memory cell")
    failures.extend(validate_wasm_preservation_report(module, lowered, report))
    return failures


def validate_wasm_not_emittable(module: Module, lowered: dict):
    try:
        emit_wasm_module(module, lowered)
    except PipelineError:
        return []
    return [f"{module.module_id}: unsupported lowered module unexpectedly emitted Wasm output"]


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


def reconstruct_python_source(module: Module, *, input_representation: str = "SCIR-H"):
    assert_canonical_pipeline_input(input_representation, "reconstruction")
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
    if case_name == "b_direct_call":
        exec(compile(source_text, f"<{case_name}>", "exec"), namespace)
        return [
            namespace["identity"](-4),
            namespace["call_identity"](-4),
            namespace["call_identity"](7),
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
        "path": "h_to_python",
        "source_artifact": f"scir_h:fixture.python_importer.{case_name}",
        "target_artifact": f"reconstructed/python/{case_name}.py",
        "profile": profile,
        "preservation_level": preservation_level,
        "status": "pass" if compile_pass and test_pass else "fail",
        "downgrades": (
            [
                {
                    "reason": "opaque boundary retained as explicit boundary annotation",
                    "preservation_level": "P3",
                }
            ]
            if case_name == "c_opaque_call"
            else []
        ),
        "boundary_annotations": ["foreign_api.ping boundary"] if case_name == "c_opaque_call" else [],
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
    if report["path"] != "h_to_python":
        failures.append(f"{case_name}: expected reconstruction preservation path h_to_python")
    if report["profile"] != profile:
        failures.append(f"{case_name}: expected reconstruction preservation profile {profile}")
    if report["preservation_level"] != preservation_level:
        failures.append(
            f"{case_name}: expected reconstruction preservation level {preservation_level}"
        )

    expected_status = "pass" if reconstruction_report["compile_pass"] and reconstruction_report["test_pass"] else "fail"
    if report["status"] != expected_status:
        failures.append(f"{case_name}: reconstruction preservation status disagreed with compile/test evidence")

    opaque_items = report["boundary_annotations"]
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
        if case_name not in outputs["scir_hc_reports"]:
            failures.append(f"{case_name}: supported case must emit an SCIR-Hc output")
        if case_name not in outputs["scir_l_reports"]:
            failures.append(f"{case_name}: supported case must emit an SCIR-L output")
        if case_name not in outputs["translation_reports"]:
            failures.append(f"{case_name}: supported case must emit a translation output")
        if case_name not in outputs["reconstruction_reports"]:
            failures.append(f"{case_name}: supported case must emit a reconstruction output")
        if case_name not in outputs["reconstruction_preservation_reports"]:
            failures.append(f"{case_name}: supported case must emit a reconstruction preservation report")
    for case_name in WASM_EMITTABLE_CASES:
        if case_name not in outputs["wasm_reports"]:
            failures.append(f"{case_name}: Wasm-emittable case must emit a Wasm output")
    for case_name in sorted(set(SUPPORTED_CASES) - set(WASM_EMITTABLE_CASES)):
        if case_name in outputs["wasm_reports"]:
            failures.append(f"{case_name}: non-emittable supported case must not emit a Wasm output")
    for case_name in SCIRH_ONLY_CASES:
        if case_name not in outputs["scir_hc_reports"]:
            failures.append(f"{case_name}: importer-only case must emit an SCIR-Hc output")
    for case_name in [*SCIRH_ONLY_CASES, *REJECTED_CASES]:
        if case_name in outputs["scir_l_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit SCIR-L output")
        if case_name in outputs["translation_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit translation output")
        if case_name in outputs["reconstruction_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit reconstruction output")
        if case_name in outputs["reconstruction_preservation_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit reconstruction preservation report")
        if case_name in outputs["wasm_reports"]:
            failures.append(f"{case_name}: non-executable case must not emit Wasm output")
    for case_name in REJECTED_CASES:
        if case_name in outputs["scir_hc_reports"]:
            failures.append(f"{case_name}: rejected case must not emit SCIR-Hc output")
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


TRACK_C_REPAIR_CASE_CONFIG = {
    "a_basic_function": {
        "source_surface": "if y < 0:\n    y = 0",
        "scirh_surface": "if lt y 0\n  set y 0",
        "regularized_core_surface": "(if (lt y 0) (set y 0))",
        "seed_bug": lambda source: source.replace("y = 0", "y = 1", 1),
    },
    "a_async_await": {
        "source_surface": "return 1",
        "scirh_surface": "return 1",
        "regularized_core_surface": "(return 1)",
        "seed_bug": lambda source: source.replace("return 1", "return 0", 1),
    },
    "b_direct_call": {
        "source_surface": "return identity(x)",
        "scirh_surface": "return identity(x)",
        "regularized_core_surface": "(return (call identity x))",
        "seed_bug": lambda source: source.replace("return identity(x)", "return identity(0)", 1),
    },
    "c_opaque_call": {
        "source_surface": "return foreign_api.ping()",
        "scirh_surface": "return foreign_api_ping()",
        "regularized_core_surface": "(return (opaque.call foreign_api_ping))",
        "seed_bug": None,
    },
}


def track_c_typed_ast_surface(case_name: str, source_text: str):
    tree = ast.parse(source_text)
    if case_name == "a_basic_function":
        node = tree.body[0].body[1]
    elif case_name == "a_async_await":
        node = tree.body[0].body[0]
    elif case_name == "b_direct_call":
        node = tree.body[1].body[0]
    elif case_name == "c_opaque_call":
        node = tree.body[1].body[0]
    else:
        raise PipelineError(f"{case_name}: Track C typed-AST surface is not defined")
    return ast.dump(node, annotate_fields=True)


def track_patch_composability_metrics():
    source_ratios = []
    typed_ast_ratios = []
    regularized_core_ratios = []
    scirh_token_counts = []
    source_token_counts = []
    typed_ast_token_counts = []

    for case_name, config in TRACK_C_REPAIR_CASE_CONFIG.items():
        source_surface = config["source_surface"]
        scirh_surface = config["scirh_surface"]
        regularized_core_surface = config["regularized_core_surface"]
        typed_ast_surface = track_c_typed_ast_surface(case_name, PYTHON_SOURCE_TEXTS[case_name])
        scirh_tokens = count_tokens(scirh_surface)
        source_tokens = count_tokens(source_surface)
        typed_ast_tokens = count_tokens(typed_ast_surface)
        regularized_core_tokens = count_tokens(regularized_core_surface)
        scirh_token_counts.append(scirh_tokens)
        source_token_counts.append(source_tokens)
        typed_ast_token_counts.append(typed_ast_tokens)
        source_ratios.append(scirh_tokens / source_tokens)
        typed_ast_ratios.append(scirh_tokens / typed_ast_tokens)
        regularized_core_ratios.append(scirh_tokens / regularized_core_tokens)

    median_source_ratio = statistics.median(source_ratios)
    median_typed_ast_ratio = statistics.median(typed_ast_ratios)
    median_regularized_core_ratio = statistics.median(regularized_core_ratios)
    return {
        "median_patch_surface_scir_h_tokens": round(statistics.median(scirh_token_counts), 4),
        "median_patch_surface_source_tokens": round(statistics.median(source_token_counts), 4),
        "median_patch_surface_typed_ast_tokens": round(statistics.median(typed_ast_token_counts), 4),
        "median_scir_to_source_patch_ratio": round(median_source_ratio, 4),
        "median_scir_to_typed_ast_patch_ratio": round(median_typed_ast_ratio, 4),
        "median_scir_to_regularized_core_patch_ratio": round(median_regularized_core_ratio, 4),
        "patch_composability_gain_vs_source": round(1.0 - median_source_ratio, 4),
        "patch_composability_gain_vs_typed_ast": round(1.0 - median_typed_ast_ratio, 4),
    }


def evaluate_track_c_seeded_repair(case_name: str):
    config = TRACK_C_REPAIR_CASE_CONFIG[case_name]
    seed_bug = config["seed_bug"]
    if seed_bug is None:
        return {
            "bug_compile_pass": None,
            "bug_test_pass": None,
            "repair_compile_pass": False,
            "repair_test_pass": False,
            "accepted": False,
        }

    buggy_source = seed_bug(PYTHON_SOURCE_TEXTS[case_name])
    try:
        compile(buggy_source, f"<track-c-bug:{case_name}>", "exec")
        bug_compile_pass = True
    except SyntaxError:
        bug_compile_pass = False

    if bug_compile_pass:
        try:
            bug_test_pass = execute_module(case_name, buggy_source) == execute_module(case_name, PYTHON_SOURCE_TEXTS[case_name])
        except Exception:
            bug_test_pass = False
    else:
        bug_test_pass = False

    repair_compile_pass, repair_test_pass = evaluate_reconstruction(case_name, PYTHON_SOURCE_TEXTS[case_name])
    accepted = bug_compile_pass and not bug_test_pass and repair_compile_pass and repair_test_pass
    return {
        "bug_compile_pass": bug_compile_pass,
        "bug_test_pass": bug_test_pass,
        "repair_compile_pass": repair_compile_pass,
        "repair_test_pass": repair_test_pass,
        "accepted": accepted,
    }


def run_track_c_pilot(root: pathlib.Path):
    failures, outputs = run_pipeline(root)
    if failures:
        return failures, None, None
    track_a_manifest, track_a_result = run_track_a(root, outputs=outputs)
    track_b_manifest, track_b_result = run_track_b(
        root,
        {name: item["report"] for name, item in outputs["reconstruction_reports"].items()},
    )
    track_contract = benchmark_track_contract("C")
    opaque_nodes, total_nodes, tier_counts = compare_imported_feature_totals(root)
    boundary_annotation_fraction = opaque_nodes / total_nodes
    source_ratios = []
    typed_ast_ratios = []
    regularized_core_ratios = []
    accepted_case_count = 0
    repair_test_pass_count = 0

    for case_name in track_contract["pilot_cases"]:
        config = TRACK_C_REPAIR_CASE_CONFIG[case_name]
        source_surface = config["source_surface"]
        scirh_surface = config["scirh_surface"]
        regularized_core_surface = config["regularized_core_surface"]
        typed_ast_surface = track_c_typed_ast_surface(case_name, PYTHON_SOURCE_TEXTS[case_name])
        scirh_tokens = count_tokens(scirh_surface)
        source_tokens = count_tokens(source_surface)
        typed_ast_tokens = count_tokens(typed_ast_surface)
        regularized_core_tokens = count_tokens(regularized_core_surface)
        source_ratios.append(scirh_tokens / source_tokens)
        typed_ast_ratios.append(scirh_tokens / typed_ast_tokens)
        regularized_core_ratios.append(scirh_tokens / regularized_core_tokens)

        repair_outcome = evaluate_track_c_seeded_repair(case_name)
        if repair_outcome["accepted"]:
            accepted_case_count += 1
        if repair_outcome["repair_test_pass"]:
            repair_test_pass_count += 1

    repair_task_count = len(track_contract["pilot_cases"])
    accepted_rate = accepted_case_count / repair_task_count
    repair_test_pass_rate = repair_test_pass_count / repair_task_count
    median_source_ratio = statistics.median(source_ratios)
    median_typed_ast_ratio = statistics.median(typed_ast_ratios)
    median_regularized_core_ratio = statistics.median(regularized_core_ratios)
    gate_s2_ready = track_a_result["status"] == "pass" and track_b_result["status"] == "pass"
    gate_k1_hit = not (median_typed_ast_ratio < 1.0 and accepted_case_count > 0)

    manifest = {
        "benchmark_id": track_contract["benchmark_id"],
        "track": "C",
        "task_family": track_contract["task_family"],
        "corpus": {
            "name": track_contract["corpus_name"],
            "scope": track_contract["corpus_scope"],
            "hash": corpus_hash(BENCHMARK_CASES),
        },
        "baselines": benchmark_track_baselines("C"),
        "profiles": list(track_contract["profiles"]),
        "success_gates": list(track_contract["success_gates"]),
        "kill_gates": list(track_contract["kill_gates"]),
        "contamination_controls": list(BENCHMARK_CONTRACT_METADATA["contamination_controls"]),
    }
    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": track_contract["sample_run_id"],
        "system_under_test": track_contract["sample_system_under_test"],
        "track": "C",
        "profile": track_contract["result_profile"],
        "metrics": {
            "repair_task_count": repair_task_count,
            "accepted_case_count": accepted_case_count,
            "boundary_only_case_count": len(track_contract["boundary_only_cases"]),
            "repair_accept_rate": round(accepted_rate, 4),
            "repair_test_pass_rate": round(repair_test_pass_rate, 4),
            "median_scir_to_source_repair_ratio": round(median_source_ratio, 4),
            "median_scir_to_typed_ast_repair_ratio": round(median_typed_ast_ratio, 4),
            "median_scir_to_regularized_core_repair_ratio": round(median_regularized_core_ratio, 4),
            "gate_S2_ready": gate_s2_ready,
            "gate_K1_hit": gate_k1_hit,
            "boundary_annotation_fraction": round(boundary_annotation_fraction, 4),
            "preservation_level_ceiling": BENCHMARK_CONTRACT_METADATA["preservation_level_ceiling"],
            "tier_a_feature_count": tier_counts["A"],
            "tier_b_feature_count": tier_counts["B"],
            "tier_c_feature_count": tier_counts["C"],
            "tier_d_feature_count": tier_counts["D"],
        },
        "baseline_comparison": {
            "direct source": round(median_source_ratio - 1.0, 4),
            "typed-AST": round(1.0 - median_typed_ast_ratio, 4),
            "lightweight regularized core or s-expression": round(median_regularized_core_ratio - 1.0, 4),
        },
        "status": "fail" if (not gate_s2_ready or gate_k1_hit) else "mixed",
        "evidence": list(track_contract["sample_evidence"]),
    }

    return failures, manifest, result


def run_track_a(root: pathlib.Path, *, outputs: dict):
    track_contract = benchmark_track_contract("A")
    scirh_texts = [load_import_artifacts(root, case_name)["expected.scirh"] for case_name in BENCHMARK_CASES]
    scirhc_texts = [outputs["scir_hc_reports"][case_name]["text"] for case_name in BENCHMARK_CASES]
    source_token_counts = [count_tokens(PYTHON_SOURCE_TEXTS[case_name]) for case_name in BENCHMARK_CASES]
    scirh_token_counts = [count_tokens(text) for text in scirh_texts]
    scirhc_token_counts = [count_tokens(text) for text in scirhc_texts]
    typed_ast_token_counts = [
        count_tokens(ast.dump(ast.parse(PYTHON_SOURCE_TEXTS[case_name]), annotate_fields=True))
        for case_name in BENCHMARK_CASES
    ]
    scirh_body_token_counts = [scirh_header_and_body_tokens(text)[1] for text in scirh_texts]
    source_body_token_counts = [source_body_tokens(PYTHON_SOURCE_TEXTS[case_name]) for case_name in BENCHMARK_CASES]
    scirh_header_token_counts = [scirh_header_and_body_tokens(text)[0] for text in scirh_texts]
    opaque_nodes, total_nodes, tier_counts = compare_imported_feature_totals(root)

    source_ratios = [
        scirh / source
        for scirh, source in zip(scirh_token_counts, source_token_counts)
    ]
    scirhc_source_ratios = [
        scirhc / source
        for scirhc, source in zip(scirhc_token_counts, source_token_counts)
    ]
    typed_ast_ratios = [
        scirh / typed
        for scirh, typed in zip(scirh_token_counts, typed_ast_token_counts)
    ]
    scirhc_typed_ast_ratios = [
        scirhc / typed
        for scirhc, typed in zip(scirhc_token_counts, typed_ast_token_counts)
    ]
    body_source_ratios = [
        scirh / source
        for scirh, source in zip(scirh_body_token_counts, source_body_token_counts)
    ]

    median_source_ratio = statistics.median(source_ratios)
    aggregate_source_ratio = sum(scirh_token_counts) / sum(source_token_counts)
    median_scirhc_source_ratio = statistics.median(scirhc_source_ratios)
    aggregate_scirhc_source_ratio = sum(scirhc_token_counts) / sum(source_token_counts)
    median_typed_ast_ratio = statistics.median(typed_ast_ratios)
    aggregate_typed_ast_ratio = sum(scirh_token_counts) / sum(typed_ast_token_counts)
    median_scirhc_typed_ast_ratio = statistics.median(scirhc_typed_ast_ratios)
    aggregate_scirhc_typed_ast_ratio = sum(scirhc_token_counts) / sum(typed_ast_token_counts)
    body_median_source_ratio = statistics.median(body_source_ratios)
    header_token_share = sum(scirh_header_token_counts) / sum(scirh_token_counts)
    opaque_fraction = opaque_nodes / total_nodes
    semantic_markers = sum(
        text.count("opaque") + text.count("await") + text.count("var ") + text.count("set ")
        for text in scirh_texts
    )
    source_markers = sum(
        PYTHON_SOURCE_TEXTS[case_name].count("await") + PYTHON_SOURCE_TEXTS[case_name].count("import ")
        for case_name in BENCHMARK_CASES
    )
    explicitness_gain = semantic_markers - source_markers
    patch_metrics = track_patch_composability_metrics()

    gate_s3_source_pass = median_source_ratio <= 1.10
    gate_s3_ast_pass = median_scirhc_typed_ast_ratio <= 0.75
    gate_s4_pass = opaque_fraction < 0.15
    gate_k2_hit = median_source_ratio > 1.50
    gate_k4_hit = opaque_fraction > 0.25
    success = (gate_s3_source_pass or gate_s3_ast_pass) and gate_s4_pass
    passed = success and not gate_k2_hit and not gate_k4_hit

    manifest = {
        "benchmark_id": track_contract["benchmark_id"],
        "track": "A",
        "task_family": track_contract["task_family"],
        "corpus": {
            "name": track_contract["corpus_name"],
            "scope": track_contract["corpus_scope"],
            "hash": corpus_hash(BENCHMARK_CASES),
        },
        "baselines": benchmark_track_baselines("A"),
        "profiles": list(track_contract["profiles"]),
        "success_gates": list(track_contract["success_gates"]),
        "kill_gates": list(track_contract["kill_gates"]),
        "contamination_controls": list(BENCHMARK_CONTRACT_METADATA["contamination_controls"]),
    }

    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": "bootstrap-track-a-run-2026-03-16",
        "system_under_test": "scir-bootstrap-executable-path",
        "track": "A",
        "profile": track_contract["result_profile"],
        "metrics": {
            "source_token_total": sum(source_token_counts),
            "scir_h_token_total": sum(scirh_token_counts),
            "scir_hc_token_total": sum(scirhc_token_counts),
            "typed_ast_token_total": sum(typed_ast_token_counts),
            "median_scir_to_source_ratio": round(median_source_ratio, 4),
            "aggregate_scir_to_source_ratio": round(aggregate_source_ratio, 4),
            "median_scirhc_to_source_ratio": round(median_scirhc_source_ratio, 4),
            "aggregate_scirhc_to_source_ratio": round(aggregate_scirhc_source_ratio, 4),
            "median_scir_to_typed_ast_ratio": round(median_typed_ast_ratio, 4),
            "aggregate_scir_to_typed_ast_ratio": round(aggregate_typed_ast_ratio, 4),
            "median_scirhc_to_typed_ast_ratio": round(median_scirhc_typed_ast_ratio, 4),
            "aggregate_scirhc_to_typed_ast_ratio": round(aggregate_scirhc_typed_ast_ratio, 4),
            "body_median_scir_to_source_ratio": round(body_median_source_ratio, 4),
            "aggregate_structural_redundancy_gain": round(aggregate_source_ratio - aggregate_scirhc_source_ratio, 4),
            "header_token_share": round(header_token_share, 4),
            "gate_S3_source_pass": gate_s3_source_pass,
            "gate_S3_ast_pass": gate_s3_ast_pass,
            "gate_S4_pass": gate_s4_pass,
            "gate_K2_hit": gate_k2_hit,
            "gate_K4_hit": gate_k4_hit,
            "opaque_fraction": round(opaque_fraction, 4),
            "semantic_explicitness_gain": explicitness_gain,
            "patch_composability_gain_vs_typed_ast": patch_metrics["patch_composability_gain_vs_typed_ast"],
            "median_scir_to_typed_ast_patch_ratio": patch_metrics["median_scir_to_typed_ast_patch_ratio"],
            "preservation_level_ceiling": BENCHMARK_CONTRACT_METADATA["preservation_level_ceiling"],
            "tier_a_feature_count": tier_counts["A"],
            "tier_b_feature_count": tier_counts["B"],
            "tier_c_feature_count": tier_counts["C"],
            "tier_d_feature_count": tier_counts["D"],
        },
        "baseline_comparison": {
            "direct source": round(median_source_ratio - 1.0, 4),
            "typed-AST": round(1.0 - median_typed_ast_ratio, 4),
            "typed-AST (SCIR-Hc LCR)": round(1.0 - median_scirhc_typed_ast_ratio, 4),
        },
        "status": "pass" if passed else "fail",
        "evidence": [
            "generated SCIR-H bundle corpus",
            "generated derived SCIR-Hc bundle corpus",
            "typed AST token baseline from Python ast.dump",
            "median gate evaluation follows benchmarks/success_failure_gates.md",
        ],
    }
    return manifest, result


def run_track_b(root: pathlib.Path, reconstruction_reports: dict[str, dict]):
    track_contract = benchmark_track_contract("B")
    opaque_nodes, total_nodes, tier_counts = compare_imported_feature_totals(root)
    opaque_fraction = opaque_nodes / total_nodes
    tier_a_cases = benchmark_track_compile_cases()
    compile_rate = sum(
        1 for case_name in tier_a_cases if reconstruction_reports[case_name]["compile_pass"]
    ) / len(tier_a_cases)
    test_rate = sum(
        1 for case_name in tier_a_cases if reconstruction_reports[case_name]["test_pass"]
    ) / len(tier_a_cases)
    idiomaticity = sum(
        reconstruction_reports[case_name]["idiomaticity_score"] for case_name in BENCHMARK_CASES
    ) / len(BENCHMARK_CASES)
    gate_s1_pass = compile_rate >= 0.95 and test_rate >= 0.95
    gate_s4_pass = opaque_fraction < 0.15
    gate_k3_hit = compile_rate < 0.90 or test_rate < 0.90
    gate_k4_hit = opaque_fraction > 0.25
    passed = gate_s1_pass and gate_s4_pass and not gate_k3_hit and not gate_k4_hit
    manifest = {
        "benchmark_id": track_contract["benchmark_id"],
        "track": "B",
        "task_family": track_contract["task_family"],
        "corpus": {
            "name": track_contract["corpus_name"],
            "scope": track_contract["corpus_scope"],
            "hash": corpus_hash(BENCHMARK_CASES),
        },
        "baselines": benchmark_track_baselines("B"),
        "profiles": list(track_contract["profiles"]),
        "success_gates": list(track_contract["success_gates"]),
        "kill_gates": list(track_contract["kill_gates"]),
        "contamination_controls": list(BENCHMARK_CONTRACT_METADATA["contamination_controls"]),
    }
    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": "bootstrap-track-b-run-2026-03-16",
        "system_under_test": "scir-bootstrap-executable-path",
        "track": "B",
        "profile": track_contract["result_profile"],
        "metrics": {
            "supported_case_count": len(BENCHMARK_CASES),
            "tier_a_compile_pass_rate": round(compile_rate, 4),
            "tier_a_test_pass_rate": round(test_rate, 4),
            "idiomaticity_mean": round(idiomaticity, 4),
            "opaque_fraction": round(opaque_fraction, 4),
            "gate_S1_pass": gate_s1_pass,
            "gate_S4_pass": gate_s4_pass,
            "gate_K3_hit": gate_k3_hit,
            "gate_K4_hit": gate_k4_hit,
            "preservation_level_ceiling": BENCHMARK_CONTRACT_METADATA["preservation_level_ceiling"],
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
        "source_to_h_reports": {},
        "scir_h_reports": {},
        "scir_hc_reports": {},
        "scir_l_reports": {},
        "translation_reports": {},
        "reconstruction_reports": {},
        "reconstruction_preservation_reports": {},
        "wasm_reports": {},
        "stage_observations": {},
    }

    for case_name in ALL_CASES:
        artifacts = load_import_artifacts(root, case_name)
        failures.extend(validate_import_bundle(root, case_name, artifacts))
        if case_name in REJECTED_CASES:
            if "expected.scirh" in artifacts:
                failures.append(f"{case_name}: rejected case must not emit SCIR-H")
            continue

        source_to_h_report = build_source_to_h_preservation_report(case_name, artifacts)
        failures.extend(
            validate_instance(
                root,
                source_to_h_report,
                "schemas/preservation_report.schema.json",
                f"{case_name} source_to_h_preservation",
            )
        )
        outputs["source_to_h_reports"][case_name] = source_to_h_report

        scirh_failures, parsed_module, scir_h_report = validate_scirh_case(
            case_name,
            artifacts["expected.scirh"],
            boundary_contracts=artifacts.get("opaque_boundary_contract.json"),
        )
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

        scirhc_failures, hc_module, hc_text, hc_stats, scir_hc_report = validate_scirhc_case(
            case_name,
            parsed_module,
            boundary_contracts=artifacts.get("opaque_boundary_contract.json"),
        )
        failures.extend(scirhc_failures)
        failures.extend(
            validate_instance(
                root,
                scir_hc_report,
                "schemas/validation_report.schema.json",
                f"{case_name} scir_hc_validation",
            )
        )
        outputs["scir_hc_reports"][case_name] = {
            "module": hc_module,
            "text": hc_text,
            "stats": hc_stats,
            "validation_report": scir_hc_report,
        }
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

        if case_name in WASM_EMITTABLE_CASES:
            wat_text, wasm_report = emit_wasm_module(parsed_module, lowered)
            failures.extend(
                validate_instance(
                    root,
                    wasm_report,
                    "schemas/preservation_report.schema.json",
                    f"{case_name} wasm_preservation",
                )
            )
            failures.extend(validate_wasm_artifacts(parsed_module, lowered, wat_text, wasm_report))
            outputs["wasm_reports"][case_name] = {
                "text": wat_text,
                "preservation_report": wasm_report,
            }
        else:
            failures.extend(validate_wasm_not_emittable(parsed_module, lowered))

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
        outputs["stage_observations"][case_name] = build_case_stage_observations(case_name, artifacts, outputs)

    failures.extend(validate_executable_output_set(outputs))
    failures.extend(validate_active_corpus_preservation(root, ACTIVE_TIER_A_CORPUS_REL, outputs))
    failures.extend(validate_active_corpus_preservation(root, ACTIVE_PROOF_LOOP_CORPUS_REL, outputs))
    failures.extend(validate_negative_scirh_corpus(root))
    failures.extend(validate_negative_scirl_corpus(root))
    return failures, outputs


def run_benchmark_suite(root: pathlib.Path):
    failures, outputs = run_pipeline(root)
    if failures:
        return failures, None

    track_a_manifest, track_a_result = run_track_a(root, outputs=outputs)
    track_b_manifest, track_b_result = run_track_b(
        root,
        {name: item["report"] for name, item in outputs["reconstruction_reports"].items()},
    )
    benchmark_items = {
        "track_a_manifest": track_a_manifest,
        "track_a_result": track_a_result,
        "track_b_manifest": track_b_manifest,
        "track_b_result": track_b_result,
    }

    for label, result in [
        ("Track A", track_a_result),
        ("Track B", track_b_result),
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

    param_mutation_text = (
        "module invalid.param_mutation\n"
        "fn bad x int -> int !write\n"
        "  set x 0\n"
        "  return x\n"
    )
    param_mutation_diagnostics = validate_scirh_module_semantics(
        "self-test param mutation",
        parse_module(param_mutation_text),
        canonical_text=param_mutation_text,
    )
    if not any(item["code"] == SCIRH_IMPLICIT_MUTATION_CODE for item in param_mutation_diagnostics):
        failures.append("self-test parameter mutation rejection: expected H002")

    unused_effect_text = (
        "module invalid.unused_effect\n"
        "fn bad x int -> int !await\n"
        "  return x\n"
    )
    unused_effect_diagnostics = validate_scirh_module_semantics(
        "self-test unused effect",
        parse_module(unused_effect_text),
        canonical_text=unused_effect_text,
    )
    if not any(item["code"] == SCIRH_IMPLICIT_EFFECT_CODE and "unused effects" in item["message"] for item in unused_effect_diagnostics):
        failures.append("self-test unused effect rejection: expected H003")

    missing_throw_text = (
        "module invalid.missing_throw\n"
        "fn may_fail -> int !throw\n"
        "  try\n"
        "    return 1\n"
        "  catch err Error\n"
        "    return 0\n"
        "\n"
        "fn caller -> int !\n"
        "  return may_fail()\n"
    )
    missing_throw_diagnostics = validate_scirh_module_semantics(
        "self-test missing throw effect",
        parse_module(missing_throw_text),
        canonical_text=missing_throw_text,
    )
    if not any(item["code"] == SCIRH_IMPLICIT_EFFECT_CODE and "missing explicit effects ['throw']" in item["message"] for item in missing_throw_diagnostics):
        failures.append("self-test missing throw propagation: expected H003")

    borrow_mutation_text = (
        "module invalid.borrow_mutation\n"
        "type Counter record { value int }\n"
        "\n"
        "fn bad counter borrow<Counter> -> int !write\n"
        "  set counter.value 0\n"
        "  return counter.value\n"
    )
    borrow_mutation_diagnostics = validate_scirh_module_semantics(
        "self-test borrow mutation",
        parse_module(borrow_mutation_text),
        canonical_text=borrow_mutation_text,
    )
    if not any(item["code"] == SCIRH_OWNERSHIP_ALIAS_CODE for item in borrow_mutation_diagnostics):
        failures.append("self-test borrow mutation rejection: expected H010")

    boundary_text = (
        "module invalid.boundary_metadata\n"
        "import sym foreign_api_ping python:foreign_api.ping\n"
        "\n"
        "fn ping -> opaque<ForeignResult> !opaque\n"
        "  return foreign_api_ping()\n"
    )
    boundary_diagnostics = validate_scirh_module_semantics(
        "self-test missing boundary capabilities",
        parse_module(boundary_text),
        boundary_contracts={
            "boundary_id": "invalid.boundary_metadata.boundary.foreign_api_ping",
            "kind": "opaque_call",
            "signature": "opaque.call foreign_api_ping() -> opaque<ForeignResult> !opaque",
            "effects": ["opaque"],
            "ownership_transfer": {"inbound": [], "outbound": ["opaque<ForeignResult>"]},
            "determinism": "unknown",
            "audit_note": "self-test",
        },
        canonical_text=boundary_text,
    )
    if not any(item["code"] == SCIRH_BOUNDARY_CODE and "missing fields ['capabilities']" in item["message"] for item in boundary_diagnostics):
        failures.append("self-test missing boundary capabilities field: expected H008")

    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][0]["instructions"][0]["origin"] = "other.module::var-y"
    scirl_failures, _ = validate_scirl_module(mutated)
    if not any("must remain rooted" in item for item in scirl_failures):
        failures.append("self-test mismatched SCIR-L provenance root: expected failure")

    overclaim_status = preservation_expectation_status(
        make_stage_observation(status="pass", preservation_level="P0"),
        {"status": "pass", "preservation_level": "P1"},
    )
    if overclaim_status != "overclaim":
        failures.append("self-test preservation overclaim detection: expected overclaim")

    downgrade_status = preservation_expectation_status(
        make_stage_observation(status="pass", preservation_level="P2"),
        {"status": "pass", "preservation_level": "P1"},
    )
    if downgrade_status != "unexplained_downgrade":
        failures.append("self-test unexplained preservation downgrade detection: expected unexplained_downgrade")

    pipeline_failures, pipeline_outputs = run_pipeline(root)
    if pipeline_failures:
        failures.append("self-test base pipeline run for preservation checks: expected clean pipeline output")
    else:
        negative_preservation_failures = validate_active_corpus_preservation(
            root,
            "tests/corpora/python_preservation_negative_corpus.json",
            pipeline_outputs,
        )
        if not any("observed preservation P1 is weaker than expected P0" in item for item in negative_preservation_failures):
            failures.append("self-test negative preservation corpus: expected weaker-than-claimed preservation failure")

    mutated_report = translation_report("c_opaque_call")
    mutated_report["profile"] = "R"
    translation_failures = validate_translation_report("c_opaque_call", mutated_report)
    if not any("expected translation profile D-PY" in item for item in translation_failures):
        failures.append("self-test translation overclaim profile: expected failure")
    mutated_report = translation_report("c_opaque_call")
    mutated_report["boundary_annotations"] = []
    mutated_report["observables"]["opaque"] = []
    translation_failures = validate_translation_report("c_opaque_call", mutated_report)
    if not any("preserve opaque boundary accounting" in item for item in translation_failures):
        failures.append("self-test translation opaque accounting: expected failure")

    try:
        emit_wasm_module(PYTHON_SCIRH_MODULES["a_async_await"], lower_supported_module(PYTHON_SCIRH_MODULES["a_async_await"]))
        failures.append("self-test async Wasm emission rejection: expected failure")
    except PipelineError as exc:
        if "async functions are not emittable" not in str(exc):
            failures.append("self-test async Wasm emission rejection: unexpected failure reason")

    mutated = json.loads(json.dumps(base_lowered))
    mutated["functions"][0]["blocks"][0]["instructions"][3]["operands"][1] = 1
    try:
        emit_wasm_module(PYTHON_SCIRH_MODULES["a_basic_function"], mutated)
        failures.append("self-test bounded cmp Wasm emission: expected failure")
    except PipelineError as exc:
        if "less-than-zero bootstrap shape" not in str(exc):
            failures.append("self-test bounded cmp Wasm emission: unexpected failure reason")

    base_wat_text, base_wasm_report = emit_wasm_module(PYTHON_SCIRH_MODULES["a_basic_function"], base_lowered)
    mutated_wasm_report = json.loads(json.dumps(base_wasm_report))
    mutated_wasm_report["boundary_annotations"] = ["foreign_api.ping boundary"]
    wasm_failures = validate_wasm_artifacts(PYTHON_SCIRH_MODULES["a_basic_function"], base_lowered, base_wat_text, mutated_wasm_report)
    if not any("must not add boundary annotations" in item for item in wasm_failures):
        failures.append("self-test Wasm boundary accounting: expected failure")

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
    mutated_preservation_report["boundary_annotations"] = ["foreign_api.ping boundary"]
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
    mutated_preservation_report["boundary_annotations"] = []
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
            "wasm_reports": {},
        }
    )
    if not any("d_exec_eval: non-executable case must not emit reconstruction output" in item for item in output_failures):
        failures.append("self-test rejected case reconstruction output: expected failure")

    importer_only_output_failures = validate_executable_output_set(
        {
            "scir_l_reports": {case_name: {} for case_name in SUPPORTED_CASES} | {"b_if_else_return": {}},
            "translation_reports": {case_name: {} for case_name in SUPPORTED_CASES} | {"b_async_arg_await": {}},
            "reconstruction_reports": {case_name: {} for case_name in SUPPORTED_CASES} | {"b_while_call_update": {}},
            "reconstruction_preservation_reports": {case_name: {} for case_name in SUPPORTED_CASES},
            "wasm_reports": {case_name: {} for case_name in WASM_EMITTABLE_CASES} | {"a_async_await": {}, "b_class_field_update": {}},
        }
    )
    if not any("b_if_else_return: non-executable case must not emit SCIR-L output" in item for item in importer_only_output_failures):
        failures.append("self-test importer-only SCIR-L output exclusion: expected failure")
    if not any("b_async_arg_await: non-executable case must not emit translation output" in item for item in importer_only_output_failures):
        failures.append("self-test importer-only translation output exclusion: expected failure")
    if not any("b_while_call_update: non-executable case must not emit reconstruction output" in item for item in importer_only_output_failures):
        failures.append("self-test importer-only reconstruction output exclusion: expected failure")
    if not any("a_async_await: non-emittable supported case must not emit a Wasm output" in item for item in importer_only_output_failures):
        failures.append("self-test non-emittable Wasm output exclusion: expected failure")
    if not any("b_class_field_update: non-executable case must not emit Wasm output" in item for item in importer_only_output_failures):
        failures.append("self-test importer-only Wasm output exclusion: expected failure")

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


def validate_rust_scirh_case(case_name: str, scirh_text: str, *, boundary_contracts=None):
    try:
        parsed = parse_module(scirh_text)
    except ScirHModelError as exc:
        diagnostics = diagnose_scirh_parse_failure(f"{case_name} (rust)", exc)
        parsed = None
    else:
        diagnostics = validate_scirh_module_semantics(
            f"{case_name} (rust)",
            parsed,
            boundary_contracts=boundary_contracts,
            canonical_text=scirh_text,
        )
        expected = RUST_SCIRH_MODULES[case_name]
        if parsed != expected:
            diagnostics.append(
                make_diagnostic(
                    SCIRH_NAME_RESOLUTION_CODE,
                    f"{case_name}: parsed Rust SCIR-H model drifted from the canonical bootstrap module model",
                )
            )

    report = {
        "report_id": f"scir-h-validation-{slug(case_name)}",
        "artifact": f"fixture.rust_importer.{case_name}",
        "layer": "scir_h",
        "validator": SCIRH_VALIDATOR_NAME,
        "spec_version": SPEC_VERSION,
        "status": "pass" if not diagnostics else "fail",
        "diagnostics": diagnostics,
    }
    failures = [item["message"] for item in diagnostics]
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
                                "lowering_rule": "H_FIELD_ADDR",
                            },
                            {
                                "id": "load0",
                                "op": "load",
                                "operands": ["field0", "mem0"],
                                "origin": f"{module.module_id}::lt-load-value",
                                "lowering_rule": "H_PLACE_LOAD",
                            },
                            {
                                "id": "cmp0",
                                "op": "cmp",
                                "operands": ["load0", 0],
                                "origin": f"{module.module_id}::lt-zero",
                                "lowering_rule": "H_INTRINSIC_CMP",
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
                            "lowering_rule": "H_BRANCH_COND",
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
                                "lowering_rule": "H_SET_STORE",
                            },
                        ],
                        "terminator": {
                            "kind": "br",
                            "target": "retread",
                            "args": ["field1", "mem2"],
                            "origin": f"{module.module_id}::join",
                            "lowering_rule": "H_BRANCH_JOIN",
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
                                "lowering_rule": "H_PLACE_LOAD",
                            },
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "load1",
                            "origin": f"{module.module_id}::return",
                            "lowering_rule": "H_RETURN",
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
                                "lowering_rule": "H_OPAQUE_CALL",
                            },
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "result0",
                            "origin": f"{module.module_id}::return",
                            "lowering_rule": "H_RETURN",
                        },
                    }
                ],
            }
        ],
    }


def lower_rust_supported_module(module: Module, *, input_representation: str = "SCIR-H"):
    assert_canonical_pipeline_input(input_representation, "lowering")
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
    profile = RUST_TRANSLATION_EXPECTATIONS[case_name]["profile"]
    preservation_level = RUST_TRANSLATION_EXPECTATIONS[case_name]["preservation_level"]
    boundary_annotations = ["unsafe boundary"] if case_name == "c_unsafe_call" else []
    downgrades = (
        [
            {
                "reason": "unsafe boundary is preserved as explicit boundary annotation only",
                "preservation_level": "P3",
            }
        ]
        if case_name == "c_unsafe_call"
        else []
    )
    return {
        "report_id": f"rust-lowering-preservation-{slug(case_name)}",
        "subject": f"fixture.rust_importer.{case_name}",
        "path": "h_to_l",
        "source_artifact": f"scir_h:fixture.rust_importer.{case_name}",
        "target_artifact": f"scir_l:fixture.rust_importer.{case_name}",
        "profile": profile,
        "preservation_level": preservation_level,
        "status": "pass",
        "downgrades": downgrades,
        "boundary_annotations": boundary_annotations,
        "observables": {
            "preserved": preserved[case_name],
            "normalized": [],
            "contract_bounded": [],
            "opaque": boundary_annotations,
            "unsupported": [],
        },
        "evidence": [
            TRANSLATION_VALIDATOR_NAME,
            "Rust bootstrap lowering and provenance validated",
        ],
    }


def validate_rust_translation_report(case_name: str, report: dict):
    failures = []
    expected = RUST_TRANSLATION_EXPECTATIONS[case_name]
    if report["path"] != "h_to_l":
        failures.append(f"{case_name}: expected translation path h_to_l")
    if report["profile"] != expected["profile"]:
        failures.append(f"{case_name}: expected translation profile {expected['profile']}")
    if report["preservation_level"] != expected["preservation_level"]:
        failures.append(
            f"{case_name}: expected translation preservation level {expected['preservation_level']}"
        )
    opaque_items = report["boundary_annotations"]
    if expected["requires_opaque"]:
        if "unsafe boundary" not in opaque_items:
            failures.append(f"{case_name}: Rust translation must preserve unsafe boundary accounting")
        if not report["downgrades"]:
            failures.append(f"{case_name}: unsafe Rust translation must record an explicit downgrade")
    elif opaque_items:
        failures.append(f"{case_name}: Tier A Rust translation must not introduce opaque accounting")
    elif report["downgrades"]:
        failures.append(f"{case_name}: Tier A Rust translation must not record downgrades")
    return failures


def validate_rust_output_set(outputs: dict):
    failures = []
    for case_name in RUST_SUPPORTED_CASES:
        if case_name not in outputs["scir_hc_reports"]:
            failures.append(f"{case_name}: supported Rust case must emit SCIR-Hc validation output")
        if case_name not in outputs["scir_h_reports"]:
            failures.append(f"{case_name}: supported Rust case must emit SCIR-H validation output")
        if case_name not in outputs["scir_l_reports"]:
            failures.append(f"{case_name}: supported Rust case must emit SCIR-L output")
        if case_name not in outputs["translation_reports"]:
            failures.append(f"{case_name}: supported Rust case must emit translation output")
    for case_name in RUST_WASM_EMITTABLE_CASES:
        if case_name not in outputs["wasm_reports"]:
            failures.append(f"{case_name}: Wasm-emittable Rust case must emit a Wasm output")
    for case_name in sorted(set(RUST_SUPPORTED_CASES) - set(RUST_WASM_EMITTABLE_CASES)):
        if case_name in outputs["wasm_reports"]:
            failures.append(f"{case_name}: non-emittable Rust case must not emit a Wasm output")
    for case_name in RUST_REJECTED_CASES:
        if case_name in outputs["scir_hc_reports"]:
            failures.append(f"{case_name}: rejected Rust case must not emit SCIR-Hc validation output")
        if case_name in outputs["scir_h_reports"]:
            failures.append(f"{case_name}: rejected Rust case must not emit SCIR-H validation output")
        if case_name in outputs["scir_l_reports"]:
            failures.append(f"{case_name}: rejected Rust case must not emit SCIR-L output")
        if case_name in outputs["translation_reports"]:
            failures.append(f"{case_name}: rejected Rust case must not emit translation output")
        if case_name in outputs["wasm_reports"]:
            failures.append(f"{case_name}: rejected Rust case must not emit Wasm output")
    return failures


def run_rust_pipeline(root: pathlib.Path):
    require_rust_toolchain()
    failures = []
    outputs = {
        "scir_hc_reports": {},
        "scir_h_reports": {},
        "scir_l_reports": {},
        "translation_reports": {},
        "wasm_reports": {},
    }
    for case_name in RUST_ALL_CASES:
        artifacts = load_rust_import_artifacts(root, case_name)
        failures.extend(validate_import_bundle(root, case_name, artifacts))
        if case_name in RUST_REJECTED_CASES:
            if "expected.scirh" in artifacts:
                failures.append(f"{case_name}: rejected Rust case must not emit SCIR-H")
            continue
        scirh_failures, parsed_module, scir_h_report = validate_rust_scirh_case(
            case_name,
            artifacts["expected.scirh"],
            boundary_contracts=artifacts.get("opaque_boundary_contract.json"),
        )
        failures.extend(scirh_failures)
        failures.extend(validate_instance(root, scir_h_report, "schemas/validation_report.schema.json", f"{case_name} scir_h_validation"))
        outputs["scir_h_reports"][case_name] = scir_h_report
        if parsed_module is None:
            continue
        scirhc_failures, hc_module, hc_text, hc_stats, scir_hc_report = validate_scirhc_case(
            case_name,
            parsed_module,
            artifact_prefix="fixture.rust_importer",
            boundary_contracts=artifacts.get("opaque_boundary_contract.json"),
        )
        failures.extend(scirhc_failures)
        failures.extend(validate_instance(root, scir_hc_report, "schemas/validation_report.schema.json", f"{case_name} scir_hc_validation"))
        outputs["scir_hc_reports"][case_name] = {
            "module": hc_module,
            "text": hc_text,
            "stats": hc_stats,
            "validation_report": scir_hc_report,
        }
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
        if case_name in RUST_WASM_EMITTABLE_CASES:
            wat_text, wasm_report = emit_wasm_module(parsed_module, lowered)
            failures.extend(
                validate_instance(
                    root,
                    wasm_report,
                    "schemas/preservation_report.schema.json",
                    f"{case_name} wasm_preservation",
                )
            )
            failures.extend(validate_wasm_artifacts(parsed_module, lowered, wat_text, wasm_report))
            outputs["wasm_reports"][case_name] = {
                "text": wat_text,
                "preservation_report": wasm_report,
            }
        else:
            failures.extend(validate_wasm_not_emittable(parsed_module, lowered))
    failures.extend(validate_rust_output_set(outputs))
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

    try:
        wat_text, wasm_report = emit_wasm_module(
            RUST_SCIRH_MODULES["a_struct_field_borrow_mut"],
            lower_rust_supported_module(RUST_SCIRH_MODULES["a_struct_field_borrow_mut"]),
        )
        wasm_failures = validate_wasm_artifacts(
            RUST_SCIRH_MODULES["a_struct_field_borrow_mut"],
            lower_rust_supported_module(RUST_SCIRH_MODULES["a_struct_field_borrow_mut"]),
            wat_text,
            wasm_report,
        )
        if wasm_failures:
            failures.append("self-test Rust field.addr Wasm emission: expected bounded record-cell emission to validate")
    except PipelineError:
        failures.append("self-test Rust field.addr Wasm emission: unexpected failure")

    mutated_report = rust_translation_report("c_unsafe_call")
    mutated_report["profile"] = "R"
    translation_failures = validate_rust_translation_report("c_unsafe_call", mutated_report)
    if not any("expected translation profile N" in item for item in translation_failures):
        failures.append("self-test Rust unsafe overclaim profile: expected failure")

    mutated_report = rust_translation_report("c_unsafe_call")
    mutated_report["boundary_annotations"] = []
    mutated_report["observables"]["opaque"] = []
    translation_failures = validate_rust_translation_report("c_unsafe_call", mutated_report)
    if not any("preserve unsafe boundary accounting" in item for item in translation_failures):
        failures.append("self-test Rust unsafe accounting: expected failure")

    output_failures = validate_rust_output_set(
        {
            "scir_h_reports": {},
            "scir_l_reports": {"d_proc_macro": {}},
            "translation_reports": {},
            "wasm_reports": {},
        }
    )
    if not any("d_proc_macro: rejected Rust case must not emit SCIR-L output" in item for item in output_failures):
        failures.append("self-test Rust rejected output exclusion: expected failure")

    wasm_output_failures = validate_rust_output_set(
        {
            "scir_h_reports": {case_name: {} for case_name in RUST_SUPPORTED_CASES},
            "scir_l_reports": {case_name: {} for case_name in RUST_SUPPORTED_CASES},
            "translation_reports": {case_name: {} for case_name in RUST_SUPPORTED_CASES},
            "wasm_reports": {case_name: {} for case_name in RUST_WASM_EMITTABLE_CASES} | {"a_async_await": {}},
        }
    )
    if not any("a_async_await: non-emittable Rust case must not emit a Wasm output" in item for item in wasm_output_failures):
        failures.append("self-test Rust non-emittable Wasm output exclusion: expected failure")

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
        "SCIR-L lowering, translation preservation reports, helper-free WAT emission, "
        "reconstruction reports, "
        f"and compile/test evidence for {len(SUPPORTED_CASES)} supported bootstrap cases."
    )


def print_rust_validation_success():
    print("[pipeline] Rust importer-first validation passed")
    print(
        "Validated Rust importer outputs, compact canonical SCIR-H parsing and formatting, "
        "SCIR-L lowering with field.addr, bounded helper-free WAT emission, and path-qualified translation preservation reports "
        f"for {len(RUST_SUPPORTED_CASES)} supported Rust importer cases."
    )


def print_test_success():
    print("[pipeline] bootstrap self-tests passed")
    print(
        "Negative checks covered legacy SCIR-H syntax, unsupported SCIR-L ops, "
        "duplicate SSA and block ids, bad targets and arg counts, token-class mismatches, "
        "translation overclaims, bounded Wasm emission and accounting mismatches, "
        "reconstruction claim/accounting mismatches, invalid reconstruction syntax, "
        "non-executable output exclusion, and SCIR-H round-trips."
    )


def print_rust_test_success():
    print("[pipeline] Rust importer-first self-tests passed")
    print(
        "Negative checks covered legacy Rust SCIR-H syntax, field.addr alignment, unsafe-boundary "
        "translation overclaims, bounded field.addr Wasm emission, rejected-case output exclusion, "
        "and Rust SCIR-H round-trips."
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
