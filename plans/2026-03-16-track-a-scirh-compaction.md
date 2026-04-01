# Track A SCIR-H compaction

Status: complete
Owner: Codex
Date: 2026-03-16

## Objective

Reduce bootstrap `SCIR-H` token inflation by fixing Track `A` gate evaluation, introducing a shared bootstrap `SCIR-H` model/parser/formatter, and cutting over to a more compact canonical text surface for the supported bootstrap subset.

## Scope

- Track `A` median-based gate evaluation and explicit diagnostic metrics
- shared bootstrap `SCIR-H` subset model, parser, and formatter
- importer, conformance, lowering, reconstruction, and benchmark refactors onto the shared model
- compact canonical `SCIR-H` syntax for the supported bootstrap subset
- required spec, validator, benchmark, and decision-register updates

## Non-goals

- broadening Python coverage beyond the fixed bootstrap corpus
- changing unsupported-case tiering or opaque-boundary disclosure policy
- changing `SCIR-L` semantics beyond consuming parsed bootstrap `SCIR-H`
- changing benchmark schemas
- starting Rust subset or runtime optimization work

## Touched files

- `plans/2026-03-16-track-a-scirh-compaction.md`
- `ARCHITECTURE.md`
- `BENCHMARK_STRATEGY.md`
- `DECISION_REGISTER.md`
- `README.md`
- `VALIDATION_STRATEGY.md`
- `benchmarks/success_failure_gates.md`
- `ci/benchmark_pipeline.md`
- `docs/scir_h_overview.md`
- `frontend/python/IMPORT_SCOPE.md`
- `plans/milestone_02_python_importer.md`
- `reports/README.md`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/python_importer_conformance.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/scir_h_bootstrap_model.py`
- `scripts/scir_python_bootstrap.py`
- `specs/scir_h_spec.md`
- `specs/validator_invariants.md`
- `tests/python_importer/cases/a_async_await/expected.scirh`
- `tests/python_importer/cases/a_basic_function/expected.scirh`
- `tests/python_importer/cases/c_opaque_call/expected.scirh`
- `validators/validator_contracts.md`

## Invariants that must remain true

- unsupported Python semantics remain explicit Tier `C` or Tier `D`
- Tier `D` outputs still do not emit canonical `SCIR-H`
- `SCIR-H` remains the canonical source for lowering and reconstruction
- benchmark gates remain the source of truth; only their implementation is corrected
- opaque boundaries remain explicit in `SCIR-H`, reports, and benchmark accounting

## Risks

- parser and formatter drift could create a second hidden canonical surface
- compact syntax could reduce token count but accidentally weaken explicit mutation or effect visibility
- benchmark fixes could expose that the bootstrap corpus still fails `K2`, requiring explicit follow-up rather than policy drift

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`
- `python -m py_compile scripts/scir_h_bootstrap_model.py scripts/scir_python_bootstrap.py scripts/python_importer_conformance.py scripts/scir_bootstrap_pipeline.py scripts/benchmark_contract_dry_run.py`

## Rollback strategy

Remove the compact syntax model/parser/formatter and restore the earlier hardcoded canonical bootstrap strings, then revert the associated doctrine updates in the same change.

## Evidence required for completion

- compact canonical `SCIR-H` goldens are reproduced by the executable importer
- `SCIR-H` validation is parse/normalize/format based for the bootstrap subset
- Track `A` reports median and aggregate ratios and evaluates gates against the median metrics
- validation, conformance, pipeline, and benchmark commands pass
- decision register records the canonical syntax cutover and metric correction

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-16
- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on 2026-03-16
- `python scripts/python_importer_conformance.py --mode test` passed on 2026-03-16
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed on 2026-03-16
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-16
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-16
- `python -m py_compile scripts/scir_h_bootstrap_model.py scripts/scir_python_bootstrap.py scripts/python_importer_conformance.py scripts/scir_bootstrap_pipeline.py scripts/benchmark_contract_dry_run.py scripts/validate_repo_contracts.py` passed on 2026-03-16
- bootstrap Track `A` now reports `median_scir_to_source_ratio=1.4737`, `aggregate_scir_to_source_ratio=1.6471`, `median_scir_to_typed_ast_ratio=0.3256`, and `gate_K2_hit=false`
- `make` remains unavailable in this Windows shell, so the top-level `make benchmark` and `make validate` targets were verified through their underlying Python commands instead of direct `make` invocation
