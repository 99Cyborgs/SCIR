# Python Function Async Importer-Only Slice

Status: complete
Owner: Codex
Date: 2026-03-20

## Objective

Admit three bounded Python function and async follow-on shapes into canonical `SCIR-H` as Milestone 02B importer work without changing the frozen executable `SCIR-L`, reconstruction, or benchmark slices.

## Scope

- promote `tests/python_importer/cases/b_if_else_return` to accepted importer-level Tier `B`
- promote `tests/python_importer/cases/b_direct_call` to accepted importer-level Tier `B`
- promote `tests/python_importer/cases/b_async_arg_await` to accepted importer-level Tier `B`
- keep the executable Python pipeline limited to the existing lowerable and reconstructable cases
- update doctrine so importer-only function and async acceptance does not look like end-to-end support

## Non-goals

- new `SCIR-H` node kinds
- `SCIR-L` lowering for the three new cases
- translation or reconstruction for the three new cases
- benchmark expansion beyond the fixed executable bootstrap corpus
- Python classes, loops, comprehensions, or `raise`

## Touched files

- `plans/2026-03-20-python-function-async-importer-only.md`
- `scripts/scir_python_bootstrap.py`
- `scripts/python_importer_conformance.py`
- `scripts/scir_bootstrap_pipeline.py`
- `frontend/python/AGENTS.md`
- `frontend/python/IMPORT_SCOPE.md`
- `docs/feature_tiering.md`
- `docs/unsupported_cases.md`
- `docs/reconstruction_policy.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `validators/validator_contracts.md`
- `tests/README.md`
- `tests/python_importer/cases/b_if_else_return/*`
- `tests/python_importer/cases/b_direct_call/*`
- `tests/python_importer/cases/b_async_arg_await/*`

## Invariants that must remain true

- `SCIR-H` remains the semantic source of truth
- the executable Python bootstrap corpus remains `a_basic_function`, `a_async_await`, and `c_opaque_call`
- Track `A`, `B`, and Python `D-PY` Track `D` remain benchmarked only on the fixed executable corpus
- importer-only follow-on cases emit no `SCIR-L`, translation, or reconstruction outputs
- unsupported Python expansion outside the named fixture slices remains explicit

## Risks

- importer-only acceptance could be misread as executable support
- executable benchmark manifests could drift if the corpus hash accidentally expands with the importer-only cases
- direct-call, explicit-else, or async-await shape drift could overclaim function coverage without exact fixture checks

## Validation steps

- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/run_repo_validation.py --require-rust`
- `make validate`
- `make benchmark`

## Rollback strategy

Revert the three `b_` cases to unaccepted follow-on work, remove them from the fixed importer corpus, and keep function and async expansion limited to the original executable bootstrap slice plus the already-admitted importer-only `d_try_except` case.

## Evidence required for completion

- the Python importer emits schema-valid Tier `B` artifacts and canonical `SCIR-H` for the three new cases
- conformance self-tests fail when explicit `else`, direct local call, or awaited local call structure drifts
- the executable Python pipeline validates the new importer outputs while emitting no `SCIR-L`, translation, or reconstruction artifacts for those cases
- benchmark manifests still hash only the fixed executable Python corpus

## Completion evidence

- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on 2026-03-20
- `python scripts/python_importer_conformance.py --mode test` passed on 2026-03-20
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed on 2026-03-20
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-20
- `python scripts/run_repo_validation.py --require-rust` passed on 2026-03-20
- `make validate` passed on 2026-03-20
- `make benchmark` passed on 2026-03-20
- `tests/python_importer/cases/b_if_else_return`, `tests/python_importer/cases/b_direct_call`, and `tests/python_importer/cases/b_async_arg_await` now emit canonical `SCIR-H` as Tier `B` with generated-vs-golden parity
- the Python bootstrap pipeline still reports compile/test evidence for 3 executable cases and rejects `SCIR-L`, translation, and reconstruction outputs for the importer-only `b_` cases
- Track `A`, `B`, and Python Track `D` benchmark manifests continue to hash only the fixed executable Python corpus
