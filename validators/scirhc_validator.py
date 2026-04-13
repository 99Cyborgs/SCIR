"""File: validators/scirhc_validator.py
Purpose: Enforce the doctrine that derived SCIR-Hc artifacts remain subordinate to canonical SCIR-H evidence.
Role in system: This validator protects benchmark and reporting surfaces from treating compression artifacts as semantic authority.
Key dependencies: _internal.scirhc_transform, scir_h_bootstrap_model normalization helpers, and benchmark report field contracts.
Side effects: Raises doctrine errors when SCIR-Hc artifacts, metrics, or reports exceed the repository's allowed claim surface.
"""
from __future__ import annotations

import re

from _internal.scirhc_transform import (
    build_scirhc_generation_context,
    internal_scirhc_transform_access,
    scirh_to_scirhc,
    scirhc_to_scirh,
)
from scir_h_bootstrap_model import (
    CompressionOrigin,
    HcModule,
    HcVarDecl,
    IfStmt,
    LoopStmt,
    Module,
    SCIRHC_AUTHORITY_BOUNDARY,
    ScirHModelError,
    TryStmt,
    canonical_content_hash,
    format_module,
    format_scirhc_module,
    normalize_hc_module,
    normalize_module,
    parse_scirhc_module,
    semantic_lineage_id,
)


HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


class ScirHcDoctrineError(ValueError):
    """Represents: A hard governance failure in SCIR-Hc derivation, reporting, or claim scoping.

    Invariants:
      - Raised only when a derived artifact or report violates the SCIR-Hc doctrine contract.
    Relationships:
      - Used by all validator helpers in this module to signal blocking failures.
    """
    pass


DEFAULT_BENCHMARK_CLAIM_CLASS = "LEXICAL_COMPRESSION_ONLY"
METRIC_CLASSES = {"DESCRIPTIVE", "EVALUATIVE", "CAUSAL"}
# Each claim class names the only admissible evidence and metrics for SCIR-Hc.
# Anything outside these sets is treated as cross-class leakage from compressed
# evidence into broader semantic claims.
CLAIM_SCOPE_RULES = {
    "LEXICAL_COMPRESSION_ONLY": {
        "evidence_ids": {"scirhc_lcr_vs_ast"},
        "metric_names": {"LCR_scirhc"},
        "metric_classes": {"LCR_scirhc": "DESCRIPTIVE"},
    },
    "GRAMMAR_REGULARITY_ONLY": {
        "evidence_ids": {"scirhc_gr_vs_ast"},
        "metric_names": {"GR_scirhc"},
        "metric_classes": {"GR_scirhc": "DESCRIPTIVE"},
    },
    "PATCH_COMPOSABILITY_ONLY": {
        "evidence_ids": {"patch_composability_vs_ast"},
        "metric_names": {"patch_composability_gain_vs_typed_ast", "SCPR_scirhc"},
        "metric_classes": {
            "patch_composability_gain_vs_typed_ast": "EVALUATIVE",
            "SCPR_scirhc": "EVALUATIVE",
        },
    },
}
FORBIDDEN_CLAIM_TERMS = (
    "semantic preservation",
    "reconstruction fidelity",
    "cross-language equivalence",
    "cross language equivalence",
    "semantic authority",
)
SEMANTIC_AUTHORITY_ESCALATION_TERMS = (
    "proves",
    "guarantees",
    "establishes",
)
AUTHORITY_IMPLYING_METRIC_TERMS = (
    "semantic",
    "authority",
    "preservation",
    "equivalence",
    "reconstruction",
    "fidelity",
    "meaning",
)
SCIRHC_REPORT_REPRESENTATION = "SCIR-Hc"
SCIRHC_DISALLOWED_REPORT_FIELDS = (
    "semantic_claims",
    "authoritative_metrics",
    "lowering_artifacts",
    "backend_outputs",
)


