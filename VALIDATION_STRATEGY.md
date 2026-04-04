# VALIDATION_STRATEGY
Status: Normative

## Objective

Validation is the enforcement layer for the narrowed SCIR MVP.
The validator stack must make unsupported, deferred, or downgraded behavior explicit.

## Active validation order

1. repository contract validation
2. derived-export synchronization
3. active and negative corpus manifest validation
4. sweep manifest validation
5. active preservation-stage expectation validation
6. Python importer fixture validation
7. Rust importer fixture validation
8. seeded invalid `SCIR-H` rejection
9. seeded invalid `SCIR-L` rejection
10. canonical formatter and identity stability checks
11. `SCIR-H` validation
12. `SCIR-Hc` derivation, doctrine, and round-trip validation
13. `H -> L` provenance and lowering-rule validation
14. `SCIR-L` validation
15. sweep smoke over the frozen Tier `A` micro corpus plus regression comparison when a baseline artifact exists
16. admitted helper-free Wasm emission validation
17. execution-backed `SCIR-L -> backend` translation validation for admitted backend paths
18. Python reconstruction validation
19. benchmark manifest and Track `A` / `B` validation

## Validator stack

| Validator | Input | Output | Blocking |
| --- | --- | --- | --- |
| repository contract checker | repository files, schemas, examples, derived exports | console report | yes |
| importer conformance checker | fixed source subset plus checked-in bundle | `module_manifest`, `feature_tier_report`, `validation_report` | yes |
| `SCIR-H` validator | canonical `SCIR-H` | `validation_report` | yes |
| `SCIR-Hc` validator | derived `SCIR-Hc` plus canonical round-trip target and benchmark-claim scope where applicable | `validation_report` | yes |
| lowering-preservation validator | paired `SCIR-H` and `SCIR-L` artifacts | `preservation_report` | yes on active lowering paths |
| `SCIR-L` validator | structured lowered module | `validation_report` | yes |
| Wasm emitter checker | admitted `SCIR-L` subset plus bounded backend contract | WAT text plus `preservation_report` | yes on admitted helper-free Wasm cases |
| backend translation validator | paired `SCIR-L` artifact, backend artifact, and bounded execution contract | `translation_validation_report` | yes on admitted backend paths |
| reconstruction validator | canonical `SCIR-H` plus reconstructed Python | `reconstruction_report`, `preservation_report` | yes on active Python round trips |
| benchmark contract checker | benchmark doctrine plus executable Track `A` / `B` bundle | `benchmark_manifest`, `benchmark_result` validation | yes |

## Active report discipline

| Scenario | Required reports |
| --- | --- |
| importer change | `module_manifest`, `feature_tier_report`, `validation_report` |
| `SCIR-H` or `SCIR-Hc` semantic-path change | `validation_report` and checklist updates |
| `H -> L` lowering change | `validation_report` for `SCIR-L`, `preservation_report`, lowering-rule coverage |
| Python reconstruction change | `reconstruction_report`, `preservation_report` |
| Wasm-contract change | emitted WAT contract, `translation_validation_report`, path-qualified `preservation_report`, and backend docs |
| benchmark change | `benchmark_manifest`, `benchmark_result`, `comparison_summary`, `contamination_report`, `benchmark_report` |
| queue, decision, or open-question change | derived export regeneration |

Schemas live in `schemas/`.

## Blocking rules

A change must not merge when any of the following is true:

