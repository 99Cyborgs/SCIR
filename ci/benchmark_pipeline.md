# Benchmark Pipeline
Status: Normative

## Current purpose

The active benchmark pipeline validates benchmark policy, manifest integrity, contamination controls, and executes Track `A` plus Track `B` checks for the fixed Python proof-loop corpus.
It also owns the slower round-trip self-test lane and full sweep report generation so those evaluation surfaces do not blur into the quick correctness gate.

Track `C` is conditional and Track `D` is deferred.

## Blocking command

```bash
make benchmark
```

## Slower lanes

1. Python proof-loop round-trip self-tests
2. full proof-loop sweep report generation plus regression comparison against the latest successful baseline artifact when available
3. Track `A` / Track `B` benchmark smoke
4. explicit claim-grade benchmark lane when manually flagged

The evaluation lane must attach `sweep_result`, `sweep_summary`, `regression_summary`, `comparison_summary`, and `contamination_report` artifacts on every run.
The explicit claim lane must additionally attach `benchmark_report.json`, `benchmark_report.md`, and `manifest_lock.json`, and it must fail when baseline results are missing, corpus hash mismatches are detected, a reproducibility block is missing, contamination is detected, or SCIR loses beyond tolerance.
