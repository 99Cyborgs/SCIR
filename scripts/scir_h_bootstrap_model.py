#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MODULE_ID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
REFERENCE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:.]*$")
TYPE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_<>]*$")
EFFECT_RE = re.compile(r"^![A-Za-z_,]*$")
INTRINSIC_OPS = ("lt", "le", "eq", "ne", "gt", "ge")
SCIRHC_AUTHORITY_BOUNDARY = "DERIVED_ONLY"

SCIR_H_KERNEL_METADATA = {
    "constructs": (
        {
            "construct": "module header",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "n/a",
                "reconstruction": "yes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept as canonical root form",
            },
        },
        {
            "construct": "`import sym`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "importer-specific only",
                "reconstruction": "n/a",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "`import type`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "n/a",
                "reconstruction": "n/a",
                "tests": "minimal",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "record `type` declaration",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "partial",
                "reconstruction": "Python and Rust surface only",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "plain `fn`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "`async fn`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes for Python subset",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "`var`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "`set` local place",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "`set` field place",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes for bounded record-like shapes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "`return`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "`if` / `else`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "Python proof loop yes; broader cases no",
                "reconstruction": "Python subset yes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept with subset-bound lowering",
            },
        },
        {
            "construct": "`loop`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "canonical parser/validator surface only; importer-only beyond that",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "validator-only",
                "lowering": "no",
                "reconstruction": "no",
                "tests": "yes",
                "mvp_status": "canonical parser/validator surface only",
                "action_taken": "kept as importer-only `SCIR-H` surface beyond parser/validator",
            },
        },
        {
            "construct": "`break`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "canonical parser/validator surface only; importer-only beyond that",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "validator-only",
                "lowering": "no",
                "reconstruction": "no",
                "tests": "yes",
                "mvp_status": "canonical parser/validator surface only",
                "action_taken": "kept as importer-only `SCIR-H` surface beyond parser/validator",
            },
        },
        {
            "construct": "`continue`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "canonical parser/validator surface only; importer-only beyond that",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "validator-only",
                "lowering": "no",
                "reconstruction": "no",
                "tests": "yes",
                "mvp_status": "canonical parser/validator surface only",
                "action_taken": "kept as importer-only `SCIR-H` surface beyond parser/validator",
            },
        },
        {
            "construct": "single-handler `try` / `catch name Type`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "canonical parser/validator surface only; importer-only beyond that",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "validator-only",
                "lowering": "no",
                "reconstruction": "no",
                "tests": "yes",
                "mvp_status": "canonical parser/validator surface only",
                "action_taken": "kept as importer-only `SCIR-H` surface beyond parser/validator",
            },
        },
        {
            "construct": "direct call `f(args)`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "subset-bound yes",
                "reconstruction": "yes for Python subset",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "`await`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes for Python subset",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "intrinsic scalar comparison",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "explicit field place `a.b`",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "fully supported in MVP",
            "checklist": {
                "grammar": "yes",
                "parser": "yes",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "yes for bounded record-like shapes",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept",
            },
        },
        {
            "construct": "opaque or unsafe boundary call",
            "spec_canonical_parser_formatter": "yes",
            "spec_downstream_status": "boundary-only importer surface; executable evidence remains subset-bound",
            "checklist": {
                "grammar": "yes",
                "parser": "importer-emitted only",
                "validator": "yes",
                "lowering": "yes",
                "reconstruction": "Python opaque case only",
                "tests": "yes",
                "mvp_status": "fully supported in MVP",
                "action_taken": "kept as boundary-only surface",
            },
        },
    ),
    "identity_model_required_markers": (
        "semantic lineage identity must not include spec version",
        "semantic lineage identity must not include pretty-view text or formatting",
        "semantic lineage identity must remain stable across formatting-only changes",
        "semantic lineage identity must remain stable across declaration reordering absorbed by semantic canonicalization",
        "canonical content hash must be derived only from canonical storage",
        "revision-scoped node identity must vary when the revision tag changes",
    ),
}


class ScirHModelError(Exception):
    pass


class CompressionOrigin(str, Enum):
    INFERRED_TYPE = "INFERRED_TYPE"
    INFERRED_EFFECT = "INFERRED_EFFECT"
    REDUNDANT_CAPABILITY = "REDUNDANT_CAPABILITY"
    OWNERSHIP_ELISION = "OWNERSHIP_ELISION"


COMPRESSION_ORIGIN_SERIALIZATION_ORDER = (
    CompressionOrigin.INFERRED_TYPE,
    CompressionOrigin.INFERRED_EFFECT,
    CompressionOrigin.REDUNDANT_CAPABILITY,
    CompressionOrigin.OWNERSHIP_ELISION,
)
COMPRESSION_ORIGIN_CODES = {
    CompressionOrigin.INFERRED_TYPE: "T",
    CompressionOrigin.INFERRED_EFFECT: "E",
    CompressionOrigin.REDUNDANT_CAPABILITY: "C",
    CompressionOrigin.OWNERSHIP_ELISION: "O",
}
COMPRESSION_ORIGIN_FROM_CODE = {
    code: origin for origin, code in COMPRESSION_ORIGIN_CODES.items()
}


@dataclass(frozen=True)
class Param:
    name: str
    type_name: str


@dataclass(frozen=True)
class ImportDecl:
    kind: str
    local_id: str
    ref: str


@dataclass(frozen=True)
class FieldType:
    name: str
    type_name: str


@dataclass(frozen=True)
class RecordType:
    fields: tuple[FieldType, ...]


@dataclass(frozen=True)
class TypeDecl:
    name: str
    type_expr: object


@dataclass(frozen=True)
class NamePlace:
    name: str


@dataclass(frozen=True)
class FieldPlace:
    base: object
    field: str


@dataclass(frozen=True)
class NameExpr:
    name: str


@dataclass(frozen=True)
class PlaceExpr:
    place: object


@dataclass(frozen=True)
class IntExpr:
    value: int


@dataclass(frozen=True)
class CallExpr:
    callee: str
    args: tuple[object, ...]


@dataclass(frozen=True)
class AwaitExpr:
    value: object


@dataclass(frozen=True)
class IntrinsicExpr:
    op: str
    args: tuple[object, object]


@dataclass(frozen=True)
class VarDecl:
    name: str
    type_name: str
    value: object


@dataclass(frozen=True)
class SetStmt:
    target: object
    value: object


@dataclass(frozen=True)
class ReturnStmt:
    value: object


@dataclass(frozen=True)
class IfStmt:
    condition: object
    then_body: tuple[object, ...]
    else_body: tuple[object, ...]


@dataclass(frozen=True)
class LoopStmt:
    loop_id: str
    body: tuple[object, ...]


@dataclass(frozen=True)
class BreakStmt:
    loop_id: str


@dataclass(frozen=True)
class ContinueStmt:
    loop_id: str


@dataclass(frozen=True)
class TryStmt:
    try_body: tuple[object, ...]
    catch_name: str
    catch_type: str
    catch_body: tuple[object, ...]


@dataclass(frozen=True)
class FunctionDecl:
    name: str
    params: tuple[Param, ...]
    return_type: str
    effects: tuple[str, ...]
    body: tuple[object, ...]
    is_async: bool = False


@dataclass(frozen=True)
class Module:
    module_id: str
    imports: tuple[ImportDecl, ...]
    type_decls: tuple[TypeDecl, ...]
    functions: tuple[FunctionDecl, ...]


@dataclass(frozen=True)
class HcVarDecl:
    name: str
    type_name: str | None
    value: object
    compression_origin: tuple[CompressionOrigin, ...] = ()


@dataclass(frozen=True)
class HcFunctionDecl:
    name: str
    params: tuple[Param, ...]
    return_type: str | None
    effects: tuple[str, ...] | None
    body: tuple[object, ...]
    compression_origin: tuple[CompressionOrigin, ...] = ()
    is_async: bool = False


@dataclass(frozen=True)
class HcModule:
    module_id: str
    imports: tuple[ImportDecl, ...]
    type_decls: tuple[TypeDecl, ...]
    functions: tuple[HcFunctionDecl, ...]
    authority_boundary: str = SCIRHC_AUTHORITY_BOUNDARY
    compression_origin: tuple[CompressionOrigin, ...] = ()


def expect_identifier(value: str, label: str):
    if not IDENTIFIER_RE.match(value):
        raise ScirHModelError(f"invalid {label}: {value!r}")


def expect_type_name(value: str, label: str):
    if not TYPE_RE.match(value):
        raise ScirHModelError(f"invalid {label}: {value!r}")


def normalize_compression_origins(origins) -> tuple[CompressionOrigin, ...]:
    if origins in (None, ()):
        return ()
    if isinstance(origins, (CompressionOrigin, str)):
        origins = (origins,)
    normalized = set()
    for item in origins:
        try:
            origin = item if isinstance(item, CompressionOrigin) else CompressionOrigin(item)
        except ValueError as exc:
            raise ScirHModelError(f"invalid compression origin: {item!r}") from exc
        normalized.add(origin)
    return tuple(origin for origin in COMPRESSION_ORIGIN_SERIALIZATION_ORDER if origin in normalized)


