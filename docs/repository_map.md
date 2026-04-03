# Repository Map
Status: Informative

## Current directories

| Path | Responsibility |
| --- | --- |
| `/` | top-level doctrine, sequencing, decisions, and command contract |
| `docs/` | explanatory doctrine and navigation |
| `specs/` | normative semantics and validator-facing contracts |
| `schemas/` | report and manifest schemas |
| `plans/` | plan template, seeds, and active execution plans |
| `frontend/` | importer doctrine |
| `validators/` | validator stack contracts |
| `backends/` | backend contracts; Wasm is active |
| `benchmarks/` | benchmark doctrine |
| `reports/` | example artifacts and derived exports |
| `tests/` | checked-in corpora and invalid examples |
| `tooling/` | active MVP tooling contracts plus deferred placeholders |
| `ci/` | CI and release policy |
| `.github/` | automation entry points |
| `scripts/` | executable bootstrap helpers |

## Missing but expected later

| Path | Status |
| --- | --- |
| `grammar/` | not yet a standalone directory |
| `parser/` | active parser still lives in `scripts/scir_h_bootstrap_model.py` |
| `formatter/` | active formatter still lives in `scripts/scir_h_bootstrap_model.py` |
| `runtime/` | not yet materialized as a standalone directory |

## Responsibility rule

Normative semantics belong in `specs/`, not in deferred tooling surfaces or historical plans.
