# Concurrency Model
Status: Normative

## Scope

SCIR must model practical concurrency without pretending universal schedule preservation.

## Canonical v0.1 primitives

- `task<T>`
- `chan<T>`
- `spawn`
- `await`
- `send`
- `recv`

## Required semantics

- async suspension points are explicit,
- task creation is explicit,
- channel operations are explicit,
- shared mutable state must be explicit in the alias model,
- concurrency-sensitive preservation claims are almost always profile-bounded.

## Deliberate v0.1 non-commitments

The source material references `select` in build-order guidance but does not include it in the published grammar.

Repository rule:

- `select` is not canonical v0.1 until `OPEN_QUESTIONS.md` resolves it and the grammar is updated.

## Profile interaction

- `R`: preserve source-visible async or concurrency shape when representable, otherwise downgrade
- `N`: map to native threads, tasks, atomics, or runtime scheduling without exact schedule preservation
- `P`: allow host-assisted async and portable subset concurrency only
- `D`: preserve host event-loop or task semantics where supported

## Validation rules

- undeclared concurrency operations are invalid,
- schedule-sensitive exactness is not assumed,
- race-freedom is conservative and subset-dependent,
- opaque or host concurrency boundaries force `P2` or `P3`.

## Non-goals

- exact cross-target scheduling equivalence,
- universal race-freedom claims across opaque or host runtime regions.
