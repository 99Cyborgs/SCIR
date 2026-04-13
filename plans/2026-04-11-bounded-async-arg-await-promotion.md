# Bounded Async Arg Await Promotion

Status: complete
Owner: Codex
Date: 2026-04-11

## Objective

Promote `b_async_arg_await` from importer-only canonical `SCIR-H` evidence into the bounded executable Python proof loop with lowering, translation, reconstruction, benchmark, and retained Track `C` synchronization, while keeping helper-free Wasm and sweep-smoke scope unchanged.

## Scope

- update the active focus and backlog to replace the completed `b_if_else_return` item with the bounded `b_async_arg_await` promotion
- promote `b_async_arg_await` to executable status in Python importer metadata, fixture expectations, corpus manifests, and benchmark case locks
- add bounded lowering, translation, execution, and reconstruction support for the parameterized async local-call shape
- keep helper-free Wasm non-emittable for this async case and preserve the frozen Tier `A` micro corpus used by sweep smoke
- synchronize benchmark examples, Track `C` sample generation, and repo-contract checks to the expanded executable proof-loop case set
- correct active reconstruction doctrine so it matches the live executable round-trip surface

## Non-goals

- no grammar widening
- no loop, class, or exception lowering
- no change to Rust executable scope
- no helper-free Wasm widening for async cases
- no sweep-smoke corpus expansion

## Touched files

- CURRENT_FOCUS.md
- BACKLOG.md
- frontend/python/IMPORT_SCOPE.md
- docs/feature_tiering.md
- docs/reconstruction_policy.md
- BENCHMARK_STRATEGY.md
- benchmarks/tracks.md
- benchmarks/success_failure_gates.md
- benchmarks/corpora_policy.md
- scripts/scir_python_bootstrap.py
- scripts/python_importer_conformance.py
- scripts/scir_bootstrap_pipeline.py
- scripts/benchmark_contract_metadata.py
- scripts/benchmark_contract_dry_run.py
- scripts/sync_python_proof_loop_artifacts.py
- tests/corpora/python_proof_loop_corpus.json
- tests/python_importer/cases/b_async_arg_await/*

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- benchmark cases remain locked exactly to executable Python proof-loop cases
- sweep smoke stays bound to the frozen Tier `A` micro corpus
- helper-free Wasm remains subset-bound and does not widen to parameterized async execution
- importer-only loop, class, and exception cases remain non-executable

## Risks

- async lowering or reconstruction support could accidentally widen beyond the single parameterized local-call shape
- benchmark and Track `C` samples can drift if the executable case set changes without synchronized sample regeneration

## Validation steps

- python scripts/python_importer_conformance.py --mode validate-fixtures
- python scripts/scir_bootstrap_pipeline.py --mode test
- python scripts/benchmark_contract_dry_run.py --output-dir artifacts/benchmark_runs/latest
- python scripts/validate_repo_contracts.py --mode test
- python scripts/validate_repo_contracts.py --mode audit
- python scripts/run_repo_validation.py
- python scripts/run_repo_validation.py --require-rust --include-track-c-pilot

## Rollback strategy

Restore `b_async_arg_await` to importer-only Tier `B` metadata, remove its executable-case contract and downstream outputs, and regenerate the benchmark and Track `C` sample surfaces so the executable registry returns to the prior locked set.

## Evidence required for completion

- updated importer fixture bundle for `b_async_arg_await`
- passing bootstrap pipeline and benchmark dry run
- passing repo-contract test and audit
- passing default and Rust-inclusive validation entrypoints
- diff review showing helper-free Wasm and sweep-smoke scope stayed frozen

## Completion evidence

- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/sync_python_proof_loop_artifacts.py --mode write`
- `python scripts/benchmark_contract_dry_run.py --output-dir artifacts/benchmark_runs/latest`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/validate_repo_contracts.py --mode audit`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot`
- `make validate`
