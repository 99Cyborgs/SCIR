# Python Import Scope
Status: Normative

## Milestone 02 bootstrap floor

Milestone 02 remains fixed to the checked-in five-case bootstrap corpus:

- `a_basic_function`
- `a_async_await`
- `c_opaque_call`
- `d_exec_eval`
- `d_try_except`

That five-case corpus remains the acceptance floor for importer conformance. The current checked-in importer conformance corpus expands it to twelve cases with named Milestone 02B follow-on fixtures. Neither the floor nor the follow-on cases imply executable lowering, reconstruction, or benchmark participation.

### Current importer conformance corpus

The checked-in Python importer conformance corpus currently contains:

- `a_basic_function`
- `a_async_await`
- `b_if_else_return`
- `b_direct_call`
- `b_async_arg_await`
- `b_while_call_update`
- `b_while_break_continue`
- `b_class_init_method`
- `b_class_field_update`
- `c_opaque_call`
- `d_exec_eval`
- `d_try_except`

### In scope right now

- modules and imports without import hooks
- plain `def` with parameters, local assignment or reassignment, `if/else`, direct local call, and `return`
- simple `async def` plus `await`, including one fixed parameterized local-await shape
- one explicit Tier `C` opaque-call case
- importer-only Tier `B` function and async follow-on cases
- importer-only Tier `B` fixed-shape `while` loop follow-on cases
- importer-only Tier `B` bounded record-like class-field normalization
- importer-only Tier `B` bounded record-like class field-update normalization through a direct local call
- one importer-only Tier `B` single-handler `try/except` normalization case

Bootstrap normalization rules for the current canonical `SCIR-H` surface:

- mutable locals normalize to `var` plus explicit `set`
- direct calls normalize to `f(args)`
- scalar comparison normalizes to intrinsic forms such as `lt x y`
- canonical storage is indentation-sensitive and newline-delimited
- bounded Python `except ValueError:` normalizes to canonical `catch err ValueError`

### Executable bootstrap path

The fixed executable Python bootstrap path remains limited to:

- `a_basic_function`
- `a_async_await`
- `c_opaque_call`

Those are the only Python cases that currently participate in `SCIR-H -> SCIR-L`, reconstruction, Track `A`, Track `B`, and Python `D-PY` Track `D`.

### Milestone 02B importer-only slice

The current Milestone 02B follow-on admits exactly eight additional importer-only shapes:

- `b_if_else_return`: `def choose_zero_or_x(x)` with `if x < 0: return 0` and explicit `else: return x`
- `b_direct_call`: `def identity(x): return x` plus `def call_identity(x): return identity(x)`
- `b_async_arg_await`: `async def fetch_value(x): return x` plus `async def load_value(x): return await fetch_value(x)`
- `b_while_call_update`: `def step_until_nonneg(step, x)` with `while x < 0: x = step(x)` and `return x`
- `b_while_break_continue`: `def step_with_escape(step, x)` with `while x < 0`, nested `if x == -1: break`, `x = step(x)`, explicit `continue`, and `return x`
- `b_class_init_method`: `class Counter` with `__init__(self, value): self.value = value` and `get(self): return self.value`, normalized as a record-like type plus plain functions over canonical field places
- `b_class_field_update`: `class Counter` with `__init__(self, value): self.value = value` and `bump(self, step): self.value = step(self.value); return self.value`, normalized as a record-like type plus plain functions over canonical field places
- `d_try_except`: a single `try` block with one unnamed `except ValueError:` handler, no `else`, no `finally`, no `raise`, and no additional handlers

These slices are Tier `B`, not Tier `A`, because:

- the follow-on cases add importer evidence without executable lowering, translation, reconstruction, or benchmark evidence,
- the loop cases normalize into canonical `loop` / `break` / `continue` control with deterministic loop ids but still lack executable downstream evidence,
- the bounded class cases reuse canonical record, field-place, and direct-call syntax but do not claim broader Python object-model fidelity,
- the exception case synthesizes the canonical catch binder,
- callable and throw modeling remain coarse in the compact bootstrap subset where applicable.

### Deferred from this slice

- Python `raise` mapping
- broader class semantics beyond the bounded record-like `b_class_init_method` and `b_class_field_update` shapes
- comprehensions
- `for`
- `while ... else`
- nested or broader loop families beyond the fixed importer-only `while` cases
- inheritance, decorators, properties, descriptors, class variables, dataclasses, metaclasses, and dynamic attribute creation
- broader dynamic features outside the fixed bootstrap corpus
- broader Python exception control beyond the importer-only `d_try_except` shape

### Explicitly unsupported in Milestone 02

- `exec` and `eval` remain Tier `D`
- import hooks and metaclass-driven semantic rewrites remain Tier `D`
- pervasive monkey patching as a semantic source of truth remains Tier `D`
- reflection-heavy host or extension behavior remains outside accepted semantic support unless a later milestone adds an explicit contract

## Deferred follow-on work

Broader Python expansion is not part of Milestone 02. Candidate follow-on work lives in `plans/milestone_02b_python_expansion.md`. The importer-only follow-on slices are tracked in `plans/2026-03-20-python-try-except-importer-only.md`, `plans/2026-03-20-python-function-async-importer-only.md`, `plans/2026-03-27-python-while-importer-only.md`, `plans/2026-03-27-python-class-importer-only.md`, and `plans/2026-03-27-python-class-field-update-importer-only.md`.

## Preservation expectations

- `R`: usually `P1`
- `D-PY`: `P0/P1` only for the supported subset
- `N` and `P`: usually `P2/P3` for host-sensitive constructs

## Importer obligations

- every downgrade must name the reason,
- every Tier `C` region must carry an opaque boundary contract,
- unsupported constructs must be rejected explicitly,
- importer-only accepted exception cases must stay explicitly outside executable lowering and reconstruction claims.
