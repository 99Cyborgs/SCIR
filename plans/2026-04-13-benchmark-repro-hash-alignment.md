# Benchmark Repro Hash Alignment

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Make claim-run reproducibility honor the same text-fixture hash contract already used by the checked-in benchmark corpus manifests so Windows and Unix checkouts replay the same fixed corpus honestly.

## Scope

- align benchmark fixture hashing with the existing LF-normalized corpus-manifest contract
- add regression coverage in the canonical unittest surface
- validate the claim lane and the replay lane on the current checkout

## Non-goals

- no benchmark track, baseline, gate, or contamination-control changes
- no corpus expansion or manifest reshaping
- no changes to SCIR-H, SCIR-Hc, or SCIR-L semantics

## Touched files

- scripts/benchmark_audit_common.py
- scripts/benchmark_repro.py
- tests/test_scirhc_doctrine.py
- plans/2026-04-13-benchmark-repro-hash-alignment.md

## Invariants that must remain true

- benchmark claims stay bound to the frozen 11-case Python proof-loop corpus
- the claim lane still compares SCIR against direct-source and typed-AST baselines
- reproducibility checks still fail on real fixture drift
- no benchmark doctrine is widened or softened

## Risks

- broadening the hash helper beyond text-fixture normalization could hide real binary drift
- regression coverage added outside the canonical unittest surface would not protect the default validation gate

## Validation steps

- python -m unittest discover -s tests -p test_scirhc_doctrine.py
- python scripts/benchmark_contract_dry_run.py --claim-run
- python scripts/benchmark_repro.py --run-id <claim run_id>
- python scripts/run_repo_validation.py
- make validate

## Rollback strategy

Revert the benchmark hash-helper change and the regression tests together if replay checks stop matching the checked-in corpus-manifest contract or if the fix masks non-text fixture drift.

## Evidence required for completion

- targeted unittest coverage for CRLF/LF-stable benchmark hashing
- successful claim run on the fixed corpus
- successful benchmark replay from the generated run_id using the default claim output bundle
- canonical repo validation still passes

## Completion evidence

- `python -m unittest discover -s tests -p test_scirhc_doctrine.py` passed with the new benchmark-repro hash normalization tests included
- `python scripts/benchmark_contract_dry_run.py --claim-run` passed on the frozen 11-case corpus and wrote run `python-proof-loop-full-20260413T160338Z`
- `python scripts/benchmark_repro.py --run-id python-proof-loop-full-20260413T160338Z` passed directly against the default `artifacts/benchmark_runs/claim` bundle after aligning replay hashing and run-id resolution with the corpus-manifest contract
- `python scripts/run_repo_validation.py` passed after the benchmark repro fix
- `make validate` passed after rerunning it serially to avoid a transient shared-artifact race with a parallel validation invocation
