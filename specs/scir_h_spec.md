# SCIR-H Specification
Status: Normative

## Scope

`SCIR-H` is the canonical high-level semantic representation used for inspection, stable transformation, AI-facing editing, and reconstruction.

## Non-negotiable properties

- structured control
- explicit mutation
- explicit effect rows
- explicit capability requirements
- explicit witness passing
- explicit ownership or alias modes
- explicit unsafe and opaque boundaries
- stable symbol identity
- canonical formatting

## Sorts and core type forms

Core sorts:

- `Module`
- `Symbol`
- `Type`
- `Effect`
- `Capability`
- `Witness`
- `Value`
- `Place`

Core ownership or alias modes:

- `own<T>`
- `borrow<T>`
- `borrow_mut<T>`
- `share<T>`
- `gc<T>`
- `opaque<T>`

Core operational effect families:

- `read`
- `write`
- `alloc`
- `throw`
- `io`
- `await`
- `spawn`
- `send`
- `recv`
- `nondet`
- `unsafe`
- `opaque`

## Canonical formatting rules

1. canonical storage is indentation-sensitive and newline-delimited; braces and semicolons are non-canonical
2. suites use two-space indentation
3. one declaration form per construct kind
4. imports sorted by class then lexical identifier
5. declarations topologically ordered by dependency
6. every public binder carries a stable identifier
7. public declarations carry explicit type, effect, capability, and witness signatures
8. effect rows render as bare `!` for empty or `!a,b` for non-empty
9. direct symbol and local calls render as `f(args)`; `invoke` remains reserved for witness or interface dispatch
10. mutable locals render as `var` binders plus explicit `set` sites; plain local references are canonical reads
11. canonical storage omits human comments
12. no implicit receiver, implicit conversion, or ambient import semantics remain

## Canonical grammar

```ebnf
Module      ::= "module" ModId NL TopDecl*
TopDecl     ::= Import | Decl
Import      ::= "import" ("sym" | "type" | "cap" | "mod") LocalId Ref NL
Decl        ::= TypeDecl | IfaceDecl | WitnessDecl | FnDecl | ForeignDecl | OpaqueDecl

TypeDecl    ::= "type" TypeId Type NL
IfaceDecl   ::= "iface" IfaceId TypeParams? NL Suite
WitnessDecl ::= "witness" WitnessId IfaceRef NL Suite
FnDecl      ::= Async? "fn" FnId TypeParams? ParamSig* "->" Type Effects Caps? NL Suite
Async       ::= "async"
ParamSig    ::= LocalId Type
Effects     ::= "!" | "!" Effect ("," Effect)*
Caps        ::= ("using" "{" CapReqList? "}")?
Suite       ::= INDENT Stmt* DEDENT

Stmt        ::= "let" LocalId Expr
              | "var" LocalId Type Expr
              | "set" Place Expr
              | "return" Expr
              | "throw" Expr
              | "if" Expr NL Suite ("else" NL Suite)?
              | "match" Expr NL Suite
              | "loop" LoopId NL Suite
              | "break" LoopId ArgList?
              | "continue" LoopId
              | "try" NL Suite "catch" LocalId Type NL Suite
              | "select" NL Suite
              | "unsafe" UnsafeTag NL Suite
              | "opaque" OpaqueTag NL Suite

SelectArm   ::= "recv" Expr "as" LocalId NL Suite
              | "send" Expr Expr NL Suite

Expr        ::= Literal
              | Place
              | Ref "(" ArgList? ")"
              | "invoke" IfaceMethodRef WitnessArg "(" ArgList? ")"
              | "record" "{" FieldInit* "}"
              | "variant" VariantTag "(" ArgList? ")"
              | "borrow" Place
              | "borrow_mut" Place
              | "await" Expr
              | "spawn" Expr
              | "send" Expr "," Expr
              | "recv" Expr
              | "cast" CastKind Expr "to" Type
              | "new_gc" Type Expr?
              | "perform" EffectOp "(" ArgList? ")"
              | IntrinsicExpr

IntrinsicExpr ::= ("lt" | "le" | "eq" | "ne" | "gt" | "ge") Expr Expr

Place       ::= LocalId ("." FieldId)*

Type        ::= PrimType
              | TypeId
              | "record" "{" FieldType* "}"
              | "variant" "{" VariantType* "}"
              | "result" "<" Type "," Type ">"
              | "task" "<" Type ">"
              | "chan" "<" Type ">"
              | "fn" "(" TypeList? ")" "->" Type Effects
              | "witness" "<" IfaceRef ">"
              | "cap" "<" CapId ">"
              | "own" "<" Type ">"
              | "borrow" "<" Type ">"
              | "borrow_mut" "<" Type ">"
              | "share" "<" Type ">"
              | "gc" "<" Type ">"
              | "opaque" "<" OpaqueId ">"

FieldType   ::= FieldId Type
FieldInit   ::= FieldId Expr
VariantType ::= VariantTag TypeList?
```

## Deliberate v0.1 exclusions

The source architecture leaves the following unresolved. They are not part of canonical v0.1 `SCIR-H` unless explicitly revised.

- first-class generator syntax
- profile-specific comment preservation in canonical text

These are tracked in `OPEN_QUESTIONS.md`.

## Minimal v0.1 structured control forms

- `try/catch` is a suite-level structured control form only: `try` newline-indented suite followed by `catch x T` newline-indented suite.
- Canonical v0.1 permits exactly one `catch` with an explicit binder and explicit caught type.
- `finally`, multi-catch, pattern-heavy exception syntax, and new rethrow syntax are out of scope.
- `select` is a suite-level structured control form over explicit channel operations only.
- Each `select` arm is either `recv chan as x` newline-indented suite or `send chan value` newline-indented suite.
- Choice is nondeterministic among ready arms; unchosen arms do not perform their channel operation.
- Default arms, timeout arms, fairness promises, and priority semantics are out of scope.

## Bootstrap compaction notes

- The executable bootstrap subset uses the compact canonical surface directly:
- `var y int x`
- `set y 0`
- `set counter.value 0`
- `return await fetch_value()`
- `if lt y 0`
- `if lt counter.value 0`
- Legacy brace-delimited bootstrap text such as `let cell`, `write`, `read`, or `call f(args)` is non-canonical after the compaction cutover.
- Comparison helpers such as `python:operator.lt` are not canonical bootstrap imports; scalar comparisons render as intrinsic expressions such as `lt x y`.
- The Rust Phase 6A slice permits readable field places such as `counter.value` and type declarations such as `type Counter record { value int }`.

## Semantic obligations

`SCIR-H` must make explicit:

- control and exceptional edges, including `try/catch` boundaries and `select` choice sites,
- mutation sites,
- readable and writable field places where source semantics depend on projection,
- capability use,
- effect obligations,
- witness materialization or passing,
- unsafe or opaque boundaries,
- cross-module dependencies.

## Importer obligations

An importer emitting `SCIR-H` must also emit:

- a `module_manifest`,
- a `feature_tier_report`,
- a `validation_report`,
- `opaque_boundary_contract` records for all `C`-tier boundaries.

## Validation obligations

See `specs/validator_invariants.md`.
