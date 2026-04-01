# Python Try Except Importer-Only Slice

Status: complete
Owner: Codex
Date: 2026-03-20

## Objective

Admit one bounded Python `try/except` shape into canonical `SCIR-H` as Milestone 02B follow-on importer work without changing the frozen executable `SCIR-L`, reconstruction, or benchmark slices.

## Scope

- extend the compact bootstrap `SCIR-H` model to parse and format canonical `try` / `catch` suites
- promote `tests/python_importer/cases/d_try_except` from rejected Tier `D` to accepted importer-level Tier `B`
- keep the executable Python pipeline limited to the existing lowerable and reconstructable cases
- update doctrine so importer-only exception acceptance does not look like end-to-end support

## Non-goals

- exception lowering in `SCIR-L`
- reconstruction for the Python `try/except` case
- support for Python `raise`, `finally`, multi-handler `except`, or bound exception names
- benchmark expansion beyond the fixed executable bootstrap corpus

## Touched files

- `plans/2026-03-20-python-try-except-importer-only.md`
- `scripts/scir_h_bootstrap_model.py`
- `scripts/scir_python_bootstrap.py`
- `scripts/python_importer_conformance.py`
- `scripts/scir_bootstrap_pipeline.py`
- `frontend/python/AGENTS.md`
- `frontend/python/IMPORT_SCOPE.md`
- `docs/feature_tiering.md`
- `docs/unsupported_cases.md`
- `docs/reconstruction_policy.md`
- `BENCHMARK_STRATEGY.md`
- `VALIDATION_STRATEGY.md`
- `validators/validator_contracts.md`
- `tests/README.md`
- `tests/python_importer/cases/d_try_except/*`

## Invariants that must remain true

- `SCIR-H` remains the semantic source of truth
- `SCIR-L` remains frozen and does not gain exception ops
- the fixed executable Python bootstrap corpus remains `a_basic_function`, `a_async_await`, and `c_opaque_call`
- Track `A`, `B`, and Python `D-PY` Track `D` remain benchmarked only on the fixed executable corpus
- unsupported Python exception surface outside the bounded slice remains explicit

## Risks

- importer-only acceptance could be misread as end-to-end exception support
- synthesized catch binders and coarse callable/effect typing could overclaim fidelity if Tier `B` is not stated everywhere
- pipeline code could accidentally start lowering or reconstructing the new case

## Validation steps

- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/run_repo_validation.py --require-rust`
- `make validate`
- `make benchmark`

## Rollback strategy

Revert `d_try_except` to rejected Tier `D`, remove canonical `try/catch` support from the compact bootstrap model, and keep the exception surface doctrine explicitly deferred.

## Evidence required for completion

- canonical `SCIR-H` parse-normalize-format support exists for the bounded `try` / `catch` shape
- the Python importer emits schema-valid Tier `B` artifacts and canonical `SCIR-H` for `d_try_except`
- the executable Python pipeline validates the new importer output while emitting no `SCIR-L`, translation, or reconstruction artifacts for that case
- doctrine files explicitly say the slice is importer-only and non-executable

## Completion evidence

- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on 2026-03-20
- `python scripts/python_importer_conformance.py --mode test` passed on 2026-03-20
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed on 2026-03-20
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-20
- `python scripts/run_repo_validation.py --require-rust` passed on 2026-03-20
- `make validate` passed on 2026-03-20
- `make benchmark` passed on 2026-03-20
- `tests/python_importer/cases/d_try_except` now emits canonical `SCIR-H` as Tier `B` with generated-vs-golden parity
- the Python bootstrap pipeline still reports compile/test evidence for 3 executable cases, leaving `d_try_except` importer-only with no `SCIR-L`, translation, or reconstruction outputs
- doctrine files now distinguish importer-only `SCIR-H` acceptance from the fixed executable bootstrap corpus
