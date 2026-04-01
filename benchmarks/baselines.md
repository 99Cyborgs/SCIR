# Baselines
Status: Normative

## Mandatory baselines

| Baseline | Why it is mandatory |
| --- | --- |
| direct source | tests whether SCIR is unnecessary because source workflows already suffice |
| canonical typed AST | strongest structured non-SCIR baseline |
| SSA-like internal IR | tests whether `SCIR-H` is unnecessary |
| MLIR-style dialect-only lowering | tests whether existing multi-level infrastructure already suffices |
| lightweight regularized core or s-expression | tests whether syntax regularity alone explains any gains |

## Strongest-baseline rule

Every benchmark manifest must identify the strongest expected baseline for its task family. Results must be interpreted against that baseline first, not against a weak comparator.

`typed-AST` is the canonical shorthand for the typed AST baseline used throughout this repository.

For the current executable Track `A` and Track `B` harness, direct source and `typed-AST` are mandatory in every manifest. Additional baselines remain track-specific.

For executable Phase 6B Track `D` manifests:

- Rust `N` must include `direct source`, `typed-AST`, and `SSA-like internal IR`,
- Python `D-PY` must include `direct source` and `typed-AST`,
- `D-JS` remains doctrine-only and therefore has no executable baseline bundle in this phase.
