# Milestone 03 — L Lowering
Status: complete

## Objective

Freeze `SCIR-L` v0.1 and the `SCIR-H -> SCIR-L` lowering contract.

## Scope

- frozen bootstrap `SCIR-L` grammar
- SSA and block-parameter rules
- effect and memory token rules
- provenance continuity
- translation-validation obligations
- milestone evidence for the existing executable lowering path

## Non-goals

- optimizer pass library
- backend-specific dialects
- reconstruction from `SCIR-L`

## Touched files

- `ARCHITECTURE.md`
- `specs/scir_l_spec.md`
- `specs/concurrency_model.md`
- `specs/validator_invariants.md`
- `validators/scir_l/AGENTS.md`
- `validators/translation/AGENTS.md`
- `validators/validator_contracts.md`
- `VALIDATION_STRATEGY.md`
- `scripts/scir_bootstrap_pipeline.py`
- `plans/milestone_03_l_lowering.md`

## Invariants

- `SCIR-L` stays derivative
- provenance survives lowering
- no `L`-only semantics

## Risks

- token model too weak or too heavy
- `SCIR-L` reconstructability expectations become overstated

## Validation steps

```bash
make validate
make benchmark
python scripts/scir_bootstrap_pipeline.py --mode validate
python scripts/scir_bootstrap_pipeline.py --mode test
```

## Rollback strategy

Reduce the `SCIR-L` opcode surface and push semantics back to `SCIR-H` where appropriate.

## Evidence required for completion

- frozen `SCIR-L` grammar
- explicit lowering invariants
- translation-validation contract
- executable bootstrap lowering matches the frozen op surface

## Completion evidence

- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed on 2026-03-16
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-16
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-16
- the frozen bootstrap `SCIR-L` surface is now documented as `const`, `cmp`, `alloc`, `store`, `load`, `call`, `async.resume`, `opaque.call`, and `ret`/`br`/`cond_br` with block parameters as the only merge mechanism
- translation validation now enforces `R/P1` for the Tier A cases and `D-PY/P3` for the opaque case
- `make` remains unavailable in this Windows shell, so milestone validation was verified through the underlying Python commands instead of direct `make` invocation
