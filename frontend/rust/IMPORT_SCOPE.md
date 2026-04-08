# Rust Import Scope
Status: Normative

## Active scope

The Rust MVP scope is importer-only safe-subset evidence.

## Active corpus

### Importer-first evidence cases

- `a_mut_local`
- `a_struct_field_borrow_mut`
- `a_async_await`
- `c_unsafe_call`

### Tier A importer-evidence cases

- `a_mut_local`
- `a_struct_field_borrow_mut`
- `a_async_await`

### Helper-free Wasm-emittable case

- `a_mut_local`
- `a_struct_field_borrow_mut`

### Await-bearing cases

- `a_async_await`

### Ownership-bearing and boundary-accounted cases

- `a_struct_field_borrow_mut`
- `c_unsafe_call`

### Rejected cases

- `d_proc_macro`
- `d_self_ref_pin`

## Supported shapes

### Tier A active importer shapes

- free functions
- named record types
- `borrow_mut` parameters
- mutable locals
- record field places in read and write positions
- simple async functions with explicit `await`

### Tier C active importer shape

- explicit unsafe call boundary imported as an opaque boundary

## Async contract

- `a_async_await` is the admitted Tier `A` await-bearing Rust case. Its importer bundle must keep `async fn load_once -> int !await` explicit in canonical `SCIR-H`, keep `return await fetch_value()` visible, and keep the optional Rust `H -> L` validation lane preserving the await boundary without implying helper-free Wasm emission, Rust reconstruction, or broader backend claims.

## Ownership and boundary contract

- `a_struct_field_borrow_mut` is the admitted Tier `A` ownership-bearing Rust case. Its importer bundle must keep `borrow_mut<Counter>` explicit in canonical `SCIR-H`, keep `counter.value` field-place mutation visible, and keep the same contract through the optional Rust `H -> L` validation lane.
- `c_unsafe_call` is the admitted Tier `C` unsafe-boundary Rust case. Its importer bundle must keep the boundary explicit, keep `capability:unsafe_ping` mirrored between `module_manifest.dependencies` and `opaque_boundary_contract.capabilities`, and keep the optional Rust `H -> L` validation lane boundary-accounting-only rather than implying Rust reconstruction, Wasm emission, or broader backend claims.

### Tier D rejected shape classes

- proc macros
- build scripts
- self-referential pin patterns
- unsafe alias choreography beyond explicit boundary treatment

## Claim boundary

Rust importer evidence must not be presented as an active round-trip, backend, or benchmark claim unless the root roadmap and benchmark strategy are updated together.
