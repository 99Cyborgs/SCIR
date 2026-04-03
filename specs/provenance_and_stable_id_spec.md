# Provenance and Stable ID Specification
Status: Normative

## Purpose

Stable identity is required for diff stability, validation, reconstruction mapping, and operator review.

## Active identifier classes

- persistent semantic lineage identity
- canonical content hash
- local or revision-scoped node identity

See `IDENTITY_MODEL.md` for the governing contract.

## Rules

- semantic lineage identity must not include spec version
- canonical formatting changes must not change semantic lineage identity
- pretty-view formatting must not affect any canonical identifier
- lowered `SCIR-L` nodes must retain traceable origin links to `SCIR-H`

## Provenance chain

```text
source span
  -> SCIR-H semantic lineage or local node identity
  -> SCIR-L origin plus lowering rule
  -> reconstructed target span or backend report
```

## Invalid states

- reconstructed output with no traceable `SCIR-H` provenance for supported regions
- lowered nodes with missing origin or lowering rule
- stable IDs derived from non-canonical view text
