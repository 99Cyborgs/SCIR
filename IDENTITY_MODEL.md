# IDENTITY_MODEL
Status: Normative

## Purpose

SCIR uses three different identities. They must not be conflated.

## Identifier classes

### Persistent semantic lineage identity

- stable across formatting-only changes
- stable across declaration reordering absorbed by semantic canonicalization
- stable across spec-version bumps when semantics do not change
- not a content hash
- not revision-scoped

### Canonical content hash

- hash of canonical storage form
- changes when canonical semantic content changes
- may change when canonical storage changes in a meaningfully visible way

### Local or revision-scoped node identity

- scoped to a specific canonical artifact revision
- suitable for diagnostics, block references, and local patch planning
- not stable across arbitrary rewrites

## Executable invariants

- semantic lineage identity must not include spec version
- semantic lineage identity must not include pretty-view text or formatting
- semantic lineage identity must remain stable across formatting-only changes
- semantic lineage identity must remain stable across declaration reordering absorbed by semantic canonicalization
- canonical content hash must be derived only from canonical storage
- revision-scoped node identity must vary when the revision tag changes

## Required separation

Persistent lineage must not include:

- spec version
- pretty-view formatting
- non-canonical comments
- provenance sidecars

Canonical content hash must not include:

- pretty-view formatting
- non-canonical comments
- revision-scoped IDs

## Canonical storage vs human-facing view

Canonical storage:

- deterministic
- hashed
- validator-facing
- newline-delimited and machine-stable

Human-facing view:

- non-canonical
- may include provenance, comments, source order notes, and elided annotations
- must never affect lineage IDs or canonical content hashes

## Migration note

The old `hash(spec_version, ...)` stable-ID story is deprecated.
Spec version remains useful for report compatibility, not for persistent semantic lineage identity.
