# Milestone 03 — L Lowering
Status: proposed

## Objective

Freeze `SCIR-L` v0.1 and the `SCIR-H -> SCIR-L` lowering contract.

## Scope

- `SCIR-L` grammar
- SSA and block-parameter rules
- effect and memory token rules
- provenance continuity
- translation-validation obligations

## Non-goals

- optimizer pass library
- backend-specific dialects
- reconstruction from `SCIR-L`

## Touched files

- `specs/scir_l_spec.md`
- `specs/concurrency_model.md`
- `specs/validator_invariants.md`
- `validators/scir_l/AGENTS.md`
- `validators/translation/AGENTS.md`
- `validators/validator_contracts.md`
- `VALIDATION_STRATEGY.md`

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
```

## Rollback strategy

Reduce the `SCIR-L` opcode surface and push semantics back to `SCIR-H` where appropriate.

## Evidence required for completion

- frozen `SCIR-L` grammar
- explicit lowering invariants
- translation-validation contract
