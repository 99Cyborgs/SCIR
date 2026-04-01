# ASSUMPTIONS
Status: Normative

These assumptions are bounded defaults. If an implementation cannot satisfy one of them, update this file and the relevant plan before proceeding.

## Architectural assumptions

| ID | Assumption |
| --- | --- |
| A1 | There is a non-trivial semantic overlap among Python, Rust, TypeScript, Go, Haskell, and disciplined subsets of C++ that is worth representing canonically. |
| A2 | A canonical semantic form helps only if it beats strong typed-AST and direct-source baselines on at least some task families. |
| A3 | A two-layer design is required because reconstruction/audit needs and backend/optimization needs diverge. |
| A4 | Escape hatches are acceptable only when explicit, auditable, and quantitatively bounded. |

## Repository bootstrap assumptions

| ID | Assumption |
| --- | --- |
| R1 | Repository root is `scir/`. |
| R2 | `specs/` are authoritative over explanatory docs. |
| R3 | JSON Schema Draft 2020-12 is the schema baseline. |
| R4 | Bootstrap commands in `Makefile` remain the repository entry points until replaced by stricter equivalents. |
| R5 | `SCIR-H` is the only canonical semantic storage form; `SCIR-L` is derivative. |
| R6 | `select` is canonical v0.1 `SCIR-H` only in minimal channel-select form with explicit `send` or `recv` arms; default, timeout, fairness, and priority semantics remain out of scope. |
| R7 | Structured `try/catch` is canonical v0.1 `SCIR-H` only in minimal single-catch form `try { ... } catch(x: T) { ... }`; `finally` and multi-catch remain out of scope. |
| R8 | The first executable benchmark harness may begin as a doctrine and report validator before full runtime integration exists. |
| R9 | Importers must classify unsupported features explicitly even before they have executable code. |
| R10 | Reconstruction claims default to `P1` unless stronger evidence exists. |

## Assumption handling rule

If work requires a stronger or weaker assumption:

- update this file,
- record the reason in the active plan,
- update `DECISION_REGISTER.md` if the change is architectural,
- update `OPEN_QUESTIONS.md` if the assumption becomes unresolved.
