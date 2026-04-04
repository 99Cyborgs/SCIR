# REPO_MAP
Status: Informative

## Root governance surface

- `AGENTS.md`: operating rules and read order
- `README.md`: repository purpose and command contract
- `SYSTEM_BOUNDARY.md`: active scope boundary
- `MVP_SCOPE.md`: exact subsystem audit and keep/defer/archive classification
- `ROADMAP.md`: active roadmap after narrowing
- `DEFERRED_COMPONENTS.md`: explicit non-MVP surfaces
- `UNSUPPORTED_CASES.md`: operator-facing unsupported boundary
- `ARCHITECTURE.md`: normative system architecture
- `LOWERING_CONTRACT.md`: `SCIR-H -> SCIR-L` derivative contract
- `IDENTITY_MODEL.md`: semantic lineage, content hash, and local identity contract
- `SPEC_COMPLETENESS_CHECKLIST.md`: spec-to-implementation coherence matrix
- `VALIDATION.md`: validation entrypoint

## Main working areas

- `specs/`: normative semantics and validator-facing contracts
- `schemas/`: report and manifest schemas
- `docs/`: explanatory doctrine and detailed navigation
- `frontend/`: importer doctrine
- `validators/`: validator stack contracts
- `runtime/`: bounded `SCIR-L` interpreter and backend execution harnesses for translation validation
- `backends/`: backend contracts; Wasm is the only active backend path
- `benchmarks/`: benchmark doctrine
- `tests/`: checked-in corpora and invalid examples
- `scripts/`: bootstrap parser, formatter, importer, lowering, and validation helpers
- `tooling/`: MVP tooling contracts plus explicitly deferred tooling surfaces
- `reports/`: illustrative report fixtures and derived exports
- `plans/`: plan template, milestone seeds, and active execution plans

## Boundary rule

Normative semantics belong in `specs/` plus the root architecture contracts named above. Deferred or archived paths must not be treated as active MVP surfaces unless the root governance files are updated together.
