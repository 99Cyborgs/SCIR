# 2026-04-01 Q-01-001 Lock the Phase 1 `SCIR-H` Kernel

Status: complete
Owner: Codex
Date: 2026-04-01

## Objective

Lock the executable `SCIR-H` kernel around the current canonical subset, canonical/view split, and persistent identity rules without widening the admitted MVP surface.

## Scope

- export one bootstrap-model summary for the executable `SCIR-H` kernel using the same construct labels as `SPEC_COMPLETENESS_CHECKLIST.md`
- mirror that kernel in `specs/scir_h_spec.md` with an explicit canonical parser/formatter and downstream-status table
- restate the enforced identity invariants in `IDENTITY_MODEL.md` in validator-checkable language
- add a repo-contract check that fails when the spec, identity model, checklist, and bootstrap model drift
- close out `Q-01-001` and advance the execution queue to the Phase 2 Python proof-loop handoff

## Non-goals

- no grammar expansion
- no `SCIR-L`, schema, benchmark, or backend widening
- no change to `semantic_lineage_id`, `canonical_content_hash`, `revision_scoped_node_id`, or `render_pretty_module` semantics
- no `STATUS.md` cleanup

## Touched files

- `scripts/scir_h_bootstrap_model.py`
- `scripts/validate_repo_contracts.py`
- `specs/scir_h_spec.md`
- `IDENTITY_MODEL.md`
- `SPEC_COMPLETENESS_CHECKLIST.md`
- `EXECUTION_QUEUE.md`
- `reports/exports/execution_queue.export.json`
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md`

## Invariants that must remain true

- `SCIR-H` remains the only normative semantic layer
- importer-only follow-on cases remain explicit and do not gain lowering, reconstruction, or backend claims
- persistent lineage remains independent of spec version and pretty-view text
- canonical content hash remains derived only from canonical storage

## Risks

- kernel-alignment checks can become noisy if spec wording stops being machine-checkable
- queue closeout can drift if the export is not regenerated with the markdown update

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/validate_repo_contracts.py --mode test`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the kernel metadata, spec/checklist/identity wording, queue closeout, and validator drift check as one unit if the repository cannot keep the executable contract and documentation aligned.

## Evidence required for completion

- the bootstrap model exports the executable kernel summary and identity markers
- the normative spec and identity model state the same kernel boundary as the executable model
- checklist rows for the active `SCIR-H` constructs match the executable kernel contract
- repository validation fails on kernel drift and passes on the final aligned state

## Completion evidence

- `scripts/scir_h_bootstrap_model.py` now exports `SCIR_H_KERNEL_METADATA` for the active `SCIR-H` kernel and enforced identity markers
- `specs/scir_h_spec.md`, `IDENTITY_MODEL.md`, and `SPEC_COMPLETENESS_CHECKLIST.md` now mirror the executable kernel boundary without promoting any construct
- `scripts/validate_repo_contracts.py` now checks kernel alignment and includes negative fixtures for spec and identity drift
- `Q-01-001` is marked done in `EXECUTION_QUEUE.md` and the queue advances to `Q-02-001`
- passed `python scripts/validate_repo_contracts.py --mode validate`
- passed `python scripts/validate_repo_contracts.py --mode test`
- passed `python scripts/build_execution_queue.py --mode check`
- passed `python scripts/run_repo_validation.py`
