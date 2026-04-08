---
name: scir-provenance-continuity
description: Harden source to SCIR-H to SCIR-L to reconstruction provenance continuity with validator-backed, schema-aware, test-backed changes. Use when lowering provenance, translation evidence, report schemas, invalid SCIR-L fixtures, or reconstruction lineage surfaces need tightening without widening importer or backend scope.
---

# SCIR Provenance Continuity

Read [prompt.md](prompt.md) for the invocation frame and [checklist.md](checklist.md) for the provenance hardening checks.

## Purpose

Keep provenance continuity executable and fail-fast across the admitted proof loop. This skill hardens the lineage path from source-facing fixtures through canonical `SCIR-H`, derivative `SCIR-L`, translation validation, and reconstruction reports so provenance is enforced by validators, schemas, and negative tests rather than by documentation alone.

## When to use

- when `origin` or `lowering_rule` coverage may be incomplete or drifting
- when translation findings need stronger `suspect_l_nodes`, `suspect_h_nodes`, or `origin_trace_links` coverage
- when reconstruction or preservation reports may overstate provenance completeness
- when negative `SCIR-L` provenance fixtures or provenance-aware tests need tightening

## Allowed scope

- read and update `LOWERING_CONTRACT.md`, `VALIDATION.md`, `VALIDATION_STRATEGY.md`, and `validators/validator_contracts.md` when provenance doctrine or validator wording changes
- read and update `scripts/scir_bootstrap_pipeline.py` and `scripts/validate_translation.py`
- read and update `validators/translation_validator.py` and the validator subtrees relevant to provenance enforcement
- read and update `schemas/preservation_report.schema.json`, `schemas/translation_validation_report.schema.json`, `schemas/reconstruction_report.schema.json`, and `schemas/validation_report.schema.json` when report contracts change
- read and update `tests/test_translation_validator.py`, `tests/test_translation_validator_mutations.py`, and `tests/invalid_scir_l/*`

## Forbidden actions

- widen parser, importer, frontend, backend, or benchmark scope
- admit new Wasm-emittable shapes or new backend semantics as part of provenance work
- add provenance theater that is not enforced by validators, schemas, or tests
- let `SCIR-Hc`, `SCIR-L`, reports, or exports become provenance authority

## Required inputs

- `LOWERING_CONTRACT.md`
- `specs/scir_l_spec.md`
- `specs/validator_invariants.md`
- `validators/validator_contracts.md`
- `validators/scir_l/AGENTS.md` and `validators/translation/AGENTS.md`
- relevant schemas under `schemas/`
- current provenance-aware tests and invalid `SCIR-L` fixtures

## Required outputs

- one bounded provenance-hardening change set or one fail-closed stop
- synchronized validator, schema, and negative-test surfaces for any changed provenance rule
- one concise summary of the exact provenance path hardened and the exact surfaces still deferred

## Validation sequence

1. Run targeted provenance tests with `python -m unittest tests.test_translation_validator tests.test_translation_validator_mutations`.
2. Run `python scripts/scir_bootstrap_pipeline.py --mode validate`.
3. Run `python scripts/validate_translation.py`.
4. If Rust provenance or shared validator behavior is touched, run `python scripts/run_repo_validation.py --require-rust`.
5. Run `python scripts/run_repo_validation.py` before calling a cross-surface provenance change complete.

## Done criteria

- every changed semantically meaningful `SCIR-L` op or terminator still carries valid `origin` and `lowering_rule` coverage
- provenance-aware report schemas and validator outputs stay synchronized
- missing-origin, invalid-origin-mapping, and invalid-lowering-rule negative coverage remains explicit and failing
- translation validation still reports provenance-linked suspect nodes when mismatches occur
- reconstruction or preservation surfaces do not overclaim provenance completeness

## Failure conditions

- the requested provenance change requires new language support, new backend scope, or new benchmark doctrine
- schema, validator, and test surfaces cannot be synchronized inside the admitted MVP boundary
- provenance can only be documented, not enforced, on the requested surface
- the tranche would need to reinterpret `SCIR-H` or `SCIR-L` semantics rather than harden existing continuity

## Escalation rules

- escalate when provenance hardening requires spec or architecture changes outside existing doctrine
- escalate when the request pressures queue ordering, benchmark claim posture, or backend admission rules
- escalate when a local validator rule conflicts with the higher-authority root doctrine
