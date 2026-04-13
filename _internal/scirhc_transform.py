"""File: _internal/scirhc_transform.py
Purpose: Guard and implement the derived-only SCIR-H <-> SCIR-Hc transform path used by reporting and doctrine checks.
Role in system: This is the internal compression boundary that keeps SCIR-Hc subordinate to canonical SCIR-H.
Key dependencies: scir_h_bootstrap_model normalization and inference helpers, dataclasses, inspect, and hashing.
Side effects: Inspects the call stack for authorized callers, computes lineage or generation tokens, and raises context errors on misuse.
"""
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
    """Represents: The canonical lineage tuple that binds derived SCIR-Hc output back to normalized SCIR-H.

    Invariants:
      - module_id identifies the normalized canonical module.
      - semantic_lineage_id and normalized_canonical_hash are both derived from normalized SCIR-H.
    Relationships:
      - Embedded inside ScirhcGenerationContext and emitted into lineage-reference payloads.
    """
    module_id: str
    semantic_lineage_id: str
    normalized_canonical_hash: str


@dataclass(frozen=True)
class ScirhcGenerationContext:
    """Represents: The report-scoped authorization bundle required to derive or reconstruct SCIR-Hc safely.

    Invariants:
      - is_report_context must stay true for executable transform calls.
      - generation_token must match the embedded lineage_root.
    Relationships:
      - Produced by build_scirhc_generation_context and validated by require_scirhc_context.
    """
    is_report_context: bool
    generation_token: str
    lineage_root: ScirhcLineageRoot


@contextmanager
def internal_scirhc_transform_access():
    """Purpose: Allow SCIR-Hc transforms only when an approved internal caller opens the access gate.

    Inputs:
      - None.
    Outputs:
      - contextmanager access window for authorized transform calls.
    Side Effects:
      - Inspects the live Python call stack.
      - Mutates the module-level internal call depth counter for nested authorized calls.
    Assumptions:
      - Only the benchmark and validation surfaces listed in ALLOWED_INTERNAL_CALLERS may trigger these transforms.
    Failure Modes:
      - Raises ScirhcContextError when an unauthorized caller attempts to open the gate.
    """
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
    """Purpose: Enforce that transform helpers run only inside an authorized access window.

    Inputs:
      - None.
    Outputs:
      - None.
    Side Effects:
      - None.
    Assumptions:
      - _INTERNAL_CALL_DEPTH is incremented only by internal_scirhc_transform_access.
    Failure Modes:
      - Raises ScirhcContextError when no authorized access window is active.
    """
    if _INTERNAL_CALL_DEPTH <= 0:
        raise ScirhcContextError("Unauthorized SCIR-Hc transform access")


def scirhc_lineage_root_payload(root: ScirhcLineageRoot) -> dict[str, str]:
    """Purpose: Render the lineage fields that downstream reports may expose for derived SCIR-Hc evidence.

    Inputs:
      - root: ScirhcLineageRoot canonical lineage tuple.
    Outputs:
      - dict[str, str] lineage reference payload without the module id wrapper.
    Side Effects:
      - None.
    Assumptions:
      - Report surfaces only need the lineage id and canonical hash, not the full context object.
    Failure Modes:
      - None.
    """
    return {
        "semantic_lineage_id": root.semantic_lineage_id,
        "normalized_canonical_hash": root.normalized_canonical_hash,
    }


def build_scirhc_lineage_root(module: Module) -> ScirhcLineageRoot:
    """Purpose: Bind a module to the normalized canonical lineage data used by SCIR-Hc generation.

    Inputs:
      - module: Module canonical or pre-normalized SCIR-H module.
    Outputs:
      - ScirhcLineageRoot derived from normalized SCIR-H.
    Side Effects:
      - None.
    Assumptions:
      - Lineage must be computed from normalized SCIR-H so formatting noise cannot spoof identity.
    Failure Modes:
      - Propagates normalization or hashing errors from the underlying model helpers.
    """
    normalized = normalize_module(module)
    return ScirhcLineageRoot(
        module_id=normalized.module_id,
        semantic_lineage_id=semantic_lineage_id(normalized),
        normalized_canonical_hash=canonical_content_hash(normalized),
    )


