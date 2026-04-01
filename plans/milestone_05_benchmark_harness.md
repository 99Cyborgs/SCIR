# Milestone 05 — Benchmark Harness
Status: complete

## Objective

Freeze the executable benchmark harness contract before broad implementation claims are made.

## Scope

- manifest and result schemas
- track and baseline definitions
- contamination control doctrine
- success and kill gates
- top-level benchmark command contract
- executable Track `A` and Track `B` behavior on the fixed bootstrap corpus

## Non-goals

- full runtime harness implementation
- proprietary-only evaluation
- checked-in generated benchmark bundles
- early Track `C` harness scaffolding

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `benchmarks/baselines.md`
- `benchmarks/corpora_policy.md`
- `benchmarks/contamination_controls.md`
- `benchmarks/success_failure_gates.md`
- `ci/benchmark_pipeline.md`
- `reports/README.md`
- `scripts/benchmark_contract_dry_run.py`
- `plans/milestone_05_benchmark_harness.md`

## Invariants

- strong baselines remain mandatory
- contamination controls remain explicit
- failure criteria remain visible
- generated benchmark bundles remain transient in this phase
- Track `C` and `D` remain doctrine-only

## Risks

- benchmark doctrine becomes non-falsifiable
- baseline selection drifts toward weak comparators

## Validation steps

```bash
make validate
make benchmark
python scripts/benchmark_contract_dry_run.py
```

## Rollback strategy

Remove weak or ambiguous benchmark claims and return to the core track definitions.

## Evidence required for completion

- executable doctrine-level benchmark dry run
- explicit success and kill gates
- baseline table
- executable Track `A` and `B` doctrine alignment

## Completion evidence

- `python scripts/benchmark_contract_dry_run.py` passed on 2026-03-16
- `python scripts/scir_bootstrap_pipeline.py --mode validate` passed on 2026-03-16
- `python scripts/scir_bootstrap_pipeline.py --mode test` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode validate` passed on 2026-03-16
- `python scripts/validate_repo_contracts.py --mode test` passed on 2026-03-16
- the benchmark doctrine and milestone seed now match the executable Track `A` and Track `B` harness on the fixed bootstrap corpus
- Track `C` and `D` remain doctrine-only and do not emit executable result bundles
- generated Track `A` and `B` benchmark bundles remain transient and are not promoted into `reports/`
- `make` remains unavailable in this Windows shell, so milestone validation was verified through the underlying Python commands instead of direct `make` invocation
