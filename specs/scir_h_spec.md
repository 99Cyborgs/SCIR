# SCIR-H Specification
Status: Normative

## Scope

`SCIR-H` is the only normative semantic representation in the SCIR MVP.
`SCIR-Hc` is a derived non-normative compression view over validated `SCIR-H`.

The active canonical subset is exactly the subset implemented by `scripts/scir_h_bootstrap_model.py` and exercised by the checked-in Python and Rust fixture corpora.
The executable kernel boundary is summarized below and must stay aligned with `SPEC_COMPLETENESS_CHECKLIST.md` and the bootstrap model metadata.

## Non-negotiable properties

- structured control
- explicit mutation
- explicit field places where source semantics depend on projection
- explicit opaque and unsafe boundaries at importer level
- deterministic canonical formatting
- semantic lineage identity independent of spec version

## Active sorts

- `Module`
- `Import`
- `Type`
- `Function`
- `Statement`
- `Expression`
- `Place`

## Active ownership and effect surface

Active type-level ownership modes:

- plain value types
- `borrow<T>`
- `borrow_mut<T>`
- `opaque<T>`

Active effects:

- empty effect row `!`
- `write`
- `await`
- `opaque`
- `unsafe`
- importer-only `throw` effect marker for the bounded Tier `B` `try/catch` slice

Anything broader is deferred and must not appear as active canonical syntax.

## Canonical formatting rules

1. canonical storage is indentation-sensitive and newline-delimited
2. suites use two-space indentation
3. canonical storage has no comments
4. imports are sorted by kind then identifier
5. direct calls render as `f(args)`
6. mutable locals render as `var` plus explicit `set`
7. field places render as `name.field`
8. effect rows render as `!` or `!a,b`
9. canonical storage is the input to the canonical content hash
10. pretty or review views are non-canonical

## Derived `SCIR-Hc` contract

`SCIR-Hc` is not canonical syntax and does not widen the semantic surface.
It exists only as a compressed representation derived from validated `SCIR-H`.

The active `SCIR-Hc` executable contract is:

- derive from normalized canonical `SCIR-H`,
- preserve `P1` semantic equivalence back to canonical `SCIR-H`,
- carry the derived-only authority marker plus machine-readable omission provenance,
- permit omission of inferable effect rows, local binding type markers, and return types,
- treat witness inlining as reserved until canonical witness syntax is active,
- treat capability hoisting as compression of boundary metadata, not as canonical syntax.

No lowering, reconstruction, or preservation claim may originate directly from stored `SCIR-Hc`.
Those paths must first reconstruct canonical `SCIR-H`.
See `specs/scir_hc_doctrine.md` for the blocking authority-boundary, derivation, round-trip, and benchmark-claim rules.

## Executable kernel boundary

| construct | canonical parser/formatter | downstream status |
| --- | --- | --- |
| module header | yes | fully supported in MVP |
| `import sym` | yes | fully supported in MVP |
| `import type` | yes | fully supported in MVP |
| record `type` declaration | yes | fully supported in MVP |
| plain `fn` | yes | fully supported in MVP |
| `async fn` | yes | fully supported in MVP |
| `var` | yes | fully supported in MVP |
| `set` local place | yes | fully supported in MVP |
| `set` field place | yes | fully supported in MVP |
| `return` | yes | fully supported in MVP |
| `if` / `else` | yes | fully supported in MVP |
| `loop` | yes | canonical parser/validator surface only; importer-only beyond that |
| `break` | yes | canonical parser/validator surface only; importer-only beyond that |
| `continue` | yes | canonical parser/validator surface only; importer-only beyond that |
| single-handler `try` / `catch name Type` | yes | canonical parser/validator surface only; importer-only beyond that |
| direct call `f(args)` | yes | fully supported in MVP |
| `await` | yes | fully supported in MVP |
| intrinsic scalar comparison | yes | fully supported in MVP |
| explicit field place `a.b` | yes | fully supported in MVP |
| opaque or unsafe boundary call | yes | boundary-only importer surface; executable evidence remains subset-bound |

`fully supported in MVP` in this table means the construct remains inside the currently admitted parser, validator, lowering, reconstruction, or boundary path documented in `SPEC_COMPLETENESS_CHECKLIST.md`. It does not widen importer parity, backend parity, or language-scope claims.

## Active canonical grammar

```ebnf
Module      ::= "module" ModId NL TopDecl*
TopDecl     ::= Import | TypeDecl | FnDecl
Import      ::= "import" ("sym" | "type") LocalId Ref NL
TypeDecl    ::= "type" TypeId TypeExpr NL
FnDecl      ::= Async? "fn" FnId ParamSig* "->" Type Effects NL Suite
Async       ::= "async"
ParamSig    ::= LocalId Type
Effects     ::= "!" | "!" Effect ("," Effect)*
Suite       ::= INDENT Stmt* DEDENT

Stmt        ::= "var" LocalId Type Expr
              | "set" Place Expr
              | "return" Expr
              | "if" Expr NL Suite ("else" NL Suite)?
              | "loop" LoopId NL Suite
              | "break" LoopId
              | "continue" LoopId
              | "try" NL Suite "catch" LocalId Type NL Suite

Expr        ::= Literal
              | Place
              | Ref "(" ArgList? ")"
              | "await" Expr
              | IntrinsicExpr

IntrinsicExpr ::= ("lt" | "le" | "eq" | "ne" | "gt" | "ge") Expr Expr

Place       ::= LocalId ("." FieldId)*
TypeExpr    ::= PrimType
              | TypeId
              | "record" "{" FieldType+ "}"

FieldType   ::= FieldId Type
```

## Deferred from the active grammar

The following are explicitly not part of the active canonical `SCIR-H` kernel:

- `iface`
- `witness`
- capability `using` clauses
- `throw`
- `match`
- `select`
- `unsafe` suites
- `opaque` suites
- `invoke`
- `spawn`, `send`, `recv`
- channel, task, result, or variant types
- expression-level `borrow` / `borrow_mut`

These may remain as future design notes only. They are not current claims.

## Semantic obligations

`SCIR-H` must make explicit:

- structured control boundaries
- mutation sites
- readable and writable field places
- async suspension points
- opaque and unsafe boundary calls
- cross-module imports

## Importer obligations

An importer emitting `SCIR-H` must also emit:

- a `module_manifest`
- a `feature_tier_report`
- a `validation_report`
- an `opaque_boundary_contract` for every Tier `C` region

## Validation obligations

Canonical `SCIR-H` and derived `SCIR-Hc` obligations live in `specs/validator_invariants.md`.
