# Validator Stack
Status: Normative

The validator stack exists to enforce canonical semantics, not to decorate invalid artifacts with warnings.

## Active validators

- `SCIR-H` validator
- `SCIR-L` validator
- translation and preservation validator for active paths

## Active ordering

1. validate `SCIR-H`
2. lower to `SCIR-L` where the path is active
3. validate `SCIR-L`
4. validate preservation and reconstruction reports
