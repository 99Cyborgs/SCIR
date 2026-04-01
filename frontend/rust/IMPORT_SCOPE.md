# Rust Import Scope
Status: Normative

## Phase 6A executable slice

### Tier A executable constructs

- free functions
- named record types
- borrowed and borrowed-mutable parameters
- mutable locals
- record field places in read and write positions
- direct calls
- scalar comparison branches
- simple async functions with explicit `await`

### Tier B deferred constructs

- methods and receiver sugar
- trait and impl dispatch
- closures
- `Result` and `Option`
- enums and pattern matching
- iterator normalization and async normalization with idiomaticity loss
- macro-expanded code imported post-expansion with provenance caveats

### Tier C executable constructs

- explicit `unsafe` call boundaries lowered as opaque

### Tier D constructs

- proc macro semantics as first-class source behavior
- build-script semantics
- self-referential pin patterns
- unsafe alias tricks and raw-pointer choreography beyond an explicit opaque boundary

## Preservation expectations

- Tier `A` Rust reconstruction claims in Phase 6A are fixed at profile `R`, preservation `P1`
- explicit unsafe boundary handling is fixed at profile `N`, preservation `P3`
- optimization claims are deferred to Phase 6B

## Importer obligations

- keep borrow modes explicit in parameter and type surfaces
- keep field-place semantics explicit rather than hidden in projection sugar
- keep Tier `C` unsafe handling explicit through opaque boundary contracts
- do not widen support via hidden unsafe helpers
