# Milestone 02 — Python Importer
Status: proposed

## Objective

Define and implement the targeted Python subset importer contract for `SCIR-H`.

## Scope

- Python subset scope
- tier classification rules
- explicit unsupported and opaque boundaries
- importer outputs: module manifest, feature tier report, validation report

## Non-goals

- broad Python reflection support
- import hooks
- metaclass-heavy frameworks
- monkey patching fidelity

## Touched files

- `frontend/README.md`
- `frontend/python/AGENTS.md`
- `frontend/python/IMPORT_SCOPE.md`
- `docs/feature_tiering.md`
- `docs/unsupported_cases.md`
- `schemas/module_manifest.schema.json`
- `schemas/feature_tier_report.schema.json`
- `VALIDATION_STRATEGY.md`

## Invariants

- no silent Tier `C` or `D` fallback
- host-sensitive semantics remain profile-qualified
- unsupported Python features stay explicit

## Risks

- subset too narrow to be useful
- class and async semantics require more `D`-profile handling than expected

## Validation steps

```bash
make validate
make benchmark
```

## Rollback strategy

Narrow the importer scope and remove over-claims rather than adding hidden runtime behavior.

## Evidence required for completion

- explicit Python scope file
- importer report contract
- unsupported-case map tied to tiers
- benchmark doctrine still coherent for the subset
