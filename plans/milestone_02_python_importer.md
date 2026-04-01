# Milestone 02 - Python Importer
Status: complete

## Objective

Freeze and validate the targeted Python subset importer contract for `SCIR-H`.

## Scope

- Python subset scope
- checked-in fixture corpus for the fixed executable bootstrap slice
- importer conformance checker for those fixtures
- tier classification rules
- explicit unsupported and opaque boundaries
- importer outputs: module manifest, feature tier report, validation report

## Non-goals

- broad Python reflection support
- executable importer breadth beyond the fixture-backed bootstrap slice
- Python `try/except` in the bootstrap slice
- Python `raise` mapping in the bootstrap slice
- import hooks
- metaclass-heavy frameworks
- monkey patching fidelity
- classes
- loops
- comprehensions

## Touched files

- `frontend/README.md`
- `frontend/python/AGENTS.md`
- `frontend/python/IMPORT_SCOPE.md`
- `Makefile`
- `scripts/python_importer_conformance.py`
- `tests/python_importer/cases/*`
- `tests/README.md`
- `README.md`
- `ci/validation_pipeline.md`
- `docs/repository_map.md`
- `VALIDATION_STRATEGY.md`

## Invariants

- no silent Tier `C` or `D` fallback
- host-sensitive semantics remain profile-qualified
- unsupported Python features stay explicit

## Risks

- subset too narrow to be useful
- fixture goldens could drift from the intended subset if not conformance-checked
- deferred Python expansion could be mistaken for already accepted Milestone 02 scope if the bootstrap-only boundary is not kept explicit

## Validation steps

```bash
make validate
python scripts/python_importer_conformance.py --mode validate-fixtures
python scripts/python_importer_conformance.py --mode test
make benchmark
```

## Rollback strategy

Narrow the importer scope and remove over-claims rather than adding hidden runtime behavior.

## Evidence required for completion

- explicit Python scope file
- fixture-backed importer acceptance corpus
- importer report contract
- conformance checker for the bootstrap fixture corpus
- benchmark doctrine still coherent for the subset

## Final Milestone 02 slice

Milestone 02 is fixed to this five-case bootstrap corpus:

- `a_basic_function`
- `a_async_await`
- `c_opaque_call`
- `d_exec_eval`
- `d_try_except`

This is the completed Milestone 02 acceptance surface. Broader Python coverage is deferred to `plans/milestone_02b_python_expansion.md` and is not implied by this milestone.

## Completion evidence

- the executable bootstrap importer reproduces the checked-in fixture bundles for the five accepted cases
- generated-vs-golden importer conformance, bootstrap lowering, reconstruction, and Track A/B benchmark execution pass on the fixed bootstrap corpus
- the bootstrap `SCIR-H` surface uses the compact canonical parser/formatter path (`var`, `set`, direct calls, intrinsic comparisons, indentation-sensitive suites)
- Track `A` gate execution follows the published median-ratio rules and the bootstrap corpus clears `K2`
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-18
- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on 2026-03-18
- `python scripts/python_importer_conformance.py --mode test` passed on 2026-03-18
- `python scripts/run_repo_validation.py --require-rust` passed on 2026-03-18
- `make validate` passed on 2026-03-18
- `make benchmark` passed on 2026-03-18
