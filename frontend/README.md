# Frontend Doctrine
Status: Normative

Frontends ingest source language subsets and emit canonical `SCIR-H`.

## Frontend obligations

Every frontend must:

- state its import scope explicitly,
- classify source features by tier,
- reject or bound unsupported constructs explicitly,
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

## Output rule

Frontends emit `SCIR-H`. They do not skip directly to `SCIR-L`.
