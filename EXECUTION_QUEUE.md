# EXECUTION_QUEUE
Status: Informative

## Purpose

This file is the canonical human-readable execution queue for low-touch agent handoff.

It is derived from:

- `IMPLEMENTATION_PLAN.md` for phase ordering
- `plans/milestone_07_typescript_witness_slice.md` for the active near-term work surface
- `OPEN_QUESTIONS.md` for unresolved blocker boundaries
- `STATUS.md` for portfolio context only, not task ordering

## Queue metadata

- Queue snapshot: `2026-03-31T00:00:00-05:00`
- Active milestone: `Phase 7 - TypeScript Witness Slice`
- Autonomy mode: `high`
- Escalation threshold: `doctrine conflict; missing source authority; sequencing violation`

## Derivation rules

- prefer the active near-term milestone before the next architecture phase
- do not violate `IMPLEMENTATION_PLAN.md` sequencing
- do not silently resolve open questions; blocked items must cite exact `OQ-*` IDs
- importer-only items do not imply lowering, reconstruction, or benchmark scope unless downstream doctrine widens explicitly
- any queued task that touches 3 or more files, or touches `specs/`, `schemas/`, or validator behavior, requires a matching plan update before implementation

## Queue items

### Q-07-012 - Define the promotion contract from dormant TypeScript placeholders to live generated-vs-golden fixtures

- Queue ID: `Q-07-012`
- Title: `Define the promotion contract from dormant TypeScript placeholders to live generated-vs-golden fixtures`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `ready`
- Why now: `TypeScript validate-fixtures now enforces the dormant placeholder corpus under the top-level validation baseline, so the next bounded task is to define exactly what must change before test mode can stop being reserved and live generated-vs-golden conformance can begin.`
- Prerequisites: `Q-07-011`
- Work instructions: `Document the promotion contract that turns the first-slice TypeScript placeholder corpus into future live generated-vs-golden fixtures, including admitted source.ts promotion to live inputs, admitted expected.scirh promotion from non-canonical sentinel text to canonical goldens, rejected-case expected.scirh absence, and do not activate live importer behavior or executable D-JS, lowering, reconstruction, or benchmark scope.`
- Touched surfaces: `plans/milestone_07_typescript_witness_slice.md`; `VALIDATION_STRATEGY.md`; `tests/README.md`; `tests/typescript_importer/README.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `defining the promotion contract would require live importer execution, schema changes, executable D-JS claims, or broader TypeScript semantic admission than the bounded interface-witness slice allows`
- Done evidence: `the placeholder-to-live promotion rules for first-slice TypeScript fixtures are explicit; test-mode preconditions are explicit; the importer-only boundary remains explicit`

### Q-07-011 - Activate TypeScript validate-fixtures mode for the dormant placeholder corpus

- Queue ID: `Q-07-011`
- Title: `Activate TypeScript validate-fixtures mode for the dormant placeholder corpus`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `Repository validation now enforces the dormant TypeScript placeholder corpus contract, so the next bounded task is to move fixed-corpus integrity checks into the reserved TypeScript conformance entrypoint without activating live importer execution or widening executable scope.`
- Prerequisites: `Q-07-010`
- Work instructions: `Implement real validate-fixtures corpus-integrity checks in scripts/typescript_importer_conformance.py for the dormant TypeScript placeholder corpus, keep test mode reserved, and do not activate live importer behavior or executable D-JS, lowering, reconstruction, or benchmark scope.`
- Touched surfaces: `scripts/typescript_importer_conformance.py`; `scripts/run_repo_validation.py`; `Makefile`; `README.md`; `ci/validation_pipeline.md`; `VALIDATION_STRATEGY.md`; `tests/README.md`; `tests/typescript_importer/README.md`; `plans/milestone_07_typescript_witness_slice.md`
- Validation: `python scripts/typescript_importer_conformance.py --mode validate-fixtures`; `python scripts/typescript_importer_conformance.py --mode test`; `python scripts/build_execution_queue.py --mode write`; `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`; `make validate`
- Escalate only if: `validate-fixtures integrity checks would require live importer output, schema changes, executable D-JS claims, or broader TypeScript semantic admission than the bounded interface-witness slice allows`
- Done evidence: `the TypeScript conformance entrypoint validates the dormant placeholder corpus shape in validate-fixtures mode; test mode remains reserved with an explicit non-live message; top-level validation commands now include the TypeScript validate-fixtures gate; the importer-only boundary remains explicit`

### Q-07-010 - Enforce the dormant TypeScript placeholder corpus contract in repository validation

- Queue ID: `Q-07-010`
- Title: `Enforce the dormant TypeScript placeholder corpus contract in repository validation`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The full dormant TypeScript placeholder corpus is now materialized on disk, so the next bounded task is to make repository-contract validation reject drift in the admitted-vs-rejected placeholder bundle shape without activating live TypeScript conformance or widening executable scope.`
- Prerequisites: `Q-07-009`
- Work instructions: `Add explicit repository-contract checks for the fully materialized dormant TypeScript placeholder corpus, including admitted/rejected file-presence rules and rejected-case expected.scirh absence; do not activate the TypeScript conformance checker or widen executable D-JS, lowering, reconstruction, or benchmark scope.`
- Touched surfaces: `scripts/validate_repo_contracts.py`; `VALIDATION_STRATEGY.md`; `tests/README.md`; `plans/milestone_07_typescript_witness_slice.md`
- Validation: `python scripts/build_execution_queue.py --mode write`; `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/validate_repo_contracts.py --mode test`; `python scripts/run_repo_validation.py`
- Escalate only if: `repository-contract enforcement would require live importer behavior, schema changes, or broader semantic admission than the bounded interface-witness slice allows`
- Done evidence: `repository validation rejects drift in the dormant TypeScript placeholder corpus shape, including exact case IDs, admitted-vs-rejected file sets, placeholder report posture, and rejected-case expected.scirh absence; the importer-only boundary remains explicit`