def _generation_token_payload(lineage_root: ScirhcLineageRoot) -> str:
    """Purpose: Produce the canonical JSON payload that generation-token hashing signs.

    Inputs:
      - lineage_root: ScirhcLineageRoot canonical lineage tuple.
    Outputs:
      - str canonical JSON payload.
    Side Effects:
      - None.
    Assumptions:
      - Token validity must depend only on stable lineage fields.
    Failure Modes:
      - None.
    """
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
    """Purpose: Derive the tamper-evident token that authorizes one SCIR-Hc generation context.

    Inputs:
      - lineage_root: ScirhcLineageRoot canonical lineage tuple.
    Outputs:
      - str SHA-256 hex token.
    Side Effects:
      - None.
    Assumptions:
      - Any mutation to lineage_root should force a different generation token.
    Failure Modes:
      - None.
    """
    return hashlib.sha256(_generation_token_payload(lineage_root).encode("utf-8")).hexdigest()


def build_scirhc_generation_context(
    module: Module,
    *,
    is_report_context: bool = True,
) -> ScirhcGenerationContext:
    """Purpose: Build the report-scoped context required by SCIR-Hc transform entrypoints.

    Inputs:
      - module: Module canonical SCIR-H module to authorize.
      - is_report_context: bool marker that keeps compression generation off non-report paths.
    Outputs:
      - ScirhcGenerationContext fully bound to the normalized module lineage.
    Side Effects:
      - None.
    Assumptions:
      - Executable SCIR-Hc transforms remain report-only in the MVP.
    Failure Modes:
      - Propagates lineage construction failures from build_scirhc_lineage_root.
    """
    lineage_root = build_scirhc_lineage_root(module)
    return ScirhcGenerationContext(
        is_report_context=is_report_context,
        generation_token=build_scirhc_generation_token(lineage_root),
        lineage_root=lineage_root,
    )


def require_scirhc_context(ctx: ScirhcGenerationContext | None) -> None:
    """Purpose: Validate that a caller supplied a structurally sound, report-scoped SCIR-Hc context.

    Inputs:
      - ctx: ScirhcGenerationContext | None candidate authorization context.
    Outputs:
      - None.
    Side Effects:
      - None.
    Assumptions:
      - A missing, malformed, or non-report context must block any transform attempt.
    Failure Modes:
      - Raises ScirhcContextError when required fields are missing, malformed, or mismatched.
    """
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
    """Purpose: Validate both authorization and lineage binding before transforming a specific module.

    Inputs:
      - module: Module candidate SCIR-H input.
      - ctx: ScirhcGenerationContext | None authorization context for that module.
    Outputs:
      - Module normalized canonical SCIR-H module.
    Side Effects:
      - None.
    Assumptions:
      - The supplied context must match the normalized module exactly, not just by module id.
    Failure Modes:
      - Raises ScirhcContextError on missing authorization, caller misuse, or lineage mismatch.
    """
    require_scirhc_context(ctx)
    _require_internal_call_context()
    normalized = normalize_module(module)
    expected_root = build_scirhc_lineage_root(normalized)
    if ctx.lineage_root != expected_root:
        raise ScirhcContextError("SCIR-Hc lineage root does not match canonical SCIR-H")
    return normalized


def _lineage_reference_dict(lineage_root: ScirhcLineageRoot) -> dict[str, dict[str, str]]:
    """Purpose: Wrap lineage payloads in the module-keyed shape expected by audit artifacts.

    Inputs:
      - lineage_root: ScirhcLineageRoot canonical lineage tuple.
    Outputs:
      - dict[str, dict[str, str]] module-id keyed lineage-reference map.
    Side Effects:
      - None.
    Assumptions:
      - Downstream audit payloads are keyed by module id, even for single-module outputs.
    Failure Modes:
      - None.
    """
    return {lineage_root.module_id: scirhc_lineage_root_payload(lineage_root)}


