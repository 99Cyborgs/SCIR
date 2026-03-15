# Validator Contracts
Status: Normative

## Input and output contract

| Validator | Input | Output |
| --- | --- | --- |
| `SCIR-H` validator | canonical `SCIR-H` | `validation_report` |
| `SCIR-L` validator | canonical `SCIR-L` | `validation_report` |
| translation validator | paired stage artifacts and claims | `preservation_report` or failing `validation_report` |

## Exit rule

Blocking validators exit non-zero on hard invariant violations.

## Diagnostic minimum

Every diagnostic must include:

- stable code,
- severity,
- message,
- artifact reference,
- node or block reference when available.

## Claim handling

A validator encountering an overstated claim must:

- fail, or
- downgrade the claim explicitly in a report.

It must not silently continue with the original claim.

## Canonical blocking conditions

- missing profile,
- missing preservation level where required,
- missing feature tier where source coverage changed,
- missing opaque boundary contract,
- malformed stable IDs or provenance,
- malformed SSA or token threading,
- unsupported semantics treated as supported.
