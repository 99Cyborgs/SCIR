# EXECUTION_QUEUE
Status: Informative

## Purpose

This file is the canonical human-readable execution queue for low-touch agent handoff.

It is derived from:

- `IMPLEMENTATION_PLAN.md` for phase ordering
- `plans/2026-04-01-mvp-narrowing-and-contract-hardening.md` for the active near-term work surface
- `OPEN_QUESTIONS.md` for unresolved blocker boundaries
- `STATUS.md` for portfolio context only, not task ordering

## Queue metadata

- Queue snapshot: `2026-04-02T12:10:00-05:00`
- Active milestone: `MVP Kernel Hardening`
- Autonomy mode: `high`
- Escalation threshold: `doctrine conflict; missing source authority; sequencing violation`

## Derivation rules

- prefer the active near-term plan before the next implementation phase
- do not violate `IMPLEMENTATION_PLAN.md` sequencing
- do not silently resolve open questions; blocked items must cite exact `OQ-*` IDs
- importer-only items do not imply new lowering, reconstruction, or benchmark scope unless downstream doctrine widens explicitly
- any queued task that touches 3 or more files, or touches `specs/`, `schemas/`, or validator behavior, requires a matching plan update before implementation

## Queue items

### Q-00-003 - Land a minimal emitter-backed Wasm slice over the frozen `SCIR-L` subset

- Queue ID: `Q-00-003`
- Title: `Land a minimal emitter-backed Wasm slice over the frozen SCIR-L subset`
- Source milestone or phase: `MVP Kernel Hardening`
- Status: `done`
- Why now: `The backend boundary is now explicit, but Wasm remains contract-first rather than emitter-backed, which leaves the MVP backend surface weaker than the narrowed roadmap intends.`
- Prerequisites: `Q-00-002`
- Work instructions: `Implement the smallest credible emitter-backed Wasm surface for the already-frozen SCIR-L subset, keep runtime helper assumptions explicit, and do not widen source-language or parity claims.`
- Touched surfaces: `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `scripts/`; `reports/examples/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `helper-free local-slot emission would require hidden runtime semantics or broader derivative op coverage`
- Done evidence: `the Wasm backend is no longer contract-only for the admitted subset`; `helper assumptions are explicit`; `preservation reporting stays path-qualified`

### Q-01-001 - Lock the Phase 1 `SCIR-H` kernel around canonical subset and identity

- Queue ID: `Q-01-001`
- Title: `Lock the Phase 1 SCIR-H kernel around canonical subset and identity`
- Source milestone or phase: `SCIR-H kernel`
- Status: `done`
- Why now: `Phase 0 boundary hardening and the first helper-free Wasm slice are landed, so the next credible step is to keep the canonical SCIR-H subset and identity rules fail-fast coherent before widening importer or backend work.`
- Prerequisites: `Q-00-003`
- Work instructions: `Keep the canonical SCIR-H subset, canonical/view split, and persistent identity rules aligned between the spec, bootstrap model, and completeness checklist without widening the executable subset.`
- Touched surfaces: `specs/scir_h_spec.md`; `scripts/scir_h_bootstrap_model.py`; `IDENTITY_MODEL.md`; `SPEC_COMPLETENESS_CHECKLIST.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `identity or canonical storage changes would require new SCIR-L semantics or phase-order changes`
- Done evidence: `canonical subset and executable parser stay aligned`; `canonical/view noninterference stays checked`; `persistent lineage and content hash rules remain coherent`

### Q-02-001 - Keep the Python proof loop locked to the canonical `SCIR-H` kernel

- Queue ID: `Q-02-001`
- Title: `Keep the Python proof loop locked to the canonical SCIR-H kernel`
- Source milestone or phase: `Python proof loop`
- Status: `done`
- Why now: `The Phase 1 SCIR-H kernel is now explicit and fail-fast, so the next credible step is to keep the Python importer, derivative lowering, and SCIR-H-driven reconstruction aligned to that fixed kernel before widening any other frontend or backend surface.`
- Prerequisites: `Q-01-001`
- Work instructions: `Keep the Python importer as the decisive proof loop, keep SCIR-L derivative to the fixed canonical SCIR-H kernel, and keep Python reconstruction driven by validated SCIR-H rather than widening importer-only follow-on cases.`
- Touched surfaces: `frontend/python/IMPORT_SCOPE.md`; `scripts/scir_python_bootstrap.py`; `scripts/scir_bootstrap_pipeline.py`; `docs/reconstruction_policy.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/python_importer_conformance.py --mode validate-fixtures`; `python scripts/scir_bootstrap_pipeline.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `keeping the Python proof loop credible would require widening the locked SCIR-H kernel, activating deferred second-language execution claims, or adding new runtime semantics`
- Done evidence: `the Python importer remains aligned to the canonical SCIR-H kernel`; `SCIR-L lowering stays derivative and subset-bound`; `Python reconstruction remains SCIR-H-driven and preservation reporting stays coherent`