def _walk_hc_statements(body):
    """Purpose: Traverse nested SCIR-Hc statement bodies so local provenance checks see every branch and loop body.

    Inputs:
      - body: iterable statement sequence from an HcFunctionDecl or nested control-flow node.
    Outputs:
      - Generator of statements in depth-first order.
    Side Effects:
      - None.
    Assumptions:
      - Only IfStmt, LoopStmt, and TryStmt introduce nested statement suites in the active subset.
    Failure Modes:
      - None.
    """
    for stmt in body:
        yield stmt
        if isinstance(stmt, IfStmt):
            yield from _walk_hc_statements(stmt.then_body)
            yield from _walk_hc_statements(stmt.else_body)
        elif isinstance(stmt, LoopStmt):
            yield from _walk_hc_statements(stmt.body)
        elif isinstance(stmt, TryStmt):
            yield from _walk_hc_statements(stmt.try_body)
            yield from _walk_hc_statements(stmt.catch_body)


def _require(condition: bool, message: str) -> None:
    """Purpose: Raise the module's doctrine-specific error type instead of generic assertion failures.

    Inputs:
      - condition: bool predicate that must hold.
      - message: str blocking diagnostic to surface on failure.
    Outputs:
      - None.
    Side Effects:
      - Raises ScirHcDoctrineError when the condition is false.
    Assumptions:
      - Doctrine validation must fail with stable, domain-specific diagnostics.
    Failure Modes:
      - Raises ScirHcDoctrineError.
    """
    if not condition:
        raise ScirHcDoctrineError(message)


def _contains_term(text: str, term: str) -> bool:
    """Purpose: Check for whole-word policy terms without matching substrings accidentally.

    Inputs:
      - text: str normalized text to scan.
      - term: str policy term that must be matched as a word boundary.
    Outputs:
      - bool whether the term appears as a word or phrase boundary match.
    Side Effects:
      - None.
    Assumptions:
      - Claim-scope filters should catch semantic overreach terms without false positives from substrings.
    Failure Modes:
      - None.
    """
    return re.search(r"\b" + re.escape(term) + r"\b", text) is not None


def _normalize_scirhc(scirhc: HcModule) -> HcModule:
    """Purpose: Normalize SCIR-Hc with doctrine-specific error wrapping.

    Inputs:
      - scirhc: HcModule candidate derived artifact.
    Outputs:
      - HcModule normalized SCIR-Hc artifact.
    Side Effects:
      - None.
    Assumptions:
      - Model-layer normalization failures should be surfaced as doctrine failures at this layer.
    Failure Modes:
      - Raises ScirHcDoctrineError when normalization fails.
    """
    try:
        return normalize_hc_module(scirhc)
    except ScirHModelError as exc:
        raise ScirHcDoctrineError(str(exc)) from exc


def _require_scoped_claim_text(text: str, claim_class: str, label: str) -> None:
    """Purpose: Reject free-text claim language that overstates what SCIR-Hc evidence is allowed to show.

    Inputs:
      - text: str claim or statement text to validate.
      - claim_class: str declared benchmark claim class.
      - label: str field label used in diagnostics.
    Outputs:
      - None.
    Side Effects:
      - Raises ScirHcDoctrineError on empty, forbidden, or authority-escalating language.
    Assumptions:
      - Claim text must stay inside the narrow evidence class declared for the report.
    Failure Modes:
      - Raises ScirHcDoctrineError.
    """
    _require(isinstance(text, str) and text, f"benchmark report {label} must be non-empty")
    lowered = text.lower()
    _require(
        not any(_contains_term(lowered, term) for term in FORBIDDEN_CLAIM_TERMS),
        f"benchmark report {label} overreaches beyond {claim_class}",
    )
    _require(
        not any(_contains_term(lowered, term) for term in SEMANTIC_AUTHORITY_ESCALATION_TERMS),
        f"benchmark report {label} escalates SCIR-Hc beyond derived-only evidence",
    )


