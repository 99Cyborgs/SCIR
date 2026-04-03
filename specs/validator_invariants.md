# Validator Invariants
Status: Normative

## Purpose

These invariants are hard constraints. Validators must reject violations.

## `SCIR-H` invariants

| Code | Invariant | Failure prevented |
| --- | --- | --- |
| H001 | no hidden control transfer | silent semantic drift |
| H002 | no implicit mutation | unsound state reasoning |
| H003 | no implicit effectful operations | false purity claims |
| H004 | no ambiguous name resolution | unstable binding |
| H005 | canonical formatting stability | noisy diffs and unstable hashes |
| H006 | deterministic canonical storage | non-reproducible hashes |
| H007 | explicit field places where source semantics depend on projection | hidden alias and mutation behavior |
| H008 | explicit opaque or unsafe boundaries | overclaimed support |
| H009 | unsupported constructs must remain deferred or rejected explicitly | false feature admission |
| H010 | ownership and alias modes constrain mutation sites | unsound borrow or opaque mutation |

## `SCIR-Hc` invariants

| Code | Invariant | Failure prevented |
| --- | --- | --- |
| HC001 | parse/format normalization is stable for compressed storage | unstable compressed transport |
| HC002 | compressed storage round-trips to semantically equivalent canonical `SCIR-H` | silent semantic drift |
| HC003 | compressed normalization statistics and boundary metadata remain internally coherent | false compression claims |
| HC004 | `SCIR-Hc` declares and preserves a derived-only authority boundary | accidental semantic-authority drift |
| HC005 | `SCIR-H -> SCIR-Hc` derivation is deterministic and idempotent | context-dependent compression drift |
| HC006 | every compressed omission is explicitly justified by node provenance and adds no hidden semantics | heuristic reconstruction or semantic injection |
| HC007 | benchmark reports keep `SCIR-Hc` evidence inside a declared claim class and evidence class | cross-class benchmark leakage |

## `SCIR-L` invariants

| Code | Invariant | Failure prevented |
| --- | --- | --- |
| L001 | well-formed CFG | invalid lowering and backend bugs |
| L002 | SSA and block-parameter correctness | malformed dataflow |
| L003 | effect token consistency | reordered non-memory effects |
| L004 | memory token consistency | unsound memory sequencing |
| L005 | provenance continuity from `SCIR-H` | un-auditable lowering |
| L006 | named lowering-rule coverage | hidden derivative semantics |
| L007 | no `SCIR-L`-only semantics | H/L drift |
| L008 | explicit boundary ops for opaque or unsafe calls | hidden interop assumptions |

## Translation-validation invariants

| Code | Invariant |
| --- | --- |
| T001 | lowering does not strengthen preservation claims silently |
| T002 | lowering does not erase required boundary annotations |
| T003 | provenance remains traceable |
| T004 | path and profile remain explicit |

## Active shape constraints

- active canonical `SCIR-H` is limited to the grammar in `specs/scir_h_spec.md`
- active derived `SCIR-Hc` must round-trip back to canonical `SCIR-H` before any downstream claim
- active derived `SCIR-Hc` must carry the derived-only authority marker and machine-readable omission provenance
- lowering, reconstruction, and backend emission must reject direct `SCIR-Hc` input
- `benchmark_report` must declare `claim_class` and `evidence_class`, and those fields must bound any `SCIR-Hc` claim surface
- active canonical `SCIR-L` is limited to the grammar in `specs/scir_l_spec.md`
- loop and `try/catch` forms may exist in importer-only `SCIR-H` slices without active lowering
- the importer-only `!throw` effect marker is admitted only on bounded Tier `B` `try/catch` evidence; standalone `throw` syntax remains unsupported
- unused declared effects are invalid in the active subset
- `borrow<T>` must not be used as a mutation root; `borrow_mut<T>` remains the only writable borrow mode
- `opaque<T>` values must not be projected as if their internals were modeled
- active lowering must carry both `origin` and `lowering_rule`
- active `SCIR-L` provenance origins must remain rooted in the emitting `SCIR-H` module id
- pretty views must not be accepted as canonical storage

## Diagnostic contract

Validators must emit stable diagnostics with:

- code
- severity
- message
- artifact path or identifier
- node, block, or lowering-rule reference where available