### Q-02-002 - Promote the bounded `b_direct_call` case into the active Python proof loop

- Queue ID: `Q-02-002`
- Title: `Promote the bounded b_direct_call case into the active Python proof loop`
- Source milestone or phase: `Python proof loop`
- Status: `done`
- Why now: `The Python proof loop is locked to the canonical SCIR-H kernel, but the bounded direct local call shape still sits in importer-only evidence even though it is the next smallest credible end-to-end executable widening.`
- Prerequisites: `Q-02-001`
- Work instructions: `Promote only the fixed b_direct_call shape into the active Python proof loop, keep lowering and reconstruction subset-bound, widen benchmark doctrine only as required by the executable case contract, and do not imply helper-free Wasm support.`
- Touched surfaces: `frontend/python/IMPORT_SCOPE.md`; `docs/reconstruction_policy.md`; `scripts/scir_python_bootstrap.py`; `scripts/scir_bootstrap_pipeline.py`; `scripts/python_importer_conformance.py`; `BENCHMARK_STRATEGY.md`; `benchmarks/`; `reports/examples/`
- Validation: `python scripts/python_importer_conformance.py --mode validate-fixtures`; `python scripts/scir_bootstrap_pipeline.py --mode validate`; `python scripts/scir_bootstrap_pipeline.py --mode test`; `python scripts/benchmark_contract_dry_run.py`; `python scripts/run_repo_validation.py --include-track-c-pilot`
- Escalate only if: `promoting b_direct_call would require widening loops, class-field shapes, try/catch, Rust execution claims, or helper-free Wasm emission`
- Done evidence: `b_direct_call is now part of the executable Python proof loop`; `reconstruction and benchmark doctrine stay aligned to the widened bounded case set`; `non-emittable Wasm boundaries remain explicit`

### Q-02-003 - Tighten validator and completeness coverage around the widened Python proof loop

- Queue ID: `Q-02-003`
- Title: `Tighten validator and completeness coverage around the widened Python proof loop`
- Source milestone or phase: `Python proof loop`
- Status: `done`
- Why now: `The bounded direct-call widening is landed, so the next credible step is to harden the validator, completeness checklist, and active-path doctrine against future drift before returning to backend widening.`
- Prerequisites: `Q-02-002`
- Work instructions: `Strengthen proof-loop drift checks, completeness markers, and negative validation around the widened Python executable set, keep importer-only follow-on cases explicit, and do not widen Wasm or Rust execution scope.`
- Touched surfaces: `SPEC_COMPLETENESS_CHECKLIST.md`; `scripts/validate_repo_contracts.py`; `scripts/scir_h_bootstrap_model.py`; `frontend/python/IMPORT_SCOPE.md`; `docs/reconstruction_policy.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/validate_repo_contracts.py --mode test`; `python scripts/run_repo_validation.py`
- Escalate only if: `hardening validator or completeness coverage would require new SCIR-H semantics, broader executable Python support, or backend-scope widening`
- Done evidence: `validator and completeness drift checks cover the widened Python proof loop`; `importer-only boundaries remain explicit`; `the next backend-facing slice can proceed from a fail-fast proof-loop contract`

### Q-03-001 - Keep Rust importer evidence aligned to the canonical `SCIR-H` kernel

- Queue ID: `Q-03-001`
- Title: `Keep Rust importer evidence aligned to the canonical SCIR-H kernel`
- Source milestone or phase: `Rust safe-subset importer`
- Status: `done`
- Why now: `The Python proof loop is now locked to the canonical SCIR-H kernel, so the next credible step is to keep the Rust importer evidence aligned to that same kernel without widening Rust into an active reconstruction, backend, or benchmark claim.`
- Prerequisites: `Q-02-001`
- Work instructions: `Keep the Rust importer subset-bound, keep ownership and unsafe boundaries explicit, and keep Rust outputs aligned to the canonical SCIR-H contract without promoting Rust into an active proof loop beyond the importer-first evidence path.`
- Touched surfaces: `frontend/rust/IMPORT_SCOPE.md`; `scripts/scir_rust_bootstrap.py`; `scripts/rust_importer_conformance.py`; `scripts/scir_bootstrap_pipeline.py`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/rust_importer_conformance.py --mode validate-fixtures`; `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`; `python scripts/run_repo_validation.py --require-rust`
- Escalate only if: `keeping Rust importer evidence aligned would require widening the locked SCIR-H kernel, activating Rust reconstruction or benchmark claims, or weakening explicit unsafe boundary handling`
- Done evidence: `the Rust importer remains aligned to the canonical SCIR-H kernel`; `ownership and unsafe boundary handling stay explicit`; `Rust evidence does not widen into active reconstruction or benchmark claims`

### Q-04-001 - Keep the Wasm reference backend MVP aligned to the bounded derivative subset

- Queue ID: `Q-04-001`
- Title: `Keep the Wasm reference backend MVP aligned to the bounded derivative subset`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The Python proof loop and Rust importer evidence are now locked to the canonical SCIR-H kernel, so the next credible step is to keep the helper-free Wasm backend, preservation reporting, and non-emittable boundaries aligned to the same bounded derivative subset without widening backend claims.`
- Prerequisites: `Q-03-001`
- Work instructions: `Keep the helper-free Wasm backend explicit, keep l_to_wasm preservation reporting path-qualified, and keep field, call, async, and opaque lowering non-emittable unless the root backend contract is widened deliberately.`
- Touched surfaces: `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `scripts/scir_bootstrap_pipeline.py`; `VALIDATION_STRATEGY.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/scir_bootstrap_pipeline.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `strengthening the Wasm MVP would require helper imports, runtime shims, new SCIR-L semantics, or wording that implies native or host parity`
- Done evidence: `the helper-free Wasm subset remains explicit and bounded`; `l_to_wasm reporting stays path-qualified`; `non-emittable derivative shapes remain explicit`

