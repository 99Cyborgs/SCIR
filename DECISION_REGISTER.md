# DECISION_REGISTER
Status: Normative

This register records repository-level architecture decisions. Add a new entry for any semantic or scope change that is not purely editorial.

| ID | Status | Decision | Constraint imposed | Reversible | First validation |
| --- | --- | --- | --- | --- | --- |
| DR-001 | accepted | SCIR is a dual representation: canonical `SCIR-H` and derivative `SCIR-L`. | `SCIR-L` must not become an independent semantic source of truth. | partly | Track B + validator drift checks |
| DR-002 | accepted | First credible product is importer + validator + lowering + reconstruction + benchmark harness. | No mass-market language work in phase 1. | yes | milestone gates 01–05 |
| DR-003 | accepted | Every claim is profile-qualified (`R`, `N`, `P`, `D`). | Unqualified preservation or performance claims are invalid. | yes | benchmark result review |
| DR-004 | accepted | Preservation levels are `P0`, `P1`, `P2`, `P3`, `PX`. | No binary “preserved/not preserved” claims. | yes | preservation report review |
| DR-005 | accepted | Feature coverage is tiered (`A`, `B`, `C`, `D`). | No vague support language. | no | frontend conformance review |
| DR-006 | accepted | Unsupported and opaque cases must be explicit. | No silent fallback to pseudo-support. | yes | importer and validator reports |
| DR-007 | accepted | Benchmark-first evaluation is mandatory. | No AI or performance claim without strong baselines. | no | Track A–D governance |
| DR-008 | accepted | Python subset importer lands before Rust subset importer. | Dynamic-host stress comes before ownership-heavy stress. | yes | milestone 02 review |
| DR-009 | accepted | Reconstruction is driven primarily from `SCIR-H`. | `SCIR-L` reconstruction is secondary and non-idiomatic. | partly | Track B review |
| DR-010 | accepted | Wasm or equivalent portable execution is the first execution backend path. | Native backend sprawl is deferred. | yes | milestone 03–05 review |
| DR-011 | accepted | Validators and report schemas are part of the trusted core surface. | Specs, schemas, and validators must evolve together. | partly | `make validate` |
| DR-012 | accepted | Architecture changes require synchronized updates to specs, docs, validator contracts, benchmarks, and this register. | No architecture drift by omission. | no | PR review + CI |

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
