# SCIR-L Validator Local Rules
Status: Normative

Read first:

1. `specs/scir_l_spec.md`
2. `specs/validator_invariants.md`
3. `specs/provenance_and_stable_id_spec.md`

Local rules:

- enforce CFG, SSA, token, and provenance correctness,
- accept only the frozen bootstrap op set unless the spec is widened first,
- treat block parameters as the only valid merge mechanism in the bootstrap subset,
- keep memory-token and effect-token classes distinct across instructions and edges,
- reject `SCIR-L` artifacts that require semantics not present in `SCIR-H`,
- do not add optimizer-specific assumptions to the validator contract.