### Q-04-002 - Land bounded helper-free Wasm emission for the fixed direct local call shape

- Queue ID: `Q-04-002`
- Title: `Land bounded helper-free Wasm emission for the fixed direct local call shape`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The widened Python proof loop and its generated-artifact sync path are now fail-fast coherent, so the next substantive backend step is the smallest useful Wasm widening: the fixed direct local call shape that still remains non-emittable.`
- Prerequisites: `Q-02-003`; `Q-04-001`
- Work instructions: `Implement the smallest helper-free Wasm emission slice for the bounded direct local call case, keep lowering-rule and preservation reporting explicit, and do not imply support for broader call graphs, async, opaque calls, or runtime shims.`
- Touched surfaces: `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `scripts/wasm_backend_metadata.py`; `scripts/scir_bootstrap_pipeline.py`; `reports/examples/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/scir_bootstrap_pipeline.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `bounded direct-call Wasm emission would require helper imports, hidden runtime semantics, broader call support, or any wording that implies native or host parity`
- Done evidence: `the fixed direct local call shape becomes explicitly Wasm-emittable or explicitly blocked with executable evidence`; `helper-free Wasm boundaries remain subset-bound`; `preservation reporting stays path-qualified`

### Q-04-003 - Assess whether field-place Wasm emission can stay helper-free without hidden layout semantics

- Queue ID: `Q-04-003`
- Title: `Assess whether field-place Wasm emission can stay helper-free without hidden layout semantics`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The helper-free Wasm backend now admits the bounded direct local call shape, so the next substantive backend question is whether any field-place lowering can be emitted without introducing hidden record layout semantics or runtime helpers.`
- Prerequisites: `Q-04-002`
- Work instructions: `Evaluate whether the smallest field-place lowering slice can be admitted helper-free, keep record layout and provenance explicit, and do not widen into implicit object layout, imports, or host-runtime assumptions.`
- Touched surfaces: `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `scripts/wasm_backend_metadata.py`; `scripts/scir_bootstrap_pipeline.py`; `VALIDATION_STRATEGY.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/scir_bootstrap_pipeline.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `field-place Wasm emission would require hidden record layout semantics, helper imports, broader memory models, or wording that implies native or host parity`
- Done evidence: `field-place Wasm emission is either explicitly admitted for a bounded helper-free slice or remains concretely blocked`; `record-layout assumptions remain explicit`; `helper-free Wasm boundaries remain subset-bound`

### Q-04-004 - Decide whether any broader Wasm backend work requires an explicit post-scalar ABI contract

