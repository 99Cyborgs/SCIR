---
name: scir-benchmark-claim-auditor
description: Audit SCIR benchmark doctrine and result surfaces when work changes benchmark manifests, claim runs, baselines, contamination controls, result bundles, or SCIR-Hc evidence usage. Use when Codex must protect benchmark credibility, require the strongest relevant baseline, and prevent SCIR-Hc evidence from leaking into semantic-authority or cross-class claims.
---

# SCIR Benchmark Claim Auditor

## Goal

Keep benchmark outputs falsifiable, baseline-credible, lineage-bound, and unable to overclaim from compressed or backend-specific evidence.

## Required context

Read `BENCHMARK_STRATEGY.md`, `benchmarks/baselines.md`, `specs/validator_invariants.md`, and any touched benchmark schemas, manifests, or example reports.

## Workflow

1. Identify the benchmark surface being changed:
   - executable sweep
   - claim run
   - illustrative example artifact
   - Track `C` pilot artifact
   - baseline adapter or comparator
2. Enforce the mandatory baselines:
   - `direct source`
   - `typed-AST`
   - `lightweight regularized core or s-expression` where the active track requires it
3. Require the correct artifact bundle for the run type:
   - sweep: `sweep_summary`, `regression_summary`, `comparison_summary.json`, `contamination_report.json`
   - claim run: `benchmark_report.json`, `benchmark_report.md`, `manifest_lock.json`
4. If `SCIR-Hc` evidence appears anywhere, require:
   - explicit `claim_class`
   - explicit `evidence_class`
   - explicit `metric_class`
   - canonical `SCIR-H` lineage binding
   - complete `scir_h_evidence` coverage
5. Check contamination controls, reproducibility block, corpus-manifest hash, and strongest relevant baseline citation.
6. Reject wording that turns Wasm success, compressed representation wins, or importer evidence into broader semantic or cross-language proof.
7. Keep Track `C` non-default and Track `D` deferred unless the root doctrine changes together.

## Active credibility traps

- comparing SCIR only to weak baselines
- publishing `SCIR-Hc` lexical wins as semantic-preservation evidence
- missing `claim_class` / `evidence_class` separation
- missing lineage references for `SCIR-Hc`
- benchmark wording that implies native parity or whole-language breadth

## Output contract

Always return:
1. `Benchmark Surface`
2. `Required Baselines and Artifacts`
3. `SCIR-Hc Evidence Boundary`
4. `Credibility Blockers`

## Hard invariants

- Always interpret results against the strongest relevant baseline first.
- Never let `SCIR-Hc` evidence imply semantic authority.
- Never let benchmark wording imply active `Track D`, native parity, or host parity.
- Never treat illustrative example artifacts as proof of benchmark breadth.