def _lineage_reference_failures(lineage_references, *, label: str) -> list[str]:
    """Purpose: Collect structural problems in the canonical-lineage references attached to SCIR-Hc artifacts or reports.

    Inputs:
      - lineage_references: candidate lineage map payload.
      - label: str diagnostic prefix naming the checked surface.
    Outputs:
      - list[str] lineage validation failures. Empty means the structure is acceptable.
    Side Effects:
      - None.
    Assumptions:
      - Each lineage entry must carry a canonical semantic lineage id and normalized canonical hash.
    Failure Modes:
      - None; returns failures instead of raising so callers can batch diagnostics.
    """
    if not isinstance(lineage_references, dict) or not lineage_references:
        return [f"{label} must declare canonical SCIR-H lineage references"]
    failures = []
    for module_id, binding in lineage_references.items():
        if not isinstance(module_id, str) or not module_id:
            failures.append(f"{label} keys must be non-empty module ids")
            continue
        if not isinstance(binding, dict):
            failures.append(f"{label} entry for {module_id!r} must be an object")
            continue
        lineage_id = binding.get("semantic_lineage_id")
        canonical_hash = binding.get("normalized_canonical_hash")
        if not (isinstance(lineage_id, str) and HEX64_RE.fullmatch(lineage_id)):
            failures.append(f"{label} entry for {module_id!r} must include a 64-character semantic lineage id")
        if not (isinstance(canonical_hash, str) and HEX64_RE.fullmatch(canonical_hash)):
            failures.append(f"{label} entry for {module_id!r} must include a 64-character normalized canonical hash")
    return failures


def _metric_items(report: dict) -> list[tuple[str, dict]]:
    """Purpose: Flatten the metric-bearing sections of a report into one iterable for downstream checks.

    Inputs:
      - report: dict benchmark report payload.
    Outputs:
      - list[tuple[str, dict]] tagged metric items from claim_gate and claims sections.
    Side Effects:
      - None.
    Assumptions:
      - Metric validation must treat evaluated conditions and claims as one combined evidence surface.
    Failure Modes:
      - Skips malformed non-dict entries rather than raising here.
    """
    items: list[tuple[str, dict]] = []
    claim_gate = report.get("claim_gate")
    if isinstance(claim_gate, dict):
        for item in claim_gate.get("evaluated_conditions", []):
            if isinstance(item, dict):
                items.append(("evaluated_condition", item))
    for item in report.get("claims", []):
        if isinstance(item, dict):
            items.append(("claim", item))
    return items


def _lineage_references(report: dict):
    """Purpose: Read lineage references from whichever report field name the surface legitimately uses.

    Inputs:
      - report: dict SCIR-Hc artifact or benchmark report payload.
    Outputs:
      - tuple[value, label] lineage-reference payload plus the logical surface label.
    Side Effects:
      - None.
    Assumptions:
      - Benchmark reports and raw SCIR-Hc artifacts expose lineage references under different field names.
    Failure Modes:
      - Returns (None, label) when neither lineage field is present.
    """
    if "scir_h_lineage_references" in report:
        return report["scir_h_lineage_references"], "benchmark report"
    if "lineage_references" in report:
        return report["lineage_references"], "SCIR-Hc artifact"
    return None, "SCIR-Hc artifact"


def assert_not_semantic_authority(scirhc: HcModule) -> None:
    """Purpose: Enforce the derived-only authority marker on a normalized SCIR-Hc artifact.

    Inputs:
      - scirhc: HcModule candidate derived artifact.
    Outputs:
      - None.
    Side Effects:
      - Raises ScirHcDoctrineError when the authority boundary marker is wrong.
    Assumptions:
      - Every valid SCIR-Hc artifact must carry SCIRHC_AUTHORITY_BOUNDARY.
    Failure Modes:
      - Raises ScirHcDoctrineError.
    """
    normalized = _normalize_scirhc(scirhc)
    _require(
        normalized.authority_boundary == SCIRHC_AUTHORITY_BOUNDARY,
        "SCIR-Hc must declare the derived-only authority boundary",
    )