- `SCIR-H` claims a construct the parser does not accept,
- `SCIR-Hc` drifts from canonical `SCIR-H` under parse-format or semantic round-trip checks,
- `SCIR-Hc` becomes semantic authority, carries unexplained omission provenance, or enters a forbidden downstream path directly,
- `SCIR-L` introduces semantics without a validated `SCIR-H` origin and named lowering rule,
- an active `translation_validation_report` passes with an unsupported backend subset, ambiguous claim strength, or despite return drift, effect drift, capability drift, branch/state trace drift, or undeclared contract deviation,
- an active preservation report omits `path`, `profile`, `preservation_level`, `downgrades`, or `boundary_annotations`,
- active corpus preservation ceilings or per-stage expectations drift from observed behavior without explicit downgrade evidence,
- benchmark reports leak `SCIR-Hc` evidence across `claim_class` / `evidence_class` boundaries,
- Python reconstruction claims a stronger profile or preservation level than the executable proof loop supports,
- Rust importer evidence silently widens into active Rust reconstruction or benchmark claims,
- an admitted helper-free Wasm case stops emitting stable WAT or starts requiring helper imports or runtime shims,
- Wasm wording implies native or host parity,
- deferred TypeScript or Track `D` surfaces re-enter active validation without root-doc updates,
- example artifacts or derived exports drift from their normative sources.

## Acceptance criteria by layer

### `SCIR-H`

Canonical `SCIR-H` must reject:

- hidden control transfer,
- implicit effects or mutation,
- ambiguous name resolution,
- non-canonical formatting,
- legacy brace-delimited bootstrap syntax,
- constructs outside the active subset, including `iface`, `witness`, `match`, `select`, standalone `throw` syntax, `invoke`, and suite-form `unsafe` or `opaque` regions.

The importer-only `!throw` effect marker remains admitted only on the bounded Tier `B` `try/catch` slice and does not promote standalone `throw` support.

Canonical bootstrap validation is parse -> normalize -> format equality on the supported subset.

### `SCIR-Hc`

Derived `SCIR-Hc` must reject:

- compressed text that does not normalize under parse -> format equality,
- any executable transform attempt that lacks a valid report-scoped generation context,
- compressed text that lacks the derived-only authority marker,
- compressed nodes that omit canonical information without valid `compression_origin` provenance,
- `SCIR-Hc` artifacts that differ from deterministic `SCIR-H -> SCIR-Hc` derivation,
- lineage references that do not match the canonical `SCIR-H` semantic lineage id and normalized canonical hash,
- any claim or evaluated metric that lacks complete canonical `SCIR-H` evidence coverage,
- compressed text that fails to reconstruct canonical `SCIR-H`,
- any round-trip that changes semantic lineage or canonical `SCIR-H` formatting,
- any semantic-idempotence check where `normalize(scirh_to_scirh(scirh_to_scirhc(scirh))) != normalize(scirh)`,
- compression claims that contradict boundary metadata or normalization statistics.

### `SCIR-L`

Active `SCIR-L` must reject:

- ops outside the frozen subset,
- malformed block parameters or control edges,
- missing provenance origin,
- provenance origin that no longer maps back into the emitting `SCIR-H` module,
- missing lowering rule,
- invalid op-to-lowering-rule pairings,
- `field.addr` without an `SCIR-H` field-place basis,
- `opaque.call` without an explicit boundary basis,
- any L-only semantic obligation.

### Translation validation

Active translation validation has two bounded responsibilities:

- `H -> L` lowering-preservation validation for the executable Python proof loop and importer-bounded Rust evidence path
- execution-backed `SCIR-L -> backend` validation for admitted helper-free Wasm emission only

Execution-backed `SCIR-L -> backend` validation must now emit a report that makes all of the following explicit:

- backend kind
- target profile
- equivalence mode
- observable dimensions checked
- backend subset class
- execution oracle
- validation strength
- downgrade reason
- subset-admission result and reason
- unsupported features detected
- helper-free subset requirement
- contract assumptions
- explicit outcome class
- provenance-linked findings when mismatches occur

Lowering-preservation validation must fail or downgrade when:

- structured control is lost beyond the declared profile,
- opaque or unsafe boundaries stop being explicit,
- a Tier `A` case gains boundary annotations,
- a `P3` case stops reporting its boundary-only downgrade,
- a stage overclaims stronger preservation than its fixture ceiling or declared stage expectation,
- a stage weakens preservation without diagnostics, downgrade reasons, boundary annotations, or an explicit non-pass status,
- lowering provenance continuity breaks.

Backend translation validation must fail when:

