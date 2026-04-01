# Executable bootstrap path

Status: complete
Owner: Codex
Date: 2026-03-16

## Objective

Implement the first executable end-to-end path for the fixed Python bootstrap corpus: importer, `SCIR-H -> SCIR-L` lowering, reconstruction, and manifest-driven Track A/B benchmark execution.

## Scope

- executable Python importer for the existing five fixture cases
- generated-vs-golden conformance validation
- minimal lowering and translation validation for the imported bootstrap semantics
- Python reconstruction from validated `SCIR-H`
- manifest-driven benchmark execution for Track `A` and Track `B`
- command-contract and doctrine updates required by the implementation

## Non-goals

- broad Python coverage beyond the fixed bootstrap corpus
- `SCIR-L` semantics beyond the imported bootstrap slice
- Track `C` or Track `D` runtime benchmarking
- Rust subset implementation
- optimizer pass development

## Touched files

- `plans/2026-03-16-executable-bootstrap-path.md`
- `Makefile`
- `README.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `ci/validation_pipeline.md`
- `ci/benchmark_pipeline.md`
- `frontend/python/IMPORT_SCOPE.md`
- `plans/milestone_02_python_importer.md`
- `plans/milestone_03_l_lowering.md`
- `plans/milestone_04_reconstruction.md`
- `plans/milestone_05_benchmark_harness.md`
- `reports/README.md`
- `scripts/python_importer_conformance.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/scir_python_bootstrap.py`
- `scripts/scir_bootstrap_pipeline.py`

## Invariants that must remain true

- `SCIR-H` remains the canonical source of truth
- unsupported Python semantics remain explicit Tier `C` or Tier `D`
- Tier `D` outputs do not emit canonical `SCIR-H`
- `SCIR-L` remains derivative and provenance-bearing
- `make validate` and `make benchmark` remain the top-level entry points

## Risks

- bootstrap scripts could overfit the checked-in goldens and hide unsupported syntax drift
- lowering may accidentally encode `SCIR-L`-only semantics if it is not constrained to the imported slice
- benchmark execution could over-claim if it treats fixture success as broad evidence

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/python_importer_conformance.py --mode test`
- `python scripts/benchmark_contract_dry_run.py`
- `make test`
- `make validate`
- `make benchmark`

## Rollback strategy

Remove the executable bootstrap scripts and revert the command/doc wiring, keeping the repository at the fixture-and-doctrine-only state until a narrower implementation path is selected.

## Evidence required for completion

- executable importer reproduces the checked-in fixture bundles for the supported cases
- lowering, translation validation, and reconstruction emit schema-valid artifacts for the bootstrap corpus
- Track `A` and Track `B` benchmark runs are generated from manifests rather than doctrine-only checks
- required validation and benchmark commands pass

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-16
- `python scripts/python_importer_conformance.py --mode validate-fixtures` passed on 2026-03-16
- `python scripts/python_importer_conformance.py --mode test` passed on 2026-03-16
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed on 2026-03-16
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-16
- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-16
- `python -m py_compile scripts/scir_python_bootstrap.py scripts/python_importer_conformance.py scripts/scir_bootstrap_pipeline.py scripts/benchmark_contract_dry_run.py scripts/validate_repo_contracts.py` passed on 2026-03-16
- `make` is still unavailable in this Windows shell, so the top-level `make test`, `make validate`, and `make benchmark` targets were verified through their underlying Python commands instead of direct `make` invocation
