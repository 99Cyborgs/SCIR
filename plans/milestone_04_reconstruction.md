# Milestone 04 — Reconstruction
Status: proposed

## Objective

Define the reconstruction contract and evidence requirements for supported subsets.

## Scope

- `SCIR-H`-driven reconstruction
- preservation reporting
- provenance mapping to output
- compile/test and idiomaticity gates

## Non-goals

- exact source trivia preservation in canonical text
- reconstruction for unsupported whole-language features

## Touched files

- `docs/reconstruction_policy.md`
- `docs/preservation_contract.md`
- `schemas/preservation_report.schema.json`
- `schemas/reconstruction_report.schema.json`
- `VALIDATION_STRATEGY.md`

## Invariants

- reconstruction claims remain profile-qualified
- unsupported and opaque cases remain explicit
- compile/test evidence is mandatory

## Risks

- generated code becomes non-idiomatic
- preservation claims are overstated

## Validation steps

```bash
make validate
make benchmark
```

## Rollback strategy

Downgrade preservation claims and narrow the supported reconstruction subset.

## Evidence required for completion

- reconstruction contract document
- report schemas
- acceptance gates for compile/test/idiomaticity