- Queue ID: `Q-04-004`
- Title: `Decide whether any broader Wasm backend work requires an explicit post-scalar ABI contract`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The field-place assessment now shows that helper-free Wasm cannot preserve caller-visible borrowed record mutation without an explicit record ABI/layout contract, so the next credible backend question is whether Phase 4 should freeze at the scalar helper-free subset or deliberately open a broader backend ABI decision.`
- Prerequisites: `Q-04-003`
- Work instructions: `Assess whether any next Wasm widening beyond the current scalar helper-free subset would require a declared record or host ABI contract, keep the current backend subset unchanged unless that contract is adopted explicitly, and do not imply native or host parity.`
- Touched surfaces: `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `ARCHITECTURE.md`; `IMPLEMENTATION_PLAN.md`; `DECISION_REGISTER.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `answering the next Wasm-widening question would require phase-order changes, a new backend memory/ABI contract, or wording that implies native or host parity`
- Done evidence: `the scalar-only helper-free Wasm boundary is either frozen explicitly or a deliberate broader ABI decision is recorded`; `field-place and other non-scalar backend shapes remain non-emittable until that decision exists`; `Phase 4 sequencing remains explicit`

### Q-04-005 - Decide whether SCIR should adopt any explicit post-scalar Wasm ABI/storage contract

- Queue ID: `Q-04-005`
- Title: `Decide whether SCIR should adopt any explicit post-scalar Wasm ABI/storage contract`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The scalar helper-free Wasm subset is now explicitly frozen, and any further backend widening would require a deliberate decision about record storage, caller-visible mutation, or host-facing ABI semantics rather than another incremental emitter slice.`
- Prerequisites: `Q-04-004`
- Work instructions: `Resolve whether SCIR should adopt a broader Wasm ABI/storage contract for non-scalar shapes, keep the current helper-free scalar subset unchanged until that decision is made, and do not imply native or host parity.`
- Touched surfaces: `ARCHITECTURE.md`; `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `VALIDATION_STRATEGY.md`; `OPEN_QUESTIONS.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Blocking open questions: `none`
- Escalate only if: `answering the Wasm ABI question would require changing phase order, broadening backend semantics beyond the MVP boundary, or introducing host-runtime parity claims`
- Done evidence: `the repository either records an explicit post-scalar Wasm ABI/storage contract or freezes Phase 4 at the helper-free scalar subset with the blocker preserved`; `field-place and other non-scalar shapes stay explicit during the decision`; `the queue no longer implies silent backend widening`

### Q-04-006 - Define the minimal post-scalar Wasm ABI/storage contract for record field mutation

- Queue ID: `Q-04-006`
- Title: `Define the minimal post-scalar Wasm ABI/storage contract for record field mutation`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The repository has now chosen to open explicit post-scalar Wasm design work, so the next credible slice is to specify the narrowest contract that can preserve caller-visible record field mutation without broadening into general host/runtime or object-layout claims.`
- Prerequisites: `Q-04-005`
- Work instructions: `Specify the smallest explicit Wasm ABI/storage contract that could carry the existing record field mutation semantics, keep it narrower than general object layout or host ABI support, and do not claim executable support until the contract, validator implications, and backend doctrine agree.`
- Touched surfaces: `ARCHITECTURE.md`; `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `VALIDATION_STRATEGY.md`; `OPEN_QUESTIONS.md`; `DECISION_REGISTER.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Blocking open questions: `none`
- Escalate only if: `the minimal ABI contract cannot be defined without broad host/runtime commitments, new SCIR-L semantics, or phase-order changes`
- Done evidence: `the repository names one minimal candidate post-scalar Wasm ABI/storage contract`; `the current scalar helper-free subset remains unchanged until later implementation work`; `the next backend slice can evaluate that contract instead of reopening whether-design work`

### Q-04-007 - Define validator and preservation obligations for the candidate Wasm record-cell ABI

- Queue ID: `Q-04-007`
- Title: `Define validator and preservation obligations for the candidate Wasm record-cell ABI`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The repository now names one candidate post-scalar Wasm contract, so the next credible slice is to define exactly what validation, downgrade, and preservation obligations would be required before that candidate could become executable.`
- Prerequisites: `Q-04-006`
- Work instructions: `Specify the validator invariants, lowering constraints, and preservation-report obligations for the candidate record-cell ABI, keep the current scalar helper-free subset unchanged, and do not claim executable support until those obligations are agreed explicitly.`
- Touched surfaces: `VALIDATION_STRATEGY.md`; `LOWERING_CONTRACT.md`; `docs/preservation_contract.md`; `DECISION_REGISTER.md`; `OPEN_QUESTIONS.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Blocking open questions: `none`
- Escalate only if: `the candidate contract cannot be bounded without new SCIR-L semantics, broader host/runtime commitments, or a higher-level scope change`
- Done evidence: `the candidate Wasm record-cell ABI has explicit validator and preservation obligations`; `the current helper-free scalar subset remains the only executable backend surface`; `the following slice can decide whether bounded implementation is credible`

### Q-04-008 - Assess whether bounded implementation of the candidate Wasm record-cell ABI is credible

- Queue ID: `Q-04-008`
- Title: `Assess whether bounded implementation of the candidate Wasm record-cell ABI is credible`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The repository now names both a candidate record-cell ABI and the validator/preservation obligations it would carry, so the next credible slice is to decide whether a bounded implementation path exists without new SCIR-L semantics or broader host/runtime commitments.`
- Prerequisites: `Q-04-007`
- Work instructions: `Assess whether the existing lowering and backend surfaces can implement the candidate record-cell ABI in one bounded slice, keep the current scalar helper-free subset unchanged unless that path is credible, and do not imply broader host/runtime or parity claims.`
- Touched surfaces: `scripts/scir_bootstrap_pipeline.py`; `scripts/wasm_backend_metadata.py`; `backends/wasm/README.md`; `VALIDATION_STRATEGY.md`; `DECISION_REGISTER.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/scir_bootstrap_pipeline.py --mode validate`; `python scripts/run_repo_validation.py`
- Blocking open questions: `none`
- Escalate only if: `bounded implementation would require new SCIR-L semantics, imported memory or host/runtime commitments, or a broader phase-order change`
- Done evidence: `the repository now shows a bounded implementation path for the record-cell ABI without new SCIR-L semantics`; `the current scalar helper-free subset remains explicit alongside the bounded record-cell path`; `the next Wasm step is driven by implementation evidence rather than design ambiguity`

