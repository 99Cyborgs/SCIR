# Benchmarks
Status: Normative

Benchmarks are part of the product boundary.

## Active executable harness

- Track `A`
- Track `B`

Active Track `A`/`B` runs now emit `comparison_summary.json`, `contamination_report.json`, `benchmark_report.json`, `benchmark_report.md`, and `manifest_lock.json` in addition to the sweep artifacts.
Track `A` report surfaces separate canonical `SCIR-H` metrics from compressed `SCIR-Hc` metrics.
`benchmark_report.json` must also declare `claim_class` and `evidence_class` so `SCIR-Hc` evidence cannot leak across claim scopes.

## Conditional pilot

- Track `C` only after the Python proof loop remains stable
- Track `C` sample artifacts in `reports/examples/` are illustrative only and stay outside the default executable benchmark gate
- the first executable Track `C` pilot is opt-in only via `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- `c_opaque_call` remains boundary-accounting-only inside that opt-in pilot
- the current disposition is to retain that pilot as a bounded diagnostic slice rather than promote it
- explicit retention and retirement criteria now govern whether that retained pilot may stay on disk unchanged
- checked-in Track `C` sample artifacts must stay identical to the current opt-in pilot outputs while continuing to satisfy the retained lock criteria
- any change to Track `C` sample status, retained-diagnostic wording, case or boundary posture, or default-gate posture requires a new decision-register entry and queue update before the sample bundle may change
- editorial-only Track `C` sample refreshes are limited to JSON-equivalent formatting changes such as whitespace, indentation, trailing-newline, or key-order normalization
- any non-editorial Track `C` sample refresh that remains within the retained pilot contract must cite `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`, `python scripts/run_repo_validation.py --include-track-c-pilot`, the regenerated corpus hash, and the regenerated `run_id` plus `system_under_test`

## Deferred

- Track `D`

## Rule

No benchmark claim is valid unless it names:

- track
- corpus
- corpus hash
- strongest baseline
- comparator metric
- active profile
- gates

## Commands

- `python scripts/benchmark_contract_dry_run.py`: benchmark smoke
- `python scripts/benchmark_contract_dry_run.py --claim-run`: explicit claim-grade benchmark lane
- `python scripts/benchmark_repro.py --run-id <run-id>`: reproduce a locked claim run
