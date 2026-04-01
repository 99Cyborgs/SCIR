# Validator Invariants
Status: Normative

## Purpose

These invariants are hard constraints. Validators must reject violations.

## `SCIR-H` invariants

| Code | Invariant | Failure prevented |
| --- | --- | --- |
| H001 | no hidden control transfer | missed exceptional edges and unstable transformations |
| H002 | no implicit effectful operations | unsound purity and capability assumptions |
| H003 | no implicit mutation | alias and state-model unsoundness |
| H004 | no implicit conversions | ambiguous semantics and backend drift |
| H005 | no ambiguous name resolution | unstable cross-module binding |
| H006 | explicit cross-module dependencies | repository-scope graph errors |
| H007 | explicit unsafe regions | false safety claims |
| H008 | explicit concurrency boundaries | false determinism and race-freedom claims |
| H009 | explicit opaque boundaries | over-claiming semantics through unknown code |
| H010 | explicit capability requirements | ambient authority leaks |
| H011 | canonical formatting stability | noisy diffs and unstable prompts |
| H012 | deterministic serialization | non-reproducible hashes and caches |

## `SCIR-L` invariants

| Code | Invariant | Failure prevented |
| --- | --- | --- |
| L001 | well-formed CFG | invalid lowering and backend control bugs |
| L002 | SSA and block-parameter correctness | malformed dataflow |
| L003 | effect token consistency | reordered non-memory effects |
| L004 | memory token consistency | unsound memory sequencing |
| L005 | provenance continuity from `SCIR-H` | un-auditable lowering |
| L006 | no `SCIR-L`-only semantics | H/L drift |
| L007 | explicit boundary ops for foreign or opaque calls | hidden interop assumptions |

## Translation-validation invariants

| Code | Invariant |
| --- | --- |
| T001 | lowering does not strengthen preservation claims silently |
| T002 | lowering does not erase required opaque or unsafe accounting |
| T003 | provenance remains traceable |
| T004 | profile contracts remain explicit |

## Canonical v0.1 shape constraints

- `H001` requires canonical exception control to appear only as indentation-sensitive `try` and `catch x T` suites; no hidden handler edges, `finally`, or multi-catch forms are valid.
- `H001` and `H008` require canonical concurrency choice to appear only as indentation-sensitive `select` suites with explicit channel `send` or `recv` arms.
- `H002` keeps non-throw effects explicit across `try/catch`; handling `throw(E)` does not hide any other effect obligation.
- `H008` forbids implicit default, timeout, fairness, or priority semantics for canonical v0.1 `select`.
- `H011` requires canonical `SCIR-H` to round-trip through parse-normalize-format with two-space indentation, newline-delimited suites, compact effect rows, direct calls rendered as `f(args)`, and mutable locals rendered as `var` plus `set`.
- `H011` also requires field places to remain in the canonical `LocalId(.FieldId)*` form.
- `L001` and `L002` require the bootstrap `SCIR-L` surface to use only `ret`, `br`, and `cond_br` terminators and block parameters as the only merge mechanism; `phi` is not part of the frozen subset.
- `L003` and `L004` require memory tokens to appear only on mutable-local lowering paths and effect tokens to appear only on lowered direct calls, `await`, and opaque boundaries in the bootstrap subset.
- `L006` forbids `SCIR-L` bootstrap ops outside `const`, `cmp`, `alloc`, `store`, `load`, `field.addr`, `call`, `async.resume`, and `opaque.call`.
- `L007` requires `opaque.call` to remain justified by an explicit `SCIR-H` opaque boundary and forbids lowering a validated direct call into `opaque.call` without that boundary.
- `T001` and `T002` require bootstrap translation validation to keep `a_basic_function` and `a_async_await` at `R/P1` and `c_opaque_call` at `D-PY/P3`; lowering may normalize structure but may not strengthen those claims.
- `T001` and `T002` also require Rust Phase 6A to keep `a_mut_local`, `a_struct_field_borrow_mut`, and `a_async_await` at `R/P1` and `c_unsafe_call` at `N/P3`.

## Diagnostic contract

Validators must produce stable diagnostics with:

- code
- severity
- message
- artifact path or identifier
- stable node ID or block reference where available
- suggested downgrade or fix when applicable
