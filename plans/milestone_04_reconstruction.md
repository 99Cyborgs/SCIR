# Milestone 04 — Reconstruction
Status: complete

## Objective

Define the reconstruction contract and evidence requirements for supported subsets.

## Scope

- `SCIR-H`-driven reconstruction
- preservation reporting
- provenance mapping to output
- compile/test and idiomaticity evidence

## Non-goals

- exact source trivia preservation in canonical text
- reconstruction for unsupported whole-language features

## Touched files

- `ARCHITECTURE.md`
- `docs/reconstruction_policy.md`
- `docs/preservation_contract.md`
- `validators/validator_contracts.md`
- `VALIDATION_STRATEGY.md`
- `scripts/scir_bootstrap_pipeline.py`
- `DECISION_REGISTER.md`
- `reports/exports/decision_register.export.json`
- `plans/milestone_04_reconstruction.md`

## Invariants

- reconstruction claims remain profile-qualified
- unsupported and opaque cases remain explicit
- compile/test evidence is mandatory
- `SCIR-L` remains diagnostic support, not the default reconstruction source

## Risks

- generated code becomes non-idiomatic
- preservation claims are overstated

## Validation steps

```bash
make validate
make benchmark
python scripts/scir_bootstrap_pipeline.py --mode validate
python scripts/scir_bootstrap_pipeline.py --mode test
```

## Rollback strategy

Downgrade preservation claims and narrow the supported reconstruction subset.

## Evidence required for completion

- reconstruction contract document
- acceptance gates for compile/test/provenance
- executable reconstruction validation for the bootstrap supported subset

## Completion evidence

- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed on 2026-03-16
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-16
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-16
- the bootstrap reconstruction contract is now frozen to `R/P1` for `a_basic_function` and `a_async_await`, and `D-PY/P3` with explicit opaque accounting for `c_opaque_call`
- reconstruction validation now blocks on compile/test evidence, line-granular provenance completeness, and opaque-accounting correctness while keeping idiomaticity as required evidence rather than a hard gate
- rejected Tier `D` cases remain importer-only failures and do not emit reconstruction artifacts
- `make` remains unavailable in this Windows shell, so milestone validation was verified through the underlying Python commands instead of direct `make` invocation
