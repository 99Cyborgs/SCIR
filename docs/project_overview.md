# Project Overview
Status: Informative

SCIR is a semantic compression MVP with two explicit layers:

- `SCIR-H`: canonical semantics
- `SCIR-L`: derivative lowering

The active product question is not "can SCIR replace mainstream languages?"
It is "can SCIR keep a narrow proof loop honest enough to justify continuing?"

## Built first

1. compact canonical `SCIR-H`
2. compact derivative `SCIR-L`
3. validators
4. Python subset importer
5. Python reconstruction
6. Rust safe-subset importer
7. Wasm reference-backend contract
8. Track `A` and `B` benchmark harness

## Current status

Implemented now:

- canonical `SCIR-H` parser/formatter, invariant-coded negative validation, and stable proof-loop fixtures
- bounded `SCIR-H -> SCIR-L` lowering plus structural validation for the active Python proof loop
- fixed Tier `A` corpus manifests and a slice-based sweep smoke lane

Partially implemented:

- importer-only Tier `B` `SCIR-H` evidence cases
- Rust importer-first evidence and bounded optional Rust validation
- helper-free Wasm emission only for the admitted fixed cases

Unsupported or deferred:

- standalone `throw` syntax
- whole-language frontend claims
- active TypeScript execution work
- broad native/backend parity claims

## Not built first

- a new end-user syntax
- active TypeScript work
- broad native backend work
- broad runtime/tooling work
- benchmark Track `D`

## Success test

SCIR continues only if the narrow proof loop remains useful against strong baselines.
