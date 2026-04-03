# UNSUPPORTED_CASES
Status: Normative

This file is the operator-facing unsupported boundary for the current MVP.

Active unsupported or deferred semantics include:

- Python `exec`, `eval`, import hooks, metaclass-driven rewrites, descriptor mutation, and monkey patching
- Python exception control beyond the bounded single-handler importer-only slice
- Rust proc macros, build scripts, self-referential pin patterns, and unsafe alias choreography beyond explicit opaque boundaries
- all TypeScript implementation work
- C++, Go, and Haskell implementation work
- canonical `SCIR-H` constructs not implemented by `scripts/scir_h_bootstrap_model.py`
- any `SCIR-L` construct not justified by `LOWERING_CONTRACT.md`
- benchmark Track `D`
- active `D-JS`

Detailed rationale and tier guidance live in `docs/unsupported_cases.md`.
