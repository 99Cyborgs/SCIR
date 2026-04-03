# CI Policy
Status: Normative

CI enforces the narrowed MVP boundary.

## Active pipelines

- fast validation pipeline
- slower evaluation pipeline

Fast validation keeps repo contracts, fixture integrity, parser/validator correctness, negative invariant corpora, and sweep smoke visible on every active change.
Slower evaluation keeps round-trip self-tests, full sweep report generation, and benchmark smoke separate from the quick gate.

Deferred tooling or frontend surfaces must not silently re-enter CI.
