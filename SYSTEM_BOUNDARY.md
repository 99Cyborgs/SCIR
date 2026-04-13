# SYSTEM_BOUNDARY
Status: Normative

## Project boundary

SCIR is an MVP semantic-substrate project.

It is not:

- a new authoring language
- a broad whole-language importer suite
- a proof-first research stack
- a universal backend program

## Active implementation target

The active implementation target is:

- Python subset importer
- canonical `SCIR-H`
- `SCIR-H` validator hardening

## Maintained but frozen support surfaces

These remain validated and preserved on disk, but they are not the current widening target:

- derived `SCIR-Hc`
- derivative `SCIR-L`
- bounded `SCIR-H -> SCIR-L` lowering
- bounded Rust importer-first evidence
- bounded Wasm reference backend
- Track `A` and Track `B` benchmark harnesses

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
