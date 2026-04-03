# SCIR-Hc Doctrine Addendum
Status: Normative

## Authority Boundary

- `SCIR-H` is the only semantic source of truth.
- `SCIR-Hc` is a derived compression of validated `SCIR-H`, never a peer semantic layer.
- Serialized `SCIR-Hc` must carry the derived-only authority marker `~D`, which maps to `authority_boundary = "DERIVED_ONLY"`.
- Executable `SCIR-Hc` transforms are internal-only and must not remain on the public bootstrap-model API surface.
- Every executable `SCIR-Hc` transform entrypoint must require a validated generation context with `is_report_context = true`, a valid generation token, and a valid lineage root.
- `SCIR-Hc` must not be accepted as canonical input to lowering, reconstruction, backend emission, preservation reporting, or semantic validation claims.
- Any pipeline path that receives `input_representation == "SCIR-Hc"` for those downstream stages must hard-stop with `ForbiddenPathError`.

## Derivation Rules

- Derive `SCIR-Hc` only from normalized validated `SCIR-H`.
- `SCIR-H -> SCIR-Hc` derivation must be deterministic, idempotent, and context-independent.
- The validated generation context must bind the derivation to the canonical `SCIR-H` module id, semantic lineage id, and normalized canonical hash for the source module.
- The active executable compression surface may omit only:
  - inferable local binding types,
  - inferable function return types,
  - inferable function effect rows.
- Every omission-bearing compressed node must carry `compression_origin` metadata using only the enum members:
  - `INFERRED_TYPE`
  - `INFERRED_EFFECT`
  - `REDUNDANT_CAPABILITY`
  - `OWNERSHIP_ELISION`
- The compact text codec uses origin letters:
  - `T` -> `INFERRED_TYPE`
  - `E` -> `INFERRED_EFFECT`
  - `C` -> `REDUNDANT_CAPABILITY`
  - `O` -> `OWNERSHIP_ELISION`
- `REDUNDANT_CAPABILITY` remains reserved in the current executable subset until canonical capability syntax becomes active. The current validator must reject derivation attempts that depend on non-empty external capability lists.
- `OWNERSHIP_ELISION` is valid only when the omitted canonical type carries an active ownership marker such as `borrow<T>`, `borrow_mut<T>`, or `opaque<T>`.

## Round-Trip Obligations

- `format_scirhc_module(parse_scirhc_module(format_scirhc_module(scirh_to_scirhc(scirh))))` must equal `format_scirhc_module(scirh_to_scirhc(scirh))`.
- `normalize(scirh)` must equal `normalize(scirhc_to_scirh(scirh_to_scirhc(scirh)))`.
- Semantic idempotence must hold:
  - `normalize(scirh_to_scirh(scirh_to_scirhc(scirh))) == normalize(scirh)`
- Semantic lineage must be preserved:
  - `semantic_lineage_id(scirh) == semantic_lineage_id(scirhc_to_scirh(scirh_to_scirhc(scirh)))`
- Deterministic reconstruction must hold:
  - `scirh_to_scirhc(scirhc_to_scirh(scirh_to_scirhc(scirh))) == scirh_to_scirhc(scirh)`
- Any failure in these obligations is a blocking validator error, not a diagnostic-only warning.

## Benchmark Interpretation Rules

- `SCIR-Hc` evidence may support only these benchmark claim classes:
  - `LEXICAL_COMPRESSION_ONLY`
  - `GRAMMAR_REGULARITY_ONLY`
  - `PATCH_COMPOSABILITY_ONLY`
- Every `benchmark_report` that cites `SCIR-Hc` evidence must carry:
  - `representation = SCIR-Hc`
  - `scir_h_lineage_references`
  - `claim_class`
  - `evidence_class`
- Every evaluated condition and claim must carry:
  - `metric_class`
  - `scir_h_evidence`
