from __future__ import annotations

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
    format_module,
    format_scirhc_module,
    normalize_hc_module,
    normalize_module,
    parse_scirhc_module,
    scirh_to_scirhc,
    scirhc_to_scirh,
    semantic_lineage_id,
)


class ScirHcDoctrineError(ValueError):
    pass


DEFAULT_BENCHMARK_CLAIM_CLASS = "LEXICAL_COMPRESSION_ONLY"
CLAIM_SCOPE_RULES = {
    "LEXICAL_COMPRESSION_ONLY": {
        "evidence_ids": {"scirhc_lcr_vs_ast"},
        "metric_names": {"LCR_scirhc"},
    },
    "GRAMMAR_REGULARITY_ONLY": {
        "evidence_ids": {"scirhc_gr_vs_ast"},
        "metric_names": {"GR_scirhc"},
    },
    "PATCH_COMPOSABILITY_ONLY": {
        "evidence_ids": {"patch_composability_vs_ast"},
        "metric_names": {"patch_composability_gain_vs_typed_ast", "SCPR_scirhc"},
    },
}
FORBIDDEN_CLAIM_TERMS = (
    "semantic preservation",
    "reconstruction fidelity",
    "cross-language equivalence",
    "cross language equivalence",
)


def _walk_hc_statements(body):
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
    if not condition:
        raise ScirHcDoctrineError(message)


def _normalize_scirhc(scirhc: HcModule) -> HcModule:
    try:
        return normalize_hc_module(scirhc)
    except ScirHModelError as exc:
        raise ScirHcDoctrineError(str(exc)) from exc


def assert_not_semantic_authority(scirhc: HcModule) -> None:
    normalized = _normalize_scirhc(scirhc)
    _require(
        normalized.authority_boundary == SCIRHC_AUTHORITY_BOUNDARY,
        "SCIR-Hc must declare the derived-only authority boundary",
    )


def assert_no_hidden_semantics(scirhc: HcModule) -> None:
    normalized = _normalize_scirhc(scirhc)
    assert_not_semantic_authority(normalized)

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
    normalized_scirh = normalize_module(scirh)
    normalized_scirhc = _normalize_scirhc(scirhc)
    assert_no_hidden_semantics(normalized_scirhc)
    expected = scirh_to_scirhc(normalized_scirh)
    _require(
        normalized_scirhc == expected,
        "SCIR-H -> SCIR-Hc derivation must be deterministic, idempotent, and context-independent",
    )
    reconstructed = scirhc_to_scirh(normalized_scirhc)
    _require(
        scirh_to_scirhc(reconstructed) == expected,
        "SCIR-Hc must remain idempotent under canonical SCIR-H reconstruction",
    )


def assert_round_trip_integrity(scirh: Module) -> None:
    normalized = normalize_module(scirh)
    derived = scirh_to_scirhc(normalized)
    rendered = format_scirhc_module(derived)
    reparsed = parse_scirhc_module(rendered)
    _require(reparsed == derived, "SCIR-Hc storage must remain stable under parse-format equality")
    reconstructed = scirhc_to_scirh(reparsed)
    _require(
        semantic_lineage_id(reconstructed) == semantic_lineage_id(normalized),
        "SCIR-Hc round-trip must preserve SCIR-H semantic lineage",
    )
    _require(
        format_module(reconstructed) == format_module(normalized),
        "SCIR-Hc round-trip must preserve normalized canonical SCIR-H formatting",
    )
    _require(
        scirh_to_scirhc(reconstructed) == derived,
        "SCIR-Hc round-trip must preserve deterministic derivation output",
    )


def assert_claim_scope_compliance(report: dict) -> None:
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

    claim_gate = report.get("claim_gate")
    _require(isinstance(claim_gate, dict), "benchmark report claim_gate must be present")
    evaluated = claim_gate.get("evaluated_conditions")
    satisfied = claim_gate.get("satisfied_conditions")
    _require(isinstance(evaluated, list), "benchmark report claim_gate.evaluated_conditions must be a list")
    _require(isinstance(satisfied, list), "benchmark report claim_gate.satisfied_conditions must be a list")
    evaluated_ids = []
    for item in evaluated:
        _require(isinstance(item, dict), "benchmark report claim_gate.evaluated_conditions entries must be objects")
        evidence_id = item.get("id")
        _require(isinstance(evidence_id, str) and evidence_id, "benchmark report evaluated condition id is required")
        evaluated_ids.append(evidence_id)
        _require(
            evidence_id in rule["evidence_ids"],
            f"benchmark report evaluated condition {evidence_id!r} leaks outside claim_class {claim_class}",
        )
    _require(
        set(evaluated_ids) == set(evidence_class),
        "benchmark report evidence_class must exactly match the evaluated claim evidence surface",
    )
    invalid_satisfied = [item for item in satisfied if item not in rule["evidence_ids"]]
    _require(
        not invalid_satisfied,
        f"benchmark report satisfied_conditions contains cross-class evidence: {invalid_satisfied!r}",
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
        statement = claim.get("statement")
        _require(isinstance(statement, str) and statement, "benchmark report claim statements must be non-empty")
        lowered = statement.lower()
        _require(
            not any(term in lowered for term in FORBIDDEN_CLAIM_TERMS),
            f"benchmark report claim statement overreaches beyond {claim_class}",
        )
