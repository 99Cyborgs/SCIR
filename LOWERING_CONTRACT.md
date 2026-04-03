# LOWERING_CONTRACT
Status: Normative

## Primary rule

`SCIR-H` is normative.
`SCIR-L` is valid only as a derivative artifact.

Every semantically meaningful `SCIR-L` instruction or terminator must carry:

- an origin reference to validated `SCIR-H`
- a named lowering rule

## Active lowering rules

| Rule ID | `SCIR-H` source shape | `SCIR-L` effect |
| --- | --- | --- |
| `H_VAR_ALLOC` | `var name T value` | `alloc` plus `store` |
| `H_SET_STORE` | `set place value` | `store` |
| `H_PLACE_LOAD` | local or field-place read in a lowered context | `load` |
| `H_FIELD_ADDR` | readable or writable field place | `field.addr` |
| `H_INTRINSIC_CMP` | intrinsic scalar comparison | `cmp` |
| `H_CONST_RET` | immediate scalar return | `const` plus `ret` |
| `H_DIRECT_CALL` | direct validated call | `call` |
| `H_AWAIT_RESUME` | `await` over a validated direct call | `async.resume` |
| `H_OPAQUE_CALL` | explicit opaque or unsafe boundary call | `opaque.call` |
| `H_BRANCH_COND` | structured conditional branch | `cond_br` |
| `H_BRANCH_JOIN` | structured join from lowered control | `br` |
| `H_RETURN` | structured return | `ret` |

## Forbidden behavior

- no L-only control or effect semantics
- no L-only exception semantics
- no backend dialect op without a named contract
- no optimizer-only fact fed back into canonical `SCIR-H`
- no missing lowering rule on semantically meaningful ops

## Wasm backend relation

### Wasm-admitted lowering rules

- `H_CONST_RET`
- `H_VAR_ALLOC`
- `H_SET_STORE`
- `H_PLACE_LOAD`
- `H_FIELD_ADDR`
- `H_INTRINSIC_CMP`
- `H_DIRECT_CALL`
- `H_BRANCH_COND`
- `H_BRANCH_JOIN`
- `H_RETURN`

### Wasm admitted-shape notes

The active helper-free Wasm backend consumes only the subset of `SCIR-L` justified by:

- `H_CONST_RET` for synchronous integer constant returns
- `H_DIRECT_CALL` for the current same-module scalar direct-call shape only
- `H_FIELD_ADDR`, `H_PLACE_LOAD`, `H_INTRINSIC_CMP`, `H_SET_STORE`, `H_BRANCH_COND`, and `H_RETURN` for the fixed record-cell `borrow_mut<Counter>` field-mutation shape only
- `H_VAR_ALLOC`, `H_SET_STORE`, `H_PLACE_LOAD`, `H_INTRINSIC_CMP`, `H_BRANCH_COND`, `H_BRANCH_JOIN`, and `H_RETURN` for the current clamp-style local-slot lowering shape

### Wasm-non-emittable lowering rules

- `H_AWAIT_RESUME`
- `H_OPAQUE_CALL`

### Wasm backend contract notes

The active helper-free Wasm backend does not emit:

- `H_AWAIT_RESUME`
- `H_OPAQUE_CALL`

`alloc` is normalized into backend-local slot state rather than linear memory or helper-runtime semantics.
`H_FIELD_ADDR` is now executable only inside the fixed record-cell ABI for `a_struct_field_borrow_mut`: module-owned linear memory, fixed `int` fields, offsets derived from canonical declaration order, and `borrow_mut<T>` record parameters represented as shared base-address handles.
Lowering doctrine for that slice still requires: canonical-order field offsets only, shared-handle callers only, explicit rejection of non-`int` record fields in the first slice, and no silent widening into imported-memory, host-object, or broader alias contracts.
That `H_FIELD_ADDR` backend contract is frozen to the fixed Rust slice and does not imply a general field-place Wasm lowering path.
Broader direct-call support, imported calls, indirect calls, and recursive call graphs remain outside the active helper-free Wasm subset.
Wasm emission does not create new semantics. It only emits the already-lowered derivative subset under profile `P` with a `P2` contract ceiling.

## Validator hook

`SCIR-L` validation must fail when:

- an op lacks origin,
- an op lacks a lowering rule,
- a lowering rule is not recognized,
- an op/lowering-rule pairing is invalid for the active subset.
