# ARCHITECTURE
Status: Normative

## Core doctrine

SCIR is a two-layer system.

| Layer | Canonical status | Purpose | Must preserve |
| --- | --- | --- | --- |
| `SCIR-H` | canonical | inspection, transformation, reconstruction, AI-facing editing | structured semantics, including explicit exception and channel-selection boundaries, explicit effects, capabilities, witnesses, ownership modes, module boundaries, stable IDs, auditable opaque regions |
| `SCIR-L` | derivative | control/dataflow analysis, lowering, optimization, backend preparation | value flow, control flow, effect/memory sequencing, lowered async/witness structures, provenance back to `SCIR-H` |

`SCIR-H` is the semantic source of truth.
`SCIR-L` must not become an independent language design.

## First credible product boundary

Required for the first credible product:

- importer for a targeted subset,
- canonical `SCIR-H`,
- `SCIR-H` validator,
- `SCIR-H -> SCIR-L` lowering,
- `SCIR-L` validator,
- reconstruction,
- preservation reporting,
- benchmark harness.

Not required for the first credible product:

- a new user language,
- broad language coverage,
- broad native backends,
- full proof stack,
- whole-language exact fidelity claims.

## System flow

```text
source text
  -> source parser
  -> source AST
  -> desugaring and semantic normalization
  -> explicit captures / witnesses / effects / capabilities / boundaries
  -> SCIR-H
  -> SCIR-H validation
  -> SCIR-L lowering
  -> SCIR-L validation
  -> optimization (profile-gated)
  -> reconstruction or backend emission
  -> preservation / validation / reconstruction reports
  -> benchmark harness
```

## Phase 1 control-surface note

Canonical v0.1 `SCIR-H` now includes:

- minimal single-catch `try/catch`
- minimal channel `select`

Their broader `SCIR-L` lowering remains future Phase 3+ work. The current repository freeze defines only the bootstrap await and opaque-boundary lowering surface.

## State and report model

Every major stage emits explicit state and explicit reports.

| Stage artifact | Required report |
| --- | --- |
| imported module | `module_manifest` + `feature_tier_report` |
| validated `SCIR-H` | `validation_report` |
| validated `SCIR-L` | `validation_report` |
| lowered or reconstructed artifact | `preservation_report` |
| reconstructed source | `reconstruction_report` |
| benchmark run | `benchmark_result` |
| opaque or unsafe boundary | `opaque_boundary_contract` |

## Compact canonical surface

The executable bootstrap subset now uses a compact canonical `SCIR-H` surface:

- indentation-sensitive suites instead of brace-delimited blocks,
- newline-delimited statements instead of semicolon-delimited storage,
- compact effect rows (`!` or `!a,b`),
- direct calls as `f(args)`,
- explicit mutation via `var` and `set`,
- explicit field places such as `counter.value`,
- intrinsic scalar comparisons such as `lt x y`.

Canonical `SCIR-H` validation for the bootstrap subset is parse-normalize-format based. Legacy bootstrap text forms such as `let cell`, `write`, `read`, and `call f(args)` are non-canonical after this cutover.

## Frozen bootstrap `SCIR-L`

Phase 3 now freezes the executable bootstrap `SCIR-L` surface around the op set already emitted by the lowering path:

- value ops: `const`, `cmp`
- memory ops: `alloc`, `store`, `load`
- place projection: `field.addr`
- effect and boundary ops: `call`, `async.resume`, `opaque.call`
- terminators: `ret`, `br`, `cond_br`
- block parameters as the only merge mechanism

This freeze is intentionally derivative and subset-bound. It does not authorize generic arithmetic, witness ops, exception lowering, loop lowering, or backend dialect growth before the source subset requires them.

Phase 6A widens the executable subset only enough to admit Rust borrowed-record field places and explicit unsafe boundaries:

- `SCIR-H` gains explicit readable and writable field places,
- `SCIR-L` gains `field.addr`,
- Rust Tier `A` reconstruction is fixed at `R/P1`,
- Rust explicit unsafe boundaries are fixed at `N/P3`,
- optimization remains Phase 6B work.

Phase 6B keeps the op surface frozen while adding profile-gated optimization and benchmark-only post-`SCIR-L` emitters:

- executable Track `D` slices exist only for Rust `N` and Python `D-PY`,
- `D-JS` remains doctrine-only,
- benchmark-only emitters do not replace the `SCIR-H`-driven reconstruction contract.

