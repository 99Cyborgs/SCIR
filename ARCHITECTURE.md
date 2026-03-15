# ARCHITECTURE
Status: Normative

## Core doctrine

SCIR is a two-layer system.

| Layer | Canonical status | Purpose | Must preserve |
| --- | --- | --- | --- |
| `SCIR-H` | canonical | inspection, transformation, reconstruction, AI-facing editing | structured semantics, explicit effects, capabilities, witnesses, ownership modes, module boundaries, stable IDs, auditable opaque regions |
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

## Target profiles

Every claim must state one or more target profiles.

| Code | Profile | Primary objective | Preservation ceiling |
| --- | --- | --- | --- |
| `R` | Reconstruction | source-faithful regeneration and auditability | `P0/P1`; `P2` only with explicit contract disclosure |
| `N` | Native performance | efficient Rust/C++-class lowering | usually `P1/P2` |
| `P` | Portable execution | safe portable execution through Wasm or equivalent | usually `P1/P2/P3` |
| `D` | Dynamic host | high-fidelity Python/TS/JS runtime interop | `P0/P1` on supported subsets, otherwise `P2/P3` |

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

## Architecture change protocol

No architecture change is complete until:

- a decision register entry exists or is updated,
- affected normative specs are updated,
- affected docs are updated,
- validator implications are updated,
- benchmark implications are updated,
- open questions are recorded if ambiguity remains.
