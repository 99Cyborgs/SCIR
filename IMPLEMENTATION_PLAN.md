# IMPLEMENTATION_PLAN
Status: Normative

## Purpose

This file fixes the active MVP implementation order.

## Sequencing rule

Do not widen beyond the current MVP without a new decision-register entry, updated root boundary docs, and an approved plan.

## Active phase plan

| Phase | Objective | Primary files | Exit gate |
| --- | --- | --- | --- |
| 0 | MVP kernel hardening | `README.md`, `SYSTEM_BOUNDARY.md`, `ARCHITECTURE.md`, `VALIDATION_STRATEGY.md`, `BENCHMARK_STRATEGY.md`, `scripts/*` | docs, scripts, schemas, and CI enforce the same narrowed MVP |
| 1 | `SCIR-H` kernel | `specs/scir_h_spec.md`, `scripts/scir_h_bootstrap_model.py`, `IDENTITY_MODEL.md`, `SPEC_COMPLETENESS_CHECKLIST.md` | canonical `SCIR-H` subset, identity rules, and canonical/view split are coherent |
| 2 | Python proof loop | `frontend/python/*`, `scripts/scir_python_bootstrap.py`, `scripts/scir_bootstrap_pipeline.py`, `docs/reconstruction_policy.md` | import -> `SCIR-H` -> validate -> `SCIR-L` -> validate -> Python reconstruction is credible |
| 3 | Rust safe-subset importer | `frontend/rust/*`, `scripts/scir_rust_bootstrap.py`, `tests/rust_importer/*` | Rust importer emits canonical `SCIR-H` and respects active unsupported boundaries |
| 4 | Retained Wasm reference backend boundary | `backends/wasm/*`, `LOWERING_CONTRACT.md`, `schemas/preservation_report.schema.json` | helper-free Wasm boundary remains explicit, subset-bound, and report-covered without becoming the active widening lane |
| 5 | Benchmark falsification loop | `benchmarks/*`, `scripts/benchmark_contract_dry_run.py` | Track `A` and Track `B` run on the fixed Python proof loop with explicit baselines and kill gates |
| 6 | Retained Track `C` pilot boundary | `benchmarks/*`, `plans/*` | Track `C` posture remains explicit, non-default, and synchronized without becoming the active benchmark gate |

## Current phase status

- Phase 2 exit gate is satisfied by the fixed 11-case Python proof loop.
- The active item after Phase 2 completion is post-proof-loop freeze enforcement and contract reset, not further Python widening.
- Phase 3 is not auto-activated; Rust remains importer-first for the remainder of the MVP, and any future Rust proof-loop, backend, or benchmark activation is a post-MVP reactivation decision.
- Phase 4 is not auto-activated; helper-free Wasm remains a bounded retained support lane for the remainder of the MVP, and any future Wasm widening, backend activation, or benchmark promotion is a post-MVP reactivation decision.
- Phase 6 is not auto-activated; Track `C` remains a retained non-default diagnostic pilot for the remainder of the MVP, and any future promotion into the default executable gate or broader benchmark claim surface is a post-MVP reactivation decision.

## Non-active work

These are not current implementation phases:

- TypeScript witness work
- active `D-JS`
- Track `D`
- native backend expansion
- broad tooling platform work

## Phase details

### Phase 0 - MVP kernel hardening

Required outcomes:

- remove contradictory MVP claims
- remove deferred surfaces from active validation and CI
- make the exact active surface visible in root docs

### Phase 1 - `SCIR-H` kernel

Required outcomes:

- `SCIR-H` subset is explicit and tested
- canonical storage and human-facing view are split
- persistent identity is decoupled from spec version

### Phase 2 - Python proof loop

Required outcomes:

- Python importer remains the decisive end-to-end loop
- `SCIR-L` lowering remains derivative
- Python reconstruction remains `SCIR-H`-driven
- the executable proof loop stays frozen at the fixed 11-case corpus until a new widening decision is recorded

### Phase 3 - Rust safe subset

Required outcomes:

- Rust importer remains subset-bound
- ownership and unsafe boundaries remain explicit
- Rust importer evidence does not silently widen executable claims
- Rust is not promoted into an active round-trip, backend, or benchmark lane inside the MVP without a new post-MVP reactivation decision

### Phase 4 - Retained Wasm reference backend boundary

Required outcomes:

- helper-free Wasm remains a retained bounded reference backend, not an auto-activating next implementation phase
- Wasm emission target is explicit
- Wasm claims remain profile `P` and subset-bound
- helper-free Wasm remains bounded to the scalar subset plus the fixed record-cell ABI slice for `a_struct_field_borrow_mut`
- broader record, borrow, imported-memory, host-facing, or parity-affecting Wasm work still requires explicit ABI/storage decisions before any further execution widening
- no native or host parity claim leaks in
- any future helper-free Wasm widening, backend activation, or benchmark promotion requires a new post-MVP reactivation decision plus synchronized roadmap, benchmark, profile/preservation, and repo-contract updates

### Phase 5 - Benchmark falsification loop

Required outcomes:

- Track `A` and `B` are executable and reproducible
- baselines remain strong
- Track `C` remains non-default and subordinate to the frozen proof loop

### Phase 6 - Retained Track `C` pilot boundary

Required outcomes:

- Track `C` remains a retained non-default diagnostic pilot, not an auto-activating post-Phase-5 benchmark lane
- checked-in Track `C` sample artifacts stay illustrative and outside the default executable benchmark gate
- opaque-boundary cases remain boundary-accounting-only inside the opt-in pilot
- any future Track `C` promotion into the default executable gate or broader benchmark claim surface requires a new post-MVP reactivation decision plus synchronized roadmap, benchmark, and repo-contract updates

## Planning trigger

Any change to this sequencing requires:

- a plan in `plans/`,
- a decision-register update,
- benchmark impact notes,
- updated `CURRENT_FOCUS.md` and `BACKLOG.md` when scope moves in or out of the active implementation lane.
