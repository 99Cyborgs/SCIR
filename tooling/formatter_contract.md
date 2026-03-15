# Formatter Contract
Status: Normative

## Responsibilities

- parse canonical `SCIR-H` and `SCIR-L`,
- emit deterministic canonical text,
- preserve stable IDs under pure formatting changes,
- reject malformed artifacts rather than guessing intent.

## Rules

- formatting must be deterministic,
- parser -> formatter -> parser must preserve semantics,
- canonical formatting is normative text storage,
- comments are not part of canonical `SCIR-H` storage.

## Command expectation

Future executable formatter work must remain reachable from the repository command contract without changing the meaning of `make validate`.
