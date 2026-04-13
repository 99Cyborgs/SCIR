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
- the bounded direct local call shape `b_direct_call`, bounded explicit branch-return shape `b_if_else_return`, bounded parameterized async local-call shape `b_async_arg_await`, bounded while-call update shape `b_while_call_update`, bounded break/continue loop-control shape `b_while_break_continue`, bounded record-like class-init shape `b_class_init_method`, bounded record-like class field-update shape `b_class_field_update`, and the exact single-handler `d_try_except` shape are part of the active Python proof loop
- broader exception-control follow-ons remain importer-only `B` or rejected `D`
- bounded opaque or unsafe calls remain `C`
- unsupported Python, Rust, and all TypeScript implementation work remain `D`
- archived TypeScript placeholder case ids are historical residue only and must not be read as live `Tier A` / `B` / `C` support

## Rule

Choose the lower tier when uncertain. Tier `C` is not semantic support.