### Q-04-009 - Implement the bounded record-cell Wasm slice for `a_struct_field_borrow_mut`

- Queue ID: `Q-04-009`
- Title: `Implement the bounded record-cell Wasm slice for a_struct_field_borrow_mut`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The repository now has both a credible bounded implementation path and explicit validator plus preservation obligations for the record-cell ABI, so the next credible backend step is to land the smallest executable post-scalar Wasm slice instead of leaving it design-only.`
- Prerequisites: `Q-04-008`
- Work instructions: `Implement the exact helper-free record-cell ABI slice for fixture.rust_importer.a_struct_field_borrow_mut, keep preservation downgrades and shared-handle evidence explicit, and do not widen into Python field places, broader record layouts, imported memory, or host-runtime claims.`
- Touched surfaces: `frontend/rust/IMPORT_SCOPE.md`; `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `VALIDATION_STRATEGY.md`; `docs/preservation_contract.md`; `scripts/scir_rust_bootstrap.py`; `scripts/wasm_backend_metadata.py`; `scripts/scir_bootstrap_pipeline.py`; `scripts/validate_repo_contracts.py`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/scir_bootstrap_pipeline.py --mode validate`; `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`; `python scripts/run_repo_validation.py --require-rust`
- Blocking open questions: `none`
- Escalate only if: `the bounded record-cell slice would require new SCIR-L semantics, imported memory conventions beyond the declared ABI, or wording that implies broader Wasm parity`
- Done evidence: `fixture.rust_importer.a_struct_field_borrow_mut now emits stable bounded Wasm`; `the l_to_wasm preservation report records record-cell-specific downgrades and evidence`; `the active Wasm-emittable Rust subset and backend doctrine stay aligned`

### Q-04-010 - Decide whether the active Wasm record-cell ABI should widen beyond the fixed Rust slice

- Queue ID: `Q-04-010`
- Title: `Decide whether the active Wasm record-cell ABI should widen beyond the fixed Rust slice`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `done`
- Why now: `The smallest executable post-scalar Wasm slice is now active, so the next credible backend question is whether that ABI should remain frozen at the fixed Rust one-field shape or widen toward broader record or Python field-place support.`
- Prerequisites: `Q-04-009`
- Work instructions: `Decide whether the current record-cell ABI should stay frozen to the fixed Rust Counter slice or widen to any additional record-mutation shapes, keep any broader layout or host commitments explicit, and do not imply general post-scalar Wasm parity.`
- Touched surfaces: `ARCHITECTURE.md`; `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `VALIDATION_STRATEGY.md`; `OPEN_QUESTIONS.md`; `DECISION_REGISTER.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py --require-rust`
- Blocking open questions: `none`
- Escalate only if: `widening the record-cell ABI would require new SCIR-L semantics, broader imported-memory or host-runtime commitments, or a phase-order change`
- Done evidence: `the fixed Rust record-cell slice is now explicitly frozen`; `the backend no longer implies incremental widening of the record-cell ABI`; `future post-scalar widening requires a new recorded contract decision`

### Q-04-011 - Decide whether to reopen Wasm widening beyond the frozen Rust record-cell slice

- Queue ID: `Q-04-011`
- Title: `Decide whether to reopen Wasm widening beyond the frozen Rust record-cell slice`
- Source milestone or phase: `Wasm reference backend MVP`
- Status: `blocked`
- Why now: `The active post-scalar Wasm boundary is now explicit and frozen, so any further backend widening should happen only if a later review chooses to reopen that decision deliberately rather than through queue drift.`
- Prerequisites: `Q-04-010`
- Work instructions: `Reassess whether any new evidence justifies reopening Wasm widening beyond the fixed Rust record-cell slice, keep broader layout and host commitments explicit, and do not imply general post-scalar Wasm parity unless a new contract decision is recorded first.`
- Touched surfaces: `ARCHITECTURE.md`; `backends/wasm/README.md`; `LOWERING_CONTRACT.md`; `VALIDATION_STRATEGY.md`; `DECISION_REGISTER.md`; `OPEN_QUESTIONS.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py --require-rust`
- Blocking open questions: `none`
- Escalate only if: `reopening Wasm widening would require new SCIR-L semantics, broader imported-memory or host-runtime commitments, or a phase-order change`
- Done evidence: `the repository either records a new widening decision explicitly or keeps the frozen record-cell ABI unchanged`; `no incremental backend drift occurs`; `the Wasm scope boundary remains deliberate`

