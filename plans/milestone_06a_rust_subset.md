# Milestone 06A - Rust Safe-Subset Importer
Status: complete

## Objective

Land the first executable Rust frontend slice on the narrow credible path: fixed fixtures, canonical `SCIR-H`, derivative `SCIR-L`, and Tier `A` Rust round-trip evidence.

## Scope

- fixed Rust bootstrap corpus under `tests/rust_importer/cases/`
- executable Rust importer and conformance checker
- minimal `SCIR-H` field-place clarification
- minimal `SCIR-L` `field.addr` lowering for borrowed-record fields
- Rust round-trip reconstruction for Tier `A` cases
- explicit Tier `C` unsafe boundary handling

## Non-goals

- traits, impl dispatch, methods, closures, generics, macros beyond rejection
- full Rust parsing
- Track `D` runtime benchmarks
- profile-gated optimization work

## Touched files

- `IMPLEMENTATION_PLAN.md`
- `specs/scir_h_spec.md`
- `specs/scir_l_spec.md`
- `VALIDATION_STRATEGY.md`
- `frontend/rust/IMPORT_SCOPE.md`
- `scripts/scir_rust_bootstrap.py`
- `scripts/rust_importer_conformance.py`
- `scripts/scir_bootstrap_pipeline.py`
- `tests/rust_importer/cases/*`

## Invariants

- Rust support remains fixture-locked in Phase 6A
- `SCIR-H` remains the semantic source of truth
- `SCIR-L` remains derivative
- Tier `C` unsafe boundaries remain explicit
- optimization claims remain deferred to Phase 6B

## Risks

- Rust field-place support may broaden faster than the validator contract if specs drift
- future Rust scope expansion may pressure the frozen `field.addr` lowering surface before Phase 6B is defined

## Validation steps

```bash
python scripts/rust_importer_conformance.py --mode validate-fixtures
python scripts/rust_importer_conformance.py --mode test
python scripts/scir_bootstrap_pipeline.py --language rust --mode validate
python scripts/scir_bootstrap_pipeline.py --language rust --mode test
make test
make validate
make benchmark
```

## Rollback strategy

Remove the Rust executable path, preserve the Python executable path, and return Phase 6 to a planned-only state if the safe subset cannot clear its explicit fixture and toolchain gates.

## Evidence required for completion

- checked-in Rust fixture corpus
- generated-vs-golden Rust importer conformance
- canonical `SCIR-H` and `SCIR-L` outputs for supported Rust cases
- Tier `A` Rust compile/test round-trip evidence
- decision register update for the Phase 6A split and minimal semantic extensions

## Completion evidence

- `python scripts/rust_importer_conformance.py --mode validate-fixtures` passed on 2026-03-16
- `python scripts/rust_importer_conformance.py --mode test` passed on 2026-03-16
- `rustc --version` reported `rustc 1.94.0 (4a4ef493e 2026-03-02)` on 2026-03-17
- `cargo --version` reported `cargo 1.94.0 (85eff7c80 2026-01-15)` on 2026-03-17
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate` passed on 2026-03-17
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode test` passed on 2026-03-17
- `python scripts/run_repo_validation.py --require-rust` passed on 2026-03-17
- `make test` passed on 2026-03-17
- `make validate` passed on 2026-03-17
- `make benchmark` passed on 2026-03-17
- the Rust executable importer, fixed fixture corpus, and language-dispatched pipeline are present on disk
- Phase 6A gate is satisfied with toolchain-backed Tier `A` compile/test evidence and explicit Tier `C` unsafe-boundary preservation
