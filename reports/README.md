# Reports
Status: Informative

This directory currently holds checked-in example artifacts that are validated against the repository JSON schemas.

These files are illustrative fixtures, not production outputs and not evidence of completed importer, validator, lowering, reconstruction, or benchmark implementations.

## Current contents

- `examples/` minimal schema-valid examples for report and manifest contracts
- `exports/` checked-in derived exports whose source-of-truth remains a normative markdown file

## Rules

- example artifacts must remain profile-qualified where applicable
- example artifacts must not overstate preservation, support, or benchmark success
- derived exports must remain mechanically derivable from their normative markdown source
- `make validate` must fail if the checked-in examples drift from their schemas
- `make validate` must fail if a checked-in derived export drifts from its markdown source or schema

## Future direction

Generated validation, preservation, reconstruction, and benchmark bundles may also live under `reports/` later, but those outputs must remain distinguishable from these checked-in examples and derived exports.
