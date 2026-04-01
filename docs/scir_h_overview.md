# SCIR-H Overview
Status: Informative

`SCIR-H` is the canonical semantic layer.

## Role

`SCIR-H` exists to make these explicit:

- module and symbol boundaries,
- types,
- effects,
- capabilities,
- witness passing,
- ownership and alias modes,
- control structure,
- mutation sites,
- unsafe and opaque boundaries,
- stable IDs and provenance.

## Design constraints

`SCIR-H` must be:

- canonical enough for formatting and diff stability,
- structured enough for reconstruction,
- explicit enough for validation,
- regular enough for AI-facing editing,
- small enough to avoid semantic sprawl.

## Minimal v0.1 control surface

- structured exception handling exists only as `try { ... } catch(x: T) { ... }`
- structured concurrency choice exists only as `select { ... }` over explicit channel `send` or `recv` arms
- `finally`, multi-catch, default arms, timeout arms, and priority semantics are outside canonical v0.1

## Canonicality rules

- indentation-sensitive suites with two-space indentation,
- newline-delimited storage with no canonical braces or semicolons,
- one declaration form per construct kind,
- sorted imports,
- topologically ordered declarations,
- stable identifiers on public structure,
- compact effect rows (`!` or `!a,b`),
- direct calls rendered as `f(args)`,
- explicit mutable binders via `var` and explicit writes via `set`,
- readable field places rendered explicitly such as `counter.value`,
- intrinsic scalar comparisons rendered explicitly (`lt`, `le`, `eq`, `ne`, `gt`, `ge`),
- no hidden conversions,
- no hidden ambient capabilities,
- no comments in canonical storage.

## Non-goals

`SCIR-H` is not:

- a user-friendly mainstream language,
- a low-level optimizer IR,
- a raw source AST,
- a place to preserve every source-language accident.

See `specs/scir_h_spec.md`.
