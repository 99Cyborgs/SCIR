# Invocation Prompt

```text
Use $scir-provenance-continuity at G:/GitHub/incubate/SCIR/.codex/skills/scir-provenance-continuity to harden source -> SCIR-H -> SCIR-L -> reconstruction provenance continuity inside the admitted SCIR MVP. Keep SCIR-H authoritative, keep SCIR-L derivative, identify any missing origin or lowering_rule coverage, tighten schemas and validator outputs only where executable enforcement exists, add or update negative tests, and fail closed if the request would widen importer or backend scope.
```

# Task Model

Harden provenance continuity as a validator-backed contract. The task is complete only when changed provenance rules are enforced by code, schemas, and tests.

# Confirmed Facts

- `SCIR-H` is the only normative semantic authority.
- `SCIR-L` is derivative-only and semantically meaningful ops require both `origin` and `lowering_rule`.
- `tests/invalid_scir_l/manifest.json` already carries negative provenance fixtures for missing origin, invalid origin mapping, and invalid lowering rule.
- `validators/translation_validator.py` emits `suspect_l_nodes`, `suspect_h_nodes`, `backend_regions`, and `origin_trace_links`.
- `schemas/translation_validation_report.schema.json` requires provenance-linked finding surfaces and `origin_trace_links`.

# Explicit Constraints

- Do not add new importer support, new backend support, or new Wasm admissions.
- Do not rely on documentation-only provenance claims.
- Do not let reports, exports, or `SCIR-Hc` become authority for lowering provenance.
- Keep the work inside current lowering, translation-validation, preservation-report, and reconstruction-report contracts.

# Execution Steps

1. Read the lowering contract, validator invariants, validator contracts, relevant local AGENTS files, and the current provenance-aware tests.
2. Identify the exact provenance gap: missing field, invalid mapping, weak finding coverage, schema mismatch, or missing negative test.
3. Change the smallest set of validator, schema, and test surfaces needed to enforce the gap.
4. Add or tighten negative fixtures when the failure mode is supposed to reject.
5. Revalidate with targeted tests first, then the repo gate.

# Required Outputs

- `Provenance surface`
- `Gap or drift fixed`
- `Changed enforcement surfaces`
- `Negative coverage`
- `Validation`
- `Residual boundary`

# Validation

- `python -m unittest tests.test_translation_validator tests.test_translation_validator_mutations`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/validate_translation.py`
- `python scripts/run_repo_validation.py`
- `python scripts/run_repo_validation.py --require-rust` when Rust provenance paths are touched

# Fail-Closed Rules

- Stop if the only fix is to widen importer, backend, or benchmark scope.
- Stop if the requested provenance change would reinterpret SCIR semantics rather than harden continuity.
- Stop if a schema or report change cannot be backed by validator or test enforcement.
- Stop if the work depends on queue, roadmap, or architecture decisions outside the provenance slice.
