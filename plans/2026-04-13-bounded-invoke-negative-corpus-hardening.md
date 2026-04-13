# Bounded Invoke Negative Corpus Hardening

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Externalize the bounded `invoke`/catch validation guarantees for the frozen `d_try_except` lowering shape into the checked-in invalid `SCIR-L` corpus.

## Scope

- add invalid lowered `SCIR-L` fixtures for exact bounded `invoke` shape drift
- update the invalid `SCIR-L` manifest with stable hashes and expected diagnostic codes
- keep the negative-fixture README aligned with the new coverage

## Non-goals

- no semantic widening of `SCIR-H` or `SCIR-L`
- no new proof-loop admissions
- no changes to positive lowering artifacts or translation semantics
- no benchmark, Rust, or Wasm scope changes

## Touched files

- plans/2026-04-13-bounded-invoke-negative-corpus-hardening.md
- tests/invalid_scir_l/manifest.json
- tests/invalid_scir_l/README.md
- tests/invalid_scir_l/invalid_invoke_catch_type.json
- tests/invalid_scir_l/invalid_invoke_effect_token.json

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only and subset-bound
- the active exceptional lowering form stays limited to the exact `d_try_except` `invoke`/`ValueError` slice
- invalid-corpus hardening must not introduce new accepted executable shapes

## Risks

- expected diagnostic-code selection must match the current validator mapping rather than an aspirational future split
- fixture hashes must match the committed file contents exactly or manifest validation will fail

## Validation steps

- python scripts/scir_bootstrap_pipeline.py --mode test
- python scripts/run_repo_validation.py

## Rollback strategy

Remove the added invalid fixtures and manifest entries together if they conflict with the current validator’s actual bounded `invoke` contract.

## Evidence required for completion

- diff review shows the invalid `SCIR-L` corpus now covers bounded `invoke` catch-type and effect-token drift
- python scripts/scir_bootstrap_pipeline.py --mode test
- python scripts/run_repo_validation.py

## Completion evidence

- diff review shows the invalid `SCIR-L` corpus now covers bounded `invoke` catch-type drift (`L001`) and trailing invoke effect-token drift (`L003`)
- direct validator probe over `tests/invalid_scir_l/invalid_invoke_catch_type.json` produced `L001`
- direct validator probe over `tests/invalid_scir_l/invalid_invoke_effect_token.json` produced `L003`
- python scripts/run_repo_validation.py passed
- make validate passed