def assert_no_semantic_authority(scirhc_obj) -> None:
    """Purpose: Reject any SCIR-Hc artifact or report surface that claims more than derived-only evidence allows.

    Inputs:
      - scirhc_obj: HcModule or dict report payload.
    Outputs:
      - None.
    Side Effects:
      - Raises ScirHcDoctrineError on authority escalation, forbidden fields, or invalid claim-class structure.
    Assumptions:
      - Raw HcModule validation and benchmark-report validation share the same no-authority rule.
    Failure Modes:
      - Raises ScirHcDoctrineError.
    """
    if isinstance(scirhc_obj, HcModule):
        assert_not_semantic_authority(scirhc_obj)
        return

    _require(isinstance(scirhc_obj, dict), "SCIR-Hc semantic-authority checks require a report object or HcModule")
    representation = scirhc_obj.get("representation")
    _require(
        representation == SCIRHC_REPORT_REPRESENTATION,
        f"benchmark report representation must be {SCIRHC_REPORT_REPRESENTATION!r}",
    )
    lineage_references, label = _lineage_references(scirhc_obj)
    for message in _lineage_reference_failures(lineage_references, label=label):
        raise ScirHcDoctrineError(message)
    disallowed_fields = [field for field in SCIRHC_DISALLOWED_REPORT_FIELDS if field in scirhc_obj]
    _require(
        not disallowed_fields,
        f"benchmark report must not contain SCIR-Hc semantic-authority fields {disallowed_fields!r}",
    )

    claim_class = scirhc_obj.get("claim_class")
    _require(
        claim_class in CLAIM_SCOPE_RULES,
        f"benchmark report claim_class must be one of {sorted(CLAIM_SCOPE_RULES)}",
    )
    allowed_metrics = CLAIM_SCOPE_RULES[claim_class]["metric_names"]

    claim_gate = scirhc_obj.get("claim_gate")
    _require(isinstance(claim_gate, dict), "benchmark report claim_gate must be present")
    evaluated = claim_gate.get("evaluated_conditions")
    _require(isinstance(evaluated, list), "benchmark report claim_gate.evaluated_conditions must be a list")
    evaluated_metrics = []
    for item in evaluated:
        _require(isinstance(item, dict), "benchmark report claim_gate.evaluated_conditions entries must be objects")
        metric = item.get("metric")
        _require(
            metric in allowed_metrics,
            f"benchmark report evaluated condition metric {metric!r} is not derived from the declared SCIR-H evidence scope",
        )
        evaluated_metrics.append(metric)
        _require_scoped_claim_text(
            item.get("statement"),
            claim_class,
            f"evaluated condition {item.get('id', '<missing>')!r} statement",
        )

    claims = scirhc_obj.get("claims")
    _require(isinstance(claims, list) and claims, "benchmark report must include at least one scoped claim")
    for claim in claims:
        _require(isinstance(claim, dict), "benchmark report claims entries must be objects")
        metric = claim.get("metric")
        _require(
            metric in allowed_metrics,
            f"benchmark report claim metric {metric!r} is not derived from the declared SCIR-H evidence scope",
        )
        _require(
            metric in evaluated_metrics,
            f"benchmark report claim metric {metric!r} is not present in claim_gate.evaluated_conditions",
        )
        _require_scoped_claim_text(claim.get("statement"), claim_class, "claim statement")


