# Invalid Canonical SCIR-H Fixtures
Status: Informative

Every `.scirh` file in this directory is intentionally invalid as canonical `SCIR-H`.
The checked-in manifest binds each fixture to the invariant code it must fail with.
Some fixtures fail parsing, while others parse successfully and then fail semantic validation.

The current fixtures cover:

- forbidden hidden control transfer
- implicit mutation and effect rows
- unresolved names and invalid field places
- canonical formatting and deterministic-storage violations
- missing opaque-boundary contracts
- unsupported legacy syntax
