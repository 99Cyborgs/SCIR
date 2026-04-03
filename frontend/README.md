# Frontend Doctrine
Status: Normative

Frontends ingest source-language subsets and emit canonical `SCIR-H`.

## Active frontends

1. Python subset importer
2. Rust safe-subset importer

## Deferred frontend

- TypeScript placeholder surface only
- deferred or archived frontend paths that remain on disk are marked with `NOT_ACTIVE.md`

## Frontend obligations

Every active frontend must:

- state its import scope explicitly
- classify source features by tier
- reject or bound unsupported constructs explicitly
- emit `module_manifest`, `feature_tier_report`, and `validation_report`
- attach `opaque_boundary_contract` records for Tier `C` regions

## Output rule

Frontends emit `SCIR-H`. They do not skip directly to `SCIR-L`.
