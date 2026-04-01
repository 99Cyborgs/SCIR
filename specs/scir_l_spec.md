# SCIR-L Specification
Status: Normative

## Scope

`SCIR-L` is the lowered control and analysis representation used for SSA-style reasoning, async/effect lowering, optimization, and backend preparation.

## Non-negotiable properties

- derivative from validated `SCIR-H`
- explicit CFG
- block parameters
- SSA values
- explicit effect and memory sequencing where required
- explicit provenance back to `SCIR-H`
- lowered async and opaque-boundary structures
- lower reconstructability than `SCIR-H`

## Core structure

Bootstrap `SCIR-L` v0.1 contains:

- modules,
- functions,
- blocks,
- SSA values,
- memory tokens,
- effect tokens,
- block terminators,
- provenance records.

## Canonical grammar

```ebnf
LModule   ::= "lmodule" ModId "{" LFn+ "}"
LFn       ::= "func" FnId "(" ParamList? ")" "->" RetTy "{" Block+ "}"
Block     ::= "^" BlockId "(" BlockParamList? ")" ":" Instr* Terminator
Instr     ::= "%" SsaId "=" Op OperandList ";"
Terminator::= "br" BlockRef "(" ArgList? ")" ";"
            | "cond_br" SsaId "," BlockRef "(" ArgList? ")" "," BlockRef "(" ArgList? ")" ";"
            | "ret" SsaId ";"

Op        ::= "const" | "cmp" | "alloc" | "store" | "load"
            | "field.addr" | "call" | "async.resume" | "opaque.call"

Operand   ::= SsaId | Lit | SymRef | MemTok | EffTok
MemTok    ::= "%" "mem" Number
EffTok    ::= "%" "eff" Number
SymRef    ::= "sym:" SymId
```

## Frozen bootstrap op surface

The Phase 3 bootstrap freeze permits exactly these op families:

- value: `const`, `cmp`
- memory: `alloc`, `store`, `load`
- place projection: `field.addr`
- direct validated call: `call`
- lowered async suspension: `async.resume`
- explicit opaque boundary: `opaque.call`
- control terminators: `ret`, `br`, `cond_br`

Deferred from this freeze:

- generic arithmetic beyond the current comparison lowering
- witness construction or projection
- exception lowering
- loop lowering
- backend-specific dialect ops
- `phi`; block parameters are the only merge mechanism

## Token model

- Memory tokens sequence mutable-cell effects only.
- Effect tokens sequence non-memory effects in the bootstrap subset.
- `alloc` consumes a memory token and yields a cell handle.
- `store` consumes a cell, value, and memory token and yields a new memory token.
- `load` consumes a cell and memory token and yields an SSA value.
- `field.addr` projects a named record field cell from a validated record cell handle and carries no independent memory or effect semantics.
- `call`, `async.resume`, and `opaque.call` consume the active effect token when one is required by the lowered function shape.
- Branches forward memory and effect state only through block arguments.

## Op meaning in the frozen subset

- `cmp` is the lowered form of bootstrap intrinsic scalar comparison, starting with `lt`.
- `field.addr` is the lowered form of bootstrap field-place projection.
- `call` is only for direct validated symbol calls in the bootstrap subset.
- `async.resume` is only the lowered form of `await`.
- `opaque.call` is only the lowered form of an explicit Tier `C` opaque boundary.

## Bootstrap lowering obligations

For the supported executable slice, `SCIR-L` must be derivable only from validated compact `SCIR-H` and must preserve these mappings:

- `var y int x` -> `alloc` + `store`
- mutable-local read -> `load`
- `if lt y 0` -> `load` + `cmp` + `cond_br`
- `set y 0` -> `store`
- `return 1` -> `const` + `ret`
- `return await fetch_value()` -> `call` + `async.resume` + `ret`
- `return foreign_api_ping()` -> `opaque.call` + `ret`
- borrowed-record parameter plus `counter.value` read -> `field.addr` + `load`
- `set counter.value 0` -> `field.addr` + `store`

## Required semantics carried from `SCIR-H`

`SCIR-L` must preserve, in lowered form:

- control-flow meaning,
- value flow,
- sequencing for memory and non-memory effects where required,
- async suspension structure for the lowered bootstrap subset,
- opaque and foreign boundary calls,
- provenance links to the originating `SCIR-H` nodes.

## Prohibited behavior

- no `SCIR-L`-only semantic obligations,
- no ops outside the frozen bootstrap surface,
- no backend-specific semantics without a contract,
- no optimizer-only facts masquerading as canonical semantics,
- no missing provenance for lowered nodes that originated in `SCIR-H`.

## Phase 6B optimization contract

Phase 6B optimization is non-canonical and profile-gated.

- Optimized artifacts must stay within the frozen bootstrap op surface.
- Optimization must not strengthen preservation claims, hide opaque accounting, or feed optimizer-only facts back into canonical `SCIR-H`.
- Allowed `N` transforms in the bootstrap subset are limited to local-cell promotion, redundant load/store elimination, redundant `field.addr` reuse, and trivial CFG cleanup.
- Allowed `D-PY` transforms in the bootstrap subset are limited to trivial CFG cleanup and dead temporary elimination; no motion across `opaque.call` or `async.resume` is valid, and no transform may alter Python-host-visible identity or event-loop order.
- `D-JS` remains doctrine-only in Phase 6B; no executable optimization contract beyond the published host-ordering prohibition is defined here.
- Benchmark-only post-`SCIR-L` emitters may execute optimized artifacts for Track `D`, but those emitters do not redefine the reconstruction contract.

## Reconstructability boundary

May remain reconstructable:

- symbol signatures,
- types,
- module dependencies,
- provenance links.

Must not be assumed idiomatically reconstructable:

- exact structured control shape,
- exact async syntax,
- exact witness syntax,
- source-local declaration layout.

## Validator obligations

See `specs/validator_invariants.md`.
