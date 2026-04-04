# Validator Stack
Status: Normative

The validator stack exists to enforce canonical semantics, not to decorate invalid artifacts with warnings.

## Active validators

- `SCIR-H` validator
- `SCIR-Hc` validator
- `SCIR-L` validator
- translation and preservation validator for active paths
- SCIR-Hc execution-context, lineage, and diff-audit validators

## Active ordering

1. validate `SCIR-H`
2. validate `SCIR-Hc` containment before any report or benchmark claim uses compressed evidence
3. lower to `SCIR-L` where the path is active
4. validate `SCIR-L`
5. validate execution-backed backend translation where a backend path is active
6. validate preservation and reconstruction reports