def carries_ownership_type(type_name: str | None) -> bool:
    return isinstance(type_name, str) and (
        type_name.startswith("borrow<")
        or type_name.startswith("borrow_mut<")
        or type_name.startswith("opaque<")
    )


def format_compression_origin_fragment(origins) -> str:
    normalized = normalize_compression_origins(origins)
    if not normalized:
        return ""
    return " ~" + "".join(COMPRESSION_ORIGIN_CODES[origin] for origin in normalized)


def parse_compression_origin_codes(code_text: str) -> tuple[CompressionOrigin, ...]:
    if not code_text:
        raise ScirHModelError("compression-origin suffix must not be empty")
    origins = []
    for code in code_text:
        origin = COMPRESSION_ORIGIN_FROM_CODE.get(code)
        if origin is None:
            raise ScirHModelError(f"invalid compression-origin code: {code!r}")
        origins.append(origin)
    return normalize_compression_origins(origins)


def split_compression_origin_suffix(text: str) -> tuple[str, tuple[CompressionOrigin, ...]]:
    if " ~" not in text:
        return text, ()
    base, suffix = text.rsplit(" ~", 1)
    return base, parse_compression_origin_codes(suffix.strip())


def normalize_effects(effects: tuple[str, ...]) -> tuple[str, ...]:
    normalized = tuple(sorted(dict.fromkeys(effects)))
    for effect in normalized:
        expect_identifier(effect, "effect")
    return normalized


def normalize_place(place):
    if isinstance(place, str):
        expect_identifier(place, "assignment target")
        return NamePlace(place)
    if isinstance(place, NamePlace):
        expect_identifier(place.name, "place")
        return place
    if isinstance(place, FieldPlace):
        return FieldPlace(normalize_place(place.base), _normalize_field_name(place.field))
    raise ScirHModelError(f"unsupported place node: {type(place).__name__}")


def format_place(place) -> str:
    place = normalize_place(place)
    if isinstance(place, NamePlace):
        return place.name
    if isinstance(place, FieldPlace):
        return f"{format_place(place.base)}.{place.field}"
    raise ScirHModelError(f"unsupported place node: {type(place).__name__}")


def parse_place(text: str):
    parts = text.split(".")
    if not parts or any(not part for part in parts):
        raise ScirHModelError(f"invalid place: {text!r}")
    place = NamePlace(parts[0])
    for field in parts[1:]:
        place = FieldPlace(place, field)
    return normalize_place(place)


def normalize_expr(expr):
    if isinstance(expr, NameExpr):
        expect_identifier(expr.name, "name expression")
        return expr
    if isinstance(expr, PlaceExpr):
        return PlaceExpr(normalize_place(expr.place))
    if isinstance(expr, IntExpr):
        return expr
    if isinstance(expr, CallExpr):
        expect_identifier(expr.callee, "call callee")
        return CallExpr(expr.callee, tuple(normalize_expr(arg) for arg in expr.args))
    if isinstance(expr, AwaitExpr):
        return AwaitExpr(normalize_expr(expr.value))
    if isinstance(expr, IntrinsicExpr):
        if expr.op not in INTRINSIC_OPS:
            raise ScirHModelError(f"unsupported intrinsic op: {expr.op!r}")
        return IntrinsicExpr(expr.op, tuple(normalize_expr(arg) for arg in expr.args))
    raise ScirHModelError(f"unsupported expression node: {type(expr).__name__}")


def normalize_stmt(stmt):
    if isinstance(stmt, VarDecl):
        expect_identifier(stmt.name, "mutable local")
        expect_type_name(stmt.type_name, "mutable local type")
        return VarDecl(stmt.name, stmt.type_name, normalize_expr(stmt.value))
    if isinstance(stmt, SetStmt):
        return SetStmt(normalize_place(stmt.target), normalize_expr(stmt.value))
    if isinstance(stmt, ReturnStmt):
        return ReturnStmt(normalize_expr(stmt.value))
    if isinstance(stmt, IfStmt):
        return IfStmt(
            normalize_expr(stmt.condition),
            tuple(normalize_stmt(item) for item in stmt.then_body),
            tuple(normalize_stmt(item) for item in stmt.else_body),
        )
    if isinstance(stmt, LoopStmt):
        expect_identifier(stmt.loop_id, "loop id")
        return LoopStmt(stmt.loop_id, tuple(normalize_stmt(item) for item in stmt.body))
    if isinstance(stmt, BreakStmt):
        expect_identifier(stmt.loop_id, "break loop id")
        return stmt
    if isinstance(stmt, ContinueStmt):
        expect_identifier(stmt.loop_id, "continue loop id")
        return stmt
    if isinstance(stmt, TryStmt):
        expect_identifier(stmt.catch_name, "catch binder")
        expect_type_name(stmt.catch_type, "catch type")
        return TryStmt(
            tuple(normalize_stmt(item) for item in stmt.try_body),
            stmt.catch_name,
            stmt.catch_type,
            tuple(normalize_stmt(item) for item in stmt.catch_body),
        )
    raise ScirHModelError(f"unsupported statement node: {type(stmt).__name__}")


def _normalize_field_name(value: str) -> str:
    expect_identifier(value, "record field")
    return value


def normalize_field_type(field: FieldType) -> FieldType:
    return FieldType(_normalize_field_name(field.name), _normalize_type_atom(field.type_name))


def _normalize_type_atom(value: str) -> str:
    expect_type_name(value, "type")
    return value


def normalize_type_expr(type_expr):
    if isinstance(type_expr, str):
        return _normalize_type_atom(type_expr)
    if isinstance(type_expr, RecordType):
        fields = tuple(normalize_field_type(field) for field in type_expr.fields)
        if not fields:
            raise ScirHModelError("record type must have at least one field")
        return RecordType(fields)
    raise ScirHModelError(f"unsupported type expression node: {type(type_expr).__name__}")


def format_type_expr(type_expr) -> str:
    type_expr = normalize_type_expr(type_expr)
    if isinstance(type_expr, str):
        return type_expr
    if isinstance(type_expr, RecordType):
        inner = " ".join(f"{field.name} {field.type_name}" for field in type_expr.fields)
        return f"record {{ {inner} }}"
    raise ScirHModelError(f"unsupported type expression node: {type(type_expr).__name__}")


def normalize_module(module: Module) -> Module:
    if not MODULE_ID_RE.match(module.module_id):
        raise ScirHModelError(f"invalid module id: {module.module_id!r}")

    imports = []
    for item in module.imports:
        if item.kind not in {"sym", "type"}:
            raise ScirHModelError(f"unsupported import kind: {item.kind!r}")
        expect_identifier(item.local_id, "import local id")
        if not REFERENCE_RE.match(item.ref):
            raise ScirHModelError(f"invalid import reference: {item.ref!r}")
        imports.append(item)
    imports = tuple(sorted(imports, key=lambda item: (item.kind, item.local_id, item.ref)))

    seen_types = set()
    type_decls = []
    for type_decl in module.type_decls:
        expect_identifier(type_decl.name, "type name")
        if type_decl.name in seen_types:
            raise ScirHModelError(f"duplicate type declaration: {type_decl.name!r}")
        seen_types.add(type_decl.name)
        type_decls.append(TypeDecl(type_decl.name, normalize_type_expr(type_decl.type_expr)))

    functions = []
    seen_functions = set()
    for function in module.functions:
        expect_identifier(function.name, "function name")
        if function.name in seen_functions:
            raise ScirHModelError(f"duplicate function declaration: {function.name!r}")
        seen_functions.add(function.name)
        params = []
        for param in function.params:
            expect_identifier(param.name, "parameter name")
            expect_type_name(param.type_name, "parameter type")
            params.append(param)
        expect_type_name(function.return_type, "return type")
        functions.append(
            FunctionDecl(
                name=function.name,
                params=tuple(params),
                return_type=function.return_type,
                effects=normalize_effects(function.effects),
                body=tuple(normalize_stmt(item) for item in function.body),
                is_async=function.is_async,
            )
        )
    return Module(
        module_id=module.module_id,
        imports=imports,
        type_decls=tuple(type_decls),
        functions=tuple(functions),
    )


def format_effects(effects: tuple[str, ...]) -> str:
    normalized = normalize_effects(effects)
    if not normalized:
        return "!"
    return "!" + ",".join(normalized)


def format_expr(expr) -> str:
    expr = normalize_expr(expr)
    if isinstance(expr, NameExpr):
        return expr.name
    if isinstance(expr, PlaceExpr):
        return format_place(expr.place)
    if isinstance(expr, IntExpr):
        return str(expr.value)
    if isinstance(expr, CallExpr):
        args = ", ".join(format_expr(arg) for arg in expr.args)
        return f"{expr.callee}({args})"
    if isinstance(expr, AwaitExpr):
        return f"await {format_expr(expr.value)}"
    if isinstance(expr, IntrinsicExpr):
        return f"{expr.op} {' '.join(format_expr(arg) for arg in expr.args)}"
    raise ScirHModelError(f"unsupported expression node: {type(expr).__name__}")


