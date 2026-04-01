# Milestone 02B Python Class Importer-Only Slice

Status: complete
Owner: Codex
Date: 2026-03-27

## Objective

Admit one bounded importer-only Python class shape into the Milestone 02B fixture corpus using existing canonical `SCIR-H` record and field-place machinery.

## Scope

- add the fixed `b_class_init_method` Python fixture
- normalize the fixture into canonical `SCIR-H` as one record-like type declaration plus plain functions
- keep the slice Tier `B` and importer-only
- update conformance, pipeline, scope, queue, and validation doctrine surfaces

## Non-goals

- executable lowering for the new class slice
- reconstruction support for the new class slice
- benchmark participation for the new class slice
- inheritance, decorators, properties, descriptors, class variables, dataclasses, metaclasses, or dynamic attribute support

## Touched files

- `plans/2026-03-27-python-class-importer-only.md`
- `scripts/scir_python_bootstrap.py`
- `scripts/python_importer_conformance.py`
- `scripts/scir_bootstrap_pipeline.py`
- `tests/python_importer/cases/b_class_init_method/source.py`
- `frontend/python/IMPORT_SCOPE.md`
- `docs/feature_tiering.md`
- `docs/unsupported_cases.md`
- `validators/validator_contracts.md`
- `VALIDATION_STRATEGY.md`
- `tests/README.md`
- `EXECUTION_QUEUE.md`

## Invariants that must remain true

- the executable Python bootstrap path remains limited to `a_basic_function`, `a_async_await`, and `c_opaque_call`
- the new class slice emits canonical `SCIR-H` only and no `SCIR-L`, translation, reconstruction, or benchmark artifacts
- no new schema or `SCIR-L` surface is introduced
- broader Python object-model semantics remain explicit deferred scope

## Risks

- the fixed class shape may not fit cleanly into existing canonical field-place syntax
- doctrine may accidentally overclaim broader Python class support

## Validation steps

- `python scripts/scir_python_bootstrap.py --source tests/python_importer/cases/b_class_init_method/source.py --output-dir tests/python_importer/cases/b_class_init_method`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/build_execution_queue.py --mode write`
- `python scripts/validate_repo_contracts.py --mode validate`

## Rollback strategy

Revert the `b_class_init_method` fixture and remove its importer, conformance, pipeline, and doctrine entries together so the importer corpus returns to the prior ten-case state.

## Evidence required for completion

- checked-in fixture bundle for `b_class_init_method`
- conformance and pipeline validation pass for the Python-side slice
- doctrine and queue text explicitly keep the class slice importer-only and bounded
