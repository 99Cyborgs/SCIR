# Wasm Backend MVP
Status: Normative

## Purpose

Wasm is the first reference execution target for the SCIR MVP.

## Active scope

The active Wasm backend is limited to helper-free stable WAT emission for the smallest admitted `SCIR-L` subset:

- synchronous `int -> int` or `() -> int` functions in the scalar slice, plus the fixed `borrow_mut<Counter> -> int` record-cell slice
- `const`
- local-slot `alloc`, `store`, and `load`
- bounded module-owned record-cell memory for the fixed Rust `borrow_mut<Counter>` field-mutation shape
- same-module direct local call only in the fixed `identity` / `call_identity` scalar shape
- `cmp` only in the current less-than-zero bootstrap shape
- `ret`, `br`, and `cond_br` only in the current clamp-style control shape
- explicit profile `P`
- explicit `P2` ceiling
- explicit downgrade and boundary reporting
- execution-backed translation validation against the paired `SCIR-L` artifact

### Admitted Python emitted modules

- `fixture.python_importer.a_basic_function`
- `fixture.python_importer.b_direct_call`

### Admitted Rust emitted modules

- `fixture.rust_importer.a_mut_local`
- `fixture.rust_importer.a_struct_field_borrow_mut`

### Admitted lowering rules

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

### Non-emittable lowering rules

- `H_AWAIT_RESUME`
- `H_OPAQUE_CALL`

### Additional non-emittable backend shapes

Not emittable in this slice:

- `field.addr` outside the bounded record-cell ABI
- imported, indirect, recursive, or broader direct-call shapes
- `async.resume`
- `opaque.call`
- record-layout widening beyond the fixed record-cell ABI
- helper imports, runtime shims, imported memory, or hidden linear-memory conventions

### Active record-cell ABI slice

The first post-scalar Wasm slice is now active only for `fixture.rust_importer.a_struct_field_borrow_mut`.
That ABI is frozen at this exact slice until a later recorded contract decision widens it.

Active constraints:

- one named record type only: `Counter { value: int }`
- field offsets derived from canonical field declaration order
- `borrow_mut<Counter>` lowered as an `i32` base-address handle into module-owned linear memory
- `field.addr` admitted only for the fixed `Counter.value` projection at offset `0`
- caller-visible mutation preserved only for callers that explicitly share the same record-cell ABI

Still blocked:

- Python field-place Wasm emission
- non-`int` record fields
- multi-record layouts
- imported memory
- host ABI claims
- GC or object-model semantics
- broader field-place shapes beyond the fixed record-cell case

## Storage model

- `alloc` lowers to backend-local slot assignment
- no helper imports or runtime shims are permitted

## Claim boundary

Wasm emission does not imply:

- native parity
- host-runtime parity
- support for deferred constructs

## Validation boundary

Admitted Wasm output now requires both:

- stable helper-free WAT inside this bounded backend contract
- a passing `translation_validation_report` that compares backend behavior against bounded `SCIR-L` execution under profile `P`

## Required report path

`l_to_wasm`
