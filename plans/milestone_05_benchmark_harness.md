# Milestone 05 — Benchmark Harness
Status: proposed

## Objective

Freeze the benchmark harness contract before broad implementation claims are made.

## Scope

- manifest and result schemas
- track and baseline definitions
- contamination control doctrine
- success and kill gates
- top-level benchmark command contract

## Non-goals

- full runtime harness implementation
- proprietary-only evaluation

## Touched files

- `BENCHMARK_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `benchmarks/baselines.md`
- `benchmarks/corpora_policy.md`
- `benchmarks/contamination_controls.md`
- `benchmarks/success_failure_gates.md`
- `schemas/benchmark_manifest.schema.json`
- `schemas/benchmark_result.schema.json`

## Invariants

- strong baselines remain mandatory
- contamination controls remain explicit
- failure criteria remain visible

## Risks

- benchmark doctrine becomes non-falsifiable
- baseline selection drifts toward weak comparators

## Validation steps

```bash
make validate
make benchmark
```

## Rollback strategy

Remove weak or ambiguous benchmark claims and return to the core track definitions.

## Evidence required for completion

- executable doctrine-level benchmark dry run
- explicit success and kill gates
- baseline table
