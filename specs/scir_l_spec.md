# SCIR-L Specification
Status: Normative

## Scope

`SCIR-L` is the lowered control and analysis representation used for SSA-style reasoning, async/effect lowering, optimization, and backend preparation.

## Non-negotiable properties

- derivative from validated `SCIR-H`
- explicit CFG
- block parameters
- SSA values
- explicit effect and memory sequencing where required
- explicit provenance back to `SCIR-H`
- lowered witness and async structures
- lower reconstructability than `SCIR-H`

## Core structure

`SCIR-L` contains:

- modules,
- functions,
- blocks,
- SSA values,
- memory tokens,
- effect tokens,
- block terminators,
- provenance records.

## Canonical grammar

```ebnf
LModule   ::= "lmodule" ModId "{" LDecl* "}"
LDecl     ::= LFn | LGlobal

LFn       ::= "func" FnId "(" ParamList? ")" "->" RetTy "{" Block+ "}"
Block     ::= "^" BlockId "(" PhiList? ")" ":" Instr* Terminator
Instr     ::= SsaId "=" Op OperandList AttrList? ";"
Terminator::= "br" BlockRef "(" ArgList? ")" ";"
            | "cond_br" SsaId "," BlockRef "(" ArgList? ")" "," BlockRef "(" ArgList? ")" ";"
            | "ret" SsaId? ";"
            | "throw" SsaId "," EffTok ";"
            | "suspend" StateId "," FrameId "," EffTok ";"

Op        ::= "const" | "add" | "sub" | "cmp" | "call"
            | "load" | "store" | "alloc" | "phi"
            | "make_witness" | "proj_witness"
            | "async.save" | "async.resume" | "effect.merge"
            | "ffi.call" | "opaque.call"

Operand   ::= SsaId | Lit | MemTok | EffTok | CapTok | BlockRef
```

## Required semantics carried from `SCIR-H`

`SCIR-L` must preserve, in lowered form:

- control-flow meaning,
- value flow,
- sequencing for memory and non-memory effects where required,
- async suspension structure,
- opaque and foreign boundary calls,
- provenance links to the originating `SCIR-H` nodes.

## Prohibited behavior

- no `SCIR-L`-only semantic obligations,
- no backend-specific semantics without a contract,
- no optimizer-only facts masquerading as canonical semantics,
- no missing provenance for lowered nodes that originated in `SCIR-H`.

## Reconstructability boundary

May remain reconstructable:

- symbol signatures,
- types,
- module dependencies,
- provenance links.

Must not be assumed idiomatically reconstructable:

- exact structured control shape,
- exact async syntax,
- exact witness syntax,
- source-local declaration layout.

## Validator obligations

See `specs/validator_invariants.md`.
