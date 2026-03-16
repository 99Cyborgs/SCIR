# DEPENDENCY_NOTES

## Internal dependency posture

- `specs/` remain the semantic source of truth
- validators and benchmarks depend on the stated architecture and support boundaries

## Portfolio dependency posture

- SCIR is currently a candidate substrate, not an operational dependency
- any promotion should be tied to a bounded extraction with a named consumer