- return values diverge,
- traps or exception outcomes diverge,
- termination kind diverges,
- required effects are missing or extra effects appear,
- undeclared capabilities are observed,
- control-flow branch outcomes collapse or diverge beyond the declared contract,
- state-write traces diverge under the declared equivalence mode,
- contract-bounded deviation is exercised without an explicit bounded contract,
- deterministic validation inputs are absent,
- helper-free Wasm subset admission is skipped,
- or helper-free Wasm execution is attempted after the subset classifier reports unsupported imports, helper trampolines, indirect calls, mutable globals, memory growth, reference types, unsupported instructions, or unsupported control constructs.

The default Wasm lane remains:

- profile `P`
- equivalence mode `contract_bounded`
- observable dimensions `returns`, `traps_or_exceptions`, `termination_kind`, `call_trace`, `branch_trace`, `state_write_trace`, `effect_trace`, and `capability_trace`
- explicit helper-free subset admission before any backend execution attempt

The experimental Python translation-validation lane is permitted only as an opt-in maintenance lane.
It must:

- reuse the same `translation_validation_report` schema,
- stay clearly marked experimental,
- keep case-qualified reconstruction profiles explicit,
- and remain outside the default repository validation gate.

### Wasm emission validation

Active Wasm emission validation applies only to the admitted helper-free local-slot subset.
It now also includes the bounded record-cell ABI for `fixture.rust_importer.a_struct_field_borrow_mut`.
That record-cell ABI must remain frozen to the fixed Rust slice unless a later recorded contract decision widens it.

It must fail when:

- emitted WAT introduces helper imports or runtime shims,
- the subset classifier reports helper trampolines, indirect calls, mutable globals, memory growth, reference types, unsupported instructions, or unsupported control constructs,
- a bounded local-slot case stops emitting path-qualified `l_to_wasm` evidence,
- `cmp` emission widens beyond the current less-than-zero bootstrap shape,
- `field.addr` emission widens beyond the fixed record-cell ABI,
- Python field-place or any additional record shape becomes Wasm-emittable without a new contract decision,
- field-place lowering is normalized into imported memory, hidden host layout, or non-shared-handle callers,
- direct-call emission widens beyond the fixed same-module scalar call shape.

Wasm validation must additionally fail when:

- a record field offset diverges from canonical field declaration order,
- a record shape includes non-`int` fields in the first post-scalar slice,
- a record handle crosses an imported, opaque, or otherwise non-shared ABI boundary,
- the emitted module relies on imported memory, hidden allocator state, or host object layout,
- execution-backed translation validation does not produce a passing `translation_validation_report`,
- preservation evidence omits the field-offset map, shared-handle caller contract, or candidate-specific downgrade reasons,
- or a non-candidate record, alias, or memory shape is emitted as if it were inside the bounded ABI.

No new Wasm surface may enter execution-backed validation unless all promotion criteria are satisfied together:

- subset classifier support lands for the new surface and fails closed when the surface is absent or malformed,
- the bounded execution oracle can observe and compare the new surface under an explicit equivalence mode,
- adversarial and mutation-based regression tests exist for the new observable dimensions and unsupported-surface rejections,
- the example `translation_validation_report` and any affected backend report examples are updated,
- and a decision-register entry plus validator-doctrine updates explicitly record the promotion.

### Admitted helper-free Wasm-emission modules

- `fixture.python_importer.a_basic_function`
- `fixture.python_importer.b_direct_call`
- `fixture.rust_importer.a_mut_local`
- `fixture.rust_importer.a_struct_field_borrow_mut`

### Reconstruction validation

Active reconstruction validation applies only to Python reconstruction from validated `SCIR-H`.

It must fail when:

- reconstructed Python does not compile,
- reconstructed Python fails the fixture behavior check,
- provenance completeness is overstated,
- a supported Tier `A` case gains boundary annotations,
- an opaque Python case loses its boundary annotation.

Rust reconstruction remains a deferred surface. It is not part of the active MVP gate.

### SCIR-Hc doctrine tests

The default gate must run `tests/test_scirhc_doctrine.py` and fail when the repository stops rejecting:

