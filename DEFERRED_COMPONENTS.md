# DEFERRED_COMPONENTS
Status: Normative

## Purpose

These paths remain on disk but are not part of the active SCIR MVP.

## Deferred or archived paths

| Path | State | Reactivation condition |
| --- | --- | --- |
| `frontend/typescript/` | deferred | only after root docs, implementation plan, validation strategy, and benchmark strategy are updated together |
| `tests/typescript_importer/` | archived placeholder corpus | only after a real TypeScript importer exists and is promoted by plan |
| `scripts/typescript_importer_conformance.py` | deferred | only after the placeholder corpus becomes live |
| `plans/milestone_07_typescript_witness_slice.md` | archived historical plan | only for historical reference; not an active roadmap source |
| `tooling/agent_api.md` | deferred | only if the checker/formatter/compiler surfaces are already stable and the patch API carries no semantic drift risk |
| `tooling/explorer_contract.md` | deferred | only if a no-burden explorer can stay derivative of canonical artifacts |
| graph, debugger, and language-server ideas in `tooling/README.md` | deferred | only after the MVP proof loop is stable |
| benchmark Track `D` surfaces in legacy scripts | deferred | only after the Wasm backend MVP is emitter-backed and earlier benchmark loops stay stable |

## Rule

Deferred or archived paths that remain on disk must carry an adjacent `NOT_ACTIVE.md` marker.

Deferred or archived paths must not be named as active commitments in:

- `README.md`
- `SYSTEM_BOUNDARY.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- CI workflow descriptions
