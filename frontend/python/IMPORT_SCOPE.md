# Python Import Scope
Status: Normative

## Active corpus

### Executable proof-loop cases

- `a_basic_function`
- `a_async_await`
- `b_direct_call`
- `c_opaque_call`
- `b_if_else_return`
- `b_async_arg_await`
- `b_while_call_update`
- `b_while_break_continue`
- `b_class_init_method`
- `b_class_field_update`
- `d_try_except`

### Importer-only canonical `SCIR-H` cases

No checked-in importer-only canonical `SCIR-H` cases remain in the active Python fixture set.
Importer-only Python support is currently empty for the frozen MVP corpus.

### Rejected cases

- `d_exec_eval`

## Active executable path

Only the executable proof-loop cases above are active end-to-end MVP claims.

## Importer-only cases

There are no active importer-only Python fixture cases in the frozen MVP corpus.
Any future importer-only case must remain explicit in this file and must not imply active lowering or reconstruction support.

## Unsupported

- `exec` / `eval`
- import hooks
- metaclasses and descriptor mutation
- broader exception control beyond the exact single-handler `ValueError` slice