### Q-07-009 - Add placeholder bundle files for the rejected TypeScript boundary cases

- Queue ID: `Q-07-009`
- Title: `Add placeholder bundle files for the rejected TypeScript boundary cases`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The admitted placeholder bundle shape is now visible on disk, so the next bounded task is to add rejected-case placeholder files that preserve the published rejection bundle contract without introducing live importer outputs or canonical SCIR-H on rejected cases.`
- Prerequisites: `Q-07-008`
- Work instructions: `Add placeholder-only rejected-case bundle files for the fixed TypeScript D-case directories and keep them clearly non-live; do not add executable D-JS, importer logic, lowering, reconstruction, or benchmark work.`
- Touched surfaces: `tests/typescript_importer/cases/`; `tests/README.md`; `plans/milestone_07_typescript_witness_slice.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/build_execution_queue.py --mode check`; `python scripts/run_repo_validation.py`
- Escalate only if: `placeholder rejected-case files would force live fixture contents, schema changes, canonical SCIR-H on rejected cases, or broader semantic admission than the bounded interface-witness slice allows`
- Done evidence: `the rejected TypeScript case directories contain placeholder bundle files only; rejected cases still omit expected.scirh; the importer-only boundary remains explicit`

### Q-07-008 - Add placeholder bundle files for the admitted TypeScript cases

- Queue ID: `Q-07-008`
- Title: `Add placeholder bundle files for the admitted TypeScript cases`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The placeholder case directories now exist, so the next bounded task is to add admitted-case placeholder files that preserve the published bundle shape without introducing live importer outputs.`
- Prerequisites: `Q-07-007`
- Work instructions: `Add placeholder-only admitted-case bundle files for the fixed TypeScript A-case directories and keep them clearly non-live; do not add executable D-JS, importer logic, lowering, reconstruction, or benchmark work.`
- Touched surfaces: `tests/typescript_importer/cases/`; `tests/README.md`; `plans/milestone_07_typescript_witness_slice.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/build_execution_queue.py --mode check`; `python scripts/run_repo_validation.py`
- Escalate only if: `placeholder admitted-case files would force live fixture contents, schema changes, or broader semantic admission than the bounded interface-witness slice allows`
- Done evidence: `the admitted TypeScript case directories contain placeholder bundle files only; the published bundle shape is visible on disk; the importer-only boundary remains explicit`

### Q-07-007 - Create the dormant TypeScript fixture directories for the fixed case matrix

