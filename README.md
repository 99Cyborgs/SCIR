# SCIR
Status: Informative

SCIR is a two-layer semantic compression substrate.

- `SCIR-H` is the canonical high-level semantic representation.
- `SCIR-L` is the lowered control and analysis form.
- The first credible product is importer + validator + lowering + reconstruction + benchmark harness.
- The first credible product is not a mass-market source language.

## Repository purpose

This repository is a Codex ingestion artifact pack. It is documentation-first and contract-first. It exists to remove ambiguity before large-scale code generation begins.

## Read order

1. `AGENTS.md`
2. `SYSTEM_BOUNDARY.md`
3. `ARCHITECTURE.md`
4. `specs/scir_h_spec.md`
5. `specs/scir_l_spec.md`
6. `specs/type_effect_capability_model.md`
7. `specs/ownership_alias_model.md`
8. `specs/interop_and_opaque_boundary_spec.md`
9. `specs/validator_invariants.md`
10. `VALIDATION_STRATEGY.md`
11. `BENCHMARK_STRATEGY.md`
12. `IMPLEMENTATION_PLAN.md`
13. `plans/PLANS.md`

## Command contract

Bootstrap commands are defined in `Makefile`.

```bash
make build
make lint
make test
make validate
make benchmark
make ci
```

Current behavior:

- `build` validates the artifact pack; there are no compiled binaries yet.
- `lint` checks repository contracts and schema parseability.
- `test` runs the bootstrap repository checks, including negative self-tests for the repository checker.
- `validate` is the blocking repository validation target and validates checked-in example report bundles against the published schemas plus the derived decision-register and open-questions exports against their markdown sources.
- `benchmark` runs a benchmark-contract dry run, including negative self-tests for the benchmark checker. It does not execute model or runtime benchmarks yet.
- `ci` runs `validate` then `benchmark`.

## Non-negotiable doctrine

- Every preservation claim is profile-qualified: `R`, `N`, `P`, or `D`.
- Every preservation label uses `P0`, `P1`, `P2`, `P3`, or `PX`.
- Every source coverage claim uses `Tier A`, `B`, `C`, or `D`.
- Unsupported cases and opaque boundaries must be explicit.
- `SCIR-H` is the canonical semantic source of truth.
- `SCIR-L` is derivative. It must not gain independent semantics.
- Benchmark-first evaluation is mandatory. Direct-source and typed-AST baselines are mandatory.
- Architecture changes are incomplete until the affected specs, docs, validators, benchmarks, and decision register entries are updated together.

## Directory summary

- `docs/` explanatory project doctrine
- `specs/` normative semantic and validator contracts
- `schemas/` machine-readable JSON Schemas for reports and manifests
- `plans/` execution plans and milestone seeds
- `frontend/` importer doctrine and language-local scope
- `validators/` validator stack rules
- `benchmarks/` evaluation doctrine
- `reports/` checked-in example bundles, derived exports, and future generated outputs
- `tooling/` tool contracts
- `ci/` CI and release policy
- `.github/` automation entry points
- `scripts/` bootstrap repository validation helpers

## Current implementation stance

Phase 1 is documentation- and contract-complete, code-light:

- freeze `SCIR-H` core,
- freeze validator invariants,
- freeze report schemas,
- freeze benchmark doctrine,
- then build Python subset import,
- then `H -> L`,
- then reconstruction,
- then benchmark harness,
- then Rust subset and optimization work.
