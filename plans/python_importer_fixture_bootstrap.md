# Python Importer Fixture Bootstrap

Status: complete
Owner: Codex
Date: 2026-03-16

## Objective

Create the first checked-in Python importer acceptance corpus and conformance checker so Milestone 02 starts from fixed fixture targets instead of ad hoc importer behavior.

## Scope

- freeze the first fixture-backed Python subset
- add checked-in `A`, `C`, and `D` case bundles under `tests/`
- add a Python importer conformance checker with negative self-tests
- wire the checker into `make test` and `make validate`
- update milestone, validation, frontend, README, and repository-map docs for the new fixture surface

## Non-goals

- implementing an executable Python importer
- expanding the bootstrap slice to classes, loops, comprehensions, `raise`, or `try/except`
- changing schemas
- touching `SCIR-L`, reconstruction, or benchmark-harness behavior

## Touched files

- `plans/python_importer_fixture_bootstrap.md`
- `plans/milestone_02_python_importer.md`
- `Makefile`
- `README.md`
- `VALIDATION_STRATEGY.md`
- `ci/validation_pipeline.md`
- `frontend/README.md`
- `frontend/python/AGENTS.md`
- `frontend/python/IMPORT_SCOPE.md`
- `docs/repository_map.md`
- `scripts/python_importer_conformance.py`
- `tests/README.md`
- `tests/python_importer/cases/*`

## Invariants that must remain true

- frontends still emit `SCIR-H`, not `SCIR-L`
- unsupported Python behavior stays explicit as Tier `C` or `D`
- Tier `D` cases do not silently emit canonical `SCIR-H`
- Tier `C` cases carry explicit opaque boundary contracts
- top-level command names remain unchanged

## Risks

- fixture contents could over-claim canonical `SCIR-H` before a real parser exists
- the first Python subset could still be too broad if fixture cases drift beyond the locked bootstrap slice
- command wiring could confuse repository validation with importer conformance unless docs stay synchronized

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Remove the `tests/python_importer/` corpus and conformance checker, restore the prior `make test` / `make validate` behavior, and keep Milestone 02 at doctrine-only status until a narrower fixture design is chosen.

## Evidence required for completion

- the fixture corpus exists with the exact `A`, `C`, and `D` cases planned for this bootstrap slice
- the conformance checker validates bundle completeness, schema compliance, and tier-specific required artifacts
- `make test` and `make validate` both include the new checker behavior
- the Python scope docs explicitly defer `try/except` and `raise` from this bootstrap slice
- validate, conformance, and benchmark dry-run commands pass

## Completion evidence

- `tests/python_importer/cases/` now contains the exact `a_basic_function`, `a_async_await`, `c_opaque_call`, `d_exec_eval`, and `d_try_except` bundles
- `scripts/python_importer_conformance.py` validates fixture completeness, schema-valid bundle artifacts, tier-specific required files, and negative-path self-tests
- `Makefile` now wires the conformance checker into `make test` and `make validate`
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-16
- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on 2026-03-16
- `python scripts/python_importer_conformance.py --mode test` passed on 2026-03-16
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-16
- `make` is not installed in this Windows session, so the updated top-level targets were validated by their underlying Python commands rather than by invoking `make` directly
