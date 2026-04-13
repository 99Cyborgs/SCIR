# Invalid SCIR-L Fixtures
Status: Informative

Every JSON module in this directory is intentionally invalid as lowered `SCIR-L`.
The active pipeline validation must confirm that each file fails `SCIR-L` structural validation with the expected invariant code.

The current fixtures cover:

- malformed CFG and unsupported terminator shapes
- SSA, effect-token, and memory-token discipline
- provenance-origin and lowering-rule drift
- unsupported ops and illegal boundary-op structure