- SCIR-Hc generation without context,
- SCIR-Hc generation outside report context,
- invalid lineage hash or missing lineage coverage,
- non-deterministic `SCIR-H -> SCIR-Hc` derivation,
- round-trip equivalence failure,
- illegal direct `SCIR-Hc` pipeline usage,
- hidden semantic injection,
- causal metric leakage, metric-authority leakage, or benchmark-claim overreach.

## Operational command contract

`make validate` remains the top-level blocking validation command.

At minimum it must:

- verify required docs, specs, schemas, and scripts exist,
- parse all JSON artifacts,
- validate checked-in example artifacts against their schemas,
- validate `DECISION_REGISTER.md`, `OPEN_QUESTIONS.md`, and `EXECUTION_QUEUE.md` against their checked-in exports,
- validate active proof-loop corpus manifests, negative-fixture manifests, and sweep manifests,
- validate the Python importer fixture corpus,
- validate the Rust importer fixture corpus,
- validate seeded invalid canonical `SCIR-H` examples,
- validate seeded invalid derivative `SCIR-L` examples,
- validate canonical formatter round-trip, identity stability, and pretty-view noninterference,
- validate `SCIR-Hc` parse-format equality, doctrine checks, plus semantic round-trip to canonical `SCIR-H`,
- validate the active Python proof loop,
- run sweep smoke on the frozen Tier `A` micro corpus and compare against the latest successful baseline artifact when available,
- require `comparison_summary.json` and `contamination_report.json` for executable sweep smoke,
- validate the admitted helper-free Wasm emitter slice, its path-qualified `l_to_wasm` reports, and its execution-backed `translation_validation_report` outputs,
- validate the active Track `A` / `B` benchmark harness and its claim-bound report surfaces,
- reject TypeScript placeholder-corpus drift from the active validation baseline,
- enforce `NOT_ACTIVE.md` markers on deferred or archived surfaces that remain on disk.

Deferred surfaces may remain on disk, but they are not part of the default blocking gate unless `DEFERRED_COMPONENTS.md` promotes them back into scope.

## Optional deeper validation

`python scripts/run_repo_validation.py --require-rust` remains the optional compatibility entrypoint for environments that want an explicit usable Rust toolchain before running the importer-first Rust `H -> L` validation slice.
That optional slice validates Rust import, canonical `SCIR-H`, bounded derivative lowering, `SCIR-L`, helper-free Wasm emission for the admitted Rust local-mutation case, and path-qualified translation preservation only.
It does not activate Rust reconstruction, Rust benchmark gates, or broader backend claims.
It is not the default MVP gate.

`python scripts/run_repo_validation.py --include-track-c-pilot` remains the optional compatibility entrypoint for the first executable Track `C` pilot.
That optional slice validates the same repository, importer, lowering, reconstruction, and Track `A` / `B` surfaces as the default gate, then runs the bounded Python single-function repair pilot on the fixed proof-loop cases only.
It keeps `c_opaque_call` boundary-accounting-only, compares against direct source, typed-AST, and regularized-core baselines, and does not activate Track `C` as a default benchmark gate.

`python scripts/validate_translation.py --include-experimental-python` remains the optional maintenance lane for bounded Python execution-backed translation validation.
`python scripts/run_repo_validation.py --include-experimental-python-translation` may invoke that same lane explicitly.
Those commands must not change the default validation gate, the active `SCIR-H -> Python` reconstruction contract, or the Wasm-first backend posture.

`python scripts/benchmark_contract_dry_run.py --claim-run` remains the explicit claim-grade benchmark lane for Track `A` and Track `B`.
That lane must fail if baseline results are missing, corpus hash mismatches are detected, a reproducibility block is missing, contamination is detected, or none of the active claim-gate conditions hold.

## Evidence for done

A validation-sensitive task is not done unless:

- touched specs and docs agree,
- the relevant schemas are current,
- active example artifacts are schema-valid,
- invalid canonical `SCIR-H` fixtures still fail,
- derived exports remain synchronized,
- `make validate` passes.
