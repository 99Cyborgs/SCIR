# Python While Importer-Only Slice

Status: complete
Owner: Codex
Date: 2026-03-27

## Objective

Admit a bounded importer-only Python `while` loop family into canonical `SCIR-H` as the next Milestone 02B follow-on slice without changing executable lowering, reconstruction, or benchmark scope.

## Scope

- promote `tests/python_importer/cases/b_while_call_update` to accepted importer-level Tier `B`
- promote `tests/python_importer/cases/b_while_break_continue` to accepted importer-level Tier `B`
- extend the compact bootstrap `SCIR-H` model to parse and format canonical `loop`, `break`, and `continue`
- keep the executable Python pipeline limited to the existing lowerable and reconstructable cases
- update doctrine and queue text so the loop slice remains explicitly importer-only

## Non-goals

- `for` loops
- `while ... else`
- nested loops beyond the fixed fixtures
- `SCIR-L` lowering for the new loop cases
- translation, reconstruction, or benchmark expansion for the new loop cases

## Touched files

- `plans/2026-03-27-python-while-importer-only.md`
- `scripts/scir_h_bootstrap_model.py`
- `scripts/scir_python_bootstrap.py`
- `scripts/python_importer_conformance.py`
- `scripts/scir_bootstrap_pipeline.py`
- `frontend/python/IMPORT_SCOPE.md`
- `docs/feature_tiering.md`
- `docs/unsupported_cases.md`
- `VALIDATION_STRATEGY.md`
- `validators/validator_contracts.md`
- `EXECUTION_QUEUE.md`
- `tests/README.md`
- `tests/python_importer/cases/b_while_call_update/*`
- `tests/python_importer/cases/b_while_break_continue/*`

## Invariants that must remain true

- `SCIR-H` remains the semantic source of truth
- the executable Python bootstrap corpus remains `a_basic_function`, `a_async_await`, and `c_opaque_call`
- importer-only loop cases emit no `SCIR-L`, translation, reconstruction, or benchmark artifacts
- broader loop semantics remain explicit unsupported or deferred work

## Risks

- loop acceptance could be misread as executable control-flow support
- canonical loop syntax could drift if parse-normalize-format rules are underspecified
- fixed-shape `break` / `continue` support could accidentally imply broader loop fidelity

## Validation steps

- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/validate_repo_contracts.py --mode validate`

## Rollback strategy

Revert the two `b_while_*` cases to deferred work, remove bootstrap loop statement support, and keep loops fully deferred from Milestone 02B importer acceptance.

## Evidence required for completion

- both new loop fixtures emit schema-valid Tier `B` artifacts and canonical `SCIR-H`
- parse-normalize-format accepts canonical `loop`, `break`, and `continue`
- the executable Python pipeline leaves the new loop cases importer-only
- doctrine and queue text explicitly describe the loop slice as non-executable
