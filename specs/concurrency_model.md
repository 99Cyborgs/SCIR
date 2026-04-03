# Concurrency Model
Status: Normative

## Active MVP scope

The active MVP models only explicit `async` / `await` in the compact subset already implemented by the parser, importers, and lowering pipeline.

## Deferred from active use

These remain out of active scope:

- channels
- `select`
- `spawn`
- send/receive operations
- fairness or scheduling contracts beyond profile-qualified notes

## Rule

No concurrency construct outside explicit `async` / `await` may appear as an active support claim until grammar, parser, validator, lowering, reconstruction, and tests are aligned.
