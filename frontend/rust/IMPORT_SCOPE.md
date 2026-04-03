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

### Tier D rejected shape classes

- proc macros
- build scripts
- self-referential pin patterns
- unsafe alias choreography beyond explicit boundary treatment

## Claim boundary

Rust importer evidence must not be presented as an active round-trip, backend, or benchmark claim unless the root roadmap and benchmark strategy are updated together.
