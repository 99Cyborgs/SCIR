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
3. `REPO_MAP.md`
4. `ARCHITECTURE.md`
5. `specs/scir_h_spec.md`
6. `specs/scir_l_spec.md`
7. `specs/type_effect_capability_model.md`
8. `specs/ownership_alias_model.md`
9. `specs/interop_and_opaque_boundary_spec.md`
10. `specs/validator_invariants.md`
11. `VALIDATION_STRATEGY.md`
12. `BENCHMARK_STRATEGY.md`
13. `IMPLEMENTATION_PLAN.md`
14. `plans/PLANS.md`
15. `EXECUTION_QUEUE.md`

## Command contract

Use the direct Python validation runner as the canonical Windows-safe entrypoint:

```bash
python scripts/run_repo_validation.py
```

For the full Rust-inclusive validation path:

```bash
python scripts/run_repo_validation.py --require-rust
```

The `Makefile` remains a convenience wrapper around the same underlying commands.

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
- `test` runs the bootstrap repository checks, Python importer generated-vs-golden conformance self-tests, Rust importer generated-vs-golden conformance self-tests, the Python bootstrap lowering/reconstruction self-tests, and the Rust Phase 6A self-tests.
- `validate` is the blocking repository validation target and validates checked-in example report bundles, derived exports including the autonomous execution queue export, the checked-in Python, TypeScript, and Rust importer fixture corpora, the executable Python bootstrap importer/lowering/reconstruction path, and the executable Rust Phase 6A path.
- `benchmark` runs benchmark doctrine checks plus manifest-driven Track `A`, Track `B`, Rust `N` Track `D`, and Python `D-PY` Track `D` harnesses on the fixed bootstrap corpus. Track `A` reports both median and aggregate token ratios while enforcing the published median-based gates. `D-JS` and Track `C` remain doctrine-only.
- `ci` runs `validate` then `benchmark`.
- the Windows-safe validation runner reports the Rust validation and executable benchmark slices as skipped when `rustc` and `cargo` are unavailable
- `python scripts/run_repo_validation.py --require-rust` and `make validate` keep Rust toolchain availability as a hard requirement when Rust validation is in scope

Direct Python equivalents:

```bash
python scripts/validate_repo_contracts.py --mode validate
python scripts/build_execution_queue.py --mode check
python scripts/python_importer_conformance.py --mode validate-fixtures
python scripts/typescript_importer_conformance.py --mode validate-fixtures
python scripts/scir_bootstrap_pipeline.py --mode validate
python scripts/benchmark_contract_dry_run.py
```

Optional Rust slice:

```bash
python scripts/rust_importer_conformance.py --mode validate-fixtures
python scripts/scir_bootstrap_pipeline.py --language rust --mode validate
```

## Non-negotiable doctrine

- Every preservation claim is profile-qualified: `R`, `N`, `P`, `D-PY`, or `D-JS`.
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
- `tests/` checked-in golden corpora and importer conformance fixtures
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
- bootstrap the Python importer with checked-in fixtures before executable importer breadth,
- then build the executable Python subset import on that fixed bootstrap slice,
- then compact the canonical bootstrap `SCIR-H` surface and correct Track `A` median-gate execution on that slice,
- then `H -> L` and reconstruction on the same slice,
- then Track `A` and Track `B` benchmark execution for that slice,
- then Rust safe-subset importer and round-trip work,
- then profile-gated optimization work.

Current roadmap after the completed Phase 6B cut:

- Milestone 02B is the active near-term Python expansion track and remains fixture-backed plus importer-first until downstream doctrine widens,
- `EXECUTION_QUEUE.md` is the canonical low-touch execution queue derived from the roadmap and active milestone docs,
- the next new architecture phase is witness-bearing second-language evidence through a TypeScript interface-shaped slice,
- `D-JS` remains doctrine-only during that witness milestone unless a later plan adds explicit executable contracts,
- no new backend track is on the immediate roadmap.