def format_stmt(stmt, indent: int) -> list[str]:
    prefix = " " * indent
    stmt = normalize_stmt(stmt)
    if isinstance(stmt, VarDecl):
        return [f"{prefix}var {stmt.name} {stmt.type_name} {format_expr(stmt.value)}"]
    if isinstance(stmt, SetStmt):
        return [f"{prefix}set {format_place(stmt.target)} {format_expr(stmt.value)}"]
    if isinstance(stmt, ReturnStmt):
        return [f"{prefix}return {format_expr(stmt.value)}"]
    if isinstance(stmt, IfStmt):
        lines = [f"{prefix}if {format_expr(stmt.condition)}"]
        for item in stmt.then_body:
            lines.extend(format_stmt(item, indent + 2))
        if stmt.else_body:
            lines.append(f"{prefix}else")
            for item in stmt.else_body:
                lines.extend(format_stmt(item, indent + 2))
        return lines
    if isinstance(stmt, LoopStmt):
        lines = [f"{prefix}loop {stmt.loop_id}"]
        for item in stmt.body:
            lines.extend(format_stmt(item, indent + 2))
        return lines
    if isinstance(stmt, BreakStmt):
        return [f"{prefix}break {stmt.loop_id}"]
    if isinstance(stmt, ContinueStmt):
        return [f"{prefix}continue {stmt.loop_id}"]
    if isinstance(stmt, TryStmt):
        lines = [f"{prefix}try"]
        for item in stmt.try_body:
            lines.extend(format_stmt(item, indent + 2))
        lines.append(f"{prefix}catch {stmt.catch_name} {stmt.catch_type}")
        for item in stmt.catch_body:
            lines.extend(format_stmt(item, indent + 2))
        return lines
    raise ScirHModelError(f"unsupported statement node: {type(stmt).__name__}")


def format_function(function: FunctionDecl) -> list[str]:
    function = FunctionDecl(
        name=function.name,
        params=function.params,
        return_type=function.return_type,
        effects=normalize_effects(function.effects),
        body=function.body,
        is_async=function.is_async,
    )
    param_fields = []
    for param in function.params:
        param_fields.extend([param.name, param.type_name])
    header_fields = []
    if function.is_async:
        header_fields.append("async")
    header_fields.extend(
        ["fn", function.name, *param_fields, "->", function.return_type, format_effects(function.effects)]
    )
    lines = [" ".join(header_fields)]
    for stmt in function.body:
        lines.extend(format_stmt(stmt, 2))
    return lines


def format_module(module: Module) -> str:
    module = normalize_module(module)
    lines = [f"module {module.module_id}"]
    for item in module.imports:
        lines.append(f"import {item.kind} {item.local_id} {item.ref}")

    top_level_chunks: list[list[str]] = []
    for type_decl in module.type_decls:
        top_level_chunks.append([f"type {type_decl.name} {format_type_expr(type_decl.type_expr)}"])
    for function in module.functions:
        top_level_chunks.append(format_function(function))

    if module.imports and top_level_chunks:
        lines.append("")
    for index, chunk in enumerate(top_level_chunks):
        if index:
            lines.append("")
        lines.extend(chunk)
    return "\n".join(lines) + "\n"


def split_indent(line: str) -> tuple[int, str]:
    if "\t" in line:
        raise ScirHModelError("tabs are not valid in canonical SCIR-H")
    leading = len(line) - len(line.lstrip(" "))
    if leading % 2:
        raise ScirHModelError(f"indentation must use two-space steps: {line!r}")
    return leading, line[leading:]


def parse_effects(token: str) -> tuple[str, ...]:
    if not EFFECT_RE.match(token):
        raise ScirHModelError(f"invalid effect row: {token!r}")
    if token == "!":
        return ()
    effects = tuple(part for part in token[1:].split(",") if part)
    return normalize_effects(effects)


def parse_atomic_expr(text: str):
    if re.fullmatch(r"-?\d+", text):
        return IntExpr(int(text))
    if "." in text:
        return PlaceExpr(parse_place(text))
    expect_identifier(text, "expression atom")
    return NameExpr(text)


def split_call_args(inner: str) -> list[str]:
    inner = inner.strip()
    if not inner:
        return []
    return [part.strip() for part in inner.split(",")]


def parse_expr(text: str):
    text = text.strip()
    if not text:
        raise ScirHModelError("missing expression")
    if text.startswith("await "):
        return AwaitExpr(parse_expr(text[6:]))
    call_match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\((.*)\)", text)
    if call_match:
        callee = call_match.group(1)
        args = tuple(parse_expr(part) for part in split_call_args(call_match.group(2)))
        return CallExpr(callee, args)
    pieces = text.split()
    if pieces[0] in INTRINSIC_OPS:
        if len(pieces) != 3:
            raise ScirHModelError(f"intrinsic expression requires two operands: {text!r}")
        return IntrinsicExpr(
            pieces[0],
            (parse_expr(pieces[1]), parse_expr(pieces[2])),
        )
    return parse_atomic_expr(text)


def parse_import(line: str) -> ImportDecl:
    fields = line.split()
    if len(fields) != 4 or fields[0] != "import":
        raise ScirHModelError(f"invalid import line: {line!r}")
    _, kind, local_id, ref = fields
    return ImportDecl(kind=kind, local_id=local_id, ref=ref)


def parse_record_type(text: str) -> RecordType:
    if not (text.startswith("record {") and text.endswith("}")):
        raise ScirHModelError(f"invalid record type: {text!r}")
    inner = text[len("record {") : -1].strip()
    if not inner:
        raise ScirHModelError("record type must contain at least one field")
    parts = inner.split()
    if len(parts) % 2:
        raise ScirHModelError(f"record type fields must appear as name/type pairs: {text!r}")
    fields = []
    for index in range(0, len(parts), 2):
        fields.append(FieldType(parts[index], parts[index + 1]))
    return RecordType(tuple(fields))


def parse_type_expr(text: str):
    text = text.strip()
    if text.startswith("record {"):
        return parse_record_type(text)
    expect_type_name(text, "type expression")
    return text


def parse_type_decl(line: str) -> TypeDecl:
    fields = line.split(maxsplit=2)
    if len(fields) != 3 or fields[0] != "type":
        raise ScirHModelError(f"invalid type declaration: {line!r}")
    return TypeDecl(name=fields[1], type_expr=parse_type_expr(fields[2]))


def parse_function_header(line: str) -> FunctionDecl:
    fields = line.split()
    is_async = False
    if fields[:2] == ["async", "fn"]:
        is_async = True
        fields = fields[2:]
    elif fields[:1] == ["fn"]:
        fields = fields[1:]
    else:
        raise ScirHModelError(f"invalid function header: {line!r}")

    if "->" not in fields:
        raise ScirHModelError(f"function header missing return marker: {line!r}")
    arrow_index = fields.index("->")
    if arrow_index < 1:
        raise ScirHModelError(f"function header missing function name: {line!r}")
    if len(fields) != arrow_index + 3:
        raise ScirHModelError(f"function header must end with return type and effects: {line!r}")

    name = fields[0]
    param_fields = fields[1:arrow_index]
    if len(param_fields) % 2:
        raise ScirHModelError(f"parameters must appear as name/type pairs: {line!r}")
    params = []
    for index in range(0, len(param_fields), 2):
        params.append(Param(param_fields[index], param_fields[index + 1]))
    return FunctionDecl(
        name=name,
        params=tuple(params),
        return_type=fields[arrow_index + 1],
        effects=parse_effects(fields[arrow_index + 2]),
        body=(),
        is_async=is_async,
    )


def parse_suite(lines: list[str], index: int, indent: int) -> tuple[tuple[object, ...], int]:
    body = []
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            index += 1
            continue
        actual_indent, content = split_indent(raw_line)
        if actual_indent < indent:
            break
        if actual_indent > indent:
            raise ScirHModelError(f"unexpected indentation: {raw_line!r}")
        if content.startswith("var "):
            fields = content.split(maxsplit=3)
            if len(fields) != 4:
                raise ScirHModelError(f"invalid var declaration: {content!r}")
            body.append(VarDecl(fields[1], fields[2], parse_expr(fields[3])))
            index += 1
            continue
        if content.startswith("set "):
            fields = content.split(maxsplit=2)
            if len(fields) != 3:
                raise ScirHModelError(f"invalid assignment: {content!r}")
            body.append(SetStmt(parse_place(fields[1]), parse_expr(fields[2])))
            index += 1
            continue
        if content.startswith("return "):
            body.append(ReturnStmt(parse_expr(content[7:])))
            index += 1
            continue
        if content.startswith("if "):
            condition = parse_expr(content[3:])
            then_body, index = parse_suite(lines, index + 1, indent + 2)
            else_body = ()
            while index < len(lines) and not lines[index].strip():
                index += 1
            if index < len(lines):
                else_indent, else_content = split_indent(lines[index])
                if else_indent == indent and else_content == "else":
                    else_body, index = parse_suite(lines, index + 1, indent + 2)
            body.append(IfStmt(condition, then_body, else_body))
            continue
        if content.startswith("loop "):
            fields = content.split()
            if len(fields) != 2:
                raise ScirHModelError(f"invalid loop statement: {content!r}")
            loop_body, index = parse_suite(lines, index + 1, indent + 2)
            body.append(LoopStmt(fields[1], loop_body))
            continue
        if content.startswith("break "):
            fields = content.split()
            if len(fields) != 2:
                raise ScirHModelError(f"invalid break statement: {content!r}")
            body.append(BreakStmt(fields[1]))
            index += 1
            continue
        if content.startswith("continue "):
            fields = content.split()
            if len(fields) != 2:
                raise ScirHModelError(f"invalid continue statement: {content!r}")
            body.append(ContinueStmt(fields[1]))
            index += 1
            continue
        if content == "try":
            try_body, index = parse_suite(lines, index + 1, indent + 2)
            while index < len(lines) and not lines[index].strip():
                index += 1
            if index >= len(lines):
                raise ScirHModelError("try statement must be followed by catch")
            catch_indent, catch_content = split_indent(lines[index])
            if catch_indent != indent or not catch_content.startswith("catch "):
                raise ScirHModelError(f"invalid catch line: {lines[index]!r}")
            catch_fields = catch_content.split()
            if len(catch_fields) != 3:
                raise ScirHModelError(f"invalid catch line: {catch_content!r}")
            catch_body, index = parse_suite(lines, index + 1, indent + 2)
            body.append(TryStmt(try_body, catch_fields[1], catch_fields[2], catch_body))
            continue
        if content == "else":
            break
        if content.startswith("catch "):
            break
        raise ScirHModelError(f"unsupported statement: {content!r}")
    return tuple(body), index


