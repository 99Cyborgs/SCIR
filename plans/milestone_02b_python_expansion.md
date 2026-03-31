# Milestone 02B - Python Expansion
Status: in-progress

## Objective

Act as the active near-term architecture milestone for Python importer expansion after the completed five-case Milestone 02 bootstrap slice.

## Scope

- additional Python function and `async def` shapes beyond the fixed bootstrap corpus
- classes with explicit instance fields
- `for` and `while`
- `raise`
- straightforward comprehensions with explicit normalization
- follow-on fixture corpus and conformance updates required for any accepted expansion
- importer-only acceptance unless and until lowering, reconstruction, and benchmark doctrine are updated for a named construct

## Non-goals

- changing the completed Milestone 02 bootstrap acceptance surface
- hidden support for reflection-heavy or monkey-patched semantics
- import hooks, metaclass rewrites, or broad dynamic protocol support

## Touched files

- `frontend/python/IMPORT_SCOPE.md`
- `frontend/python/AGENTS.md`
- `docs/feature_tiering.md`
- `docs/unsupported_cases.md`
- `scripts/python_importer_conformance.py`
- `tests/python_importer/cases/*`
- `plans/milestone_02b_python_expansion.md`

## Invariants

- the completed Milestone 02 five-case corpus remains the bootstrap acceptance floor
- every new accepted construct must be fixture-backed and tier-explicit
- unsupported or opaque Python semantics remain explicit
- importer acceptance alone does not widen executable claims

## Risks

- Python expansion can overclaim support faster than fixture and validator evidence grows
- class, loop, and exception semantics can push host-sensitive behavior beyond the current bootstrap doctrine

## Validation steps

```bash
python scripts/python_importer_conformance.py --mode validate-fixtures
python scripts/python_importer_conformance.py --mode test
python scripts/run_repo_validation.py --require-rust
make validate
make benchmark
```

## Rollback strategy

Keep rejected or deferred constructs outside the accepted fixture corpus rather than weakening bootstrap-only guarantees.

## Evidence required for completion

- accepted follow-on Python constructs are explicitly scoped
- new fixture cases and conformance expectations exist for every accepted construct
- doctrine and unsupported-case language stay synchronized with the accepted expansion
- any executable claim for a new construct is backed by explicit lowering, reconstruction, and benchmark doctrine updates

## Current slice evidence

- the checked-in importer conformance corpus already includes `b_class_field_update` as a bounded Tier `B` importer-only case
- `frontend/python/IMPORT_SCOPE.md`, `scripts/scir_python_bootstrap.py`, `scripts/python_importer_conformance.py`, `scripts/scir_bootstrap_pipeline.py`, and `VALIDATION_STRATEGY.md` all treat `b_class_field_update` as admitted and importer-only
- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on `2026-03-27`
- `python scripts/python_importer_conformance.py --mode test` passed on `2026-03-27`
- `python scripts/run_repo_validation.py` passed on `2026-03-27` with an explicit Rust skip after detecting that the active GNU toolchain was unusable and the installed MSVC fallback could not link because `link.exe` was unavailable
- `python scripts/run_repo_validation.py --require-rust` failed on `2026-03-27` with that same precise toolchain diagnosis
- `python scripts/run_repo_validation.py --require-rust` passed on `2026-03-30` after the local Windows environment exposed the MSVC compiler and linker in the active shell
- `python scripts/benchmark_contract_dry_run.py` passed on `2026-03-30` under that same Rust-inclusive environment
- the bounded class field-update slice is therefore fully validated and remains importer-only with no widened lowering, reconstruction, or benchmark claim for the admitted 02B follow-on cases
- Milestone 02B remains `in-progress` only because explicit closeout and next-phase handoff recording is still pending
