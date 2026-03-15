# Provenance and Stable ID Specification
Status: Normative

## Purpose

Stable identity is required for diff stability, patch composition, validation, and reconstruction mapping.

## Identifier classes

- `GlobalId = hash(spec_version, module_path, decl_kind, canonical_decl_header)`
- `StableNodeId = hash(GlobalId, canonical_subtree_path)`
- `LocalId = function-local ordinal assigned after normalization`

## Rules

- canonical formatting changes must not change stable IDs,
- local rewrites may change `LocalId` but should preserve `StableNodeId` where the subtree identity remains,
- provenance metadata must not affect semantic hashes,
- every lowered `SCIR-L` instruction that originates from `SCIR-H` should carry an origin reference when feasible.

## Provenance chain

```text
source span
  -> SCIR-H StableNodeId
  -> SCIR-L origin record
  -> reconstructed target span or emitted debug record
```

## Required mappings

- source -> `SCIR-H`
- `SCIR-H` -> `SCIR-L`
- `SCIR-H` or `SCIR-L` -> target output

## Invalid states

- reconstructed output with no source or `SCIR-H` provenance for supported regions,
- lowered nodes with missing origin links where the source is supported,
- stable IDs derived from non-canonical text.
