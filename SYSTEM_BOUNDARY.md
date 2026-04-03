# SYSTEM_BOUNDARY
Status: Normative

## Project boundary

SCIR is an MVP semantic-substrate project.

It is not:

- a new authoring language,
- a broad whole-language importer suite,
- a proof-first research stack,
- a universal backend program.

## Active scope now

- canonical `SCIR-H`
- derivative `SCIR-L`
- `SCIR-H` validator
- `SCIR-L` validator
- lowering provenance and derivative-only checks
- Python subset importer
- Rust safe-subset importer
- Python reconstruction from validated `SCIR-H`
- Wasm reference-backend MVP contract
- Track `A` and Track `B` benchmark harnesses

## Not active in this MVP

- TypeScript, C++, Go, and Haskell implementation work
- repository-scale issue-repair benchmarks
- native backend performance claims
- dynamic-host `D-JS` execution claims
- graph explorer, debugger, language server, proof bridge, and agent patch API work beyond no-burden placeholders
- benchmark Track `D`

## Language boundary

Active implementation languages:

- Python
- Rust

Deferred language surfaces:

- TypeScript
- C++
- Go
- Haskell

These may remain discussed as future stress targets only. They are not current implementation commitments.

## Execution boundary

Active execution targets:

1. Python reconstruction from validated `SCIR-H`
2. Wasm reference backend MVP under profile `P`

Non-active execution targets:

- native parity claims
- broad host-runtime parity claims
- `D-JS`

## Unsupported-case policy

If a construct is outside the implemented bootstrap subset, it must be:

- explicitly Tier `C` with an opaque or unsafe boundary contract,
- explicitly Tier `D` and rejected,
- or explicitly deferred in `UNSUPPORTED_CASES.md` and `DEFERRED_COMPONENTS.md`.

No silent fallback is permitted.

## Claim boundary

No document, report, benchmark, example, validator, or script may claim:

- whole-language support,
- universal fidelity,
- backend-independent semantics,
- Wasm success as proof of native or host-runtime parity,
- active TypeScript implementation work,
- active Track `D` benchmark evidence.