### Q-05-001 - Keep the benchmark falsification loop aligned to the fixed Python proof loop

- Queue ID: `Q-05-001`
- Title: `Keep the benchmark falsification loop aligned to the fixed Python proof loop`
- Source milestone or phase: `Benchmark falsification loop`
- Status: `done`
- Why now: `The Wasm reference backend MVP is now locked to the bounded derivative subset, so the next credible step is to keep Track A and Track B benchmark doctrine executable against the fixed Python proof loop without silently widening benchmark surfaces.`
- Prerequisites: `Q-04-001`
- Work instructions: `Keep benchmark manifests, baselines, gates, and dry-run validation tied to the fixed Python proof loop, keep Track C conditional, and do not reactivate Track D or second-language benchmark claims.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `scripts/benchmark_contract_dry_run.py`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py`; `python scripts/run_repo_validation.py`
- Escalate only if: `keeping Track A and Track B executable would require reactivating Track D, repository-scale issue repair, or second-language execution evidence before the Python proof loop doctrine widens`
- Done evidence: `Track A and Track B remain executable and bounded`; `benchmark baselines and kill gates remain explicit`; `Track C remains conditional and Track D remains deferred`

### Q-06-001 - Prepare a minimal conditional Track `C` pilot without widening the default gate

- Queue ID: `Q-06-001`
- Title: `Prepare a minimal conditional Track C pilot without widening the default gate`
- Source milestone or phase: `Optional Track C pilot`
- Status: `done`
- Why now: `Track A and Track B are now locked to the fixed Python proof loop, so the next benchmark-facing step is a minimal Track C pilot only if it can stay conditional, baseline-heavy, and outside the default blocking gate.`
- Prerequisites: `Q-05-001`
- Work instructions: `Design the smallest credible Track C pilot over controlled repair or editing tasks, keep baselines and contamination controls explicit, and do not activate Track C in the default benchmark gate unless earlier proof-loop stability remains intact.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py`; `python scripts/run_repo_validation.py`
- Escalate only if: `a credible Track C pilot would require broader corpus claims, relaxed baselines, or default-gate activation before the fixed Python proof loop remains stable`
- Done evidence: `Track C remains explicitly conditional`; `pilot baselines and contamination controls remain strong`; `the default benchmark gate remains limited to Track A and Track B`

### Q-06-002 - Assess whether a non-default executable Track `C` pilot is justified without widening the default gate

- Queue ID: `Q-06-002`
- Title: `Assess whether a non-default executable Track C pilot is justified without widening the default gate`
- Source milestone or phase: `Optional Track C pilot`
- Status: `done`
- Why now: `The first Track C pilot doctrine is now fixed as a conditional Python repair sample, so the next credible question is whether that same bounded task family merits any non-default executable pilot at all without weakening the active Track A and Track B gate.`
- Prerequisites: `Q-06-001`
- Work instructions: `Evaluate whether a non-default executable Track C pilot can be justified over the same fixed Python single-function repair cases, keep strong baselines and contamination controls explicit, and do not widen the default benchmark bundle or claim broader repair coverage.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py`; `python scripts/run_repo_validation.py`
- Escalate only if: `a non-default Track C pilot would require a broader corpus, weaker baselines, or any change that promotes Track C into the default executable benchmark gate`
- Done evidence: `any Track C executable pilot remains explicitly non-default`; `the fixed Python proof-loop repair family stays bounded`; `Track A and Track B remain the only active executable benchmark tracks`

### Q-06-003 - Decide whether to keep, harden, or retire the non-default Track `C` pilot without promoting it into the default gate

- Queue ID: `Q-06-003`
- Title: `Decide whether to keep, harden, or retire the non-default Track C pilot without promoting it into the default gate`
- Source milestone or phase: `Optional Track C pilot`
- Status: `done`
- Why now: `The first executable Track C pilot is now available as an explicit opt-in slice, so the next credible question is whether that bounded pilot should stay as-is, gain stronger evidence collection, or be retired before any broader benchmark claim is considered.`
- Prerequisites: `Q-06-002`
- Work instructions: `Assess the bounded opt-in Track C pilot using the fixed Python repair cases, keep strong baselines and contamination controls explicit, and decide whether the pilot should be retained, tightened, or retired without promoting it into the default executable gate.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `reports/examples/`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`; `python scripts/run_repo_validation.py --include-track-c-pilot`
- Escalate only if: `keeping the opt-in pilot would require a broader corpus, weaker baselines, or any change that turns Track C into a default executable benchmark gate`
- Done evidence: `the Track C pilot disposition is explicit`; `the fixed Python repair family remains bounded`; `Track A and Track B remain the only default executable benchmark tracks`

