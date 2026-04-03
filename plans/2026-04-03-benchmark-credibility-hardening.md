# 2026-04-03 Benchmark Credibility Hardening

Status: completed
Owner: Codex
Date: 2026-04-03

## Objective

Make SCIR benchmark and sweep claims externally defensible by adding concrete baseline adapters, contamination controls, audit-grade result rows, claim-bound reporting, baseline-vs-SCIR comparison summaries, CI gates, and reproducible rerun support without widening the MVP feature surface.

## Scope

- implement concrete direct-source, typed-AST, and normalized baseline adapters under `benchmarks/baselines/`
- extend corpus, benchmark, and sweep report contracts with manifest-hash, reproducibility, contamination, and audit-row fields
- enforce split tagging, duplicate and near-duplicate contamination detection, and manifest snapshot locking for reportable corpora
- generate machine-readable and markdown benchmark reports plus comparison summaries that bind every claim to corpus hash, baseline, and metric evidence
- extend the existing sweep and benchmark scripts so baseline rows and SCIR rows share the same audit row shape and comparison logic
- add CI benchmark smoke and explicit claim-run enforcement for baseline presence, contamination cleanliness, reproducibility completeness, and tolerated baseline deltas

## Non-goals

- add new languages, new benchmark tracks, or broader corpus families
- widen SCIR-H, SCIR-L, validator, lowering, or backend semantics
- optimize performance or introduce synthetic benchmark wins
- add new production services or third-party dependencies

## Touched files

- `plans/2026-04-03-benchmark-credibility-hardening.md`
- `BENCHMARK_STRATEGY.md`
- `VALIDATION_STRATEGY.md`
- `VALIDATION.md`
- `benchmarks/README.md`
- `benchmarks/baselines.md`
- `benchmarks/contamination_controls.md`
- `benchmarks/corpora_policy.md`
- `benchmarks/success_failure_gates.md`
- `ci/benchmark_pipeline.md`
- `ci/validation_pipeline.md`
- `Makefile`
- `.github/workflows/benchmarks.yml`
- `.github/workflows/validate.yml`
- `reports/README.md`
- `reports/examples/*.json` for updated benchmark, contamination, comparison, and sweep examples
- `schemas/benchmark_manifest.schema.json`
- `schemas/benchmark_result.schema.json`
- `schemas/corpus_manifest.schema.json`
- `schemas/sweep_result.schema.json`
- `schemas/sweep_summary.schema.json`
- `schemas/regression_summary.schema.json`
- new benchmark report and contamination/comparison schemas under `schemas/`
- new baseline adapter modules under `benchmarks/baselines/`
- `scripts/benchmark_contract_metadata.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/scir_sweep.py`
- `scripts/run_repo_validation.py`
- `scripts/validate_repo_contracts.py`
- new reproducibility helper script under `scripts/`
- `tests/corpora/*.json`
- `tests/sweeps/*.json`

## Invariants that must remain true

- SCIR-H remains the only normative semantic source of truth
- SCIR-L remains derivative and may not gain baseline-only semantics
- active benchmark execution remains limited to the fixed Python proof-loop corpus and bounded optional Track C pilot
- no benchmark claim is valid without explicit corpus hash, baseline comparator, profile, and metric evidence
- contamination and subset limitations remain explicit rather than hidden inside aggregate metrics
- `python scripts/run_repo_validation.py` remains the canonical Windows-safe validation entrypoint

## Risks

- baseline adapter rows can drift from SCIR row semantics if schemas, scripts, and examples are not updated together
- contamination detection may expose overlaps or fixture-shape assumptions that require corpus metadata backfill
- report hardening can invalidate current benchmark fixtures, examples, and CI expectations if not migrated in one slice
- manifest locking can become brittle if reproduction uses mutable paths instead of content-addressed snapshots

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_smoke.json --output-dir artifacts/test-sweep-smoke`
- `python scripts/benchmark_contract_dry_run.py --output-dir artifacts/test-bench-smoke`
- `python scripts/benchmark_contract_dry_run.py --claim-run --output-dir artifacts/test-bench-claim`
- `python scripts/benchmark_repro.py --run-id <generated-run-id> --output-dir artifacts/test-bench-repro`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Back out the benchmark-credibility hardening as one coordinated slice if the new schemas, adapters, report outputs, and CI checks cannot remain aligned with the fixed MVP proof loop, then reland starting with baseline adapters and contamination enforcement before claim reports and CI promotion.

## Evidence required for completion

- concrete source, typed-AST, and normalized baseline adapters execute on the fixed corpus and emit shared audit-row outputs
- corpus manifests carry split, origin, and synthetic-vs-real metadata, and contamination reports detect duplicate or near-duplicate leakage
- benchmark and sweep result rows include manifest hash, reproducibility, and audit metadata sufficient to rerun by run id
- benchmark reports and comparison summaries bind every claim to corpus hash, baseline, metric, and explicit limitation disclaimers
- CI separately enforces benchmark smoke and explicit claim runs and fails on missing baselines, contamination, reproducibility gaps, or out-of-tolerance baseline losses
- a dedicated reproduction command reruns SCIR and all baselines from a recorded run id and reproduces the audit artifacts

## Completion evidence

- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-04-03 after example, schema, and command-contract updates
- `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_smoke.json --output-dir artifacts/verify-sweep-smoke` passed and emitted `comparison_summary.json` plus `contamination_report.json`
- `python scripts/benchmark_contract_dry_run.py --output-dir artifacts/verify-benchmark-smoke` passed and emitted `benchmark_report.json`, `benchmark_report.md`, and `manifest_lock.json`
- `python scripts/benchmark_contract_dry_run.py --claim-run` failed only on the intended claim gate `SCIR lost to one or more baselines beyond tolerance` while still writing the full claim artifact bundle under `artifacts/benchmark_runs/python-proof-loop-full-20260403T165210Z`
- `python scripts/benchmark_repro.py --run-id python-proof-loop-full-20260403T165210Z` reproduced the locked artifact bundle under `artifacts/benchmark_repro/python-proof-loop-full-20260403T165210Z/reproduced_run` and recorded `reproduced_exit_code: 1`, matching the original claim-gate failure
- `python scripts/run_repo_validation.py` passed end to end in smoke mode on 2026-04-03