def assert_no_hidden_semantics(scirhc: HcModule) -> None:
    """Purpose: Require every SCIR-Hc omission to be provenance-justified and semantically subordinate.

    Inputs:
      - scirhc: HcModule candidate derived artifact.
    Outputs:
      - None.
    Side Effects:
      - Raises ScirHcDoctrineError when omitted fields or compression origins do not line up.
    Assumptions:
      - Compression may only remove information that canonical inference can recover without minting semantics.
    Failure Modes:
      - Raises ScirHcDoctrineError.
    """

    normalized = _normalize_scirhc(scirhc)
    assert_no_semantic_authority(normalized)

    for origin in normalized.compression_origin:
        _require(
            origin is CompressionOrigin.REDUNDANT_CAPABILITY,
            "module-level SCIR-Hc provenance may only record redundant capability elision",
        )

    for function in normalized.functions:
        function_origins = set(function.compression_origin)
        type_origins = {
            CompressionOrigin.INFERRED_TYPE,
            CompressionOrigin.OWNERSHIP_ELISION,
        }
        type_origin_count = len(function_origins & type_origins)
        if function.return_type is None:
            _require(
                type_origin_count == 1,
                f"function {function.name!r} omits its return type without a single explainable provenance origin",
            )
        else:
            _require(
                type_origin_count == 0,
                f"function {function.name!r} keeps an explicit return type but still carries type-elision provenance",
            )
        if function.effects is None:
            _require(
                CompressionOrigin.INFERRED_EFFECT in function_origins,
                f"function {function.name!r} omits effects without INFERRED_EFFECT provenance",
            )
        else:
            _require(
                CompressionOrigin.INFERRED_EFFECT not in function_origins,
                f"function {function.name!r} keeps explicit effects but still carries effect-elision provenance",
            )
        _require(
            CompressionOrigin.REDUNDANT_CAPABILITY not in function_origins,
            f"function {function.name!r} must not hide capability provenance at function scope",
        )
        for stmt in _walk_hc_statements(function.body):
            if not isinstance(stmt, HcVarDecl):
                continue
            stmt_origins = set(stmt.compression_origin)
            if stmt.type_name is None:
                _require(
                    len(stmt_origins) == 1
                    and stmt_origins <= {
                        CompressionOrigin.INFERRED_TYPE,
                        CompressionOrigin.OWNERSHIP_ELISION,
                    },
                    f"local {stmt.name!r} omits its type without a single explainable provenance origin",
                )
            else:
                _require(
                    not stmt_origins,
                    f"local {stmt.name!r} keeps an explicit type but still carries compression provenance",
                )


def assert_deterministic_derivation(scirh: Module, scirhc: HcModule) -> None:
    """Purpose: Prove that one SCIR-Hc artifact is the deterministic result of canonical SCIR-H derivation.

    Inputs:
      - scirh: Module canonical SCIR-H source.
      - scirhc: HcModule candidate derived artifact.
    Outputs:
      - None.
    Side Effects:
      - Opens the internal transform access gate for authorized derivation or reconstruction checks.
    Assumptions:
      - SCIR-Hc must never become an alternative authoring form with multiple valid encodings.
    Failure Modes:
      - Raises ScirHcDoctrineError when derivation, idempotence, or reconstruction drift is detected.
    """

    normalized_scirh = normalize_module(scirh)
    normalized_scirhc = _normalize_scirhc(scirhc)
    assert_no_hidden_semantics(normalized_scirhc)
    ctx = build_scirhc_generation_context(normalized_scirh)
    with internal_scirhc_transform_access():
        expected = scirh_to_scirhc(normalized_scirh, ctx=ctx)
        _require(
            normalized_scirhc == expected,
            "SCIR-H -> SCIR-Hc derivation must be deterministic, idempotent, and context-independent",
        )
        reconstructed = scirhc_to_scirh(normalized_scirhc, ctx=ctx)
        _require(
            scirh_to_scirhc(reconstructed, ctx=ctx) == expected,
            "SCIR-Hc must remain idempotent under canonical SCIR-H reconstruction",
        )