- Queue ID: `Q-07-007`
- Title: `Create the dormant TypeScript fixture directories for the fixed case matrix`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The reserved corpus root and dormant conformance scaffold now existed, so the next bounded task was to create the empty first-slice fixture directories for the fixed TypeScript case matrix without adding real fixture content or importer execution.`
- Prerequisites: `Q-07-006`
- Work instructions: `Create the dormant case directories for the fixed first-slice TypeScript matrix and keep them placeholder-only; do not add live fixture contents, importer logic, executable D-JS, lowering, reconstruction, or benchmark work.`
- Touched surfaces: `tests/typescript_importer/cases/`; `tests/README.md`; `plans/milestone_07_typescript_witness_slice.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/build_execution_queue.py --mode check`; `python scripts/run_repo_validation.py`
- Escalate only if: `creating the dormant case directories would force live fixtures, schema changes, or broader semantic admission than the bounded interface-witness slice allows`
- Done evidence: `the fixed TypeScript case directories exist on disk; they remain placeholder-only; the importer-only boundary remains explicit`

### Q-07-006 - Reserve the dormant TypeScript conformance scaffold and corpus root

- Queue ID: `Q-07-006`
- Title: `Reserve the dormant TypeScript conformance scaffold and corpus root`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The future conformance contract was explicit, so the next bounded task was to reserve the non-executable filesystem and script scaffold that future TypeScript importer work will fill in.`
- Prerequisites: `Q-07-005`
- Work instructions: `Add the dormant TypeScript corpus root and non-executable conformance-checker scaffold surfaces needed by the published contract; do not add importer logic, executable D-JS, lowering, reconstruction, or benchmark work.`
- Touched surfaces: `tests/README.md`; `frontend/README.md`; `scripts/`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/build_execution_queue.py --mode check`; `python scripts/run_repo_validation.py`
- Escalate only if: `reserving the dormant TypeScript scaffold would require live importer behavior, schema changes, or broader semantic admission than the bounded interface-witness slice allows`
- Done evidence: `the dormant TypeScript corpus root is reserved; the non-executable conformance scaffold is explicit; the importer-only boundary remains explicit`

### Q-07-005 - Define the TypeScript conformance checker contract and validation entrypoint

- Queue ID: `Q-07-005`
- Title: `Define the TypeScript conformance checker contract and validation entrypoint`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The initial TypeScript corpus layout and case matrix were explicit, so the next bounded task was to define how future conformance checking would consume that corpus and integrate with repository validation without implying importer implementation was already present.`
- Prerequisites: `Q-07-004`
- Work instructions: `Define the future TypeScript conformance checker contract, expected command entrypoint, and repository-validation integration for the importer-only interface witness corpus; do not add executable D-JS, lowering, reconstruction, or benchmark work.`
- Touched surfaces: `VALIDATION_STRATEGY.md`; `tests/README.md`; `frontend/README.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/build_execution_queue.py --mode check`; `python scripts/run_repo_validation.py`
- Escalate only if: `the conformance contract cannot be stated without implementing importer code, adding schemas, or broadening the first Phase 7 slice beyond importer-only witness evidence`
- Done evidence: `the future TypeScript conformance checker contract is explicit; repository validation expectations are explicit; executable D-JS scope remains deferred`

### Q-07-004 - Define the initial TypeScript fixture corpus layout and case matrix

- Queue ID: `Q-07-004`
- Title: `Define the initial TypeScript fixture corpus layout and case matrix`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The fixture/report contract was explicit, so the next bounded task was to define the first concrete TypeScript fixture corpus layout and case matrix that an importer implementation will be required to satisfy.`
- Prerequisites: `Q-07-003`
- Work instructions: `Define the initial TypeScript importer corpus layout, enumerate the first admitted and rejected interface-witness cases, and keep the corpus importer-only; do not add executable D-JS, lowering, reconstruction, or benchmark work.`
- Touched surfaces: `plans/milestone_07_typescript_witness_slice.md`; `frontend/typescript/IMPORT_SCOPE.md`; `tests/README.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/build_execution_queue.py --mode check`; `python scripts/run_repo_validation.py`
- Escalate only if: `the case matrix cannot be defined without adding new schemas, executable artifacts, or broadening the first Phase 7 slice beyond interface-shaped witness doctrine`
- Done evidence: `the initial TypeScript corpus layout is explicit; admitted and rejected first-slice cases are enumerated; the importer-only boundary remains explicit`

### Q-07-003 - Define the fixture and report contract for the first interface witness slice

- Queue ID: `Q-07-003`
- Title: `Define the fixture and report contract for the first interface witness slice`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The planning handoff and implementation-facing doctrine were explicit, so the next bounded Phase 7 task was to define the minimal fixture and report expectations for the importer-only interface witness slice before any importer implementation began.`
- Prerequisites: `Q-07-002`
- Work instructions: `Define the minimal checked-in fixture shape, report obligations, and rejection boundaries for the first importer-only TypeScript interface witness slice; do not add executable D-JS, lowering, reconstruction, or benchmark work.`
- Touched surfaces: `plans/milestone_07_typescript_witness_slice.md`; `VALIDATION_STRATEGY.md`; `frontend/typescript/IMPORT_SCOPE.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/build_execution_queue.py --mode check`; `python scripts/run_repo_validation.py`
- Escalate only if: `the fixture and report contract cannot be stated without adding schemas, executable artifacts, or broader TypeScript semantic admission than the bounded interface slice allows`
- Done evidence: `fixture expectations are explicit for the first interface slice; report-visible witness semantics and rejection boundaries are explicit; executable D-JS scope remains deferred`

