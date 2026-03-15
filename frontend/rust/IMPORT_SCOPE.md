# Rust Import Scope
Status: Normative

## Initial targeted subset

### Tier A candidate constructs

- modules and visibility
- structs, enums, pattern matching
- functions, closures, methods
- traits and impls in safe structured cases
- `Result` and `Option`
- explicit ownership and borrowing in safe code
- simple async functions where runtime assumptions are explicit

### Tier B candidate constructs

- trait object and specialization-sensitive cases
- iterator and async normalization with idiomaticity loss
- macro-expanded code when imported post-expansion with provenance caveats

### Tier C constructs

- `unsafe` blocks
- foreign or ABI-sensitive boundaries
- host intrinsics
- unsupported alias or pin patterns

### Tier D constructs

- proc macro semantics as first-class source behavior
- build-script semantics
- unsupported self-referential patterns

## Preservation expectations

- `N`: often the strongest profile for the safe subset
- `R`: `P0/P1` where source-shape preservation remains credible
- `P` and `D`: usually weaker except for selected structured cases

## Importer obligations

- keep ownership modes explicit,
- keep trait lowering visible as witnesses,
- do not widen support via hidden unsafe helpers.