- `evidence_class` must contain only evidence IDs valid for the declared `claim_class`.
- `claim_gate.evaluated_conditions`, `claim_gate.satisfied_conditions`, and `claims[*]` must stay inside the declared claim class.
- `claims[*].metric` must be present in `claim_gate.evaluated_conditions[*].metric`.
- `scir_h_lineage_references` must bind each cited canonical module to both semantic lineage id and normalized canonical hash.
- Every evaluated condition and claim must map to at least one cited canonical `SCIR-H` module.
- `metric_class = CAUSAL` is forbidden unless the report carries explicit `SCIR-H` evidence mapping for that metric inside the evaluated condition set.
- Metrics that imply semantic authority are invalid even when their enclosing claim text stays scoped.
- evaluated and claimed statement text must not use authority-escalation language such as `proves`, `guarantees`, or `establishes`.
- Cross-class inference is invalid.
- Implicit generalization is invalid.
- `SCIR-Hc` benchmark evidence must not be used to claim:
  - semantic preservation,
  - reconstruction fidelity,
  - cross-language equivalence,
  - semantic authority.

## Forbidden Uses

- Do not treat `SCIR-Hc` as canonical storage.
- Do not treat `SCIR-Hc` as a semantic disambiguation layer.
- Do not use `SCIR-Hc` directly as the source for `SCIR-H -> SCIR-L` lowering.
- Do not use `SCIR-Hc` directly as the source for Python reconstruction.
- Do not use `SCIR-Hc` directly as the source for backend emission.
- Do not encode semantics in `compression_origin` that are absent from canonical `SCIR-H`.
- Do not require heuristic or model-dependent reconstruction to recover canonical `SCIR-H`.

## Validation Requirements

- `validators/scirhc_validator.py` is the executable doctrine authority for `SCIR-Hc`.
- The following checks are mandatory and blocking:
  - `assert_not_semantic_authority(scirhc)`
  - `assert_no_semantic_authority(scirhc_obj)`
  - `assert_deterministic_derivation(scirh, scirhc)`
  - `assert_semantic_idempotence(scirh)`
  - `assert_round_trip_integrity(scirh)`
  - `assert_no_hidden_semantics(scirhc)`
  - `assert_lineage_integrity(report, canonical_registry)`
  - `assert_metric_authority(metrics, claim_gate)`
  - `assert_claim_scope_compliance(report, canonical_registry)`
- Report-producing paths must emit `scirhc_diff_audit.json` with structural diff, dropped fields, normalized fields, and compression statistics for the cited canonical `SCIR-H` modules.
- `SCIR-Hc` validation reports must fail hard on any authority-boundary drift, unexplained omission, derivation mismatch, lineage spoofing, incomplete lineage coverage, round-trip drift, semantic-idempotence drift, metric-authority leakage, or benchmark-claim overreach.
- `tests/test_scirhc_doctrine.py` must cover missing context, non-report context, invalid lineage hash, incomplete lineage coverage, causal-metric leakage, metric-authority leakage, round-trip failure, illegal pipeline use, and direct public transform access.

## Failure Modes

- Authority drift: `SCIR-Hc` is accepted where canonical `SCIR-H` is required.
- Non-deterministic compression: repeated derivation yields different `SCIR-Hc` for the same normalized `SCIR-H`.
- Lineage spoofing: an `SCIR-Hc` artifact or benchmark report cites canonical lineage without matching the normalized canonical hash.
- Hidden semantic injection: omitted information is not explainable by `compression_origin`.
- Round-trip drift: reconstructed canonical `SCIR-H` changes lineage or canonical formatting.
- Metric authority leakage: a metric class or metric payload implies semantic authority or causality outside the declared evidence surface.
- Benchmark leakage: `SCIR-Hc` evidence is generalized beyond the declared claim class.
- The detailed operator-facing registry for these failure modes lives in `docs/SCIR_HC_FAILURE_MODES.md`.
