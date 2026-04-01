# Benchmarks
Status: Normative

Benchmarks are not an afterthought. They are part of the product boundary.

## Required benchmark components

- track definition
- baseline definition
- corpus policy
- contamination controls
- success and failure gates
- manifest schema
- result schema

## Rule

No benchmark claim is valid unless it names the active profile, baseline, corpus scope, and gating rule.

## Current executable freeze

The current executable harness is intentionally narrow:

- Track `A` and Track `B` run only on the fixed Python bootstrap corpus,
- Track `D` runs only on fixed Rust `N` and Python `D-PY` corpora,
- Track `C` remains doctrine-only,
- `D-JS` remains doctrine-only,
- generated benchmark bundles stay transient and are not promoted into `reports/`.
