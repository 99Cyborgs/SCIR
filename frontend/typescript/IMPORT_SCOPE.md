# TypeScript Import Scope
Status: Normative

## Initial targeted subset

### Tier A candidate constructs

- modules
- functions and `async` functions
- interfaces as explicit witnesses
- classes without proxy or decorator semantics
- promises normalized to async effects
- structured object and record-like patterns

### Tier B candidate constructs

- structural interface normalization with reduced idiomaticity
- selected prototype-based class behavior
- event-loop-sensitive async behavior where profile `D` remains explicit

### Tier C constructs

- host runtime stubs
- dynamic property traps
- JS interop surfaces not semantically modeled

### Tier D constructs

- decorators that materially affect runtime semantics
- proxies
- emit-dependent reflection as semantic source of truth
- advanced type-level computation used as executable semantics

## Preservation expectations

- `D` is usually the primary profile
- `R` is possible for structured subsets
- `N` claims are weak unless host semantics are removed

## Importer obligations

- keep structural typing explicit as witnesses or contracts,
- keep host-runtime assumptions explicit,
- do not erase proxy or decorator behavior into fake support.
