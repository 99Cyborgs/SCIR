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

## Diagnostic contract

Validators must produce stable diagnostics with:

- code
- severity
- message
- artifact path or identifier
- stable node ID or block reference where available
- suggested downgrade or fix when applicable
