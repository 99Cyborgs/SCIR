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