def parse_module(text: str) -> Module:
    if not text.endswith("\n"):
        raise ScirHModelError("canonical SCIR-H text must end with a newline")
    raw_lines = text.splitlines()
    if not raw_lines:
        raise ScirHModelError("empty SCIR-H text")
    if any(line != line.rstrip(" ") for line in raw_lines):
        raise ScirHModelError("canonical SCIR-H text must not use trailing spaces")
    while raw_lines and not raw_lines[0].strip():
        raw_lines.pop(0)
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()
    if not raw_lines:
        raise ScirHModelError("empty SCIR-H text")

    header = raw_lines[0]
    if not header.startswith("module "):
        raise ScirHModelError(f"invalid module header: {header!r}")
    module_id = header.split(" ", 1)[1]
    if " " in module_id:
        raise ScirHModelError(f"invalid module id: {module_id!r}")

    imports = []
    type_decls = []
    functions = []
    index = 1
    while index < len(raw_lines):
        line = raw_lines[index]
        if not line.strip():
            index += 1
            continue
        indent, content = split_indent(line)
        if indent != 0:
            raise ScirHModelError(f"top-level declarations must not be indented: {line!r}")
        if content.startswith("import "):
            imports.append(parse_import(content))
            index += 1
            continue
        if content.startswith("type "):
            type_decls.append(parse_type_decl(content))
            index += 1
            continue
        if content.startswith("fn ") or content.startswith("async fn "):
            function = parse_function_header(content)
            body, index = parse_suite(raw_lines, index + 1, 2)
            functions.append(
                FunctionDecl(
                    name=function.name,
                    params=function.params,
                    return_type=function.return_type,
                    effects=function.effects,
                    body=body,
                    is_async=function.is_async,
                )
            )
            continue
        raise ScirHModelError(f"unsupported top-level declaration: {content!r}")
    return normalize_module(
        Module(
            module_id=module_id,
            imports=tuple(imports),
            type_decls=tuple(type_decls),
            functions=tuple(functions),
        )
    )


def normalize_hc_stmt(stmt):
    if isinstance(stmt, HcVarDecl):
        expect_identifier(stmt.name, "compressed mutable local")
        if stmt.type_name is not None:
            expect_type_name(stmt.type_name, "compressed mutable local type")
        origins = normalize_compression_origins(stmt.compression_origin)
        allowed_origins = {
            CompressionOrigin.INFERRED_TYPE,
            CompressionOrigin.OWNERSHIP_ELISION,
        }
        if stmt.type_name is None:
            if len(origins) != 1 or origins[0] not in allowed_origins:
                raise ScirHModelError(
                    f"compressed mutable local {stmt.name!r} must explain type elision with exactly one allowed compression origin"
                )
        elif origins:
            raise ScirHModelError(
                f"compressed mutable local {stmt.name!r} must not carry compression-origin metadata when its type remains explicit"
            )
        return HcVarDecl(stmt.name, stmt.type_name, normalize_expr(stmt.value), origins)
    if isinstance(stmt, SetStmt):
        return SetStmt(normalize_place(stmt.target), normalize_expr(stmt.value))
    if isinstance(stmt, ReturnStmt):
        return ReturnStmt(normalize_expr(stmt.value))
    if isinstance(stmt, IfStmt):
        return IfStmt(
            normalize_expr(stmt.condition),
            tuple(normalize_hc_stmt(item) for item in stmt.then_body),
            tuple(normalize_hc_stmt(item) for item in stmt.else_body),
        )
    if isinstance(stmt, LoopStmt):
        expect_identifier(stmt.loop_id, "compressed loop id")
        return LoopStmt(stmt.loop_id, tuple(normalize_hc_stmt(item) for item in stmt.body))
    if isinstance(stmt, BreakStmt):
        expect_identifier(stmt.loop_id, "compressed break loop id")
        return stmt
    if isinstance(stmt, ContinueStmt):
        expect_identifier(stmt.loop_id, "compressed continue loop id")
        return stmt
    if isinstance(stmt, TryStmt):
        expect_identifier(stmt.catch_name, "compressed catch binder")
        expect_type_name(stmt.catch_type, "compressed catch type")
        return TryStmt(
            tuple(normalize_hc_stmt(item) for item in stmt.try_body),
            stmt.catch_name,
            stmt.catch_type,
            tuple(normalize_hc_stmt(item) for item in stmt.catch_body),
        )
    raise ScirHModelError(f"unsupported compressed statement node: {type(stmt).__name__}")


def normalize_hc_module(module: HcModule) -> HcModule:
    if not MODULE_ID_RE.match(module.module_id):
        raise ScirHModelError(f"invalid compressed module id: {module.module_id!r}")
    if module.authority_boundary != SCIRHC_AUTHORITY_BOUNDARY:
        raise ScirHModelError(
            f"compressed module authority boundary must be {SCIRHC_AUTHORITY_BOUNDARY!r}"
        )
    module_origins = normalize_compression_origins(module.compression_origin)
    invalid_module_origins = [
        origin
        for origin in module_origins
        if origin is not CompressionOrigin.REDUNDANT_CAPABILITY
    ]
    if invalid_module_origins:
        raise ScirHModelError(
            "compressed module compression_origin may only contain REDUNDANT_CAPABILITY"
        )

    imports = []
    for item in module.imports:
        if item.kind not in {"sym", "type"}:
            raise ScirHModelError(f"unsupported compressed import kind: {item.kind!r}")
        expect_identifier(item.local_id, "compressed import local id")
        if not REFERENCE_RE.match(item.ref):
            raise ScirHModelError(f"invalid compressed import reference: {item.ref!r}")
        imports.append(item)
    imports = tuple(sorted(imports, key=lambda item: (item.kind, item.local_id, item.ref)))

    seen_types = set()
    type_decls = []
    for type_decl in module.type_decls:
        expect_identifier(type_decl.name, "compressed type name")
        if type_decl.name in seen_types:
            raise ScirHModelError(f"duplicate compressed type declaration: {type_decl.name!r}")
        seen_types.add(type_decl.name)
        type_decls.append(TypeDecl(type_decl.name, normalize_type_expr(type_decl.type_expr)))

    seen_functions = set()
    functions = []
    for function in module.functions:
        expect_identifier(function.name, "compressed function name")
        if function.name in seen_functions:
            raise ScirHModelError(f"duplicate compressed function declaration: {function.name!r}")
        seen_functions.add(function.name)
        params = []
        for param in function.params:
            expect_identifier(param.name, "compressed parameter name")
            expect_type_name(param.type_name, "compressed parameter type")
            params.append(param)
        if function.return_type is not None:
            expect_type_name(function.return_type, "compressed return type")
        effects = None if function.effects is None else normalize_effects(function.effects)
        origins = normalize_compression_origins(function.compression_origin)
        has_type_elision = function.return_type is None
        has_effect_elision = effects is None
        type_origins = {
            CompressionOrigin.INFERRED_TYPE,
            CompressionOrigin.OWNERSHIP_ELISION,
        }
        used_type_origins = [origin for origin in origins if origin in type_origins]
        if has_type_elision:
            if len(used_type_origins) != 1:
                raise ScirHModelError(
                    f"compressed function {function.name!r} must explain return-type elision with exactly one type-related compression origin"
                )
        elif used_type_origins:
            raise ScirHModelError(
                f"compressed function {function.name!r} must not carry return-type compression metadata when its return type remains explicit"
            )
        if has_effect_elision and CompressionOrigin.INFERRED_EFFECT not in origins:
            raise ScirHModelError(
                f"compressed function {function.name!r} must explain effect-row elision with INFERRED_EFFECT"
            )
        if not has_effect_elision and CompressionOrigin.INFERRED_EFFECT in origins:
            raise ScirHModelError(
                f"compressed function {function.name!r} must not carry effect compression metadata when its effects remain explicit"
            )
        invalid_function_origins = [
            origin
            for origin in origins
            if origin not in type_origins | {CompressionOrigin.INFERRED_EFFECT}
        ]
        if invalid_function_origins:
            raise ScirHModelError(
                f"compressed function {function.name!r} uses unsupported compression-origin metadata"
            )
        functions.append(
            HcFunctionDecl(
                name=function.name,
                params=tuple(params),
                return_type=function.return_type,
                effects=effects,
                body=tuple(normalize_hc_stmt(item) for item in function.body),
                compression_origin=origins,
                is_async=function.is_async,
            )
        )
    return HcModule(
        module_id=module.module_id,
        imports=imports,
        type_decls=tuple(type_decls),
        functions=tuple(functions),
        authority_boundary=SCIRHC_AUTHORITY_BOUNDARY,
        compression_origin=module_origins,
    )


