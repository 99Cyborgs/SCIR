# Repo Documentation Batch 10

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Add comment-only documentation to the first lowering slice of `scripts/scir_bootstrap_pipeline.py` so the admitted proof-loop lowering paths are readable without changing behavior.

## Scope

- Add docstrings for:
  - `is_local_place`
  - the first Python lowering entrypoints:
    - `lower_basic_function`
    - `lower_async_module`
    - `lower_if_else_return_module`
    - `lower_while_call_update_module`
    - `lower_while_break_continue_module`
    - `lower_direct_call_module`
    - `lower_opaque_module`
    - `lower_class_init_module`
    - `lower_class_field_update_module`
    - `lower_try_except_module`
    - `lower_supported_module`
  - the matcher helpers:
    - `match_while_call_update_module`
    - `match_while_break_continue_module`
    - `match_class_init_module`
    - `match_class_field_update_module`
    - `match_try_except_module`
- Add a narrow inline comment clarifying that the lowering dispatcher is the active proof-loop support boundary

## Non-goals

- No logic changes, refactors, renames, or stage-order changes
- No edits to SCIR-L validation, Wasm emission, reconstruction, benchmark, or Rust lowering sections in this batch
- No validator, schema, or fixture-contract changes

## Touched files

- `plans/2026-04-13-repo-documentation-batch-10.md`
- `scripts/scir_bootstrap_pipeline.py`

## Invariants that must remain true

- Lowering remains whitelist-based and canonical-`SCIR-H`-only
- Unsupported fixture shapes still fail with `PipelineError`
- The canonical repo validation gate continues to pass after the edits

## Risks

- GitNexus reported `lower_basic_function` as `CRITICAL` because it is reachable from `lower_supported_module`, `run_pipeline`, sweep, benchmark, and Rust self-test surfaces
- This slice encodes the active proof-loop support boundary, so inaccurate comments would misstate which cases are intentionally admitted

## Validation steps

- `python -m py_compile G:\GitHub\incubate\SCIR\scripts\scir_bootstrap_pipeline.py`
- `python scripts/run_repo_lint.py`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert only the documentation edits in `scripts/scir_bootstrap_pipeline.py` and this historical batch plan if review finds any mismatch between the prose and the actual lowering behavior.

## Evidence required for completion

- Diff review confirming comment-only edits in the first lowering slice of `scripts/scir_bootstrap_pipeline.py`
- GitNexus impact recorded for `lower_basic_function` on 2026-04-13 and treated as a comment-only critical-sensitivity surface
- `python -m py_compile G:\GitHub\incubate\SCIR\scripts\scir_bootstrap_pipeline.py` passed on 2026-04-13
- `python scripts/run_repo_lint.py` passed on 2026-04-13
- `python scripts/run_repo_validation.py` passed on 2026-04-13
