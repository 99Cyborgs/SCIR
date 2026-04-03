# Validator Contracts
Status: Normative

## Input and output contract

| Validator | Input | Output |
| --- | --- | --- |
| `SCIR-H` validator | canonical `SCIR-H` | `validation_report` |
| `SCIR-Hc` validator | derived `SCIR-Hc` plus canonical round-trip target | `validation_report` |
| `SCIR-L` validator | derivative `SCIR-L` | `validation_report` |
| preservation validator | paired stage artifacts and claims | `preservation_report` or failing `validation_report` |
| reconstruction checker | reconstructed source plus claims | `reconstruction_report` plus `preservation_report` |

## Active blocking conditions

- unsupported active grammar in canonical `SCIR-H`
- `SCIR-Hc` parse-format instability, missing generation context, authority-boundary drift, hidden-semantics drift, deterministic-derivation drift, lineage-integrity drift, semantic-idempotence drift, or semantic round-trip drift
- missing path, profile, or preservation level
- missing opaque-boundary contract where required
- missing or mismatched boundary capability metadata
- unused active effect rows or borrow-mode mutation violations
- missing `origin` or `lowering_rule` on active `SCIR-L`
- `origin` that no longer points back into the emitting `SCIR-H` module
- `SCIR-L` op outside the active subset
- `SCIR-Hc` entering lowering, reconstruction, or backend emission directly
- `benchmark_report` claim scope leaking `SCIR-Hc` evidence across claim classes, lineage coverage, or metric-class authority boundaries
- active TypeScript or `D-JS` claim
- active Track `D` claim
- importer-only `B`-tier cases producing active lowering or reconstruction artifacts

## Structural rejections

- reject pretty views as canonical storage
- reject any active construct not listed in `SPEC_COMPLETENESS_CHECKLIST.md`
- reject standalone `throw` syntax or broader `throw` effect discharge outside the importer-only Tier `B` `try/catch` slice
- reject preservation overclaims or unexplained downgrades against the active corpus expectations
- reject `SCIR-Hc` nodes that omit canonical information without `compression_origin` provenance
- reject `benchmark_report` claim/evidence mixes that generalize `SCIR-Hc` beyond the declared claim class
- reject `SCIR-Hc` lineage references that do not match canonical module lineage or normalized canonical hash
- reject `benchmark_report` metrics that imply semantic authority or causal semantics outside the declared evaluated evidence surface
- reject any Wasm claim that implies native or host parity