def format_hc_type_expr(type_expr) -> str:
    type_expr = normalize_type_expr(type_expr)
    if isinstance(type_expr, str):
        return type_expr
    if isinstance(type_expr, RecordType):
        return "{" + ",".join(f"{field.name}:{field.type_name}" for field in type_expr.fields) + "}"
    raise ScirHModelError(f"unsupported compressed type expression node: {type(type_expr).__name__}")


def parse_hc_type_expr(text: str):
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        if not inner:
            raise ScirHModelError("compressed record type must contain at least one field")
        fields = []
        for item in inner.split(","):
            if ":" not in item:
                raise ScirHModelError(f"invalid compressed record field: {item!r}")
            field_name, field_type = item.split(":", 1)
            fields.append(FieldType(field_name.strip(), field_type.strip()))
        return RecordType(tuple(fields))
    return parse_type_expr(text)


def format_hc_expr(expr) -> str:
    expr = normalize_expr(expr)
    if isinstance(expr, AwaitExpr):
        return "@" + format_hc_expr(expr.value)
    return format_expr(expr)


def parse_hc_expr(text: str):
    text = text.strip()
    if not text:
        raise ScirHModelError("missing compressed expression")
    if text.startswith("@"):
        return AwaitExpr(parse_hc_expr(text[1:]))
    return parse_expr(text)


def format_hc_stmt(stmt, indent: int) -> list[str]:
    prefix = " " * indent
    stmt = normalize_hc_stmt(stmt)
    if isinstance(stmt, HcVarDecl):
        type_suffix = f":{stmt.type_name}" if stmt.type_name is not None else ""
        return [
            f"{prefix}v {stmt.name}{type_suffix}={format_hc_expr(stmt.value)}"
            f"{format_compression_origin_fragment(stmt.compression_origin)}"
        ]
    if isinstance(stmt, SetStmt):
        return [f"{prefix}s {format_place(stmt.target)}={format_hc_expr(stmt.value)}"]
    if isinstance(stmt, ReturnStmt):
        return [f"{prefix}r {format_hc_expr(stmt.value)}"]
    if isinstance(stmt, IfStmt):
        lines = [f"{prefix}? {format_hc_expr(stmt.condition)}"]
        for item in stmt.then_body:
            lines.extend(format_hc_stmt(item, indent + 2))
        if stmt.else_body:
            lines.append(f"{prefix}else")
            for item in stmt.else_body:
                lines.extend(format_hc_stmt(item, indent + 2))
        return lines
    if isinstance(stmt, LoopStmt):
        lines = [f"{prefix}l {stmt.loop_id}"]
        for item in stmt.body:
            lines.extend(format_hc_stmt(item, indent + 2))
        return lines
    if isinstance(stmt, BreakStmt):
        return [f"{prefix}b {stmt.loop_id}"]
    if isinstance(stmt, ContinueStmt):
        return [f"{prefix}c {stmt.loop_id}"]
    if isinstance(stmt, TryStmt):
        lines = [f"{prefix}try"]
        for item in stmt.try_body:
            lines.extend(format_hc_stmt(item, indent + 2))
        lines.append(f"{prefix}catch {stmt.catch_name}:{stmt.catch_type}")
        for item in stmt.catch_body:
            lines.extend(format_hc_stmt(item, indent + 2))
        return lines
    raise ScirHModelError(f"unsupported compressed statement node: {type(stmt).__name__}")


def format_hc_function(function: HcFunctionDecl) -> list[str]:
    function = normalize_hc_module(
        HcModule(module_id="compressed.placeholder", imports=(), type_decls=(), functions=(function,))
    ).functions[0]
    params = ",".join(f"{param.name}:{param.type_name}" for param in function.params)
    header = f"{'af' if function.is_async else 'f'} {function.name}({params})"
    if function.return_type is not None:
        header += f"->{function.return_type}"
    if function.effects is not None:
        header += f" {format_effects(function.effects)}"
    header += format_compression_origin_fragment(function.compression_origin)
    lines = [header]
    for stmt in function.body:
        lines.extend(format_hc_stmt(stmt, 2))
    return lines


def format_scirhc_module(module: HcModule) -> str:
    module = normalize_hc_module(module)
    header = f"m {module.module_id} ~D"
    if module.compression_origin:
        header += ":" + "".join(COMPRESSION_ORIGIN_CODES[origin] for origin in module.compression_origin)
    lines = [header]
    for item in module.imports:
        lines.append(f"i{item.kind[0]} {item.local_id} {item.ref}")

    top_level_chunks: list[list[str]] = []
    for type_decl in module.type_decls:
        top_level_chunks.append([f"t {type_decl.name} {format_hc_type_expr(type_decl.type_expr)}"])
    for function in module.functions:
        top_level_chunks.append(format_hc_function(function))

    if module.imports and top_level_chunks:
        lines.append("")
    for index, chunk in enumerate(top_level_chunks):
        if index:
            lines.append("")
        lines.extend(chunk)
    return "\n".join(lines) + "\n"


def parse_hc_import(line: str) -> ImportDecl:
    fields = line.split(maxsplit=2)
    if len(fields) != 3 or fields[0] not in {"is", "it"}:
        raise ScirHModelError(f"invalid compressed import line: {line!r}")
    kind = "sym" if fields[0] == "is" else "type"
    return ImportDecl(kind=kind, local_id=fields[1], ref=fields[2])


def parse_hc_type_decl(line: str) -> TypeDecl:
    fields = line.split(maxsplit=2)
    if len(fields) != 3 or fields[0] != "t":
        raise ScirHModelError(f"invalid compressed type declaration: {line!r}")
    return TypeDecl(name=fields[1], type_expr=parse_hc_type_expr(fields[2]))


def parse_hc_params(text: str) -> tuple[Param, ...]:
    text = text.strip()
    if not text:
        return ()
    params = []
    for item in text.split(","):
        if ":" not in item:
            raise ScirHModelError(f"invalid compressed parameter entry: {item!r}")
        name, type_name = item.split(":", 1)
        params.append(Param(name.strip(), type_name.strip()))
    return tuple(params)


def parse_hc_function_header(line: str) -> HcFunctionDecl:
    line, origins = split_compression_origin_suffix(line)
    if line.startswith("af "):
        is_async = True
        remainder = line[3:]
    elif line.startswith("f "):
        is_async = False
        remainder = line[2:]
    else:
        raise ScirHModelError(f"invalid compressed function header: {line!r}")

    if "(" not in remainder or ")" not in remainder:
        raise ScirHModelError(f"invalid compressed function header: {line!r}")
    paren_open = remainder.index("(")
    paren_close = remainder.index(")", paren_open)
    name = remainder[:paren_open].strip()
    params = parse_hc_params(remainder[paren_open + 1 : paren_close])
    suffix = remainder[paren_close + 1 :].strip()
    return_type = None
    effects = None
    if suffix:
        effect_fragment = None
        if " !" in suffix:
            suffix, effect_text = suffix.rsplit(" !", 1)
            effect_fragment = "!" + effect_text
        elif suffix.startswith("!"):
            effect_fragment = suffix
            suffix = ""
        suffix = suffix.strip()
        if suffix:
            if not suffix.startswith("->"):
                raise ScirHModelError(f"invalid compressed function header suffix: {line!r}")
            return_type = suffix[2:].strip() or None
        if effect_fragment is not None:
            effects = parse_effects(effect_fragment)
    return HcFunctionDecl(
        name=name,
        params=params,
        return_type=return_type,
        effects=effects,
        body=(),
        compression_origin=origins,
        is_async=is_async,
    )