def assert_semantic_idempotence(scirh: Module) -> None:
    """Purpose: Verify that deriving then reconstructing SCIR-Hc returns the same normalized canonical SCIR-H.

    Inputs:
      - scirh: Module canonical SCIR-H source.
    Outputs:
      - None.
    Side Effects:
      - Uses the internal transform access gate to derive and reconstruct SCIR-Hc.
    Assumptions:
      - Canonical SCIR-H should be stable under the derived-only projection.
    Failure Modes:
      - Raises ScirHcDoctrineError when normalization changes across the round trip.
    """
    normalized = normalize_module(scirh)
    ctx = build_scirhc_generation_context(normalized)
    with internal_scirhc_transform_access():
        derived = scirh_to_scirhc(normalized, ctx=ctx)
        reconstructed = scirhc_to_scirh(derived, ctx=ctx)
    if normalize_module(reconstructed) != normalized:
        raise ScirHcDoctrineError("Non-idempotent SCIR-Hc projection")


def assert_round_trip_integrity(scirh: Module) -> None:
    """Purpose: Validate the full SCIR-H -> SCIR-Hc text -> SCIR-H round trip for one canonical module.

    Inputs:
      - scirh: Module canonical SCIR-H source.
    Outputs:
      - None.
    Side Effects:
      - Derives, formats, parses, and reconstructs SCIR-Hc inside an authorized transform scope.
    Assumptions:
      - Stability requires equal normalized modules, preserved lineage ids, preserved canonical formatting, and deterministic re-derivation.
    Failure Modes:
      - Raises ScirHcDoctrineError when any stage of the round trip drifts.
    """
    normalized = normalize_module(scirh)
    ctx = build_scirhc_generation_context(normalized)
    with internal_scirhc_transform_access():
        derived = scirh_to_scirhc(normalized, ctx=ctx)
        rendered = format_scirhc_module(derived)
        reparsed = parse_scirhc_module(rendered)
        _require(reparsed == derived, "SCIR-Hc storage must remain stable under parse-format equality")
        reconstructed = normalize_module(scirhc_to_scirh(reparsed, ctx=ctx))
        _require(
            reconstructed == normalized,
            "SCIR-Hc round-trip must preserve normalized canonical SCIR-H",
        )
        _require(
            semantic_lineage_id(reconstructed) == semantic_lineage_id(normalized),
            "SCIR-Hc round-trip must preserve SCIR-H semantic lineage",
        )
        _require(
            format_module(reconstructed) == format_module(normalized),
            "SCIR-Hc round-trip must preserve normalized canonical SCIR-H formatting",
        )
        _require(
            scirh_to_scirhc(reconstructed, ctx=ctx) == derived,
            "SCIR-Hc round-trip must preserve deterministic derivation output",
        )
    assert_semantic_idempotence(normalized)


