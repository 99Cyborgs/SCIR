# Preflight Checks

- [ ] Read `LOWERING_CONTRACT.md`.
- [ ] Read `specs/scir_l_spec.md` and `specs/validator_invariants.md`.
- [ ] Read `validators/validator_contracts.md`.
- [ ] Read `validators/scir_l/AGENTS.md` and `validators/translation/AGENTS.md`.
- [ ] Read the relevant schemas and provenance-aware tests.

# In-Flight Checks

- [ ] Identify the exact provenance gap.
- [ ] Keep `SCIR-H` authoritative and `SCIR-L` derivative-only.
- [ ] Keep every changed `SCIR-L` op or terminator tied to valid `origin` and `lowering_rule` coverage.
- [ ] Keep schema, validator, and test changes synchronized.
- [ ] Add or tighten negative fixtures if the gap is supposed to reject.

# Output Checks

- [ ] State the exact provenance surface hardened.
- [ ] State the exact enforcement surfaces changed.
- [ ] State the exact negative coverage added or preserved.
- [ ] State the exact deferred boundary that still remains out of scope.

# Validation Checks

- [ ] Run `python -m unittest tests.test_translation_validator tests.test_translation_validator_mutations`.
- [ ] Run `python scripts/scir_bootstrap_pipeline.py --mode validate`.
- [ ] Run `python scripts/validate_translation.py`.
- [ ] Run `python scripts/run_repo_validation.py`.
- [ ] If Rust provenance paths changed, run `python scripts/run_repo_validation.py --require-rust`.

# Closeout Checks

- [ ] Missing-origin and invalid-mapping failures still reject.
- [ ] Translation findings still surface provenance-linked suspects.
- [ ] Reconstruction or preservation reports do not overclaim provenance completeness.
- [ ] No importer, backend, or benchmark scope was widened.
