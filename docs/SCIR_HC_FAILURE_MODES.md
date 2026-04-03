# SCIR-Hc Failure Modes
Status: Informative

## lexical gain without task gain

- detection signal: `SCIR-Hc` token metrics improve while Track `B` or scoped claim evidence does not improve in the declared claim class
- validator hook: `assert_claim_scope_compliance(report)` plus the active Track `A` / `B` claim-gate checks
- mitigation: treat the gain as lexical-only diagnostic evidence and reject any broader AI-thesis or semantic claim

## non-deterministic compression

- detection signal: `scirh_to_scirhc(scirh)` differs across repeated derivations or differs from `scirh_to_scirhc(scirhc_to_scirh(scirhc))`
- validator hook: `assert_deterministic_derivation(scirh, scirhc)`
- mitigation: block the artifact, remove context-dependent compression logic, and keep only deterministic omission rules derived from canonical `SCIR-H`

## lineage spoofing

- detection signal: an `SCIR-Hc` artifact or benchmark report carries `scir_h_lineage_references` that do not match the cited canonical module semantic lineage id or normalized canonical hash
- validator hook: `assert_lineage_integrity(report, canonical_registry)`
- mitigation: rebuild the artifact from validated canonical `SCIR-H`, regenerate the lineage-bound token, and reject any partially bound or hand-edited lineage payload

## hidden semantic injection

- detection signal: compressed nodes omit canonical information without valid `compression_origin` metadata, or provenance metadata appears on nodes that keep the canonical field explicit
- validator hook: `assert_no_hidden_semantics(scirhc)`
- mitigation: restore the omitted canonical field or emit the correct machine-readable provenance; do not recover meaning through heuristics

## benchmark leakage

- detection signal: `benchmark_report` mixes evidence or claims across `claim_class` boundaries, or `SCIR-Hc` evidence is used to imply preservation, reconstruction fidelity, or cross-language equivalence
- validator hook: `assert_claim_scope_compliance(report)`
- mitigation: narrow the report to one claim class, keep non-matching evidence diagnostic only, and reject overreaching claims

## invalid reconstruction equivalence

- detection signal: `SCIR-H -> SCIR-Hc -> SCIR-H` changes semantic lineage, canonical formatting, or deterministic re-derivation output
- validator hook: `assert_round_trip_integrity(scirh)`
- mitigation: stop the pipeline, restore the lost canonical information, and keep `SCIR-Hc` out of downstream semantic paths until the round-trip is exact again

## payload-level claim leakage

- mechanism: a benchmark report reuses valid `SCIR-Hc` evidence IDs while changing the metric or statement payload to carry claims outside the declared evidence scope
- detection method: compare `claim_gate.evaluated_conditions[*]`, `claim_gate.satisfied_conditions`, `claims[*]`, and `claim_class` through `assert_claim_scope_compliance(report)`
- enforcement layer: validator and benchmark claim-audit checks
- mitigation: force claims and evaluated conditions back onto the declared evidence surface and reject any metric not present in the evaluated condition set

## semantic authority escalation

- mechanism: `SCIR-Hc` report payloads use authority language such as `proves`, `guarantees`, or `establishes`, or add reserved authority-bearing fields
- detection method: inspect report statements and reserved field names through `assert_no_semantic_authority(...)`
- enforcement layer: validator and benchmark-report schema
- mitigation: strip authority language, keep only scoped benchmark evidence, and retain canonical `SCIR-H` as the sole semantic authority

## metric authority leakage

- mechanism: a metric name, metric class, or metric payload implies semantic authority or causality outside the declared evaluated evidence set even if the enclosing claim text stays superficially scoped
- detection method: inspect `metric_class`, `scir_h_evidence`, and metric/statement payloads through `assert_metric_authority(...)`
- enforcement layer: validator and benchmark claim audit
- mitigation: reclassify or remove the metric, bind it to explicit canonical `SCIR-H` evidence when allowed, and reject any authority-implying metric surface

## round-trip normalization drift

- mechanism: reconstructed canonical `SCIR-H` differs from normalized source even if formatting or lineage checks would otherwise look stable
- detection method: direct normalized-model equality in `assert_round_trip_integrity(scirh)`
- enforcement layer: validator
- mitigation: restore the omitted canonical information and reject the compressed artifact until normalized equality is exact again

## pipeline privilege violation

- mechanism: `SCIR-Hc` is passed into lowering, reconstruction, backend emission, or an executable transform is invoked without validated report-scoped generation context
- detection method: `assert_canonical_pipeline_input(...)`, `make_scirhc_generation_context(...)`, and internal transform access checks reject `SCIR-Hc` outside canonical-input and report-only generation boundaries
- enforcement layer: pipeline
- mitigation: route all semantic work through canonical `SCIR-H` and keep `SCIR-Hc` generation restricted to validation/benchmark reporting surfaces

## cross-class report contamination

- mechanism: a benchmark report marked as `SCIR-Hc` carries disallowed semantic fields, backend/lowering outputs, or omits canonical lineage references
- detection method: schema validation against `schemas/benchmark_report.schema.json` plus benchmark claim-audit checks
- enforcement layer: schema and benchmark claim audit
- mitigation: keep the report surface limited to scoped benchmark evidence, explicit SCIR-H lineage references, and the declared audit artifacts only
