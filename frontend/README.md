# Frontend Doctrine
Status: Normative

Frontends ingest source language subsets and emit canonical `SCIR-H`.

## Frontend obligations

Every frontend must:

- state its import scope explicitly,
- classify source features by tier,
- reject or bound unsupported constructs explicitly,
- land checked-in conformance fixtures before broadening executable importer behavior,
- emit a module manifest,
- emit a feature tier report,
- emit a validation report,
- attach opaque boundary contracts for every Tier `C` region.

## Frontend non-goals

Frontends must not:

- claim whole-language fidelity,
- hide host-runtime magic,
- invent semantics absent from the specs,
- skip tier classification.

## Initial priority order

1. Python subset
2. Rust safe subset
3. TypeScript structured subset

## Current executable slices

- Python bootstrap slice: executable importer, lowering, reconstruction, and Track `A`/`B` benchmark automation
- Rust Phase 6A slice: executable fixed-corpus importer, lowering, and Tier `A` round-trip path; benchmark work remains deferred

## Output rule

Frontends emit `SCIR-H`. They do not skip directly to `SCIR-L`.

Early frontend slices may begin with checked-in fixture bundles and conformance checks before executable importer code exists, but those fixtures must still target canonical `SCIR-H`.

For the current Phase 7 TypeScript witness slice, the initial checked-in evidence package is explicitly importer-only:

- admitted fixtures must include source text, canonical `SCIR-H`, `module_manifest`, `feature_tier_report`, and `validation_report`
- rejected boundary fixtures must omit canonical `SCIR-H` while still carrying the importer reports
- no TypeScript fixture in this slice may imply executable `D-JS`, lowering, reconstruction, or benchmark scope
- the initial future TypeScript case matrix is fixed to `a_interface_decl`, `a_interface_local_witness_use`, `d_function_decl`, `d_async_function`, `d_class_implements_interface`, `d_prototype_assignment`, `d_decorator_class`, `d_proxy_construct`, and `d_type_level_runtime_gate`

Future TypeScript importer work must also land a language-local conformance checker before broadening importer behavior:

- it must validate the fixed TypeScript corpus shape and report bundle
- it must expose fixture-integrity and generated-vs-golden conformance modes analogous to the Python and Rust conformance tools
- until that checker exists, TypeScript witness work remains documentation-backed, scaffold-reserved, and importer-only
