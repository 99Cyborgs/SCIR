# Python Import Scope
Status: Normative

## Active corpus

### Executable proof-loop cases

- `a_basic_function`
- `a_async_await`
- `b_direct_call`
- `c_opaque_call`

### Importer-only canonical `SCIR-H` cases

- `b_if_else_return`
- `b_async_arg_await`
- `b_while_call_update`
- `b_while_break_continue`
- `b_class_init_method`
- `b_class_field_update`
- `d_try_except`

### Rejected cases

- `d_exec_eval`

## Active executable path

Only the executable proof-loop cases above are active end-to-end MVP claims.

## Importer-only cases

The importer-only cases above remain canonical `SCIR-H` evidence only. They do not imply active lowering or reconstruction support.

## Unsupported

- `exec` / `eval`
- import hooks
- metaclasses and descriptor mutation
- broader exception control
