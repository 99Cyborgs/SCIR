# ASSUMPTIONS
Status: Normative

These assumptions are bounded defaults. If an implementation cannot satisfy one of them, update this file and the relevant plan before proceeding.

## Architectural assumptions

| ID | Assumption |
| --- | --- |
| A1 | There is a non-trivial semantic overlap between the active Python subset and the active Rust safe subset that is worth representing canonically. |
| A2 | A canonical semantic form helps only if it beats strong direct-source and typed-AST baselines on at least some narrow task families. |
| A3 | A two-layer design is justified only if `SCIR-H` remains normative and `SCIR-L` stays derivative. |
| A4 | Escape hatches are acceptable only when explicit, auditable, and quantitatively bounded. |

## Repository bootstrap assumptions

| ID | Assumption |
| --- | --- |
| R1 | `specs/` are authoritative over explanatory docs. |
| R2 | JSON Schema Draft 2020-12 is the schema baseline. |
| R3 | `scripts/scir_h_bootstrap_model.py` is the active parser, formatter, and canonicalizer until a dedicated package replaces it. |
| R4 | Bootstrap commands in `Makefile` remain the repository entry points until replaced by stricter equivalents. |
| R5 | `SCIR-H` is the only canonical semantic storage form; `SCIR-L` is derivative only. |
| R6 | The active canonical `SCIR-H` subset excludes `select`, `iface`, `witness`, `match`, `throw`, `invoke`, and suite-form `unsafe` or `opaque` regions. |
| R7 | Minimal single-handler `try` / `catch name Type` remains importer-visible `SCIR-H`, but it is not part of the active executable lowering or reconstruction path. |
| R8 | The active frontends are Python and Rust only; TypeScript remains deferred. |
| R9 | The first backend claim is a Wasm reference-backend contract under profile `P`, not native or host parity. |
| R10 | Python reconstruction claims default to `P1` unless stronger evidence exists. |

## Assumption handling rule

If work requires a stronger or weaker assumption:

- update this file,
- record the reason in the active plan,
- update `DECISION_REGISTER.md` if the change is architectural,
- update `OPEN_QUESTIONS.md` if the assumption becomes unresolved.
