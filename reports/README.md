# Reports
Status: Informative

This directory currently holds checked-in example artifacts that are validated against the repository JSON schemas.

These files are illustrative fixtures, not production outputs and not evidence of completed importer, validator, lowering, reconstruction, or benchmark implementations.

## Current contents

- `examples/` minimal schema-valid examples for report and manifest contracts
- `exports/` checked-in derived exports whose source-of-truth remains a normative markdown file
- `exports/execution_queue.export.json` is the agent-facing export derived from `EXECUTION_QUEUE.md`

## Rules

- example artifacts must remain profile-qualified where applicable
- example artifacts must not overstate preservation, support, or benchmark success
- derived exports must remain mechanically derivable from their normative markdown source
- the execution queue export must remain mechanically derivable from `EXECUTION_QUEUE.md` and consistent with the active roadmap documents
- `make validate` must fail if the checked-in examples drift from their schemas
- `make validate` must fail if a checked-in derived export drifts from its markdown source or schema

## Future direction

The executable bootstrap scripts now generate validation, preservation, reconstruction, and benchmark bundles transiently during `make validate` and `make benchmark`.

Current transient Track `A` bundles include both median and aggregate token-ratio diagnostics, with pass/fail determined by the published median-based success and kill gates.

Current transient Track `B` bundles include Tier `A` compile/test rates, idiomaticity evidence, preservation ceiling, tier distribution, and opaque-fraction diagnostics.

Current transient Track `D` bundles include separate Rust `N` and Python `D-PY` executable results with `S5` and `K8` metrics on the fixed bootstrap corpus. `D-JS` and Track `C` generated bundles remain out of scope for the current executable harness.

Checked-in generated bundles still remain out of scope for now. If they are promoted into `reports/` later, they must remain distinguishable from these checked-in examples and derived exports.
