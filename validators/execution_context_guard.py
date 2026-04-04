"""Structured execution guard for trusted SCIR-Hc transform entrypoints."""
from __future__ import annotations

import hashlib
import json
import re
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

from scir_h_bootstrap_model import (
    Module,
    ScirhcContextError,
    canonical_content_hash,
    normalize_module,
    semantic_lineage_id,
)


HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


class ScirhcReportSurface(str, Enum):
    VALIDATION_REPORT = "validation_report"
    BENCHMARK_OUTPUT = "benchmark_output"


class TrustedScirhcCaller(str, Enum):
    PIPELINE_VALIDATION = "pipeline.validation"
    BENCHMARK_CLAIM = "benchmark.claim"
    SCIRHC_VALIDATOR = "validator.scirhc"


@dataclass(frozen=True)
class ScirhcExecutionCapability:
    caller: TrustedScirhcCaller
    nonce: object


@dataclass(frozen=True)
class ScirhcExecutionProvenance:
    caller: TrustedScirhcCaller


@dataclass(frozen=True)
class ScirhcLineageRoot:
    module_id: str
    semantic_lineage_id: str
    normalized_canonical_hash: str


@dataclass(frozen=True)
class ScirhcGenerationContext:
    report_surface: ScirhcReportSurface
    generation_token: str
    lineage_root: ScirhcLineageRoot
    provenance: ScirhcExecutionProvenance
    capability: ScirhcExecutionCapability

    @property
    def is_report_context(self) -> bool:
        return True


_REGISTERED_CAPABILITIES: dict[object, TrustedScirhcCaller] = {}
_ACTIVE_EXECUTION_STACK: list[tuple[str, str, str, TrustedScirhcCaller]] = []


def register_trusted_scirhc_caller(caller: TrustedScirhcCaller) -> ScirhcExecutionCapability:
    nonce = object()
    capability = ScirhcExecutionCapability(caller=caller, nonce=nonce)
    _REGISTERED_CAPABILITIES[nonce] = caller
    return capability


def build_scirhc_lineage_root(module: Module) -> ScirhcLineageRoot:
    normalized = normalize_module(module)
    return ScirhcLineageRoot(
        module_id=normalized.module_id,
        semantic_lineage_id=semantic_lineage_id(normalized),
        normalized_canonical_hash=canonical_content_hash(normalized),
    )


def scirhc_lineage_root_payload(root: ScirhcLineageRoot) -> dict[str, str]:
    return {
        "semantic_lineage_id": root.semantic_lineage_id,
        "normalized_canonical_hash": root.normalized_canonical_hash,
    }


def build_scirhc_execution_provenance(
    caller: TrustedScirhcCaller,
) -> ScirhcExecutionProvenance:
    return ScirhcExecutionProvenance(caller=caller)


def _generation_token_payload(lineage_root: ScirhcLineageRoot, provenance: ScirhcExecutionProvenance) -> str:
    return json.dumps(
        {
            "module_id": lineage_root.module_id,
            "semantic_lineage_id": lineage_root.semantic_lineage_id,
            "normalized_canonical_hash": lineage_root.normalized_canonical_hash,
            "caller": provenance.caller.value,
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def build_scirhc_generation_token(
    lineage_root: ScirhcLineageRoot,
    provenance: ScirhcExecutionProvenance,
) -> str:
    return hashlib.sha256(_generation_token_payload(lineage_root, provenance).encode("utf-8")).hexdigest()


def build_scirhc_generation_context(
    module: Module,
    *,
    report_surface: ScirhcReportSurface,
    capability: ScirhcExecutionCapability,
) -> ScirhcGenerationContext:
    provenance = build_scirhc_execution_provenance(capability.caller)
    lineage_root = build_scirhc_lineage_root(module)
    return ScirhcGenerationContext(
        report_surface=report_surface,
        generation_token=build_scirhc_generation_token(lineage_root, provenance),
        lineage_root=lineage_root,
        provenance=provenance,
        capability=capability,
    )


def validate_scirhc_context(
    ctx: ScirhcGenerationContext | None,
    *,
    allowed_callers: frozenset[TrustedScirhcCaller],
) -> None:
    if ctx is None:
        raise ScirhcContextError("Missing SCIR-Hc generation context")
    if not isinstance(ctx, ScirhcGenerationContext):
        raise ScirhcContextError("Invalid SCIR-Hc generation context")
    if not isinstance(ctx.report_surface, ScirhcReportSurface):
        raise ScirhcContextError("Invalid SCIR-Hc report surface")
    if not isinstance(ctx.provenance, ScirhcExecutionProvenance):
        raise ScirhcContextError("Missing SCIR-Hc call provenance")
    if ctx.provenance.caller not in allowed_callers:
        raise ScirhcContextError("Unauthorized SCIR-Hc transform provenance")
    if not isinstance(ctx.lineage_root, ScirhcLineageRoot):
        raise ScirhcContextError("Invalid lineage root")
    if not HEX64_RE.fullmatch(ctx.generation_token):
        raise ScirhcContextError("Invalid generation token")
    if not HEX64_RE.fullmatch(ctx.lineage_root.semantic_lineage_id):
        raise ScirhcContextError("Invalid lineage root semantic lineage id")
    if not HEX64_RE.fullmatch(ctx.lineage_root.normalized_canonical_hash):
        raise ScirhcContextError("Invalid lineage root canonical hash")
    registered_caller = _REGISTERED_CAPABILITIES.get(ctx.capability.nonce)
    if registered_caller != ctx.capability.caller:
        raise ScirhcContextError("Untrusted SCIR-Hc execution capability")
    if registered_caller != ctx.provenance.caller:
        raise ScirhcContextError("SCIR-Hc execution capability provenance mismatch")
    expected_token = build_scirhc_generation_token(ctx.lineage_root, ctx.provenance)
    if ctx.generation_token != expected_token:
        raise ScirhcContextError("Invalid generation token")


def require_lineage_root_match(module: Module, ctx: ScirhcGenerationContext) -> Module:
    normalized = normalize_module(module)
    expected_root = build_scirhc_lineage_root(normalized)
    if ctx.lineage_root != expected_root:
        raise ScirhcContextError("SCIR-Hc lineage root does not match canonical SCIR-H")
    return normalized


@contextmanager
def activate_scirhc_execution(
    ctx: ScirhcGenerationContext,
    *,
    allowed_callers: frozenset[TrustedScirhcCaller],
):
    validate_scirhc_context(ctx, allowed_callers=allowed_callers)
    _ACTIVE_EXECUTION_STACK.append(
        (
            ctx.generation_token,
            ctx.lineage_root.module_id,
            ctx.lineage_root.normalized_canonical_hash,
            ctx.provenance.caller,
        )
    )
    try:
        yield
    finally:
        _ACTIVE_EXECUTION_STACK.pop()


def require_active_scirhc_execution(
    ctx: ScirhcGenerationContext,
    *,
    allowed_callers: frozenset[TrustedScirhcCaller],
) -> None:
    validate_scirhc_context(ctx, allowed_callers=allowed_callers)
    if not _ACTIVE_EXECUTION_STACK:
        raise ScirhcContextError("Unauthorized SCIR-Hc transform access")
    active_token, module_id, canonical_hash, caller = _ACTIVE_EXECUTION_STACK[-1]
    if (
        active_token != ctx.generation_token
        or module_id != ctx.lineage_root.module_id
        or canonical_hash != ctx.lineage_root.normalized_canonical_hash
        or caller != ctx.provenance.caller
    ):
        raise ScirhcContextError("SCIR-Hc execution scope mismatch")
