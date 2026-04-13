# Strong-Baseline Falsification Phase

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Turn the active Track `A` and Track `B` benchmark doctrine into an executable strong-baseline falsification phase over the frozen 11-case Python proof-loop corpus.

## Scope

- make Track `A` and Track `B` compare SCIR against the mandatory direct-source and typed-AST baselines, plus the retained regularized-core baseline, on the active frozen corpus
- make baseline attribution, tie/loss/win interpretation, and continuation-vs-stop outcome explicit in executable benchmark artifacts
- harden claim mode so it fails when the active strong-baseline comparison does not justify continuation
- keep schemas, examples, and benchmark doctrine aligned with the executable benchmark output

## Non-goals

- no new Python proof-loop cases
- no new semantic constructs or widened importer scope
- no Rust or Wasm promotion into active benchmark claims
- no Track `C` promotion
- no Track `D` activation
- no architecture rewrite

## Touched files

- plans/2026-04-13-strong-baseline-falsification-phase.md
- SYSTEM_BOUNDARY.md
- CURRENT_FOCUS.md
- README.md
- ARCHITECTURE.md
- BENCHMARK_STRATEGY.md
- VALIDATION_STRATEGY.md
- benchmarks/README.md
- benchmarks/baselines.md
- benchmarks/success_failure_gates.md
- reports/README.md
- scripts/benchmark_contract_metadata.py
- scripts/benchmark_contract_dry_run.py
- scripts/validate_repo_contracts.py
- schemas/comparison_summary.schema.json
- schemas/benchmark_result.schema.json
- schemas/benchmark_report.schema.json
- reports/examples/comparison_summary.example.json
- reports/examples/benchmark_result.example.json
- reports/examples/benchmark_report.example.json

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic authority
- `SCIR-L` remains derivative-only
- the active corpus remains the frozen 11-case executable Python proof loop
- direct-source and typed-AST baselines remain mandatory for active tracks
- Rust importer evidence remains outside active benchmark corpus and claims
- helper-free Wasm evidence remains outside active benchmark corpus and claims
- Track `C` remains retained non-default
- Track `D` remains deferred

## Risks

- tightening claim-mode failure conditions may expose that the current benchmark outcome does not justify continuation
- schema changes may require synchronized example and validator updates to avoid false contract failures
- decision logic must not accidentally turn benchmark execution failure into a scope-widening or semantics-changing path

## Validation steps

- python scripts/benchmark_contract_dry_run.py
- python scripts/benchmark_contract_dry_run.py --claim-run
- python scripts/run_repo_validation.py
- python scripts/benchmark_repro.py --run-id python-proof-loop-full-20260413T164501Z

## Rollback strategy

Revert the falsification-phase changes together if the updated decision logic or schema changes break benchmark execution without improving baseline fairness or artifact truthfulness.

## Evidence required for completion

- diff review shows benchmark doctrine, schemas, examples, and executable logic agree on Track `A` and Track `B` strong-baseline falsification
- direct-source and typed-AST baselines are fully attributed in active Track `A` and Track `B` outputs
- benchmark artifacts record strongest-baseline attribution and explicit continuation-vs-stop outcome
- python scripts/benchmark_contract_dry_run.py
- python scripts/benchmark_contract_dry_run.py --claim-run
- python scripts/run_repo_validation.py
- python scripts/benchmark_repro.py --run-id python-proof-loop-full-20260413T164501Z

## Completion evidence

- `python scripts/benchmark_contract_dry_run.py`
  Result: exit `0`; Track `A` pass, Track `B` pass, continuation decision `SCIR_USEFUL_BUT_UNNECESSARY`, `claim_ready=False`.
- `python scripts/benchmark_contract_dry_run.py --claim-run`
  Result: exit `1`; blocked exactly because continuation decision is `SCIR_USEFUL_BUT_UNNECESSARY`.
- `python scripts/run_repo_validation.py`
  Result: exit `0`; repository contract, importer conformance, bootstrap pipeline, sweep smoke, and benchmark smoke all passed.
- `python scripts/benchmark_repro.py --run-id python-proof-loop-full-20260413T164501Z`
  Result: exit `0`; reproduced the locked smoke run into `artifacts/benchmark_repro/python-proof-loop-full-20260413T164501Z/reproduced_run`, and the reproduced claim lane exited `1` for the same continuation-decision block.
