# EXECUTION_QUEUE
Status: Informative

## Purpose

This file is the canonical human-readable execution queue for low-touch agent handoff.

It is derived from:

- `IMPLEMENTATION_PLAN.md` for phase ordering
- `plans/milestone_02b_python_expansion.md` for the active near-term work surface
- `OPEN_QUESTIONS.md` for unresolved blocker boundaries
- `STATUS.md` for portfolio context only, not task ordering

## Queue metadata

- Queue snapshot: `2026-03-30T00:00:00-05:00`
- Active milestone: `Milestone 02B - Python Expansion`
- Autonomy mode: `high`
- Escalation threshold: `doctrine conflict; missing source authority; sequencing violation`

## Derivation rules

- prefer the active near-term milestone before the next architecture phase
- do not violate `IMPLEMENTATION_PLAN.md` sequencing
- do not silently resolve open questions; blocked items must cite exact `OQ-*` IDs
- importer-only items do not imply lowering, reconstruction, or benchmark scope unless downstream doctrine widens explicitly
- any queued task that touches 3 or more files, or touches `specs/`, `schemas/`, or validator behavior, requires a matching plan update before implementation

## Queue items

### Q-02B-005 - Record Milestone 02B closeout and phase-handoff readiness

- Queue ID: `Q-02B-005`
- Title: `Record Milestone 02B closeout and phase-handoff readiness`
- Source milestone or phase: `Milestone 02B - Python Expansion`
- Status: `ready`
- Why now: `The Rust-inclusive validation gate is now green, so the remaining 02B work is explicit milestone closeout and a bounded handoff toward the next architecture phase without silently changing the queue regime.`
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

### Q-07-001 - Prepare the TypeScript witness-slice planning handoff

- Queue ID: `Q-07-001`
- Title: `Prepare the TypeScript witness-slice planning handoff`
- Source milestone or phase: `Phase 7 - TypeScript Witness Slice`
- Status: `blocked`
- Why now: `Phase 7 is the next architecture phase after Milestone 02B, but it is not ready while the active queue source remains 02B and the witness slice is still bounded by unresolved contract questions.`
- Prerequisites: `Milestone 02B complete`
- Work instructions: `Keep the first witness-bearing second-language item limited to a planning handoff for TypeScript interface-shaped witnesses; do not admit executable D-JS lowering, reconstruction, or benchmark work under the current roadmap.`
- Touched surfaces: `plans/milestone_07_typescript_witness_slice.md`; `frontend/typescript/IMPORT_SCOPE.md`; `VALIDATION_STRATEGY.md`
- Validation: `python scripts/validate_repo_contracts.py --mode validate`; `python scripts/run_repo_validation.py`
- Escalate only if: `Milestone 02B is complete and OQ-018 or OQ-019 still block the witness-slice contract, or a proposed task widens executable D-JS scope before the published downstream gates exist`
- Done evidence: `02B is complete; the witness slice remains doctrine-only until a later plan widens downstream contracts explicitly`
