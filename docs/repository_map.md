# Repository Map
Status: Informative

## Current directories

| Path | Responsibility |
| --- | --- |
| `/` | top-level doctrine, sequencing, decisions, and command contract |
| `docs/` | explanatory doctrine and repository-level navigation |
| `specs/` | normative semantics and validator-facing contracts |
| `schemas/` | machine-readable report and manifest schemas |
| `plans/` | plan template and milestone seeds |
| `frontend/` | importer doctrine and language-local scope |
| `validators/` | validator stack contracts and local rules |
| `benchmarks/` | empirical evaluation doctrine |
| `reports/` | checked-in example report artifacts, derived exports for normative registers, and later generated validation and benchmark bundles |
| `tooling/` | tool interface contracts |
| `ci/` | CI and release policy |
| `.github/` | automation entry points |
| `scripts/` | bootstrap validation helpers |

## Future code roots

These directories are expected later. Do not create them ad hoc without a plan.

| Planned path | Responsibility |
| --- | --- |
| `frontend/<lang>/importer/` | language-specific importer implementation |
| `scir-h/` | parser, formatter, canonicalizer |
| `scir-l/` | lowering and IR utilities |
| `runtime/` | profile-specific runtime support |
| `backends/` | reconstruction and emission backends |
| `benchmarks/harness/` | executable benchmark runner |
| `tests/` | golden corpora, validator, lowering, and reconstruction tests |

## Responsibility rule

Normative semantics belong in `specs/`, not in ad hoc code comments or tool-specific behavior.
