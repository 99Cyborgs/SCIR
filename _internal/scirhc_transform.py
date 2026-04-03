from __future__ import annotations

import hashlib
import inspect
import json
import pathlib
import re
from contextlib import contextmanager
from dataclasses import dataclass

from scir_h_bootstrap_model import (
    CompressionOrigin,
    FunctionDecl,
    HcFunctionDecl,
    HcModule,
    HcVarDecl,
    Module,
    ScirHModelError,
    ScirhcContextError,
    SCIRHC_AUTHORITY_BOUNDARY,
    _body_required_effects,
    _expr_type,
    _record_field_type_map,
    _scirh_stmt_to_scirhc,
    _scirhc_stmt_to_scirh,
    canonical_content_hash,
    carries_ownership_type,
    format_module,
    infer_hc_function_effects,
    infer_hc_function_return_types,
    infer_scirh_function_return_type,
    normalize_hc_module,
    normalize_module,
    parse_scirhc_module,
    semantic_lineage_id,
)


HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_INTERNAL_CALL_DEPTH = 0
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ALLOWED_INTERNAL_CALLERS = {
    REPO_ROOT / "scripts" / "scir_bootstrap_pipeline.py",
    REPO_ROOT / "scripts" / "benchmark_contract_dry_run.py",
    REPO_ROOT / "validators" / "scirhc_validator.py",
}


@dataclass(frozen=True)
class ScirhcLineageRoot:
    module_id: str
    semantic_lineage_id: str
    normalized_canonical_hash: str


@dataclass(frozen=True)
class ScirhcGenerationContext:
    is_report_context: bool
    generation_token: str
    lineage_root: ScirhcLineageRoot


@contextmanager
def internal_scirhc_transform_access():
    global _INTERNAL_CALL_DEPTH
    stack_paths = {
        pathlib.Path(frame_info.filename).resolve()
        for frame_info in inspect.stack()
    }
    if not any(path in ALLOWED_INTERNAL_CALLERS for path in stack_paths):
        raise ScirhcContextError("Unauthorized SCIR-Hc transform access")
    _INTERNAL_CALL_DEPTH += 1
    try:
        yield
    finally:
        _INTERNAL_CALL_DEPTH -= 1


def _require_internal_call_context() -> None:
    if _INTERNAL_CALL_DEPTH <= 0:
        raise ScirhcContextError("Unauthorized SCIR-Hc transform access")


def scirhc_lineage_root_payload(root: ScirhcLineageRoot) -> dict[str, str]:
    return {
        "semantic_lineage_id": root.semantic_lineage_id,
        "normalized_canonical_hash": root.normalized_canonical_hash,
    }


def build_scirhc_lineage_root(module: Module) -> ScirhcLineageRoot:
    normalized = normalize_module(module)
    return ScirhcLineageRoot(
        module_id=normalized.module_id,
        semantic_lineage_id=semantic_lineage_id(normalized),
        normalized_canonical_hash=canonical_content_hash(normalized),
    )


def _generation_token_payload(lineage_root: ScirhcLineageRoot) -> str:
    return json.dumps(
        {
            "module_id": lineage_root.module_id,
            "semantic_lineage_id": lineage_root.semantic_lineage_id,
            "normalized_canonical_hash": lineage_root.normalized_canonical_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def build_scirhc_generation_token(lineage_root: ScirhcLineageRoot) -> str:
    return hashlib.sha256(_generation_token_payload(lineage_root).encode("utf-8")).hexdigest()


def build_scirhc_generation_context(
    module: Module,
    *,
    is_report_context: bool = True,
) -> ScirhcGenerationContext:
    lineage_root = build_scirhc_lineage_root(module)
    return ScirhcGenerationContext(
        is_report_context=is_report_context,
        generation_token=build_scirhc_generation_token(lineage_root),
        lineage_root=lineage_root,
    )


def require_scirhc_context(ctx: ScirhcGenerationContext | None) -> None:
    if ctx is None:
        raise ScirhcContextError("Missing SCIR-Hc generation context")
    if not ctx.is_report_context:
        raise ScirhcContextError("SCIR-Hc generation allowed only in report context")
    if not ctx.generation_token:
        raise ScirhcContextError("Missing generation token")
    if not ctx.lineage_root:
        raise ScirhcContextError("Missing lineage root")
    if not isinstance(ctx.lineage_root, ScirhcLineageRoot):
        raise ScirhcContextError("Invalid lineage root")
    if not HEX64_RE.fullmatch(ctx.generation_token):
        raise ScirhcContextError("Invalid generation token")
    if not HEX64_RE.fullmatch(ctx.lineage_root.semantic_lineage_id):
        raise ScirhcContextError("Invalid lineage root semantic lineage id")
    if not HEX64_RE.fullmatch(ctx.lineage_root.normalized_canonical_hash):
        raise ScirhcContextError("Invalid lineage root canonical hash")
    expected_token = build_scirhc_generation_token(ctx.lineage_root)
    if ctx.generation_token != expected_token:
        raise ScirhcContextError("Invalid generation token")


def _require_context_for_module(module: Module, ctx: ScirhcGenerationContext | None) -> Module:
    require_scirhc_context(ctx)
    _require_internal_call_context()
    normalized = normalize_module(module)
    expected_root = build_scirhc_lineage_root(normalized)
    if ctx.lineage_root != expected_root:
        raise ScirhcContextError("SCIR-Hc lineage root does not match canonical SCIR-H")
    return normalized


def _lineage_reference_dict(lineage_root: ScirhcLineageRoot) -> dict[str, dict[str, str]]:
    return {lineage_root.module_id: scirhc_lineage_root_payload(lineage_root)}


def scirh_to_scirhc(
    module: Module,
    *,
    ctx: ScirhcGenerationContext | None = None,
    boundary_contracts=None,
) -> HcModule:
    normalized = _require_context_for_module(module, ctx)
    record_field_types = _record_field_type_map(normalized)
    function_returns = {function.name: function.return_type for function in normalized.functions}
    explicit_effects = {function.name: function.effects for function in normalized.functions}
    import_effects = {item.local_id: ("opaque",) for item in normalized.imports if item.kind == "sym"}
    functions = []
    for function in normalized.functions:
        bindings = {param.name: param.type_name for param in function.params}
        inferred_return = infer_scirh_function_return_type(normalized, function)
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
            module_id=normalized.module_id,
            imports=normalized.imports,
            type_decls=normalized.type_decls,
            functions=tuple(functions),
            authority_boundary=SCIRHC_AUTHORITY_BOUNDARY,
            compression_origin=(),
        )
    )