def parse_hc_suite(lines: list[str], index: int, indent: int) -> tuple[tuple[object, ...], int]:
    body = []
    while index < len(lines):
        raw_line = lines[index]
        if not raw_line.strip():
            index += 1
            continue
        actual_indent, content = split_indent(raw_line)
        if actual_indent < indent:
            break
        if actual_indent > indent:
            raise ScirHModelError(f"unexpected compressed indentation: {raw_line!r}")
        content, origins = split_compression_origin_suffix(content)
        if content.startswith("v "):
            payload = content[2:]
            if "=" not in payload:
                raise ScirHModelError(f"invalid compressed var declaration: {content!r}")
            left, expr_text = payload.split("=", 1)
            left = left.strip()
            type_name = None
            if ":" in left:
                name, type_name = left.split(":", 1)
                name = name.strip()
                type_name = type_name.strip()
            else:
                name = left
            body.append(HcVarDecl(name, type_name, parse_hc_expr(expr_text), origins))
            index += 1
            continue
        if origins:
            raise ScirHModelError(
                f"compression-origin metadata is only valid on compressed var declarations: {raw_line!r}"
            )
        if content.startswith("s "):
            payload = content[2:]
            if "=" not in payload:
                raise ScirHModelError(f"invalid compressed assignment: {content!r}")
            place_text, expr_text = payload.split("=", 1)
            body.append(SetStmt(parse_place(place_text.strip()), parse_hc_expr(expr_text)))
            index += 1
            continue
        if content.startswith("r "):
            body.append(ReturnStmt(parse_hc_expr(content[2:])))
            index += 1
            continue
        if content.startswith("? "):
            condition = parse_hc_expr(content[2:])
            then_body, index = parse_hc_suite(lines, index + 1, indent + 2)
            else_body = ()
            while index < len(lines) and not lines[index].strip():
                index += 1
            if index < len(lines):
                else_indent, else_content = split_indent(lines[index])
                if else_indent == indent and else_content == "else":
                    else_body, index = parse_hc_suite(lines, index + 1, indent + 2)
            body.append(IfStmt(condition, then_body, else_body))
            continue
        if content.startswith("l "):
            fields = content.split()
            if len(fields) != 2:
                raise ScirHModelError(f"invalid compressed loop statement: {content!r}")
            loop_body, index = parse_hc_suite(lines, index + 1, indent + 2)
            body.append(LoopStmt(fields[1], loop_body))
            continue
        if content.startswith("b "):
            fields = content.split()
            if len(fields) != 2:
                raise ScirHModelError(f"invalid compressed break statement: {content!r}")
            body.append(BreakStmt(fields[1]))
            index += 1
            continue
        if content.startswith("c "):
            fields = content.split()
            if len(fields) != 2:
                raise ScirHModelError(f"invalid compressed continue statement: {content!r}")
            body.append(ContinueStmt(fields[1]))
            index += 1
            continue
        if content == "try":
            try_body, index = parse_hc_suite(lines, index + 1, indent + 2)
            while index < len(lines) and not lines[index].strip():
                index += 1
            if index >= len(lines):
                raise ScirHModelError("compressed try statement must be followed by catch")
            catch_indent, catch_content = split_indent(lines[index])
            if catch_indent != indent or not catch_content.startswith("catch "):
                raise ScirHModelError(f"invalid compressed catch line: {lines[index]!r}")
            payload = catch_content[6:]
            if ":" not in payload:
                raise ScirHModelError(f"invalid compressed catch line: {catch_content!r}")
            catch_name, catch_type = payload.split(":", 1)
            catch_body, index = parse_hc_suite(lines, index + 1, indent + 2)
            body.append(TryStmt(try_body, catch_name.strip(), catch_type.strip(), catch_body))
            continue
        if content == "else" or content.startswith("catch "):
            break
        raise ScirHModelError(f"unsupported compressed statement: {content!r}")
    return tuple(body), index


def parse_scirhc_module(text: str) -> HcModule:
    if not text.endswith("\n"):
        raise ScirHModelError("compressed SCIR-Hc text must end with a newline")
    raw_lines = text.splitlines()
    if not raw_lines:
        raise ScirHModelError("empty compressed SCIR-Hc text")
    if any(line != line.rstrip(" ") for line in raw_lines):
        raise ScirHModelError("compressed SCIR-Hc text must not use trailing spaces")
    while raw_lines and not raw_lines[0].strip():
        raw_lines.pop(0)
    while raw_lines and not raw_lines[-1].strip():
        raw_lines.pop()
    if not raw_lines:
        raise ScirHModelError("empty compressed SCIR-Hc text")

    header = raw_lines[0]
    if not header.startswith("m "):
        raise ScirHModelError(f"invalid compressed module header: {header!r}")
    module_payload = header.split(" ", 1)[1]
    if " ~" not in module_payload:
        raise ScirHModelError("compressed module header must declare the derived-only authority boundary")
    module_id, header_suffix = module_payload.rsplit(" ~", 1)
    if " " in module_id:
        raise ScirHModelError(f"invalid compressed module id: {module_id!r}")
    authority_boundary = SCIRHC_AUTHORITY_BOUNDARY
    module_origins = ()
    if ":" in header_suffix:
        authority_code, origin_codes = header_suffix.split(":", 1)
        module_origins = parse_compression_origin_codes(origin_codes)
    else:
        authority_code = header_suffix
    if authority_code != "D":
        raise ScirHModelError(f"invalid compressed module authority marker: {authority_code!r}")

    imports = []
    type_decls = []
    functions = []
    index = 1
    while index < len(raw_lines):
        line = raw_lines[index]
        if not line.strip():
            index += 1
            continue
        indent, content = split_indent(line)
        if indent != 0:
            raise ScirHModelError(f"compressed top-level declarations must not be indented: {line!r}")
        if content.startswith("is ") or content.startswith("it "):
            imports.append(parse_hc_import(content))
            index += 1
            continue
        if content.startswith("t "):
            type_decls.append(parse_hc_type_decl(content))
            index += 1
            continue
        if content.startswith("f ") or content.startswith("af "):
            function = parse_hc_function_header(content)
            body, index = parse_hc_suite(raw_lines, index + 1, 2)
            functions.append(
                HcFunctionDecl(
                    name=function.name,
                    params=function.params,
                    return_type=function.return_type,
                    effects=function.effects,
                    body=body,
                    compression_origin=function.compression_origin,
                    is_async=function.is_async,
                )
            )
            continue
        raise ScirHModelError(f"unsupported compressed top-level declaration: {content!r}")
    return normalize_hc_module(
        HcModule(
            module_id=module_id,
            imports=tuple(imports),
            type_decls=tuple(type_decls),
            functions=tuple(functions),
            authority_boundary=authority_boundary,
            compression_origin=module_origins,
        )
    )


def _unwrap_named_type(type_name: str | None) -> str | None:
    if type_name is None:
        return None
    if type_name.endswith(">") and "<" in type_name:
        return type_name.split("<", 1)[1][:-1]
    return type_name


def _record_field_type_map(module) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    for type_decl in module.type_decls:
        type_expr = normalize_type_expr(type_decl.type_expr)
        if isinstance(type_expr, RecordType):
            mapping[type_decl.name] = {field.name: field.type_name for field in type_expr.fields}
    return mapping


def _place_type(place, bindings: dict[str, str], record_field_types: dict[str, dict[str, str]]) -> str | None:
    place = normalize_place(place)
    if isinstance(place, NamePlace):
        return bindings.get(place.name)
    if isinstance(place, FieldPlace):
        base_type = _place_type(place.base, bindings, record_field_types)
        record_name = _unwrap_named_type(base_type)
        if record_name is None:
            return None
        return record_field_types.get(record_name, {}).get(place.field)
    return None


def _expr_type(
    expr,
    bindings: dict[str, str],
    function_returns: dict[str, str],
    record_field_types: dict[str, dict[str, str]],
    import_returns: dict[str, str],
) -> str | None:
    expr = normalize_expr(expr)
    if isinstance(expr, NameExpr):
        return bindings.get(expr.name)
    if isinstance(expr, PlaceExpr):
        return _place_type(expr.place, bindings, record_field_types)
    if isinstance(expr, IntExpr):
        return "int"
    if isinstance(expr, CallExpr):
        if expr.callee in function_returns:
            return function_returns[expr.callee]
        return import_returns.get(expr.callee)
    if isinstance(expr, AwaitExpr):
        return _expr_type(expr.value, bindings, function_returns, record_field_types, import_returns)
    if isinstance(expr, IntrinsicExpr):
        return "int"
    return None


