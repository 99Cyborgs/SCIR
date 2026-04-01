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
| importer conformance checker | fixed source subset + generated importer output + checked-in importer fixture bundle | `module_manifest` + `feature_tier_report` + `validation_report` | yes |
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
| execution-queue change | `execution_queue` export |

Schemas live in `schemas/`.

For the current Phase 7 TypeScript witness slice, the conformance-checker contract is partially active:

- the TypeScript checker must mirror the Python and Rust importer conformance model where the Phase 7 placeholder corpus permits
- `validate-fixtures` is now active for checked-in dormant placeholder-corpus integrity
- `test` remains reserved for future generated-vs-golden conformance against live importer output
- repository validation must continue to enforce the fixed nine-case dormant TypeScript placeholder corpus shape at the repo-contract layer, including admitted-vs-rejected file-set rules, rejected-case `expected.scirh` absence, placeholder report posture, and explicit non-live diagnostic markers
- the active `validate-fixtures` checker must treat admitted `expected.scirh` files as non-canonical sentinels rather than parseable canonical `SCIR-H`
- the reserved `test` path in `scripts/typescript_importer_conformance.py` must fail clearly as non-live and must not claim generated-vs-golden validation

## Blocking rules

A change must not merge when any of the following is true:

- hard invariant violation remains unresolved,
- profile claim is missing,
- preservation level is missing,
- tier classification is missing where source coverage changed,
- opaque boundary lacks a contract,
- translation step increased claims without evidence,
- canonical `SCIR-H` contains richer `try/catch` or `select` surface than the published v0.1 contract,
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
- `try/catch` outside the canonical single-catch shape `try` / `catch x T` suites,
- `select` arms that are not explicit channel `send` or `recv`,
- `select` default, timeout, fairness, or priority semantics,
- hidden exception discharge or hidden concurrency choice edges,
- missing stable IDs where required,
- non-canonical formatting,
- legacy bootstrap brace/semicolon text after the compact canonical cutover,
- `call f(args)`, `let cell`, `write`, or `read` in canonical bootstrap `SCIR-H`.
- field-place syntax outside the canonical `LocalId(.FieldId)*` form.

Bootstrap canonical validation is parse -> normalize -> format equality on the supported subset, not raw string matching against hand-maintained literals.

### `SCIR-L`

Must reject:

- malformed SSA or block parameters,
- ops outside the frozen bootstrap set,
- missing or inconsistent provenance,
- unsound effect or memory token threading,
- hidden merge state outside block parameters,
- `field.addr` without a corresponding validated `SCIR-H` field place,
- control-flow edges not justified by the lowered `SCIR-H`,
- `opaque.call` without a corresponding explicit opaque boundary,
- Phase 6B optimizer rewrites outside the published `N` and `D-PY` contracts,
- `SCIR-L`-only semantic obligations.

### Translation validation

Must downgrade or fail when:

- structured control loss exceeds the declared profile,
- host, FFI, or scheduling assumptions become stronger,
- opaque boundaries increase without disclosure,
- witness, capability, or ownership meaning changes without contract coverage.

For the current bootstrap Phase 3 slice, translation validation must also enforce:

- `a_basic_function` and `a_async_await` remain `R/P1`,
- `c_opaque_call` remains `D-PY/P3`,
- importer-only `SCIR-H` cases such as `b_if_else_return`, `b_direct_call`, `b_async_arg_await`, `b_while_call_update`, `b_while_break_continue`, `b_class_init_method`, `b_class_field_update`, and the bounded Python `d_try_except` slice emit no `SCIR-L` or translation artifacts on the executable path,
- `a_mut_local`, `a_struct_field_borrow_mut`, and `a_async_await` remain `R/P1` on the Rust Phase 6A path,
- `c_unsafe_call` remains `N/P3`,
- `opaque` observables remain present on the opaque case and absent on the Tier A cases.

For post-02B and future witness-bearing second-language work, translation validation must also enforce:

- importer-only expansion slices emit no executable `SCIR-L`, translation, reconstruction, or benchmark artifacts until a published downstream contract exists for those slices,
- TypeScript interface-shaped witness evidence remains explicit in reports and does not rely on hidden host-runtime or backend assumptions,
- the first Phase 7 TypeScript slice is limited to interface-shaped witness declarations and module-local consumption doctrine, not general function, class, async, or prototype execution semantics,
- the first checked-in TypeScript fixture contract reuses the existing importer bundle model: admitted cases carry source text, canonical `SCIR-H`, `module_manifest`, `feature_tier_report`, and `validation_report`, while rejected boundary cases omit canonical `SCIR-H`,
- `H -> L` provenance continuity remains blocking for any newly admitted witness-bearing path,
- downgrade reporting remains profile-qualified and cannot be replaced by informal milestone prose,
- optimizer-only facts do not flow back into canonical `SCIR-H`,
- `D-JS` executable claims remain invalid until a later milestone adds explicit lowering, translation-validation, reconstruction, and benchmark gates.

