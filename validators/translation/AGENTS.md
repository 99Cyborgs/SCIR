# Translation Validator Local Rules
Status: Normative

Read first:

1. `docs/preservation_contract.md`
2. `specs/validator_invariants.md`
3. `specs/interop_and_opaque_boundary_spec.md`

Local rules:

- translation validation may downgrade or fail claims; it must not silently strengthen them,
- preserve or report opaque and unsafe accounting,
- require explicit contracts for `P2` and `P3`,
- do not treat benchmark parity as proof of semantic parity.
