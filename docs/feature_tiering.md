# Feature Tiering
Status: Normative

Tiering is the only valid language for source-coverage claims.

| Tier | Meaning | Typical ceiling |
| --- | --- | --- |
| `A` | validator-understood semantics with active proof-loop evidence | `P0/P1` |
| `B` | validator-understood semantics without active downstream proof-loop evidence | `P1/P2` |
| `C` | opaque or unsafe boundary only | `P3` |
| `D` | rejected or unsupported | `PX` |

## Active guidance

- Python proof-loop cases remain `A`
- the bounded direct local call shape `b_direct_call` is now part of the active Python proof loop and remains the only promoted follow-on call case
- importer-only loop and `try/catch` cases remain `B`
- bounded opaque or unsafe calls remain `C`
- unsupported Python, Rust, and all TypeScript implementation work remain `D`

## Rule

Choose the lower tier when uncertain. Tier `C` is not semantic support.