### Q-07-002 - Record the bounded interface-witness doctrine in the implementation surfaces

- Queue ID: `Q-07-002`
- Title: `Record the bounded interface-witness doctrine in the implementation surfaces`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `The planning handoff contract was explicit, so the next bounded task was to mirror that contract into the implementation-facing surfaces that would govern future TypeScript importer work without admitting execution scope.`
- Prerequisites: `Q-07-001`
- Work instructions: `Update the TypeScript-facing implementation surfaces so the first Phase 7 slice is expressed as importer-only interface witness doctrine, keep host assumptions and report obligations explicit, and do not admit executable D-JS, lowering, reconstruction, or benchmark work.`
- Touched surfaces: `frontend/typescript/IMPORT_SCOPE.md`; `VALIDATION_STRATEGY.md`; `validators/validator_contracts.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/build_execution_queue.py --mode check`; `python scripts/run_repo_validation.py`
- Escalate only if: `implementation-facing doctrine cannot express the bounded interface slice without changing schemas, adding executable artifacts, or silently broadening classes, async behavior, or prototype semantics`
- Done evidence: `implementation-facing doctrine agrees on the bounded interface slice; report-visible witness and host assumptions remain explicit; executable D-JS scope remains deferred`

### Q-07-001 - Prepare the TypeScript witness-slice planning handoff