### Reconstruction validation

Must fail when:

- reconstructed Python does not compile,
- reconstructed Python changes the fixture behavior under the bootstrap execution harness,
- `reconstruction_report` claims a profile or preservation level stronger than the fixed bootstrap case matrix,
- `preservation_report` drops required opaque accounting or introduces opaque observables on a Tier `A` case,
- `provenance_complete` is true while any non-empty canonical `SCIR-H` line lacks a provenance entry,
- rejected Tier `D` cases emit reconstruction outputs.

For the current bootstrap Phase 4 slice, reconstruction validation must also enforce:

- `a_basic_function` and `a_async_await` remain `R/P1`,
- `c_opaque_call` remains `D-PY/P3`,
- importer-only `SCIR-H` cases such as `b_if_else_return`, `b_direct_call`, `b_async_arg_await`, `b_while_call_update`, `b_while_break_continue`, `b_class_init_method`, `b_class_field_update`, and the bounded Python `d_try_except` slice emit no reconstruction artifacts,
- idiomaticity is recorded but is not a separate blocking threshold,
- compile/test evidence and provenance completeness are blocking.

For the current Rust Phase 6A slice, reconstruction validation must also enforce:

- `a_mut_local`, `a_struct_field_borrow_mut`, and `a_async_await` remain `R/P1`,
- `c_unsafe_call` does not emit reconstruction outputs,
- missing `rustc` or `cargo` is a blocking validation failure for the Rust path.

## Operational command contract

`make validate` must remain the top-level blocking validation command.

At minimum it must:

- verify repository structure,
- parse all JSON schemas,
- validate checked-in example report and manifest artifacts against their schemas,
- validate the checked-in decision-register export against both `DECISION_REGISTER.md` and its schema,
- validate the checked-in open-questions export against both `OPEN_QUESTIONS.md` and its schema,
- validate the checked-in execution-queue export against `EXECUTION_QUEUE.md`, the active milestone, and its schema,
- validate the checked-in Python importer fixture corpus against its conformance checker when that corpus exists,
- validate the checked-in Rust importer fixture corpus against its conformance checker when that corpus exists,
- validate the checked-in TypeScript importer fixture corpus against the TypeScript conformance checker `validate-fixtures` mode,
- validate the executable bootstrap importer against the checked-in Python fixture goldens,
- allow checked-in Python importer fixtures such as `b_if_else_return`, `b_direct_call`, `b_async_arg_await`, `b_while_call_update`, `b_while_break_continue`, `b_class_init_method`, `b_class_field_update`, and `d_try_except` to stop at validated canonical `SCIR-H` when they are explicitly marked outside the executable lowering and reconstruction path,
- validate the executable Rust importer against the checked-in Rust fixture goldens,
- once a live TypeScript importer exists and the placeholder corpus is promoted to live goldens, run the TypeScript conformance checker `test` mode against the fixed interface-witness corpus and keep the slice importer-only unless a later milestone widens downstream contracts,
- validate bootstrap `SCIR-H`, `SCIR-L`, translation, and reconstruction reports for the supported executable slice,
- require `rustc` and `cargo` before executing the Rust Phase 6A lowering and reconstruction path,
- validate the compact bootstrap `SCIR-H` parser/formatter round-trip and reject legacy bootstrap syntax as non-canonical,
- reject bootstrap `SCIR-L` artifacts that drift beyond the frozen op set, token model, or translation claims,
- keep benchmark-only post-`SCIR-L` emitters out of reconstruction claims,
- reject bootstrap reconstruction artifacts that overclaim profile or preservation, lose opaque accounting, misreport compile/test results, or claim complete provenance with missing canonical-line coverage,
- reject executable `D-JS` or witness-bearing second-language artifacts that lack a published validator and report contract,
- reject Phase 7 TypeScript planning-slice artifacts that emit executable `SCIR-L`, translation, reconstruction, or benchmark outputs before a published downstream contract exists,
- reject dormant first-slice TypeScript placeholder-corpus drift in case IDs, admitted-vs-rejected file sets, declared tiers, report summaries, validation statuses, and non-live boundary markers until the TypeScript checker exists,
- reject first-slice TypeScript fixture bundles that omit required importer reports or that include canonical `SCIR-H` for rejected boundary cases,
- reject any future TypeScript conformance checker that diverges from the published corpus layout, mode contract, or importer-only boundary for the first slice,
- verify required docs exist,
- verify benchmark doctrine files exist,
- exit non-zero on missing required files or malformed JSON.

## Evidence for done

A validation-sensitive task is not done unless:

- the relevant validator contract file is current,
- the relevant schemas are current,
- the relevant report examples are derivable from the spec and schema-valid,
- checked-in importer fixtures, generated-vs-golden conformance checks, and the executable bootstrap pipeline are current when importer code remains bootstrap-only,
- derived exports remain synchronized with their normative markdown source,
- the execution queue remains synchronized with its markdown source and roadmap constraints,
- `make validate` passes.