### Q-06-004 - Lock explicit retention and retirement criteria for the retained non-default Track `C` pilot

- Queue ID: `Q-06-004`
- Title: `Lock explicit retention and retirement criteria for the retained non-default Track C pilot`
- Source milestone or phase: `Optional Track C pilot`
- Status: `done`
- Why now: `The current Track C pilot has now been retained as a bounded diagnostic slice, so the next credible step is to lock the exact retention and retirement criteria around that pilot before any later review reopens the choice.`
- Prerequisites: `Q-06-003`
- Work instructions: `Codify the exact evidence thresholds and retirement triggers for the retained opt-in Track C pilot, keep the fixed Python repair corpus and strong baselines explicit, and do not promote Track C into the default executable gate.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `scripts/benchmark_contract_metadata.py`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`; `python scripts/run_repo_validation.py --include-track-c-pilot`
- Escalate only if: `retaining the pilot would require a broader corpus, weaker baselines, or any change that turns Track C into a default executable benchmark gate`
- Done evidence: `retention and retirement criteria are explicit`; `the retained Track C pilot stays bounded`; `Track A and Track B remain the only default executable benchmark tracks`

### Q-06-005 - Keep the retained non-default Track `C` pilot’s sample evidence and lock criteria synchronized

- Queue ID: `Q-06-005`
- Title: `Keep the retained non-default Track C pilot's sample evidence and lock criteria synchronized`
- Source milestone or phase: `Optional Track C pilot`
- Status: `done`
- Why now: `The retained Track C pilot now has explicit keep and retire conditions, so the next credible step is to keep the checked-in sample evidence and those lock criteria synchronized as the optional pilot evolves.`
- Prerequisites: `Q-06-004`
- Work instructions: `Keep the retained Track C sample artifacts, lock criteria, and opt-in runner outputs synchronized, and do not weaken any retirement trigger or promote Track C into the default executable gate.`
- Touched surfaces: `reports/examples/`; `BENCHMARK_STRATEGY.md`; `benchmarks/`; `scripts/benchmark_contract_dry_run.py`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`; `python scripts/run_repo_validation.py --include-track-c-pilot`
- Escalate only if: `keeping the sample evidence synchronized would require a broader corpus, weaker criteria, or any change that turns Track C into a default executable benchmark gate`
- Done evidence: `sample evidence stays synchronized with retained-pilot criteria`; `retirement triggers remain explicit`; `Track A and Track B remain the only default executable benchmark tracks`

### Q-06-006 - Require an explicit re-decision before the retained non-default Track `C` sample bundle changes posture

- Queue ID: `Q-06-006`
- Title: `Require an explicit re-decision before the retained non-default Track C sample bundle changes posture`
- Source milestone or phase: `Optional Track C pilot`
- Status: `done`
- Why now: `The retained Track C sample bundle is now synchronized to the current opt-in pilot and its keep/retire criteria, so the next credible step is to require explicit governance before any later sample refresh changes that retained posture.`
- Prerequisites: `Q-06-005`
- Work instructions: `Codify which Track C sample-bundle changes require a new decision or queue update, keep the non-default pilot surface bounded, and do not promote Track C into the default executable benchmark gate.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `DECISION_REGISTER.md`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`; `python scripts/run_repo_validation.py --include-track-c-pilot`
- Escalate only if: `requiring explicit sample-refresh re-decision would need broader corpus, weaker criteria, or any change that turns Track C into a default executable benchmark gate`
- Done evidence: `sample-refresh governance boundaries are explicit`; `retained Track C sample evidence remains bounded and synchronized`; `Track A and Track B remain the only default executable benchmark tracks`

### Q-06-007 - Distinguish editorial Track `C` sample refreshes from governance-triggering posture changes

- Queue ID: `Q-06-007`
- Title: `Distinguish editorial Track C sample refreshes from governance-triggering posture changes`
- Source milestone or phase: `Optional Track C pilot`
- Status: `done`
- Why now: `The retained Track C sample bundle now requires explicit governance before posture changes, so the next credible step is to distinguish which future sample refreshes are editorial-only and which ones must reopen Track C governance.`
- Prerequisites: `Q-06-006`
- Work instructions: `Codify the narrow set of Track C sample refreshes that remain editorial-only, keep posture-changing refreshes governance-gated, and do not promote Track C into the default executable benchmark gate.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`; `python scripts/run_repo_validation.py --include-track-c-pilot`
- Escalate only if: `distinguishing editorial sample refreshes would need broader corpus, weaker criteria, or any change that turns Track C into a default executable benchmark gate`
- Done evidence: `editorial-only versus governance-triggering Track C sample refresh boundaries are explicit`; `retained Track C sample evidence remains bounded and synchronized`; `Track A and Track B remain the only default executable benchmark tracks`

### Q-06-008 - Require explicit regeneration provenance for any non-editorial Track `C` sample refresh

- Queue ID: `Q-06-008`
- Title: `Require explicit regeneration provenance for any non-editorial Track C sample refresh`
- Source milestone or phase: `Optional Track C pilot`
- Status: `done`
- Why now: `The editorial-only Track C sample refresh boundary is now explicit, so the next credible step is to require a narrow provenance path for any later non-editorial refresh that still remains within the retained non-default pilot.`
- Prerequisites: `Q-06-007`
- Work instructions: `Codify how any non-editorial Track C sample refresh must cite regeneration provenance from the opt-in runner, keep posture-changing refreshes governance-gated, and do not promote Track C into the default executable benchmark gate.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `reports/README.md`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`; `python scripts/run_repo_validation.py --include-track-c-pilot`
- Escalate only if: `requiring sample-refresh provenance would need broader corpus, weaker criteria, or any change that turns Track C into a default executable benchmark gate`
- Done evidence: `non-editorial Track C sample refresh provenance requirements are explicit`; `editorial-only refreshes remain narrow`; `Track A and Track B remain the only default executable benchmark tracks`

### Q-06-009 - Lock a minimal provenance-note format for non-editorial Track `C` sample refreshes

- Queue ID: `Q-06-009`
- Title: `Lock a minimal provenance-note format for non-editorial Track C sample refreshes`
- Source milestone or phase: `Optional Track C pilot`
- Status: `ready`
- Why now: `The required Track C regeneration provenance fields are now explicit, so the next credible step is to lock the minimal note format for any future non-editorial refresh that still remains within the retained non-default pilot.`
- Prerequisites: `Q-06-008`
- Work instructions: `Codify the minimal provenance-note shape for any non-editorial Track C sample refresh, keep exact opt-in commands and regenerated hash/run identifiers explicit, and do not promote Track C into the default executable benchmark gate.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `reports/README.md`; `plans/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`; `python scripts/run_repo_validation.py --include-track-c-pilot`
- Escalate only if: `locking a provenance-note format would need broader corpus, weaker criteria, or any change that turns Track C into a default executable benchmark gate`
- Done evidence: `non-editorial Track C provenance-note format is explicit`; `runner-derived provenance remains mandatory`; `Track A and Track B remain the only default executable benchmark tracks`