def assert_lineage_integrity(report: dict, canonical_registry: dict[str, Module] | None = None) -> None:
    """Purpose: Bind every SCIR-Hc report surface back to canonical module lineage and normalized hashes.

    Inputs:
      - report: dict artifact or benchmark report payload carrying lineage references.
      - canonical_registry: dict[str, Module] | None optional canonical modules used for exact lineage verification.
    Outputs:
      - None.
    Side Effects:
      - Raises ScirHcDoctrineError when lineage coverage is missing or mismatched.
    Assumptions:
      - Every metric or claim that mentions SCIR-Hc evidence must point back to declared canonical module lineage.
    Failure Modes:
      - Raises ScirHcDoctrineError.
    """

    _require(isinstance(report, dict), "SCIR-Hc lineage validation requires an object payload")
    lineage_references, label = _lineage_references(report)
    for message in _lineage_reference_failures(lineage_references, label=label):
        raise ScirHcDoctrineError(message)

    for module_id, binding in lineage_references.items():
        canonical = None if canonical_registry is None else canonical_registry.get(module_id)
        if canonical_registry is not None and canonical is None:
            raise ScirHcDoctrineError("Lineage reference not found")
        if canonical is None:
            continue
        normalized = normalize_module(canonical)
        if binding["semantic_lineage_id"] != semantic_lineage_id(normalized):
            raise ScirHcDoctrineError("Lineage semantic id mismatch")
        if binding["normalized_canonical_hash"] != canonical_content_hash(normalized):
            raise ScirHcDoctrineError("Lineage hash mismatch")

    for kind, item in _metric_items(report):
        evidence = item.get("scir_h_evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ScirHcDoctrineError("Incomplete lineage coverage")
        if not all(isinstance(entry, str) and entry for entry in evidence):
            raise ScirHcDoctrineError("Incomplete lineage coverage")
        if any(entry not in lineage_references for entry in evidence):
            raise ScirHcDoctrineError("Incomplete lineage coverage")


def implies_semantic_authority(metric: dict) -> bool:
    """Purpose: Detect metric names or statements that imply semantic-authority claims.

    Inputs:
      - metric: dict metric or claim payload.
    Outputs:
      - bool whether the metric text implies forbidden semantic authority.
    Side Effects:
      - None.
    Assumptions:
      - Semantic overreach can appear in either the metric key or the human-readable statement text.
    Failure Modes:
      - None.
    """
    metric_name = metric.get("metric")
    statement = metric.get("statement")
    fragments = []
    if isinstance(metric_name, str):
        fragments.append(metric_name.lower())
    if isinstance(statement, str):
        fragments.append(statement.lower())
    joined = " ".join(fragments)
    return any(_contains_term(joined, term) for term in AUTHORITY_IMPLYING_METRIC_TERMS)


def assert_metric_authority(metrics: list[dict], claim_gate: dict) -> None:
    """Purpose: Ensure metric metadata does not introduce authority claims outside the evaluated benchmark surface.

    Inputs:
      - metrics: list[dict] combined metric-bearing claim and condition payloads.
      - claim_gate: dict benchmark report claim gate.
    Outputs:
      - None.
    Side Effects:
      - Raises ScirHcDoctrineError when causal metrics or metric text exceed policy.
    Assumptions:
      - Causal metrics are only valid when explicitly evaluated and tied to SCIR-H evidence.
    Failure Modes:
      - Raises ScirHcDoctrineError.
    """
    _require(isinstance(claim_gate, dict), "benchmark report claim_gate must be present")
    evaluated = claim_gate.get("evaluated_conditions")
    _require(isinstance(evaluated, list), "benchmark report claim_gate.evaluated_conditions must be a list")
    evaluated_metrics = {item.get("metric") for item in evaluated if isinstance(item, dict)}
    for metric in metrics:
        _require(isinstance(metric, dict), "benchmark report metrics must be objects")
        metric_name = metric.get("metric")
        _require(isinstance(metric_name, str) and metric_name, "benchmark report metric name is required")
        metric_class = metric.get("metric_class")
        _require(metric_class in METRIC_CLASSES, "benchmark report metric_class is invalid")
        if metric_class == "CAUSAL":
            evidence = metric.get("scir_h_evidence")
            if metric_name not in evaluated_metrics or not isinstance(evidence, list) or not evidence:
                raise ScirHcDoctrineError("Causal metric outside evaluated conditions")
        if implies_semantic_authority(metric):
            raise ScirHcDoctrineError("Metric implies semantic authority")


def assert_claim_scope_compliance(report: dict, canonical_registry: dict[str, Module] | None = None) -> None:
    """Purpose: Reject benchmark reports that use SCIR-Hc evidence outside the declared claim and evidence classes.

    Inputs:
      - report: dict benchmark report payload.
      - canonical_registry: dict[str, Module] | None optional canonical lineage registry for exact binding checks.
    Outputs:
      - None.
    Side Effects:
      - Raises ScirHcDoctrineError when the report leaks metrics, evidence ids, or lineage beyond the declared claim class.
    Assumptions:
      - Claim scope is valid only when evidence_class, evaluated conditions, satisfied conditions, claims, metrics, and lineage all agree.
    Failure Modes:
      - Raises ScirHcDoctrineError.
    """

    _require(isinstance(report, dict), "benchmark report must be an object")
    claim_class = report.get("claim_class")
    _require(
        claim_class in CLAIM_SCOPE_RULES,
        f"benchmark report claim_class must be one of {sorted(CLAIM_SCOPE_RULES)}",
    )
    rule = CLAIM_SCOPE_RULES[claim_class]
    evidence_class = report.get("evidence_class")
    _require(isinstance(evidence_class, list) and evidence_class, "benchmark report must declare evidence_class")
    _require(
        len(evidence_class) == len(set(evidence_class)),
        "benchmark report evidence_class entries must be unique",
    )
    invalid_evidence = [item for item in evidence_class if item not in rule["evidence_ids"]]
    _require(
        not invalid_evidence,
        f"benchmark report evidence_class contains cross-class or forbidden evidence: {invalid_evidence!r}",
    )
    assert_no_semantic_authority(report)

    claim_gate = report.get("claim_gate")
    _require(isinstance(claim_gate, dict), "benchmark report claim_gate must be present")
    evaluated = claim_gate.get("evaluated_conditions")
    satisfied = claim_gate.get("satisfied_conditions")
    _require(isinstance(evaluated, list), "benchmark report claim_gate.evaluated_conditions must be a list")
    _require(isinstance(satisfied, list), "benchmark report claim_gate.satisfied_conditions must be a list")
    evaluated_ids = []
    metric_items = []
    for item in evaluated:
        _require(isinstance(item, dict), "benchmark report claim_gate.evaluated_conditions entries must be objects")
        evidence_id = item.get("id")
        _require(isinstance(evidence_id, str) and evidence_id, "benchmark report evaluated condition id is required")
        evaluated_ids.append(evidence_id)
        _require(
            evidence_id in rule["evidence_ids"],
            f"benchmark report evaluated condition {evidence_id!r} leaks outside claim_class {claim_class}",
        )
        metric = item.get("metric")
        _require(
            metric in rule["metric_names"],
            f"benchmark report evaluated condition metric {metric!r} exceeds claim_class {claim_class}",
        )
        expected_metric_class = rule["metric_classes"][metric]
        _require(
            item.get("metric_class") == expected_metric_class,
            f"benchmark report metric_class for {metric!r} must be {expected_metric_class}",
        )
        _require_scoped_claim_text(
            item.get("statement"),
            claim_class,
            f"evaluated condition {evidence_id!r} statement",
        )
        metric_items.append(item)
    _require(
        len(evaluated_ids) == len(set(evaluated_ids)),
        "benchmark report evaluated condition ids must be unique",
    )
    _require(
        set(evaluated_ids) == set(evidence_class),
        "benchmark report evidence_class must exactly match the evaluated claim evidence surface",
    )
    _require(
        len(satisfied) == len(set(satisfied)),
        "benchmark report satisfied_conditions entries must be unique",
    )
    invalid_satisfied = [item for item in satisfied if item not in rule["evidence_ids"]]
    _require(
        not invalid_satisfied,
        f"benchmark report satisfied_conditions contains cross-class evidence: {invalid_satisfied!r}",
    )
    _require(
        set(satisfied).issubset(set(evaluated_ids)),
        "benchmark report satisfied_conditions must be a subset of the evaluated claim evidence surface",
    )

    claims = report.get("claims")
    _require(isinstance(claims, list) and claims, "benchmark report must include at least one scoped claim")
    for claim in claims:
        _require(isinstance(claim, dict), "benchmark report claims entries must be objects")
        metric = claim.get("metric")
        _require(
            metric in rule["metric_names"],
            f"benchmark report claim metric {metric!r} exceeds claim_class {claim_class}",
        )
        expected_metric_class = rule["metric_classes"][metric]
        _require(
            claim.get("metric_class") == expected_metric_class,
            f"benchmark report metric_class for {metric!r} must be {expected_metric_class}",
        )
        _require_scoped_claim_text(claim.get("statement"), claim_class, "claim statement")
        metric_items.append(claim)

    assert_metric_authority(metric_items, claim_gate)
    assert_lineage_integrity(report, canonical_registry=canonical_registry)
