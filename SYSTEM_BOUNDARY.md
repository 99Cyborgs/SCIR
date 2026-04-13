# SYSTEM_BOUNDARY
Status: Normative

## Project boundary

SCIR is an MVP semantic-substrate project.

It is not:

- a new authoring language
- a broad whole-language importer suite
- a proof-first research stack
- a universal backend program

## Active repository target

The active repository target is:

- Frozen 11-case Python proof-loop
- strong-baseline falsification
- Track `A` and Track `B`

## Current narrowed MVP boundary

The current narrowed MVP boundary kept executable for later baseline comparison includes:

- canonical `SCIR-H`
- derived `SCIR-Hc`
- derivative `SCIR-L`
- validator coverage for `SCIR-H`, `SCIR-Hc`, `SCIR-L`, and `SCIR-H -> SCIR-L` preservation
- Python subset import on the frozen 11-case proof loop
- Python reconstruction from validated `SCIR-H`
- bounded Rust importer-first evidence
- bounded Wasm reference backend validation for the admitted helper-free subset
- Track `A` and Track `B` strong-baseline benchmark comparison

## Maintained but frozen support surfaces

These remain validated and preserved on disk, but they are not the current widening target:

- derived `SCIR-Hc`
- derivative `SCIR-L`
- bounded `SCIR-H -> SCIR-L` lowering
- Python reconstruction from validated `SCIR-H`
- bounded Rust importer-first evidence
- bounded Wasm reference backend
- Track `A` and Track `B` strong-baseline benchmark comparison

## Not active now

- TypeScript, C++, Go, and Haskell implementation work
- release-bundle expansion
- Track `C` promotion
- Track `D`
- native backend parity claims
- broad host-runtime parity claims
- new tooling platform surfaces

## Unsupported-case policy

If a construct is outside the implemented subset, it must remain:

- explicitly Tier `C` with an opaque or unsafe boundary contract
- explicitly Tier `D` and rejected
- or explicitly deferred in `docs/unsupported_cases.md` and `BACKLOG.md`

No silent fallback is permitted.

## Claim boundary

No document, report, example, validator, or script may claim:

- whole-language support
- universal fidelity
- backend-independent semantics
- Wasm success as proof of native or host-runtime parity
- active release-bundle machinery by default
