# Validator Contracts
Status: Normative

## Input and output contract

| Validator | Input | Output |
| --- | --- | --- |
| `SCIR-H` validator | canonical `SCIR-H` | `validation_report` |
| `SCIR-L` validator | canonical `SCIR-L` | `validation_report` |
| translation validator | paired stage artifacts and claims | `preservation_report` or failing `validation_report` |
| reconstruction checker | reconstructed source + provenance map + claims | `reconstruction_report` + `preservation_report` |

## Exit rule

Blocking validators exit non-zero on hard invariant violations.

## Diagnostic minimum

Every diagnostic must include:

- stable code,
- severity,
- message,
- artifact reference,
- node or block reference when available.

## Claim handling

A validator encountering an overstated claim must:

- fail, or
- downgrade the claim explicitly in a report.

It must not silently continue with the original claim.

## Canonical blocking conditions

- missing profile,
- legacy profile code `D` after the `D-PY` / `D-JS` split,
- missing preservation level where required,
- missing feature tier where source coverage changed,
- missing opaque boundary contract,
- malformed stable IDs or provenance,
- malformed SSA or token threading,
- brace-delimited or semicolon-delimited text in canonical `SCIR-H`,
- non-canonical direct-call syntax such as `call f(args)`,
- non-canonical mutable-local syntax such as `let cell`, `write`, or `read`,
- field-place syntax outside the canonical `LocalId(.FieldId)*` form,
- non-canonical `try/catch` shape, including missing catch binder or type, `finally`, or multiple catches,
- non-canonical `select` shape, including non-channel arms, default arms, timeout arms, or priority semantics,
- `SCIR-L` ops outside the frozen bootstrap set,
- executable `SCIR-L`, translation, or reconstruction artifacts emitted for importer-only `SCIR-H` acceptance slices such as `b_if_else_return`, `b_direct_call`, `b_async_arg_await`, `b_while_call_update`, `b_while_break_continue`, `b_class_init_method`, `b_class_field_update`, or `d_try_except` without a published downstream contract,
- executable `D-JS` or witness-bearing second-language artifacts emitted without a published validator, preservation, and benchmark contract,
- TypeScript interface-shaped witness artifacts whose reports fail to make witness semantics or host assumptions explicit,
- executable `SCIR-L`, translation, reconstruction, or benchmark artifacts emitted for the first Phase 7 TypeScript interface slice before a published downstream contract exists,
- `field.addr` without a corresponding validated field place in `SCIR-H`,
- hidden merge state instead of block-parameter SSA,
- effect tokens used where memory tokens are required or the reverse,
- `opaque.call` without a corresponding explicit opaque boundary in `SCIR-H`,
- optimizer-only facts reflected back into canonical `SCIR-H`,
- reconstruction report claims that disagree with actual compile/test execution,
- reconstruction report marked provenance-complete with missing canonical-line provenance coverage,
- opaque observables introduced on Tier `A` reconstruction output,
- required opaque observables missing from the Tier `C` reconstruction output,
- unsupported semantics treated as supported.

## Canonical v0.1 structural rejections

- reject any `try/catch` form other than indentation-sensitive `try` / `catch x T` suites
- reject any `select` form unless every arm is an explicit channel `send` or `recv`
- reject implicit exception discharge or implicit concurrency choice semantics