Post-6B roadmap sequencing is now explicit:

- the immediate near-term semantic expansion milestone is Python Milestone 02B,
- the next new architecture phase is witness-bearing second-language evidence,
- the default candidate slice is TypeScript interface-shaped witnesses before Rust trait/impl execution work,
- no new backend track is introduced by that sequencing.

## Frozen bootstrap reconstruction

Phase 4 freezes the executable reconstruction path as `SCIR-H`-driven and subset-bound:

- validated compact `SCIR-H` is the reconstruction source of truth,
- `SCIR-L` may provide diagnostics but is not the default reconstruction source,
- `a_basic_function` and `a_async_await` reconstruct at `R/P1`,
- `c_opaque_call` reconstructs at `D-PY/P3` with explicit opaque accounting preserved,
- rejected Tier `D` cases do not produce reconstruction artifacts,
- provenance completeness for the bootstrap slice is line-granular over non-empty canonical `SCIR-H` lines.

## Target profiles

Every claim must state one or more target profiles.

| Code | Profile | Primary objective | Preservation ceiling |
| --- | --- | --- | --- |
| `R` | Reconstruction | source-faithful regeneration and auditability | `P0/P1`; `P2` only with explicit contract disclosure |
| `N` | Native performance | efficient Rust/C++-class lowering | usually `P1/P2` |
| `P` | Portable execution | safe portable execution through Wasm or equivalent | usually `P1/P2/P3` |
| `D-PY` | Dynamic host (Python) | high-fidelity Python runtime interop | `P0/P1` on supported subsets, otherwise `P2/P3` |
| `D-JS` | Dynamic host (JS/TS) | high-fidelity JS/TS runtime interop | `P0/P1` on supported subsets, otherwise `P2/P3` |

See `docs/target_profiles.md`.

## Preservation levels

Canonical labels:

- `P0` exact semantic and observable behavior preservation
- `P1` semantically equivalent normalized preservation
- `P2` contract-bounded preservation
- `P3` opaque-boundary preservation only
- `PX` unsupported

See `docs/preservation_contract.md`.

## Feature tiers

Canonical labels:

- `A`: validator-understood semantics, high-fidelity reconstruction expected
- `B`: validator-understood semantics with normalization loss
- `C`: opaque or unsafe boundary only
- `D`: rejected / unsupported

See `docs/feature_tiering.md`.

## Cross-cutting invariants

The following are hard repository invariants.

- no hidden control transfer
- no implicit effectful operations in canonical `SCIR-H`
- no implicit mutation in canonical `SCIR-H`
- no implicit conversions in canonical `SCIR-H`
- no ambiguous name resolution
- explicit cross-module dependencies
- explicit unsafe, opaque, concurrency, and capability boundaries
- deterministic parser/formatter and deterministic serialization
- provenance from source to `SCIR-H`; from `SCIR-H` to `SCIR-L`; from `SCIR-H` or `SCIR-L` to reconstructed output

See `specs/validator_invariants.md`.

## Stable identity and provenance

Canonical identity model:

- `GlobalId = hash(spec_version, module_path, decl_kind, canonical_decl_header)`
- `StableNodeId = hash(GlobalId, canonical_subtree_path)`
- `LocalId = function-local ordinal assigned after normalization`

Stable IDs survive formatting and most local rewrites. Local IDs do not.

See `specs/provenance_and_stable_id_spec.md`.

## Trust boundary

Trusted or narrow-trust components:

- `SCIR-H` validator
- `SCIR-L` validator
- runtime core for the active profile
- proof checker kernel, if used

Partially trusted or best-effort components:

- importers
- optimizers
- most backends
- foreign bindings
- host runtimes

Mitigation is translation validation, differential testing, contract checks, and explicit downgrade rules.

Post-02B and Phase 7 work must tighten this trust boundary rather than bypass it:

- `H -> L` provenance continuity remains blocking,
- downgrade reporting must stay profile-qualified,
- optimizer-only facts must not flow back into canonical `SCIR-H`,
- witness-bearing second-language work does not authorize executable `D-JS` artifacts without a later published contract.

## Architecture change protocol

No architecture change is complete until:

- a decision register entry exists or is updated,
- affected normative specs are updated,
- affected docs are updated,
- validator implications are updated,
- benchmark implications are updated,
- open questions are recorded if ambiguity remains.
