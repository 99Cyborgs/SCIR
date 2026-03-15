# VALIDATION_STRATEGY
Status: Normative

## Objective

Validation is the enforcement layer for SCIR invariants. Unsupported or weakly modeled semantics must fail fast or downgrade explicitly.

## Validation order

1. repository contract validation
2. importer conformance validation
3. `SCIR-H` validation
4. `SCIR-L` lowering precondition checks
5. `SCIR-L` validation
6. translation validation on selected steps
7. reconstruction validation
8. benchmark contract validation

## Validator stack

| Validator | Input | Output | Blocking |
| --- | --- | --- | --- |
| repository contract checker | repository files | console report | yes |
| importer conformance checker | source subset + importer output | `module_manifest` + `feature_tier_report` + `validation_report` | yes |
| `SCIR-H` validator | canonical `SCIR-H` | `validation_report` | yes |
| `SCIR-L` validator | canonical `SCIR-L` | `validation_report` | yes |
| translation validator | paired artifacts across stages | `preservation_report` or downgrade | selected but blocking for safety-critical lowering steps |
| reconstruction checker | reconstructed source + tests | `reconstruction_report` + `preservation_report` | yes for round-trip claims |
| benchmark contract checker | manifests and result bundles | `benchmark_result` structure validation | yes |

## Report discipline

Every non-trivial stage change must emit or update the relevant report type.

| Scenario | Required reports |
| --- | --- |
| importer change | `module_manifest`, `feature_tier_report`, `validation_report` |
| `SCIR-H` semantic change | `validation_report`, possibly `preservation_report` if reconstruction is affected |
| `H -> L` lowering change | `validation_report` for `SCIR-L`, `preservation_report`, translation-validation evidence |
| reconstruction change | `reconstruction_report`, `preservation_report` |
| benchmark harness or result change | `benchmark_manifest`, `benchmark_result` |

Schemas live in `schemas/`.

## Blocking rules

A change must not merge when any of the following is true:

- hard invariant violation remains unresolved,
- profile claim is missing,
- preservation level is missing,
- tier classification is missing where source coverage changed,
- opaque boundary lacks a contract,
- translation step increased claims without evidence,
- benchmark gates were affected but benchmark docs were not updated.

## Acceptance criteria by layer

### `SCIR-H`

Must reject:

- hidden control transfer,
- implicit effects,
- implicit mutation,
- ambiguous name resolution,
- undeclared capability use,
- undeclared opaque or unsafe region,
- missing stable IDs where required,
- non-canonical formatting.

### `SCIR-L`

Must reject:

- malformed SSA or block parameters,
- missing or inconsistent provenance,
- unsound effect or memory token threading,
- control-flow edges not justified by the lowered `SCIR-H`,
- `SCIR-L`-only semantic obligations.

### Translation validation

Must downgrade or fail when:

- structured control loss exceeds the declared profile,
- host, FFI, or scheduling assumptions become stronger,
- opaque boundaries increase without disclosure,
- witness, capability, or ownership meaning changes without contract coverage.

## Operational command contract

`make validate` must remain the top-level blocking validation command.

At minimum it must:

- verify repository structure,
- parse all JSON schemas,
- validate checked-in example report and manifest artifacts against their schemas,
- validate the checked-in decision-register export against both `DECISION_REGISTER.md` and its schema,
- validate the checked-in open-questions export against both `OPEN_QUESTIONS.md` and its schema,
- verify required docs exist,
- verify benchmark doctrine files exist,
- exit non-zero on missing required files or malformed JSON.

## Evidence for done

A validation-sensitive task is not done unless:

- the relevant validator contract file is current,
- the relevant schemas are current,
- the relevant report examples are derivable from the spec and schema-valid,
- derived exports remain synchronized with their normative markdown source,
- `make validate` passes.