def scirh_to_scirhc(
    module: Module,
    *,
    ctx: ScirhcGenerationContext | None = None,
    boundary_contracts=None,
) -> HcModule:
    """Purpose: Derive compressed SCIR-Hc from canonical SCIR-H while recording every permitted omission.

    Inputs:
      - module: Module canonical SCIR-H input.
      - ctx: ScirhcGenerationContext | None required report-scoped authorization context.
      - boundary_contracts: Optional boundary metadata carried through to the underlying model helpers.
    Outputs:
      - HcModule normalized derived SCIR-Hc artifact.
    Side Effects:
      - None.
    Assumptions:
      - Only inferred return types, inferred effects, and ownership-related elisions may be compressed away.
    Failure Modes:
      - Raises ScirhcContextError when authorization or lineage checks fail.
      - Propagates model-helper failures if the source module is invalid.
    """
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
    """Purpose: Reconstruct canonical SCIR-H from a validated derived SCIR-Hc artifact.

    Inputs:
      - module: HcModule derived SCIR-Hc input.
      - ctx: ScirhcGenerationContext | None authorization context bound to the expected canonical lineage.
    Outputs:
      - Module normalized canonical SCIR-H reconstruction.
    Side Effects:
      - None.
    Assumptions:
      - Missing types and effects in SCIR-Hc are recoverable only through canonical inference helpers.
    Failure Modes:
      - Raises ScirhcContextError when authorization fails or reconstructed lineage does not match the context.
      - Propagates normalization or inference failures from the model helpers.
    """
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
    """Purpose: Count the specific compressions applied when deriving SCIR-Hc from canonical SCIR-H.

    Inputs:
      - module: Module canonical SCIR-H source.
      - ctx: ScirhcGenerationContext | None required authorization context.
      - boundary_contracts: Optional boundary metadata forwarded to derivation.
    Outputs:
      - dict[str, int] normalization statistics for report payloads.
    Side Effects:
      - None.
    Assumptions:
      - Statistics are informative only after the same authorization and lineage checks as the real transform.
    Failure Modes:
      - Raises ScirhcContextError on invalid context.
      - Propagates transform failures from scirh_to_scirhc.
    """
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
    """Purpose: Check that SCIR-Hc text rendering and reconstruction stay lossless for one canonical module.

    Inputs:
      - module: Module canonical SCIR-H source.
      - ctx: ScirhcGenerationContext | None required authorization context.
      - boundary_contracts: Optional boundary metadata forwarded to derivation.
    Outputs:
      - list[str] human-readable diagnostics. Empty means the round trip stayed stable.
    Side Effects:
      - None.
    Assumptions:
      - Round-trip validation must compare both semantic lineage and canonical formatting, not just object equality.
    Failure Modes:
      - Raises ScirhcContextError when the caller is unauthorized.
    """
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
    """Purpose: Describe exactly which canonical SCIR-H fields were omitted or preserved in a derived SCIR-Hc artifact.

    Inputs:
      - module: Module canonical SCIR-H source.
      - scirhc: HcModule derived SCIR-Hc artifact to audit.
      - ctx: ScirhcGenerationContext | None required authorization context.
      - boundary_contracts: Optional boundary metadata forwarded to normalization-stat computation.
    Outputs:
      - dict[str, object] diff-audit payload for benchmark and doctrine reporting.
    Side Effects:
      - None.
    Assumptions:
      - The audited SCIR-Hc artifact must describe the same module lineage as the canonical source.
    Failure Modes:
      - Raises ScirhcContextError when module ids or authorization contexts do not match.
    """
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
