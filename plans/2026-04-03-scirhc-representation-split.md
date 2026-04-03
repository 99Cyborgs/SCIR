# 2026-04-03 SCIR-Hc Representation Split

Status: completed
Owner: Codex
Date: 2026-04-03

## Objective

Introduce a derivative compressed `SCIR-Hc` representation alongside canonical explicit `SCIR-H` so the repository can measure lexical compression separately from semantic explicitness, validate `SCIR-H <-> SCIR-Hc` semantic round-trips, and update benchmark claim logic without weakening baselines or contamination controls.

## Scope

- define `SCIR-Hc` as a derivative AI-facing representation of validated `SCIR-H`
- add `scirh_to_scirhc()` plus `SCIR-Hc -> SCIR-H` semantic round-trip validation
- implement token-aware normalization for duplicate effect rows, single-use witness inlining hooks, capability hoisting hooks, and inferable ownership elision in the active subset
- extend Track `A` / sweep / claim metrics to report `SCIR-H` and `SCIR-Hc` side by side
- update claim logic, benchmark reports, schemas, examples, and doctrine for the new explicit-vs-compressed split

## Non-goals

- changing canonical `SCIR-H` semantics or removing it as the only normative semantic source of truth
- weakening contamination controls, deleting baselines, or broadening the executable corpus
- activating deferred witness or capability syntax as new canonical `SCIR-H` surface
- adding new external dependencies or services

## Touched files

- `plans/2026-04-03-scirhc-representation-split.md`
- `ARCHITECTURE.md`
- `BENCHMARK_STRATEGY.md`
- `DECISION_REGISTER.md`
- `VALIDATION_STRATEGY.md`
- `benchmarks/README.md`
- `benchmarks/tracks.md`
- `benchmarks/success_failure_gates.md`
- `docs/scir_h_overview.md`
- `reports/exports/decision_register.export.json`
- `reports/README.md`
- `reports/examples/benchmark_report.example.json`
- `reports/examples/benchmark_result.example.json`
- `reports/examples/comparison_summary.example.json`
- `reports/examples/sweep_result.example.json`
- `schemas/benchmark_report.schema.json`
- `schemas/comparison_summary.schema.json`
- `schemas/validation_report.schema.json`
- `scripts/benchmark_audit_common.py`
- `scripts/benchmark_contract_dry_run.py`
- `scripts/benchmark_contract_metadata.py`
- `scripts/scir_bootstrap_pipeline.py`
- `scripts/scir_h_bootstrap_model.py`
- `scripts/scir_sweep.py`
- `specs/scir_h_spec.md`
- `specs/validator_invariants.md`
- `validators/validator_contracts.md`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic source of truth
- `SCIR-Hc` remains derivative and may not introduce semantics not present in validated `SCIR-H`
- preservation claims stay path-qualified and explicit, with `SCIR-Hc -> SCIR-H` treated as `P1` normalization at strongest
- mandatory baselines remain direct source, typed-AST, and normalized baseline where already required
- contamination controls, manifest locking, and reproducibility requirements remain blocking
- unsupported witness and capability syntax does not silently become active canonical `SCIR-H`

## Risks

- a compressed text surface can become a second hidden canonical form if the round-trip and validator boundaries are weak
- ownership or effect elision can accidentally erase semantics that the current validator requires to stay explicit
- benchmark claim rewiring can drift from schemas, examples, or doctrine and break auditability
- the current active subset lacks canonical witness/capability syntax, so compression hooks for those surfaces must stay derivative-only and explicitly bounded

## Validation steps

- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/scir_bootstrap_pipeline.py --mode test`
- `python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_smoke.json --output-dir artifacts/test-scirhc-sweep`
- `python scripts/benchmark_contract_dry_run.py --output-dir artifacts/test-scirhc-benchmark`
- `python scripts/benchmark_contract_dry_run.py --claim-run --output-dir artifacts/test-scirhc-claim`
- `python scripts/validate_repo_contracts.py --mode validate`

## Rollback strategy

Remove the derivative `SCIR-Hc` transform, metrics, and claim-path wiring as one coordinated slice while preserving any purely editorial doctrine clarifications that still match the canonical `SCIR-H` architecture, then restore the prior benchmark report schema and claim-gate behavior in the same rollback.

## Evidence required for completion

- `SCIR-Hc` is generated from validated `SCIR-H` and round-trips back to semantically equivalent `SCIR-H`
- Track `A` and sweep artifacts report separate explicit and compressed representation metrics
- claim-mode reporting records the new pass/fail gate basis and failure attribution categories
- touched schemas and example artifacts validate against the updated contracts
- benchmark and validation commands above pass or any remaining failure is explicit and aligned with the new claim gate

## Completion evidence

- `python -m py_compile scripts/scir_h_bootstrap_model.py scripts/scir_bootstrap_pipeline.py scripts/scir_sweep.py scripts/benchmark_audit_common.py scripts/benchmark_contract_metadata.py scripts/benchmark_contract_dry_run.py` passed
- targeted `SCIR-Hc` smoke checks over `a_basic_function`, `a_async_await`, `b_direct_call`, `b_while_break_continue`, and `c_opaque_call` preserved semantic lineage and canonical `SCIR-H` formatting after `SCIR-H -> SCIR-Hc -> SCIR-H`
- `python scripts/benchmark_contract_dry_run.py --claim-run` passed
- claim-run evidence from `artifacts/benchmark_runs/python-proof-loop-full-20260403T174820Z/benchmark_report.json` recorded:
  - `explicit_representation_metrics.LCR = 1.6569`
  - `compressed_representation_metrics.LCR_scirhc = 1.5061`
  - `claim_gate.passed = true`
  - satisfied conditions: `scirhc_lcr_vs_ast`, `patch_composability_vs_ast`
- `python scripts/run_repo_validation.py` passed after synchronizing `reports/exports/decision_register.export.json`
