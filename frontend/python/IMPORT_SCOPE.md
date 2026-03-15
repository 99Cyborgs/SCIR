# Python Import Scope
Status: Normative

## Initial targeted subset

### Tier A candidate constructs

- modules and imports without import hooks
- functions and `async def`
- simple classes with explicit instance fields
- `if`, `for`, `while`, `return`
- local mutation
- exceptions via `raise`
- simple `await`
- straightforward comprehensions when normalization is explicit
- typed or inferable scalar, record-like, and result-like structures

### Tier B candidate constructs

- class sugar normalized into records plus methods
- generators and iterator protocols where normalization is explicit
- context-manager style patterns only when lowered to explicit effectful structure with clear limits
- selected dynamic features that remain validator-understood but less reconstructable

### Tier C constructs

- reflective attribute mutation
- dynamic descriptor behavior
- C-extension or foreign boundaries
- host object protocols not modeled semantically

### Tier D constructs

- `exec`
- `eval`
- import hooks
- metaclass-driven semantic rewrites
- pervasive monkey patching as semantic source of truth

## Preservation expectations

- `R`: usually `P1`
- `D`: `P0/P1` only for the supported subset
- `N` and `P`: usually `P2/P3` for host-sensitive constructs

## Importer obligations

- every downgrade must name the reason,
- every Tier `C` region must carry an opaque boundary contract,
- unsupported constructs must be rejected explicitly.
