# SCIR-L Specification
Status: Normative

## Scope

`SCIR-L` is a derivative lowering of validated `SCIR-H`.

It exists only for:

- explicit CFG reasoning
- SSA-style value flow
- memory and effect sequencing
- backend preparation
- Wasm reference-backend emission

## Non-negotiable properties

- derivative from validated `SCIR-H`
- explicit CFG
- block parameters
- SSA values
- explicit memory and effect sequencing where required
- explicit origin plus named lowering rule
- no L-only semantic commitments

## Active canonical surface

The active subset contains:

- modules
- functions
- blocks
- block parameters
- the op set `const`, `cmp`, `alloc`, `store`, `load`, `field.addr`, `call`, `async.resume`, `opaque.call`
- the terminators `ret`, `br`, `cond_br`, `invoke`

## Text rendering contract

The repository can render canonical `SCIR-L` text for review, but the active validator operates over the structured lowering artifact emitted by `scripts/scir_bootstrap_pipeline.py`.

There is no standalone MVP `SCIR-L` parser package yet.

## Frozen active grammar

```ebnf
LModule   ::= "lmodule" ModId "{" LFn+ "}"
LFn       ::= "func" FnId "(" ParamList? ")" "->" RetTy "{" Block+ "}"
Block     ::= "^" BlockId "(" BlockParamList? ")" ":" Instr* Terminator
Instr     ::= "%" SsaId "=" Op OperandList ";"
Terminator::= "br" BlockRef "(" ArgList? ")" ";"
            | "cond_br" SsaId "," BlockRef "(" ArgList? ")" "," BlockRef "(" ArgList? ")" ";"
            | "ret" SsaId ";"
            | "invoke" Ref "(" ArgList? ")" "->" SsaId "," BlockRef "(" ArgList? ")" "," "catch" Type BlockRef "(" ArgList? ")" ";"
Op        ::= "const" | "cmp" | "alloc" | "store" | "load"
            | "field.addr" | "call" | "async.resume" | "opaque.call"
```

## Token model

- memory tokens sequence mutable effects
- effect tokens sequence non-memory effects where the lowered shape requires them
- block parameters are the only merge mechanism

## Required lowering provenance

Every semantically meaningful op must carry:

- `origin`
- `lowering_rule`

See `LOWERING_CONTRACT.md`.

## Active bounded exception slice

The active subset admits exactly one exceptional CFG form:

- the `invoke` terminator for the fixed `d_try_except` proof-loop slice,
- one direct symbolic callee,
- one `ValueError` catch edge,
- one carried normal return value,
- no standalone `throw`, rethrow, finally, or multi-handler semantics.

## Deferred from the active subset

- loop lowering for importer-only loop cases
- broader exception lowering
- witness or interface ops
- backend dialect ops
- optimizer-only semantics
- native or host-specific semantics

## Reconstructability boundary

`SCIR-L` is not the default reconstruction source.
Python reconstruction in the MVP is `SCIR-H`-driven.

## Validator obligations

See `specs/validator_invariants.md`.
