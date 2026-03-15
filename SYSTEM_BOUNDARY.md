# SYSTEM_BOUNDARY
Status: Normative

## Project boundary

SCIR is a semantic substrate project.

It is not, in the first credible product cycle, a source-language replacement project.

## In scope now

### Mandatory first-product scope

- `SCIR-H` canonical representation
- `SCIR-L` lowered representation
- parser / formatter contract for both
- stable symbol identity and provenance
- `SCIR-H` validator
- `SCIR-L` validator
- translation validation hooks
- preservation reporting
- reconstruction pipeline
- benchmark harness and baseline adapters

### First implementation scope

- Python subset importer
- Rust subset importer after Python subset
- Wasm or equivalent portable execution path first
- reconstruction-first path before broad backend work
- benchmark tracks A–D, starting with Track A and B pilots

## Explicitly out of scope for the first credible product

- a mass-market user-facing language
- whole-language fidelity for Python, C++, Haskell, or any other language
- broad C++ support
- advanced proof stack before validator value exists
- backend sprawl
- hidden runtime shims that erase semantic mismatch
- unsupported semantics silently mapped to supported semantics
- benchmarkless AI claims

## Language support boundary

The repository discusses these languages as overlapping semantic families, not full-fidelity commitments:

- Python
- Rust
- TypeScript
- Go
- Haskell
- disciplined subsets of C++

Initial implementation priority is Python then Rust.

## Execution target boundary

Initial target priority:

1. reconstruction back to the source language subset,
2. portable execution profile `P`,
3. native profile `N` only after `H`, `L`, and reconstruction are credible,
4. dynamic-host profile `D` where host fidelity is a requirement.

## Unsupported-case policy

If a construct is not modeled, it must be one of:

- Tier `C` with an explicit opaque or unsafe boundary contract,
- Tier `D` with importer rejection,
- an open question recorded in `OPEN_QUESTIONS.md`.

No silent fallback is permitted.

## Claim boundary

No PR, report, plan, or benchmark may claim any of the following without explicit evidence:

- exact preservation without profile and `P0`,
- support for a feature without a tier,
- safety across an unsafe or opaque boundary,
- repository-scale AI value without strong direct-source and typed-AST baselines,
- profile-independent semantics.

## Stop conditions

The AI-facing thesis must narrow or terminate if any kill criterion in `benchmarks/success_failure_gates.md` is triggered.
