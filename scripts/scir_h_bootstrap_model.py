#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass


IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MODULE_ID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
REFERENCE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:.]*$")
TYPE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_<>]*$")
EFFECT_RE = re.compile(r"^![A-Za-z_,]*$")
INTRINSIC_OPS = ("lt", "le", "eq", "ne", "gt", "ge")


class ScirHModelError(Exception):
    pass


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


def expect_identifier(value: str, label: str):
    if not IDENTIFIER_RE.match(value):
        raise ScirHModelError(f"invalid {label}: {value!r}")


def expect_type_name(value: str, label: str):
    if not TYPE_RE.match(value):
        raise ScirHModelError(f"invalid {label}: {value!r}")


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
