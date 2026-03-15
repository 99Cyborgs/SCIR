# Validator Stack
Status: Normative

The validator stack exists to enforce canonical semantics, not to decorate already-invalid artifacts with warnings.

## Validators

- `SCIR-H` validator
- `SCIR-L` validator
- translation validator

## Required outputs

All validators emit `validation_report` or `preservation_report` artifacts using repository schemas.

## Ordering

1. validate `SCIR-H`
2. lower to `SCIR-L`
3. validate `SCIR-L`
4. run translation validation on selected transitions
5. validate reconstruction and benchmark results as needed

See `validators/validator_contracts.md`.
