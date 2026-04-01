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
- `select`

## Required semantics

- async suspension points are explicit,
- task creation is explicit,
- channel operations are explicit,
- `select` is explicit structured control in `SCIR-H`,
- every `select` arm is an explicit channel `send` or `recv` operation,
- if one or more arms are ready, exactly one ready arm is chosen nondeterministically,
- a chosen `recv` arm may bind its received value for that arm body only,
- unchosen arms do not perform their channel operation,
- shared mutable state must be explicit in the alias model,
- concurrency-sensitive preservation claims are almost always profile-bounded.

## Deliberate v0.1 non-commitments

- no default arm,
- no timeout arm,
- no fairness guarantee,
- no priority semantics,
- no non-channel selection surface in canonical v0.1,
- no broad `SCIR-L` concurrency lowering design is defined here beyond the bootstrap subset,
- Phase 3 freezes only simple `await` lowering to `async.resume`; `select`, `spawn`, `send`, and `recv` lowering remain deferred.

## Profile interaction

- `R`: preserve source-visible async or concurrency shape when representable, otherwise downgrade
- `N`: map to native threads, tasks, atomics, or runtime scheduling without exact schedule preservation
- `P`: allow host-assisted async and portable subset concurrency only
- `D-PY`: preserve Python event-loop or task semantics where supported
- `D-JS`: preserve JS/TS event-loop or task semantics where supported

## Validation rules

- undeclared concurrency operations are invalid,
- schedule-sensitive exactness is not assumed,
- race-freedom is conservative and subset-dependent,
- opaque or host concurrency boundaries force `P2` or `P3`.

## Non-goals

- exact cross-target scheduling equivalence,
- universal race-freedom claims across opaque or host runtime regions.