def _body_required_effects(
    body,
    function_effects: dict[str, tuple[str, ...]],
    import_effects: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    effects: set[str] = set()

    def visit_expr(expr):
        expr = normalize_expr(expr)
        if isinstance(expr, CallExpr):
            for arg in expr.args:
                visit_expr(arg)
            if expr.callee in function_effects:
                effects.update(function_effects[expr.callee])
            elif expr.callee in import_effects:
                effects.update(import_effects[expr.callee])
            return
        if isinstance(expr, AwaitExpr):
            effects.add("await")
            visit_expr(expr.value)
            return
        if isinstance(expr, IntrinsicExpr):
            for arg in expr.args:
                visit_expr(arg)

    def visit_stmt(stmt):
        if isinstance(stmt, HcVarDecl):
            visit_expr(stmt.value)
            return
        stmt = normalize_stmt(stmt)
        if isinstance(stmt, VarDecl):
            visit_expr(stmt.value)
            return
        if isinstance(stmt, SetStmt):
            effects.add("write")
            visit_expr(stmt.value)
            return
        if isinstance(stmt, ReturnStmt):
            visit_expr(stmt.value)
            return
        if isinstance(stmt, IfStmt):
            visit_expr(stmt.condition)
            for item in stmt.then_body:
                visit_stmt(item)
            for item in stmt.else_body:
                visit_stmt(item)
            return
        if isinstance(stmt, LoopStmt):
            for item in stmt.body:
                visit_stmt(item)
            return
        if isinstance(stmt, TryStmt):
            effects.add("throw")
            for item in stmt.try_body:
                visit_stmt(item)
            for item in stmt.catch_body:
                visit_stmt(item)

    for item in body:
        visit_stmt(item)
    return tuple(sorted(effects))


def _collect_return_types(
    body,
    bindings: dict[str, str],
    function_returns: dict[str, str],
    record_field_types: dict[str, dict[str, str]],
    import_returns: dict[str, str],
) -> tuple[set[str], bool]:
    return_types: set[str] = set()
    unresolved = False
    current_bindings = dict(bindings)

    for stmt in body:
        if isinstance(stmt, HcVarDecl):
            binding_type = stmt.type_name or _expr_type(
                stmt.value,
                current_bindings,
                function_returns,
                record_field_types,
                import_returns,
            )
            if binding_type is None:
                unresolved = True
            else:
                current_bindings[stmt.name] = binding_type
            continue
        stmt = normalize_stmt(stmt)
        if isinstance(stmt, VarDecl):
            current_bindings[stmt.name] = stmt.type_name
            continue
        if isinstance(stmt, ReturnStmt):
            return_type = _expr_type(
                stmt.value,
                current_bindings,
                function_returns,
                record_field_types,
                import_returns,
            )
            if return_type is None:
                unresolved = True
            else:
                return_types.add(return_type)
            continue
        if isinstance(stmt, IfStmt):
            then_types, then_unresolved = _collect_return_types(
                stmt.then_body,
                dict(current_bindings),
                function_returns,
                record_field_types,
                import_returns,
            )
            else_types, else_unresolved = _collect_return_types(
                stmt.else_body,
                dict(current_bindings),
                function_returns,
                record_field_types,
                import_returns,
            )
            return_types.update(then_types)
            return_types.update(else_types)
            unresolved = unresolved or then_unresolved or else_unresolved
            continue
        if isinstance(stmt, LoopStmt):
            nested_types, nested_unresolved = _collect_return_types(
                stmt.body,
                dict(current_bindings),
                function_returns,
                record_field_types,
                import_returns,
            )
            return_types.update(nested_types)
            unresolved = unresolved or nested_unresolved
            continue
        if isinstance(stmt, TryStmt):
            try_types, try_unresolved = _collect_return_types(
                stmt.try_body,
                dict(current_bindings),
                function_returns,
                record_field_types,
                import_returns,
            )
            catch_bindings = dict(current_bindings)
            catch_bindings[stmt.catch_name] = stmt.catch_type
            catch_types, catch_unresolved = _collect_return_types(
                stmt.catch_body,
                catch_bindings,
                function_returns,
                record_field_types,
                import_returns,
            )
            return_types.update(try_types)
            return_types.update(catch_types)
            unresolved = unresolved or try_unresolved or catch_unresolved
    return return_types, unresolved


def infer_scirh_function_return_type(module: Module, function: FunctionDecl) -> str | None:
    module = normalize_module(module)
    record_field_types = _record_field_type_map(module)
    function_returns = {item.name: item.return_type for item in module.functions}
    bindings = {param.name: param.type_name for param in function.params}
    return_types, unresolved = _collect_return_types(function.body, bindings, function_returns, record_field_types, {})
    if unresolved or len(return_types) != 1:
        return None
    return next(iter(return_types))


def infer_hc_function_return_types(module: HcModule) -> dict[str, str]:
    module = normalize_hc_module(module)
    record_field_types = _record_field_type_map(module)
    function_returns = {
        function.name: function.return_type
        for function in module.functions
        if function.return_type is not None
    }
    changed = True
    while changed:
        changed = False
        for function in module.functions:
            if function.name in function_returns:
                continue
            bindings = {param.name: param.type_name for param in function.params}
            return_types, unresolved = _collect_return_types(
                function.body,
                bindings,
                function_returns,
                record_field_types,
                {},
            )
            if unresolved or len(return_types) != 1:
                continue
            function_returns[function.name] = next(iter(return_types))
            changed = True
    missing = [function.name for function in module.functions if function.name not in function_returns]
    if missing:
        raise ScirHModelError(
            "compressed SCIR-Hc could not infer return types for " + ", ".join(sorted(missing))
        )
    return function_returns


def infer_hc_function_effects(module: HcModule) -> dict[str, tuple[str, ...]]:
    module = normalize_hc_module(module)
    import_effects = {item.local_id: ("opaque",) for item in module.imports if item.kind == "sym"}
    function_effects = {
        function.name: normalize_effects(function.effects) if function.effects is not None else ()
        for function in module.functions
    }
    changed = True
    while changed:
        changed = False
        for function in module.functions:
            inferred = _body_required_effects(function.body, function_effects, import_effects)
            resolved = normalize_effects(function.effects) if function.effects is not None else inferred
            if function_effects[function.name] != resolved:
                function_effects[function.name] = resolved
                changed = True
    return function_effects


def _scirh_stmt_to_scirhc(
    stmt,
    bindings: dict[str, str],
    function_returns: dict[str, str],
    record_field_types: dict[str, dict[str, str]],
):
    stmt = normalize_stmt(stmt)
    if isinstance(stmt, VarDecl):
        inferred_type = _expr_type(stmt.value, bindings, function_returns, record_field_types, {})
        type_name = None if inferred_type == stmt.type_name else stmt.type_name
        bindings[stmt.name] = stmt.type_name
        origins = ()
        if type_name is None:
            origins = (
                (CompressionOrigin.OWNERSHIP_ELISION,)
                if carries_ownership_type(stmt.type_name)
                else (CompressionOrigin.INFERRED_TYPE,)
            )
        return HcVarDecl(stmt.name, type_name, stmt.value, origins)
    if isinstance(stmt, IfStmt):
        then_body = tuple(
            _scirh_stmt_to_scirhc(item, dict(bindings), function_returns, record_field_types)
            for item in stmt.then_body
        )
        else_body = tuple(
            _scirh_stmt_to_scirhc(item, dict(bindings), function_returns, record_field_types)
            for item in stmt.else_body
        )
        return IfStmt(stmt.condition, then_body, else_body)
    if isinstance(stmt, LoopStmt):
        loop_body = tuple(
            _scirh_stmt_to_scirhc(item, dict(bindings), function_returns, record_field_types)
            for item in stmt.body
        )
        return LoopStmt(stmt.loop_id, loop_body)
    if isinstance(stmt, TryStmt):
        try_body = tuple(
            _scirh_stmt_to_scirhc(item, dict(bindings), function_returns, record_field_types)
            for item in stmt.try_body
        )
        catch_bindings = dict(bindings)
        catch_bindings[stmt.catch_name] = stmt.catch_type
        catch_body = tuple(
            _scirh_stmt_to_scirhc(item, catch_bindings, function_returns, record_field_types)
            for item in stmt.catch_body
        )
        return TryStmt(try_body, stmt.catch_name, stmt.catch_type, catch_body)
    return stmt


def scirh_to_scirhc(module: Module, *, boundary_contracts=None) -> HcModule:
    module = normalize_module(module)
    record_field_types = _record_field_type_map(module)
    function_returns = {function.name: function.return_type for function in module.functions}
    explicit_effects = {function.name: function.effects for function in module.functions}
    import_effects = {item.local_id: ("opaque",) for item in module.imports if item.kind == "sym"}
    functions = []
    for function in module.functions:
        bindings = {param.name: param.type_name for param in function.params}
        inferred_return = infer_scirh_function_return_type(module, function)
        inferred_effects = _body_required_effects(function.body, explicit_effects, import_effects)
        body = tuple(
            _scirh_stmt_to_scirhc(item, bindings, function_returns, record_field_types)
            for item in function.body
        )
        compression_origin = []
        return_type = function.return_type
        if inferred_return == function.return_type:
            return_type = None
            compression_origin.append(
                CompressionOrigin.OWNERSHIP_ELISION
                if carries_ownership_type(function.return_type)
                else CompressionOrigin.INFERRED_TYPE
            )
        effects = function.effects
        if inferred_effects == function.effects:
            effects = None
            compression_origin.append(CompressionOrigin.INFERRED_EFFECT)
        functions.append(
            HcFunctionDecl(
                name=function.name,
                params=function.params,
                return_type=return_type,
                effects=effects,
                body=body,
                compression_origin=tuple(compression_origin),
                is_async=function.is_async,
            )
        )
    return normalize_hc_module(
        HcModule(
            module_id=module.module_id,
            imports=module.imports,
            type_decls=module.type_decls,
            functions=tuple(functions),
            authority_boundary=SCIRHC_AUTHORITY_BOUNDARY,
            compression_origin=(),
        )
    )


def _scirhc_stmt_to_scirh(
    stmt,
    bindings: dict[str, str],
    function_returns: dict[str, str],
    record_field_types: dict[str, dict[str, str]],
):
    if isinstance(stmt, HcVarDecl):
        inferred_type = stmt.type_name or _expr_type(
            stmt.value,
            bindings,
            function_returns,
            record_field_types,
            {},
        )
        if inferred_type is None:
            raise ScirHModelError(f"compressed local {stmt.name!r} requires an explicit type or inferable initializer")
        bindings[stmt.name] = inferred_type
        return VarDecl(stmt.name, inferred_type, normalize_expr(stmt.value))
    stmt = normalize_stmt(stmt)
    if isinstance(stmt, IfStmt):
        then_body = tuple(
            _scirhc_stmt_to_scirh(item, dict(bindings), function_returns, record_field_types)
            for item in stmt.then_body
        )
        else_body = tuple(
            _scirhc_stmt_to_scirh(item, dict(bindings), function_returns, record_field_types)
            for item in stmt.else_body
        )
        return IfStmt(stmt.condition, then_body, else_body)
    if isinstance(stmt, LoopStmt):
        loop_body = tuple(
            _scirhc_stmt_to_scirh(item, dict(bindings), function_returns, record_field_types)
            for item in stmt.body
        )
        return LoopStmt(stmt.loop_id, loop_body)
    if isinstance(stmt, TryStmt):
        try_body = tuple(
            _scirhc_stmt_to_scirh(item, dict(bindings), function_returns, record_field_types)
            for item in stmt.try_body
        )
        catch_bindings = dict(bindings)
        catch_bindings[stmt.catch_name] = stmt.catch_type
        catch_body = tuple(
            _scirhc_stmt_to_scirh(item, catch_bindings, function_returns, record_field_types)
            for item in stmt.catch_body
        )
        return TryStmt(try_body, stmt.catch_name, stmt.catch_type, catch_body)
    return stmt


def scirhc_to_scirh(module: HcModule) -> Module:
    module = normalize_hc_module(module)
    record_field_types = _record_field_type_map(module)
    function_returns = infer_hc_function_return_types(module)
    function_effects = infer_hc_function_effects(module)
    functions = []
    for function in module.functions:
        bindings = {param.name: param.type_name for param in function.params}
        body = tuple(
            _scirhc_stmt_to_scirh(item, bindings, function_returns, record_field_types)
            for item in function.body
        )
        functions.append(
            FunctionDecl(
                name=function.name,
                params=function.params,
                return_type=function.return_type or function_returns[function.name],
                effects=function.effects if function.effects is not None else function_effects[function.name],
                body=body,
                is_async=function.is_async,
            )
        )
    return normalize_module(
        Module(
            module_id=module.module_id,
            imports=module.imports,
            type_decls=module.type_decls,
            functions=tuple(functions),
        )
    )


def scirhc_normalization_stats(module: Module, *, boundary_contracts=None) -> dict[str, int]:
    module = normalize_module(module)
    hc_module = scirh_to_scirhc(module, boundary_contracts=boundary_contracts)
    effect_rows_deduplicated = sum(
        1
        for function in hc_module.functions
        if CompressionOrigin.INFERRED_EFFECT in function.compression_origin
    )
    return_types_inferred = sum(
        1
        for function in hc_module.functions
        if any(
            origin in function.compression_origin
            for origin in (CompressionOrigin.INFERRED_TYPE, CompressionOrigin.OWNERSHIP_ELISION)
        )
    )
    ownership_markers_elided = sum(
        1
        for function in hc_module.functions
        for stmt in function.body
        if isinstance(stmt, HcVarDecl) and CompressionOrigin.OWNERSHIP_ELISION in stmt.compression_origin
    ) + sum(
        1
        for function in hc_module.functions
        if CompressionOrigin.OWNERSHIP_ELISION in function.compression_origin
    )
    capabilities_hoisted = 1 if CompressionOrigin.REDUNDANT_CAPABILITY in hc_module.compression_origin else 0
    return {
        "effect_rows_deduplicated": effect_rows_deduplicated,
        "return_types_inferred": return_types_inferred,
        "ownership_markers_elided": ownership_markers_elided,
        "single_use_witnesses_inlined": 0,
        "capabilities_hoisted": capabilities_hoisted,
    }


def validate_scirhc_roundtrip(module: Module, *, boundary_contracts=None) -> list[str]:
    diagnostics = []
    hc_module = scirh_to_scirhc(module, boundary_contracts=boundary_contracts)
    hc_text = format_scirhc_module(hc_module)
    parsed_hc = parse_scirhc_module(hc_text)
    if parsed_hc != hc_module:
        diagnostics.append("compressed SCIR-Hc text is not normalized under parse-format equality")
    roundtripped = scirhc_to_scirh(parsed_hc)
    if semantic_lineage_id(roundtripped) != semantic_lineage_id(module):
        diagnostics.append("compressed SCIR-Hc round-trip drifted semantic lineage")
    if format_module(roundtripped) != format_module(module):
        diagnostics.append("compressed SCIR-Hc round-trip drifted canonical SCIR-H formatting")
    stats = scirhc_normalization_stats(module, boundary_contracts=boundary_contracts)
    if stats["effect_rows_deduplicated"] < 0 or stats["ownership_markers_elided"] < 0:
        diagnostics.append("compressed SCIR-Hc normalization stats became invalid")
    return diagnostics


def _semantic_expr_key(expr):
    expr = normalize_expr(expr)
    if isinstance(expr, NameExpr):
        return ("name", expr.name)
    if isinstance(expr, PlaceExpr):
        return ("place", format_place(expr.place))
    if isinstance(expr, IntExpr):
        return ("int", expr.value)
    if isinstance(expr, CallExpr):
        return ("call", expr.callee, tuple(_semantic_expr_key(arg) for arg in expr.args))
    if isinstance(expr, AwaitExpr):
        return ("await", _semantic_expr_key(expr.value))
    if isinstance(expr, IntrinsicExpr):
        return ("intrinsic", expr.op, tuple(_semantic_expr_key(arg) for arg in expr.args))
    raise ScirHModelError(f"unsupported expression node: {type(expr).__name__}")


def _semantic_stmt_key(stmt):
    stmt = normalize_stmt(stmt)
    if isinstance(stmt, VarDecl):
        return ("var", stmt.name, stmt.type_name, _semantic_expr_key(stmt.value))
    if isinstance(stmt, SetStmt):
        return ("set", format_place(stmt.target), _semantic_expr_key(stmt.value))
    if isinstance(stmt, ReturnStmt):
        return ("return", _semantic_expr_key(stmt.value))
    if isinstance(stmt, IfStmt):
        return (
            "if",
            _semantic_expr_key(stmt.condition),
            tuple(_semantic_stmt_key(item) for item in stmt.then_body),
            tuple(_semantic_stmt_key(item) for item in stmt.else_body),
        )
    if isinstance(stmt, LoopStmt):
        return ("loop", stmt.loop_id, tuple(_semantic_stmt_key(item) for item in stmt.body))
    if isinstance(stmt, BreakStmt):
        return ("break", stmt.loop_id)
    if isinstance(stmt, ContinueStmt):
        return ("continue", stmt.loop_id)
    if isinstance(stmt, TryStmt):
        return (
            "try",
            tuple(_semantic_stmt_key(item) for item in stmt.try_body),
            stmt.catch_name,
            stmt.catch_type,
            tuple(_semantic_stmt_key(item) for item in stmt.catch_body),
        )
    raise ScirHModelError(f"unsupported statement node: {type(stmt).__name__}")


def _semantic_type_key(type_expr):
    type_expr = normalize_type_expr(type_expr)
    if isinstance(type_expr, str):
        return ("type", type_expr)
    if isinstance(type_expr, RecordType):
        return (
            "record",
            tuple((field.name, field.type_name) for field in type_expr.fields),
        )
    raise ScirHModelError(f"unsupported type expression node: {type(type_expr).__name__}")


def semantic_lineage_payload(module: Module) -> dict:
    module = normalize_module(module)
    return {
        "module_id": module.module_id,
        "imports": sorted((item.kind, item.local_id, item.ref) for item in module.imports),
        "type_decls": sorted(
            (type_decl.name, _semantic_type_key(type_decl.type_expr))
            for type_decl in module.type_decls
        ),
        "functions": sorted(
            (
                function.name,
                function.is_async,
                tuple((param.name, param.type_name) for param in function.params),
                function.return_type,
                tuple(function.effects),
                tuple(_semantic_stmt_key(stmt) for stmt in function.body),
            )
            for function in module.functions
        ),
    }


def semantic_lineage_id(module: Module) -> str:
    payload = json.dumps(
        semantic_lineage_payload(module),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def canonical_content_hash(module: Module) -> str:
    canonical_text = format_module(module)
    return hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()


def revision_scoped_node_id(
    module: Module,
    *,
    decl_name: str,
    node_path: str,
    revision_tag: str,
) -> str:
    payload = (
        canonical_content_hash(module),
        decl_name,
        node_path,
        revision_tag,
    )
    text = "::".join(payload)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_pretty_module(module: Module, *, include_identity: bool = True) -> str:
    module = normalize_module(module)
    lines = [f"# Pretty view for {module.module_id}"]
    if include_identity:
        lines.append(f"# semantic_lineage_id: {semantic_lineage_id(module)}")
        lines.append(f"# canonical_content_hash: {canonical_content_hash(module)}")
    lines.append("")
    lines.append(f"module {module.module_id}")
    for item in module.imports:
        lines.append(f"import {item.kind} {item.local_id} {item.ref}")
    if module.imports and (module.type_decls or module.functions):
        lines.append("")
    for type_decl in module.type_decls:
        lines.append(f"# type {type_decl.name}")
        lines.append(f"type {type_decl.name} {format_type_expr(type_decl.type_expr)}")
        lines.append("")
    for index, function in enumerate(module.functions):
        header = format_function(function)
        lines.append(f"# function {function.name}")
        lines.extend(header)
        if index != len(module.functions) - 1:
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
