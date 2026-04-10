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
