# Portfolio Positioning
Status: Informative

## Architecture snapshot

SCIR is a two-layer semantic system:

- `SCIR-H` is the canonical high-level semantic representation
- `SCIR-L` is the derivative lowered control/dataflow form

Its credible first product is importer + validator + lowering + reconstruction + benchmark harness. Portfolio governance should preserve that narrow path and avoid importing the full semantic surface into core prematurely.

## Promotion posture

### Current class

`incubate`

### Suggested promotion mode

`module extraction`

### Rule

Keep SCIR as a separate substrate repo unless a bounded importer, validator, schema, or contract becomes operationally necessary for core or another incubate repo.

## Promotion triggers

- an identified consumer
- benchmark-backed value for that consumer
- a bounded extraction target with manageable audit cost

## Integration risks

- semantic overreach: promoting too early would force core to load doctrine it does not yet consume
- claim inflation: portfolio language could imply support or maturity beyond benchmark evidence
- audit cost: whole-repo promotion would add a large semantic review surface

## Dependency posture

### Internal

- `specs/` remain the semantic source of truth
- validators and benchmarks depend on the stated architecture and support boundaries

### Portfolio

- SCIR is currently a candidate substrate, not an operational dependency
- any promotion should be tied to a bounded extraction with a named consumer
