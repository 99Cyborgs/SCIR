# DECISION_REGISTER
Status: Normative

This register records repository-level architectural decisions. Operational queues, timestamped checkpoints, and run bookkeeping do not belong here.

| ID | Status | Decision | Constraint imposed | Reversible | First validation |
| --- | --- | --- | --- | --- | --- |
| DR-001 | accepted | `SCIR-H` is the only normative semantic representation. | No other layer, report, or backend artifact may define semantics independently. | no | `make validate` |
| DR-002 | accepted | `SCIR-L` is derivative only. | Every semantically meaningful `SCIR-L` op must carry validated `SCIR-H` origin plus a named lowering rule. | partly | `python scripts/scir_bootstrap_pipeline.py --mode validate` |
| DR-003 | accepted | The Python subset importer is the active implementation lane. | Scope-widening work defaults to Python subset import, canonical `SCIR-H`, and validator hardening before other fronts. | yes | `python scripts/run_repo_validation.py` |
| DR-004 | accepted | Rust remains importer-first evidence only in the MVP. | Rust support must stay subset-bound and must not silently become the active proof loop. | yes | `python scripts/rust_importer_conformance.py --mode validate-fixtures` |
| DR-005 | accepted | Wasm remains a bounded reference backend. | Wasm success does not imply native parity, host parity, or broader semantic support. | yes | `python scripts/scir_bootstrap_pipeline.py --mode validate` |
| DR-006 | accepted | Benchmarking is retained but subordinate to implementation value. | Track `A` and `B` may remain runnable, but they do not control the active widening target. | yes | `python scripts/benchmark_contract_dry_run.py` |
| DR-007 | accepted | Release-bundle machinery is opt-in only. | No default validation, CI, or README command may depend on release-bundle generation. | yes | `python scripts/run_repo_validation.py` |
| DR-008 | accepted | Repository control surfaces are limited to `CURRENT_FOCUS.md`, `BACKLOG.md`, and this register. | Queue chains, derived exports, and timestamp-driven execution control are not part of the default operating model. | yes | `python scripts/validate_repo_contracts.py --mode validate` |
| DR-009 | accepted | Executable proof-loop promotions must synchronize locked benchmark and retained Track `C` sample surfaces in the same change. | Promoting an executable Python case requires matching updates to benchmark case lists, Track `C` pilot/sample contracts, and focus/backlog records. | yes | `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot` |
| DR-010 | accepted | The parameterized async local-call shape may widen the executable Python proof loop without widening helper-free Wasm or sweep smoke. | `b_async_arg_await` must stay exact-shape, remain helper-free-Wasm non-emittable, and must not alter the frozen Tier `A` sweep micro corpus. | yes | `python scripts/run_repo_validation.py --include-track-c-pilot` |
| DR-011 | accepted | The bounded while-call update shape may widen the executable Python proof loop without widening break/continue, classes, exceptions, helper-free Wasm, or sweep smoke. | `b_while_call_update` must stay exact-shape, remain helper-free-Wasm non-emittable, and must not alter the frozen Tier `A` sweep micro corpus or importer-only posture of `b_while_break_continue`, class cases, and `d_try_except`. | yes | `python scripts/run_repo_validation.py --include-track-c-pilot` |
| DR-012 | accepted | The bounded break/continue loop-control shape may widen the executable Python proof loop without widening classes, exceptions, helper-free Wasm, or sweep smoke. | `b_while_break_continue` must stay exact-shape, remain helper-free-Wasm non-emittable, and must not alter the frozen Tier `A` sweep micro corpus or importer-only posture of class cases and `d_try_except`. | yes | `python scripts/run_repo_validation.py --include-track-c-pilot` |
| DR-013 | accepted | The bounded record-like class-init shape may widen the executable Python proof loop without widening class field-update semantics, exceptions, helper-free Wasm, or sweep smoke. | `b_class_init_method` must stay exact-shape, remain helper-free-Wasm non-emittable, and must not alter the frozen Tier `A` sweep micro corpus or importer-only posture of `b_class_field_update` and `d_try_except`. | yes | `python scripts/run_repo_validation.py --include-track-c-pilot` |
| DR-014 | accepted | The bounded record-like class field-update shape may widen the executable Python proof loop without widening exception lowering, helper-free Wasm, or sweep smoke. | `b_class_field_update` must stay exact-shape, remain helper-free-Wasm non-emittable, and must not alter the frozen Tier `A` sweep micro corpus or importer-only posture of `d_try_except`. | yes | `python scripts/run_repo_validation.py --include-track-c-pilot` |
| DR-015 | accepted | The exact single-handler `d_try_except` shape may widen the executable Python proof loop through one bounded derivative exception form without widening standalone `throw`, broader exception control, helper-free Wasm, or sweep smoke. | `d_try_except` must stay exact-shape, use only the fixed `ValueError` catch/default-return lowering path, remain helper-free-Wasm non-emittable, and must not imply broader exception lowering beyond the admitted proof-loop slice. | yes | `python scripts/run_repo_validation.py --include-track-c-pilot` |
| DR-016 | accepted | The 11-case Python executable proof loop is frozen as the current MVP corpus. | Completing Phase 2 does not auto-activate Rust round-trip, helper-free Wasm widening, or Track `C` promotion; future widening requires a new decision, updated root boundary docs, and synchronized repo contracts. | yes | `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot` |
| DR-017 | accepted | Rust remains importer-first evidence for the remainder of the MVP. | Rust must not become an active round-trip, backend, or benchmark lane inside the MVP; any such change is a post-MVP reactivation decision that must update roadmap, benchmark doctrine, and repo-contract surfaces together. | yes | `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot` |
| DR-018 | accepted | Helper-free Wasm remains a bounded retained backend surface for the remainder of the MVP. | Wasm must not become an active backend-expansion or benchmark lane inside the MVP; any broader Wasm widening, backend activation, or benchmark promotion is a post-MVP reactivation decision that must update roadmap, benchmark doctrine, target-profile and preservation docs, and repo-contract surfaces together. | yes | `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot` |
| DR-019 | accepted | Track `C` remains a retained non-default diagnostic pilot for the remainder of the MVP. | Track `C` must not become the default executable benchmark gate or a broader benchmark claim lane inside the MVP; any such change is a post-MVP reactivation decision that must update roadmap, benchmark doctrine, benchmark metadata, and repo-contract surfaces together. | yes | `python scripts/run_repo_validation.py --require-rust --include-track-c-pilot` |

## Entry template

```text
ID:
Status: accepted | superseded | rejected | pending
Decision:
Reason:
Constraint imposed:
Files updated:
Reversible:
First validation:
Open questions created:
```