### Q-00-002 - Keep Track `A` and Track `B` locked to the fixed Python proof loop

- Queue ID: `Q-00-002`
- Title: `Keep Track A and Track B locked to the fixed Python proof loop`
- Source milestone or phase: `MVP Kernel Hardening`
- Status: `done`
- Why now: `The benchmark harness is part of the MVP gate, so it has to remain tied to the fixed Python proof loop instead of drifting back toward deferred runtime or second-language claims.`
- Prerequisites: `Q-00-001`
- Work instructions: `Keep benchmark manifests, gates, and baselines limited to the fixed Python proof loop, maintain direct-source and typed-AST baselines, and do not reactivate Track D or broad Track C claims.`
- Touched surfaces: `BENCHMARK_STRATEGY.md`; `benchmarks/`; `scripts/benchmark_contract_dry_run.py`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/benchmark_contract_dry_run.py`; `make benchmark`
- Escalate only if: `a requested benchmark change requires Track D, repository-scale issue repair, or second-language execution evidence before the Python proof loop is stable`
- Done evidence: `Track A and Track B remain reproducible and bounded`; `Track C remains conditional`; `Track D remains deferred`

### Q-00-001 - Maintain spec completeness and identity-hardening gates

- Queue ID: `Q-00-001`
- Title: `Maintain spec completeness and identity-hardening gates`
- Source milestone or phase: `MVP Kernel Hardening`
- Status: `done`
- Why now: `The narrowed MVP only stays coherent if construct coverage, canonical formatting, and identity behavior keep failing fast when they drift.`
- Prerequisites: `none`
- Work instructions: `Keep the spec-completeness checklist, invalid canonical SCIR-H fixtures, and identity-stability checks aligned with the executable parser, validator, lowering, and reconstruction path.`
- Touched surfaces: `SPEC_COMPLETENESS_CHECKLIST.md`; `IDENTITY_MODEL.md`; `scripts/validate_repo_contracts.py`; `tests/invalid_scir_h/`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode test`; `make test`
- Escalate only if: `a construct cannot be categorized as supported, importer-only, deferred, or removed without changing normative semantics`
- Done evidence: `construct-by-construct status stays explicit`; `invalid canonical examples fail`; `lineage and canonical/view separation stay checked`
