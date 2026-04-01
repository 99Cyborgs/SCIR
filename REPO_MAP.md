# Repo Map
Status: Informative

## Root governance surface

- `AGENTS.md`: operating rules and mandatory read order
- `README.md`: repository purpose and command contract
- `SYSTEM_BOUNDARY.md`: scope boundary for the current substrate build
- `STATUS.md`: current portfolio posture and blockers
- `EXECUTION_QUEUE.md`: canonical low-touch execution queue derived from roadmap docs
- `REPO_MAP.md`: compact root map for portfolio governance alignment
- `VALIDATION.md`: validation entrypoint
- `ARCHITECTURE_SUMMARY.md`: compact architecture summary
- `DEPENDENCY_NOTES.md`: external dependency posture
- `INTEGRATION_RISKS.md`: integration and promotion risks
- `PROMOTION_NOTES.md`: promotion posture

## Detailed structure

- `docs/repository_map.md`: detailed directory-by-directory structure guide for local execution work

## Main working areas

- `specs/`: normative semantics and validator-facing contracts
- `schemas/`: machine-readable report and manifest schemas
- `docs/`: explanatory doctrine and detailed repository navigation
- `plans/`: plan template and milestone seeds
- `frontend/`: importer doctrine and language-local scope
- `validators/`: validator stack contracts and local rules
- `benchmarks/`: empirical evaluation doctrine
- `reports/`: checked-in example artifacts and derived exports
- `tests/`: checked-in corpora and importer conformance fixtures
- `tooling/`: tool interface contracts
- `ci/`: CI and release policy
- `scripts/`: bootstrap validation and importer-conformance helpers

## Boundary rule

Use `REPO_MAP.md` for the compact root operating surface and `docs/repository_map.md` for the detailed internal structure map. Do not move semantic authority out of `specs/`.