def scirhc_to_scirh(
    module: HcModule,
    *,
    ctx: ScirhcGenerationContext | None = None,
) -> Module:
    require_scirhc_context(ctx)
    _require_internal_call_context()
    normalized_hc = normalize_hc_module(module)
    record_field_types = _record_field_type_map(normalized_hc)
    function_returns = infer_hc_function_return_types(normalized_hc)
    function_effects = infer_hc_function_effects(normalized_hc)
    functions = []
    for function in normalized_hc.functions:
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
    reconstructed = normalize_module(
        Module(
            module_id=normalized_hc.module_id,
            imports=normalized_hc.imports,
            type_decls=normalized_hc.type_decls,
            functions=tuple(functions),
        )
    )
    expected_root = build_scirhc_lineage_root(reconstructed)
    if ctx.lineage_root != expected_root:
        raise ScirhcContextError("SCIR-Hc lineage root does not match reconstructed canonical SCIR-H")
    return reconstructed


def scirhc_normalization_stats(
    module: Module,
    *,
    ctx: ScirhcGenerationContext | None = None,
    boundary_contracts=None,
) -> dict[str, int]:
    normalized = _require_context_for_module(module, ctx)
    hc_module = scirh_to_scirhc(normalized, ctx=ctx, boundary_contracts=boundary_contracts)
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


def validate_scirhc_roundtrip(
    module: Module,
    *,
    ctx: ScirhcGenerationContext | None = None,
    boundary_contracts=None,
) -> list[str]:
    normalized = _require_context_for_module(module, ctx)
    diagnostics = []
    hc_module = scirh_to_scirhc(normalized, ctx=ctx, boundary_contracts=boundary_contracts)
    from scir_h_bootstrap_model import format_scirhc_module

    hc_text = format_scirhc_module(hc_module)
    parsed_hc = parse_scirhc_module(hc_text)
    if parsed_hc != hc_module:
        diagnostics.append("compressed SCIR-Hc text is not normalized under parse-format equality")
    roundtripped = scirhc_to_scirh(parsed_hc, ctx=ctx)
    if semantic_lineage_id(roundtripped) != semantic_lineage_id(normalized):
        diagnostics.append("compressed SCIR-Hc round-trip drifted semantic lineage")
    if format_module(roundtripped) != format_module(normalized):
        diagnostics.append("compressed SCIR-Hc round-trip drifted canonical SCIR-H formatting")
    stats = scirhc_normalization_stats(normalized, ctx=ctx, boundary_contracts=boundary_contracts)
    if stats["effect_rows_deduplicated"] < 0 or stats["ownership_markers_elided"] < 0:
        diagnostics.append("compressed SCIR-Hc normalization stats became invalid")
    return diagnostics


def generate_scirhc_diff_audit(
    module: Module,
    scirhc: HcModule,
    *,
    ctx: ScirhcGenerationContext | None = None,
    boundary_contracts=None,
) -> dict[str, object]:
    normalized = _require_context_for_module(module, ctx)
    normalized_hc = normalize_hc_module(scirhc)
    if normalized_hc.module_id != normalized.module_id:
        raise ScirhcContextError("SCIR-Hc diff audit requires a matching canonical module id")
    dropped_fields: list[str] = []
    structural_diff = {
        "function_return_type_omissions": [],
        "function_effect_row_omissions": [],
        "local_type_omissions": [],
    }
    for scirh_function, scirhc_function in zip(normalized.functions, normalized_hc.functions):
        if scirhc_function.return_type is None:
            field_name = f"functions.{scirh_function.name}.return_type"
            dropped_fields.append(field_name)
            structural_diff["function_return_type_omissions"].append(field_name)
        if scirhc_function.effects is None:
            field_name = f"functions.{scirh_function.name}.effects"
            dropped_fields.append(field_name)
            structural_diff["function_effect_row_omissions"].append(field_name)
        for stmt_index, stmt in enumerate(scirhc_function.body):
            if not isinstance(stmt, HcVarDecl) or stmt.type_name is not None:
                continue
            field_name = f"functions.{scirh_function.name}.body[{stmt_index}].type_name"
            dropped_fields.append(field_name)
            structural_diff["local_type_omissions"].append(field_name)
    stats = scirhc_normalization_stats(normalized, ctx=ctx, boundary_contracts=boundary_contracts)
    return {
        "module_id": normalized.module_id,
        "lineage_references": _lineage_reference_dict(ctx.lineage_root),
        "structural_diff": structural_diff,
        "dropped_fields": dropped_fields,
        "normalized_fields": [],
        "compression_statistics": stats,
    }
