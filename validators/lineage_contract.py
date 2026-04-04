"""Strict lineage binding checks for derived SCIR-Hc artifacts and reports."""
from __future__ import annotations

import re

from scir_h_bootstrap_model import Module, canonical_content_hash, normalize_module, semantic_lineage_id


HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


class LineageContractError(ValueError):
    pass


def canonical_lineage_binding(module: Module) -> dict[str, str]:
    normalized = normalize_module(module)
    return {
        "semantic_lineage_id": semantic_lineage_id(normalized),
        "normalized_canonical_hash": canonical_content_hash(normalized),
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise LineageContractError(message)


def _metric_items(report: dict) -> list[dict]:
    items: list[dict] = []
    claim_gate = report.get("claim_gate")
    if isinstance(claim_gate, dict):
        evaluated = claim_gate.get("evaluated_conditions")
        if isinstance(evaluated, list):
            items.extend(item for item in evaluated if isinstance(item, dict))
    claims = report.get("claims")
    if isinstance(claims, list):
        items.extend(item for item in claims if isinstance(item, dict))
    return items


def _validate_binding_shape(binding: dict, *, module_id: str, label: str) -> None:
    _require(isinstance(binding, dict), f"{label} entry for {module_id!r} must be an object")
    lineage_id = binding.get("semantic_lineage_id")
    canonical_hash = binding.get("normalized_canonical_hash")
    _require(
        isinstance(lineage_id, str) and HEX64_RE.fullmatch(lineage_id),
        f"{label} entry for {module_id!r} must include a 64-character semantic lineage id",
    )
    _require(
        isinstance(canonical_hash, str) and HEX64_RE.fullmatch(canonical_hash),
        f"{label} entry for {module_id!r} must include a 64-character normalized canonical hash",
    )


def assert_complete_lineage_binding(
    lineage_references,
    *,
    canonical_registry: dict[str, Module] | None = None,
    required_modules: set[str] | None = None,
    metric_items: list[dict] | None = None,
    label: str = "SCIR-Hc artifact",
) -> None:
    _require(isinstance(lineage_references, dict) and lineage_references, f"{label} must declare canonical SCIR-H lineage references")
    expected_modules = set(required_modules or ())
    if canonical_registry is not None:
        expected_modules.update(canonical_registry)
    missing_modules = sorted(expected_modules - set(lineage_references))
    _require(not missing_modules, f"{label} is missing lineage bindings for {missing_modules!r}")

    for module_id, binding in lineage_references.items():
        _require(isinstance(module_id, str) and module_id, f"{label} keys must be non-empty module ids")
        _validate_binding_shape(binding, module_id=module_id, label=label)
        if canonical_registry is None:
            continue
        canonical = canonical_registry.get(module_id)
        _require(canonical is not None, f"{label} references unknown canonical module {module_id!r}")
        expected_binding = canonical_lineage_binding(canonical)
        _require(
            binding["semantic_lineage_id"] == expected_binding["semantic_lineage_id"],
            "Lineage semantic id mismatch",
        )
        _require(
            binding["normalized_canonical_hash"] == expected_binding["normalized_canonical_hash"],
            "Lineage hash mismatch",
        )

    for item in metric_items or ():
        evidence = item.get("scir_h_evidence")
        _require(isinstance(evidence, list) and evidence, "Incomplete lineage coverage")
        _require(
            all(isinstance(entry, str) and entry for entry in evidence),
            "Incomplete lineage coverage",
        )
        _require(
            all(entry in lineage_references for entry in evidence),
            "Incomplete lineage coverage",
        )


def assert_report_lineage_binding(
    report: dict,
    *,
    canonical_registry: dict[str, Module] | None = None,
    required_modules: set[str] | None = None,
) -> None:
    _require(isinstance(report, dict), "SCIR-Hc lineage validation requires an object payload")
    lineage_references = report.get("scir_h_lineage_references")
    label = "benchmark report"
    if lineage_references is None:
        lineage_references = report.get("lineage_references")
        label = "SCIR-Hc artifact"
    assert_complete_lineage_binding(
        lineage_references,
        canonical_registry=canonical_registry,
        required_modules=required_modules,
        metric_items=_metric_items(report),
        label=label,
    )
