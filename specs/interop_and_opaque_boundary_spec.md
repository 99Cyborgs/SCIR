# Interop and Opaque Boundary Specification
Status: Normative

## Purpose

The MVP needs explicit escape hatches without pretending they are semantically modeled.

## Active boundary forms

- importer-emitted opaque foreign call
- importer-emitted explicit unsafe call boundary
- boundary-valued `opaque<T>` types

## Mandatory metadata

Every active opaque or unsafe boundary must record:

1. boundary ID
2. boundary kind
3. declared signature
4. declared effect summary
5. ownership-transfer summary
6. capability requirements, if any
7. determinism classification
8. audit note

## Preservation rules

- `P3` is the default ceiling for explicit opaque or unsafe boundaries
- stronger claims require explicit evidence
- boundary annotations must remain visible in preservation reports

## Validation rules

- a boundary without metadata is invalid
- boundary metadata must include capability requirements even when that list is empty
- boundary capability requirements must align with `module_manifest.dependencies` entries in `capability:<name>` form
- boundary metadata must remain symbol-consistent with the imported call site
- a boundary cannot silently mint semantics
- a validated direct call cannot be rewritten into `opaque.call` without an explicit boundary
