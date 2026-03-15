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

1. one declaration form per construct kind
2. imports sorted by class then lexical identifier
3. declarations topologically ordered by dependency
4. every public binder carries a stable identifier
5. public declarations carry explicit type, effect, capability, and witness signatures
6. canonical storage omits human comments
7. no implicit receiver, implicit conversion, or ambient import semantics remain

## Canonical grammar

```ebnf
Module      ::= "module" ModId "{" Import* Decl* "}"
Import      ::= "import" ("sym" | "type" | "cap" | "mod") LocalId ":" Ref ";"
Decl        ::= TypeDecl | IfaceDecl | WitnessDecl | FnDecl | ForeignDecl | OpaqueDecl

TypeDecl    ::= "type" TypeId "=" Type ";"
IfaceDecl   ::= "iface" IfaceId TypeParams? "{" FnSig* "}"
WitnessDecl ::= "witness" WitnessId ":" IfaceRef "=" "{" Binding* "}" ";"
FnDecl      ::= Async? "fn" FnId TypeParams? "(" ParamList? ")" "->" Type Effects Caps Body
Async       ::= "async"
Effects     ::= "!" "{" EffectList? "}"
Caps        ::= ("using" "{" CapReqList? "}")?
Body        ::= Block

Block       ::= "{" Stmt* Term "}"
Stmt        ::= "let" LocalId "=" Expr ";"
              | "let cell" LocalId ":" Type "=" Expr ";"
              | "write" Place "<-" Expr ";"
              | "unsafe" UnsafeTag Block
              | "opaque" OpaqueTag Block

Term        ::= "return" Expr ";"
              | "throw" Expr ";"
              | "if" Expr Block "else" Block
              | "match" Expr "{" Arm+ "}"
              | "loop" LoopId Block
              | "break" LoopId "(" ArgList? ")" ";"
              | "continue" LoopId ";"

Expr        ::= Literal
              | LocalId
              | "call" Ref "(" ArgList? ")"
              | "invoke" IfaceMethodRef WitnessArg "(" ArgList? ")"
              | "record" "{" FieldInit* "}"
              | "variant" VariantTag "(" ArgList? ")"
              | "read" Place
              | "borrow" Place
              | "borrow_mut" Place
              | "await" Expr
              | "spawn" Expr
              | "send" Expr "," Expr
              | "recv" Expr
              | "cast" CastKind Expr "to" Type
              | "new_gc" Type Expr?
              | "perform" EffectOp "(" ArgList? ")"

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
```

## Deliberate v0.1 exclusions

The source architecture leaves the following unresolved. They are not part of canonical v0.1 `SCIR-H` unless explicitly revised.

- structured `try/catch` syntax
- `select`
- first-class generator syntax
- profile-specific comment preservation in canonical text

These are tracked in `OPEN_QUESTIONS.md`.

## Semantic obligations

`SCIR-H` must make explicit:

- control and exceptional edges,
- mutation sites,
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
