# SCIR-H Validator Local Rules
Status: Normative

Read first:

1. `specs/scir_h_spec.md`
2. `specs/type_effect_capability_model.md`
3. `specs/ownership_alias_model.md`
4. `specs/validator_invariants.md`

Local rules:

- reject hidden effects, hidden mutation, ambiguous resolution, and missing capability declarations,
- keep diagnostics stable and machine-referenceable,
- do not weaken invariants to accommodate frontend convenience,
- when in doubt, reject or force a downgrade rather than infer unsupported semantics.