- Queue ID: `Q-07-001`
- Title: `Prepare the TypeScript witness-slice planning handoff`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `done`
- Why now: `Milestone 02B was explicitly complete, so the next bounded step was to make the TypeScript witness slice the active planning surface while keeping it doctrine-only and non-executable.`
- Prerequisites: `Milestone 02B complete`
- Work instructions: `Keep the first witness-bearing second-language item limited to a planning handoff for TypeScript interface-shaped witnesses; do not admit executable D-JS lowering, reconstruction, or benchmark work under the current roadmap.`
- Touched surfaces: `plans/milestone_07_typescript_witness_slice.md`; `frontend/typescript/IMPORT_SCOPE.md`; `VALIDATION_STRATEGY.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `OQ-018 or OQ-019 force a broader witness contract than the interface-shaped doctrine-only slice, or a proposed task widens executable D-JS scope before the published downstream gates exist`
- Done evidence: `Phase 7 is the explicit active queue source; the witness slice remains doctrine-only until a later plan widens downstream contracts explicitly`

### Q-02B-005 - Record Milestone 02B closeout and phase-handoff readiness

- Queue ID: `Q-02B-005`
- Title: `Record Milestone 02B closeout and phase-handoff readiness`
- Source milestone or phase: `Milestone 02B - Python Expansion`
- Status: `done`
- Why now: `The Rust-inclusive validation gate was green, so the remaining 02B work was explicit milestone closeout and a bounded handoff toward the next architecture phase without silently changing the queue regime.`
- Prerequisites: `Q-02B-004`
- Work instructions: `Record Milestone 02B completion evidence, decide the minimal queue and milestone-source updates needed for a clean Phase 7 handoff, and keep the witness slice doctrine-only until a later task widens downstream contracts explicitly.`
- Touched surfaces: `plans/milestone_02b_python_expansion.md`; `EXECUTION_QUEUE.md`; `plans/milestone_07_typescript_witness_slice.md`
- Validation: `python scripts/build_execution_queue.py --mode check`; `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py --require-rust`
- Escalate only if: `closing Milestone 02B requires changing phase ordering, changing the queue generator contract, or widening executable D-JS or witness-bearing scope before the published downstream gates exist`
- Done evidence: `Milestone 02B completion is explicit; the next queue source is explicit; Phase 7 remains doctrine-only until a later task widens downstream contracts explicitly`

### Q-02B-004 - Run the milestone validation gate for the admitted slice

- Queue ID: `Q-02B-004`
- Title: `Run the milestone validation gate for the admitted slice`
- Source milestone or phase: `Milestone 02B - Python Expansion`
- Status: `done`
- Why now: `Admission, fixture coverage, and doctrine sync were already in place for the bounded class field-update slice, and the remaining near-term work was to record the validation-gate outcome without widening executable scope.`
- Prerequisites: `Q-02B-003`
- Work instructions: `Run the canonical importer and repository validation commands for the admitted slice, record the Python-side validation outcome, keep the slice importer-only, and note any unrelated broader validation blockers without widening executable claims.`
- Touched surfaces: `scripts/run_repo_validation.py`; `VALIDATION.md`; `reports/`
- Validation: `python scripts/python_importer_conformance.py --mode validate-fixtures`; `python scripts/python_importer_conformance.py --mode test`; `python scripts/run_repo_validation.py --require-rust`; `python scripts/benchmark_contract_dry_run.py`
- Escalate only if: `validation passes only by widening executable claims, by skipping required fixture coverage, by contradicting milestone scope language, or if broader repo validation fails outside the admitted Python slice and must be recorded as a separate blocker`
- Done evidence: `Python-side validation commands pass; Rust-inclusive validation and benchmark commands pass in the validated environment; importer-only status remains explicit; no lowering, reconstruction, or benchmark claim was widened implicitly`

### Q-02B-001 - Admit the bounded Python class field-update shape

- Queue ID: `Q-02B-001`
- Title: `Admit the bounded Python class field-update shape`
- Source milestone or phase: `Milestone 02B - Python Expansion`
- Status: `done`
- Why now: `The bounded importer-only class field-update slice is already admitted in the checked-in 02B corpus and must remain explicit as a completed prerequisite for the remaining milestone gate work.`
- Prerequisites: `Milestone 02B remains the active roadmap priority; the completed Milestone 02 five-case corpus remains the acceptance floor.`
- Work instructions: `Admit exactly the importer-only b_class_field_update case, normalize it into a canonical record-like type declaration plus plain functions over explicit field places and direct local call syntax, and keep lowering, reconstruction, and benchmark scope unchanged.`
- Touched surfaces: `frontend/python/IMPORT_SCOPE.md`; `plans/milestone_02b_python_expansion.md`; `tests/python_importer/cases/*`
- Validation: `python scripts/python_importer_conformance.py --mode validate-fixtures`; `python scripts/run_repo_validation.py`
- Escalate only if: `the bounded class update slice requires inheritance, decorators, dynamic attributes, descriptor behavior, or cannot stay importer-only under current downstream contracts`
- Done evidence: `accepted construct scope is explicit; fixture-backed acceptance criteria exist; importer-only boundaries remain explicit`

### Q-02B-002 - Add fixture and conformance evidence for the admitted slice

- Queue ID: `Q-02B-002`
- Title: `Add fixture and conformance evidence for the admitted slice`
- Source milestone or phase: `Milestone 02B - Python Expansion`
- Status: `done`
- Why now: `The admitted class field-update slice already has a checked-in fixture bundle and conformance coverage, so this prerequisite is complete and serves as evidence for the remaining milestone gate work.`
- Prerequisites: `Q-02B-001`
- Work instructions: `Add or update the minimal checked-in Python importer fixtures and conformance expectations required to prove the newly admitted slice, keeping unsupported and opaque cases explicit.`
- Touched surfaces: `tests/python_importer/cases/*`; `scripts/python_importer_conformance.py`
- Validation: `python scripts/python_importer_conformance.py --mode validate-fixtures`; `python scripts/python_importer_conformance.py --mode test`
- Escalate only if: `the admitted slice cannot be represented with fixture-backed expectations or requires relaxing the fixed bootstrap acceptance floor`
- Done evidence: `new or updated fixtures exist; conformance expectations are explicit; unsupported behavior remains explicit rather than silently accepted`

### Q-02B-003 - Sync importer-scope, tier, and unsupported-case doctrine

- Queue ID: `Q-02B-003`
- Title: `Sync importer-scope, tier, and unsupported-case doctrine`
- Source milestone or phase: `Milestone 02B - Python Expansion`
- Status: `done`
- Why now: `The Python importer scope and downstream validation doctrine already name the bounded class field-update slice as Tier B and importer-only, so doctrine sync is complete for this admitted construct.`
- Prerequisites: `Q-02B-002`
- Work instructions: `Update the Python importer scope and the relevant tier or unsupported-case doctrine so the accepted slice, rejection boundaries, and any opaque treatment are explicit and profile-qualified where needed.`
- Touched surfaces: `frontend/python/IMPORT_SCOPE.md`; `docs/feature_tiering.md`; `docs/unsupported_cases.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `make validate`
- Escalate only if: `the slice requires new tier semantics, changes unsupported-case handling outside the current doctrine, or creates unresolved semantic ambiguity that belongs in OPEN_QUESTIONS.md`
- Done evidence: `scope and doctrine agree; unsupported and opaque boundaries are explicit; any required plan update is recorded before implementation`
