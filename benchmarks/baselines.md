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
