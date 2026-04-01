# Feature Tiering
Status: Normative

Tiering is the only valid language for source coverage claims.

| Tier | Meaning | Typical preservation ceiling |
| --- | --- | --- |
| `A` | validator-understood semantics, high-fidelity reconstruction expected | `P0/P1` |
| `B` | validator-understood semantics with normalization loss or reduced idiomaticity | `P1/P2` |
| `C` | opaque, unsafe, foreign, or host-stub boundary only | `P3` |
| `D` | rejected or unsupported | `PX` |

## Classification rules

- classify by construct, not by marketing label,
- choose the lower tier when uncertain,
- document the downgrade reason,
- do not promote a construct to Tier `A` without reconstruction and validation evidence,
- do not treat Tier `C` as supported semantics.

## Language guidance

- Python reflection, metaclasses, `exec/eval`, import hooks, monkey patching: `C` or `D`
- Python fixed-shape `if/else` return, direct local call, and parameterized local `async` / `await` imported to canonical `SCIR-H` without executable lowering or reconstruction: `B`
- Python fixed-shape `while` normalization, including bounded explicit `break` / `continue`, imported to canonical `SCIR-H` without executable lowering or reconstruction: `B`
- Python bounded record-like class import with one explicit `self.field` assignment in `__init__` and one fixed field-read method, imported to canonical `SCIR-H` without executable lowering or reconstruction: `B`
- Python bounded record-like class import with one explicit `self.field` assignment in `__init__` and one fixed field-update method through a direct local call, imported to canonical `SCIR-H` without executable lowering or reconstruction: `B`
- Python minimal single-handler `try/except` imported to canonical `SCIR-H` without executable lowering or reconstruction: `B`
- Python `raise`, `finally`, multi-handler `except`, and bound-exception fidelity beyond the bounded importer slice: `D`
- Rust Phase 6A free functions, borrowed-record field mutation, and simple async/await: `A`
- Rust explicit unsafe call boundaries: `C`
- Rust proc macros and self-referential pin or aliasing tricks: `D`
- TypeScript decorators, proxies, emit-dependent reflection: `C` or `D`
- C++ macros, UB-sensitive code, complex templates, inline assembly: `C` or `D`
- Go `unsafe` and `cgo`: `C`
- Haskell Template Haskell and extension-heavy semantics: `C` or `D`

See language-local scope files in `frontend/*/IMPORT_SCOPE.md`.
