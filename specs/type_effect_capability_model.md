# Type, Effect, and Capability Model
Status: Normative

## Purpose

This file defines the active typing and effect surface that importers, validators, and lowering rules must agree on for the MVP.

## Active scope

The active MVP uses only the effect and type surface required by:

- the Python proof loop,
- the Rust safe-subset importer,
- explicit opaque and unsafe boundaries.

## Active type rules

- function parameters and returns are explicit
- record field types are explicit
- `borrow<T>` and `borrow_mut<T>` may appear in type positions for Rust import
- `opaque<T>` may appear at explicit boundary points

## Active effect rules

- public boundaries use explicit finite effect rows
- `write` remains explicit
- `await` remains explicit
- `opaque` and `unsafe` remain explicit
- the importer-only `try/catch` slice may carry an explicit `throw` effect marker without promoting standalone `throw` syntax
- empty effect rows render as `!`
- declared active effects must match observed behavior; missing or unused effect rows are invalid

## Deferred from active use

- capability `using` clauses
- witness dispatch
- standalone `throw` expressions or statements and broader `throw` effect discharge
- broader effect polymorphism

These remain future design topics, not active canonical requirements.

## Exported-interface rule

Public declarations in the active subset carry explicit type and effect signatures in canonical storage.

## Active capability accounting

Capabilities are not first-class canonical syntax in the MVP.
When an importer emits an opaque or unsafe boundary that requires a capability, it must:

- record the requirement in the boundary contract `capabilities` field, and
- mirror the requirement in `module_manifest.dependencies` using the `capability:<name>` form.

Capability imports outside explicit boundary cases are invalid in the active subset.

## Lowering rule

Effect elimination or specialization belongs to derivative lowering and backend contracts, never to canonical `SCIR-H`.
