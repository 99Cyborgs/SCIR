# Interop and Opaque Boundary Specification
Status: Normative

## Purpose

SCIR needs escape hatches without losing auditability.

## Boundary forms

- `opaque type T : contract {...}`
- `opaque.call f(args) : τ ! ε using K`
- `unsafe <tag> { ... }`
- `foreign mod/path::symbol : sig`
- `host.stub <runtime> <name> : sig`
- `trusted.runtime <service> : cap<C>`

## Mandatory metadata

Every opaque or unsafe boundary must record:

1. boundary ID
2. boundary kind
3. declared signature
4. declared effect summary
5. ownership-transfer summary
6. capability requirements
7. determinism classification
8. audit note or proof-obligation reference

## Analysis forfeited across opaque regions

- deep alias reasoning
- deep effect soundness beyond the declared summary
- devirtualization or specialization through the boundary
- race-freedom or determinism proofs beyond the boundary
- reconstruction of internal semantics

## Preservation rules

- `P3` is the normal ceiling for opaque boundaries
- stronger claims require an explicit contract and evidence
- unsupported internals remain unsupported even if the boundary surface is typed

## Validation rules

- a boundary without metadata is invalid
- a boundary cannot silently mint capabilities
- unsafe code must remain marked and auditable
- foreign and host boundaries must be counted in reports
