# DECISION_REGISTER
Status: Normative

This register records repository-level architecture decisions. Add a new entry for any semantic or scope change that is not purely editorial.

| ID | Status | Decision | Constraint imposed | Reversible | First validation |
| --- | --- | --- | --- | --- | --- |
| DR-001 | accepted | SCIR is a dual representation: canonical `SCIR-H` and derivative `SCIR-L`. | `SCIR-L` must not become an independent semantic source of truth. | partly | Track B + validator drift checks |
| DR-002 | accepted | First credible product is importer + validator + lowering + reconstruction + benchmark harness. | No mass-market language work in phase 1. | yes | milestone gates 01–05 |
| DR-003 | accepted | Every claim is profile-qualified (`R`, `N`, `P`, `D-PY`, `D-JS`). | Unqualified preservation or performance claims are invalid, and monolithic `D` is not a valid canonical profile code. | yes | benchmark result review |
| DR-004 | accepted | Preservation levels are `P0`, `P1`, `P2`, `P3`, `PX`. | No binary “preserved/not preserved” claims. | yes | preservation report review |
| DR-005 | accepted | Feature coverage is tiered (`A`, `B`, `C`, `D`). | No vague support language. | no | frontend conformance review |
| DR-006 | accepted | Unsupported and opaque cases must be explicit. | No silent fallback to pseudo-support. | yes | importer and validator reports |
| DR-007 | accepted | Benchmark-first evaluation is mandatory. | No AI or performance claim without strong baselines. | no | Track A–D governance |
| DR-008 | accepted | Python subset importer lands before Rust subset importer. | Dynamic-host stress comes before ownership-heavy stress. | yes | milestone 02 review |
| DR-009 | accepted | Reconstruction is driven primarily from `SCIR-H`. | `SCIR-L` reconstruction is secondary and non-idiomatic. | partly | Track B review |
| DR-010 | accepted | Wasm or equivalent portable execution is the first execution backend path. | Native backend sprawl is deferred. | yes | milestone 03–05 review |
| DR-011 | accepted | Validators and report schemas are part of the trusted core surface. | Specs, schemas, and validators must evolve together. | partly | `make validate` |
| DR-012 | accepted | Architecture changes require synchronized updates to specs, docs, validator contracts, benchmarks, and this register. | No architecture drift by omission. | no | PR review + CI |
| DR-013 | accepted | Canonical v0.1 `SCIR-H` includes minimal structured `try/catch`. | Exactly one `catch(x: T)` block is allowed; no `finally`, no multi-catch, and `SCIR-L` lowering remains deferred to Phase 3. | yes | `make validate` + milestone 01 review |
| DR-014 | accepted | Canonical v0.1 `SCIR-H` includes minimal channel `select`. | Arms must be explicit channel `send` or `recv`; no default, timeout, fairness, or priority semantics, and `SCIR-L` lowering remains deferred to Phase 3. | yes | `make validate` + milestone 01 review |
| DR-015 | accepted | The executable bootstrap `SCIR-H` surface uses compact indentation-sensitive canonical text. | Canonical bootstrap storage uses newline-delimited suites, compact effect rows, direct calls as `f(args)`, explicit mutation via `var` and `set`, intrinsic scalar comparisons, and rejects legacy brace-delimited bootstrap syntax as non-canonical. | yes | `python scripts/scir_bootstrap_pipeline.py --mode validate` |
| DR-016 | accepted | Automated Track `A` gate evaluation follows the published median-ratio doctrine. | `S3` and `K2` use median token ratios; aggregate ratios remain diagnostic only; automated benchmark status fails if an automated kill gate is hit. | yes | `python scripts/benchmark_contract_dry_run.py` |
| DR-017 | accepted | Phase 3 freezes bootstrap `SCIR-L` to the minimal derivative lowering surface already emitted by the executable path. | `SCIR-L` is limited to `const`, `cmp`, `alloc`, `store`, `load`, `call`, `async.resume`, `opaque.call`, and `ret`/`br`/`cond_br` with block parameters as the only merge mechanism until source coverage requires more. | yes | `python scripts/scir_bootstrap_pipeline.py --mode validate` |
| DR-018 | accepted | Phase 4 freezes bootstrap reconstruction as an `SCIR-H`-driven contract with explicit compile/test, provenance, and opaque-accounting checks. | Supported reconstruction is limited to `a_basic_function` and `a_async_await` at `R/P1` and `c_opaque_call` at `D-PY/P3`; `SCIR-L` remains diagnostic-only for reconstruction; rejected Tier `D` cases do not emit reconstruction artifacts. | yes | `python scripts/scir_bootstrap_pipeline.py --mode validate` |
| DR-019 | accepted | Phase 6 is split so Rust safe-subset evidence lands before any optimization claim, and the only new bootstrap semantics are `SCIR-H` field places and `SCIR-L` `field.addr`. | Phase 6A stays fixture-locked to Rust free functions, borrowed-record field places, async, and explicit unsafe boundaries; optimization and Track `D` remain Phase 6B work. | yes | `python scripts/rust_importer_conformance.py --mode test` |
| DR-020 | accepted | Phase 6B splits the dynamic-host profile into `D-PY` and `D-JS`, activates executable Track `D` slices for Rust `N` and Python `D-PY`, and keeps benchmark-only `SCIR-L` emitters non-normative. | Monolithic `D` is invalid after migration; `D-JS` remains doctrine-only in Phase 6B; reconstruction stays `SCIR-H`-driven; witness-bearing second-language execution remains deferred. | yes | `python scripts/benchmark_contract_dry_run.py` |
| DR-021 | accepted | Milestone 02 is fixed to the five-case Python bootstrap importer corpus, and broader Python coverage moves to a follow-on expansion plan. | Do not claim Python importer support beyond `a_basic_function`, `a_async_await`, `c_opaque_call`, `d_exec_eval`, and `d_try_except` without a new plan and fixture-backed evidence. | yes | `python scripts/python_importer_conformance.py --mode validate-fixtures` |
| DR-022 | accepted | After Phase 6B, the roadmap prioritizes Python Milestone 02B first, then TypeScript interface-shaped witness evidence as Phase 7, before any broader backend/runtime expansion. | Milestone 02B remains fixture-backed and importer-first unless downstream doctrine widens; `D-JS` stays non-executable in Phase 7 unless a later plan adds explicit validator, preservation, reconstruction, and benchmark gates; no new backend track is introduced by this sequencing. | yes | `python scripts/validate_repo_contracts.py --mode validate` |
| DR-023 | accepted | The repository maintains a derived autonomous execution queue as an operational handoff surface anchored to the roadmap and active milestone docs. | `EXECUTION_QUEUE.md` may order and decompose work, but it must not override `IMPLEMENTATION_PLAN.md`; blocked items must cite exact open questions; importer-only Milestone 02B items and Phase 7 witness items must not widen executable scope by queue prose alone. | yes | `python scripts/build_execution_queue.py --mode check` |

## Entry template

Use this template for new entries.

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
