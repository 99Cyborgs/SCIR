# 2026-04-01 MVP Narrowing and Contract Hardening

Status: in-progress
Owner: Codex
Date: 2026-04-01

## Objective

Refactor the repository into a coherent SCIR MVP centered on `SCIR-H`, derivative `SCIR-L`, the H/L validators, Python and Rust importers, Python reconstruction, Wasm as the first reference execution target, and a benchmark harness focused on the smallest falsifiable loops.

## Scope

- narrow repository doctrine, roadmap, and command surfaces to the active MVP
- make `SCIR-H` the only normative semantic layer and document `SCIR-L` as derivative-only
- reconcile spec, grammar, parser, validator, lowering, reconstruction, tests, and examples around the implemented bootstrap subset
- redesign the identity contract so semantic lineage is not coupled to spec version
- separate canonical storage from non-canonical human-facing view
- simplify preservation reporting into a smaller machine-generated operator surface
- remove TypeScript and non-MVP tooling from active validation, CI, and roadmap claims
- add minimum viable tests and validation hooks for checklist coverage, identity stability, invalid examples, lowering provenance, and benchmark-manifest integrity

## Non-goals

- implement a live TypeScript importer
- widen supported language scope beyond Python and Rust
- claim a universal backend or proof story
- add heavyweight new services or dependencies

## Touched files

- `README.md`
- `SYSTEM_BOUNDARY.md`
- `ARCHITECTURE.md`
- `IMPLEMENTATION_PLAN.md`
- `VALIDATION.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`
- `DECISION_REGISTER.md`
- `OPEN_QUESTIONS.md`
- `REPO_MAP.md`
- `docs/*`
- `specs/*`
- `frontend/*`
- `validators/*`
- `benchmarks/*`
- `tooling/*`
- `ci/*`
- `.github/workflows/*`
- `schemas/*`
- `scripts/*`
- `tests/*`
- `reports/examples/*`
- `reports/exports/*`

## Invariants that must remain true

- `SCIR-H` remains the semantic source of truth
- `SCIR-L` remains derivative and cannot acquire L-only semantics
- unsupported and opaque cases remain explicit
- no new mass-market authoring language is introduced
- benchmark claims remain profile-qualified and baseline-qualified
- repository validation remains Windows-safe through `python scripts/run_repo_validation.py`

## Risks

- narrowing doctrine may break existing repo-contract checks unless scripts and exports are updated together
- reducing scope may expose missing active-path contracts, especially for Wasm reference emission and the execution queue
- changing the identity model may create drift between documentation, examples, and validator expectations

## Validation steps

- `python scripts/validate_repo_contracts.py --mode validate`
- `python scripts/python_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --mode validate`
- `python scripts/rust_importer_conformance.py --mode validate-fixtures`
- `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- `python scripts/build_execution_queue.py --mode check`
- `python scripts/benchmark_contract_dry_run.py`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert the MVP-narrowing patch set as a unit if validation cannot be brought back to a consistent state, then re-apply in smaller slices starting with documentation and validation-surface alignment before schema or script changes.

## Evidence required for completion

- repo docs and specs agree on the narrowed MVP
- validator, benchmark, and CI entrypoints enforce the narrowed scope
- spec completeness, identity, invalid-example, provenance, and benchmark-integrity checks are executable
- derived exports match updated markdown sources
- exact deferred and archived surfaces are documented

## Completion evidence for this execution slice

- root boundary docs, specs, benchmark doctrine, validation doctrine, and roadmap surfaces were rewritten around the narrowed MVP
- `SCIR-H` was documented as the only normative semantic layer and the lowering path now enforces named lowering rules plus provenance on active `SCIR-L`
- persistent lineage identity, canonical content hash, and revision-scoped node identity were separated, with canonical versus pretty-view noninterference checks
- preservation reporting was reduced to a path-qualified machine-facing schema and refreshed examples
- a helper-free emitter-backed Wasm slice now emits stable WAT for `fixture.python_importer.a_basic_function` in the default path and `fixture.rust_importer.a_mut_local` in the optional Rust path
- `OQ-002` was resolved into a bounded local-slot Wasm subset, `DR-013` recorded the constraint, and the execution queue advanced to the Phase 1 `SCIR-H` kernel handoff
- the Phase 1 `SCIR-H` kernel is now mirrored by executable bootstrap metadata, a normative spec kernel table, checklist rows with aligned importer-only wording, and identity-model markers for the enforced noninterference rules
- repository contract validation now fails on drift between `scripts/scir_h_bootstrap_model.py`, `specs/scir_h_spec.md`, `IDENTITY_MODEL.md`, and `SPEC_COMPLETENESS_CHECKLIST.md`
- `Q-01-001` is closed and the execution queue now advances to `Q-02-001` for the Phase 2 Python proof-loop handoff
- `scripts/scir_python_bootstrap.py` now exports `PYTHON_PROOF_LOOP_METADATA` so the executable Python proof-loop boundary has one authoritative case contract
- `scripts/scir_bootstrap_pipeline.py` now derives executable Python cases, importer-only cases, reconstruction expectations, benchmark cases, and Wasm-emittable cases from that metadata instead of parallel hard-coded lists
- repository contract validation now fails on drift between `PYTHON_PROOF_LOOP_METADATA`, `frontend/python/IMPORT_SCOPE.md`, and `docs/reconstruction_policy.md`
- `Q-02-001` is closed and the execution queue now advances to `Q-03-001` for the Rust importer-alignment handoff
- `scripts/scir_rust_bootstrap.py` now exports `RUST_IMPORTER_METADATA` so the Rust importer-first evidence path has one authoritative case contract
- `scripts/scir_bootstrap_pipeline.py` and `scripts/rust_importer_conformance.py` now derive Rust case classifications and translation expectations from that metadata instead of parallel hard-coded lists
- repository contract validation now fails on drift between `RUST_IMPORTER_METADATA` and `frontend/rust/IMPORT_SCOPE.md`, and stale Rust reconstruction-only pipeline helpers were removed from the active code path
- `Q-03-001` is closed and the execution queue now advances to `Q-04-001` for the Wasm MVP alignment handoff
- `scripts/wasm_backend_metadata.py` now exports the authoritative helper-free Wasm backend contract for emitted Python and Rust modules, admitted lowering rules, non-emittable lowering rules, and `l_to_wasm` preservation-report strings
- `scripts/scir_bootstrap_pipeline.py` now derives Wasm-emittable Python and Rust cases plus Wasm preservation reporting from that metadata and rejects lowering rules outside the admitted Wasm contract
- repository contract validation now fails on drift between `WASM_BACKEND_METADATA`, `backends/wasm/README.md`, `LOWERING_CONTRACT.md`, `VALIDATION_STRATEGY.md`, and `reports/examples/preservation_l_to_wasm.example.json`
- `Q-04-001` is closed and the execution queue now advances to `Q-05-001` for the benchmark falsification loop handoff
- `scripts/benchmark_contract_metadata.py` now exports the authoritative benchmark contract for the active executable tracks, fixed Python proof-loop benchmark cases, baselines, gates, profiles, and contamination controls
- `scripts/scir_bootstrap_pipeline.py` and `scripts/benchmark_contract_dry_run.py` now derive Track `A` and Track `B` executable benchmark expectations from that metadata instead of parallel hard-coded benchmark constants
- repository contract validation now fails on drift between `BENCHMARK_CONTRACT_METADATA`, `BENCHMARK_STRATEGY.md`, `benchmarks/tracks.md`, `benchmarks/baselines.md`, and `benchmarks/success_failure_gates.md`
- `Q-05-001` is closed and the execution queue now advances to `Q-06-001` for the optional Track `C` pilot handoff
- `scripts/benchmark_contract_metadata.py` now also fixes the first Track `C` pilot as a conditional Python single-function repair sample over the executable Python proof-loop cases, with direct source, typed-AST, and regularized-core baselines plus `S2` and `K1` gates
- benchmark doctrine docs and illustrative sample artifacts now expose machine-checkable Track `C` pilot task-family, corpus, baseline, gate, and non-default-posture markers
- `DR-014` records the Track `C` pilot decision, `OQ-005` is resolved and removed, and repository plus benchmark validation now fail if Track `C` sample artifacts drift back toward the default executable gate
- `Q-06-001` is closed and the execution queue now advances to `Q-06-002` for the next conditional Track `C` assessment
- the first executable Track `C` pilot is now available only through explicit `--include-track-c-pilot` commands, while `make benchmark` and the default validation runner remain Track `A` / `B` only
- checked-in Track `C` sample artifacts now mirror the bounded opt-in pilot output, including the fixed proof-loop corpus hash, mixed result posture, accepted-case counts, and boundary-only accounting for `c_opaque_call`
- `DR-015` records the opt-in executable-pilot decision, repository validation now fails if Track `C` leaks into the default gate, and `Q-06-002` is closed with `Q-06-003` queued next
- the retained-disposition decision for the non-default Track `C` pilot is now explicit in shared benchmark metadata, benchmark doctrine, and repo-validation drift checks
- `reports/examples/benchmark_track_c_result.example.json` now records retained bounded-diagnostic evidence rather than implying a promotion claim
- `DR-016` records the retained Track `C` disposition, `Q-06-003` is closed, and the execution queue now advances to `Q-06-004`
- the retained Track `C` pilot now has explicit machine-checkable retention criteria and retirement triggers in shared benchmark metadata plus benchmark doctrine
- benchmark and repository validation now fail if those Track `C` lock criteria drift from the retained opt-in pilot contract
- `DR-017` records the lock-criteria decision, `Q-06-004` is closed, and the execution queue now advances to `Q-06-005`
- the retained Track `C` pilot now has explicit machine-checkable sample-synchronization requirements tying the checked-in sample manifest/result to the current opt-in runner output and retained keep/retire criteria
- benchmark and repository validation now fail if the Track `C` sample-synchronization doctrine drifts, if the checked-in sample evidence drifts, or if the sample lock metrics weaken
- `DR-018` records the synchronized sample-bundle decision, `Q-06-005` is closed, and the execution queue now advances to `Q-06-006`
- the retained Track `C` pilot now has explicit machine-checkable sample-posture re-decision triggers covering status, retained-diagnostic wording, task-family or case/boundary posture, and default-gate or promotion posture changes
- benchmark and repository validation now fail with governance-specific Track `C` re-decision messages when the checked-in sample status, evidence, or case/boundary posture drifts
- `DR-019` records the sample-posture re-decision boundary, `Q-06-006` is closed, and the execution queue now advances to `Q-06-007`
- the retained Track `C` pilot now has explicit machine-checkable editorial-only sample refresh allowances limited to JSON-equivalent formatting changes that preserve parsed sample content
- benchmark and repository validation now fail if the Track `C` editorial-only refresh doctrine drifts while still allowing formatting-only JSON-equivalent sample refreshes
- `DR-020` records the editorial-only refresh boundary, `Q-06-007` is closed, and the execution queue now advances to `Q-06-008`
- the retained Track `C` pilot now has explicit machine-checkable non-editorial sample-refresh provenance requirements tied to the opt-in runner command pair plus the regenerated manifest hash and result identifiers
- benchmark and repository validation now fail if the Track `C` provenance doctrine drifts or if the operator-facing provenance rule disappears from the benchmark and reports readmes
- `DR-021` records the non-editorial regeneration-provenance boundary, `Q-06-008` is closed, and the execution queue now advances to `Q-06-009`
- the fixed Python `b_direct_call` case is now part of the active executable proof loop, with shared metadata, importer conformance, SCIR-H to SCIR-L lowering, reconstruction expectations, and benchmark case selection all widened together
- Python proof-loop doctrine, feature-tier guidance, completeness checklist wording, and Track `C` sample artifacts now agree on the widened bounded direct-call case set and the resulting three accepted non-opaque repair cases
- `DR-022` records the bounded direct-call promotion, `Q-02-002` is closed, and the execution queue now advances to validator/completeness hardening before any further Wasm widening
- a new generator-backed sync command now regenerates checked-in Python importer artifacts and Track `C` sample artifacts directly from the authoritative proof-loop generators instead of relying on manual multi-file updates
- repo-contract validation now treats that sync command as part of the active command surface, and the queue closes `Q-02-003` with the next ready slice returning to substantive Wasm widening work
- the helper-free Wasm backend now emits bounded same-module scalar direct calls for `fixture.python_importer.b_direct_call`, while imported, indirect, recursive, async, opaque, and broader call-graph shapes remain explicitly non-emittable
- `DR-023` records the bounded direct-call Wasm widening, `Q-04-002` is closed, and the execution queue now advances to the next substantive Wasm field-place assessment
- the field-place Wasm assessment now closes as an explicit blocker: helper-free Wasm rejects `H_FIELD_ADDR` because the active backend has no record ABI/layout contract for caller-visible borrowed record mutation, not because of an incidental missing opcode implementation
- `scripts/scir_bootstrap_pipeline.py` now raises that blocker reason directly for the concrete Rust field-place case, and repo-contract validation fails if the Wasm docs stop stating the scalar-only signature boundary and record-layout blocker explicitly
- `DR-024` records the blocker, `Q-04-003` is closed, and the execution queue now advances to the next deliberate Wasm ABI-boundary decision rather than silently widening the backend
- root architecture and implementation-order doctrine now state that broader Wasm work beyond the helper-free scalar subset requires an explicit ABI/storage contract decision rather than incremental emitter widening
- `DR-025` records that post-scalar ABI gate, `OQ-005` now captures the unresolved backend-expansion decision, and `Q-04-004` is closed with `Q-04-005` blocked on that review point
- the repository now explicitly opens post-scalar Wasm ABI/storage design as architecture work while keeping the current helper-free scalar backend unchanged
- `DR-026` records that the broader Wasm ABI/storage design track is now active, `OQ-005` is resolved into the narrower contract-definition question `OQ-006`, and `Q-04-005` is closed with `Q-04-006` ready as the first contract-definition slice
- the first candidate post-scalar Wasm contract is now explicit: a module-owned linear-memory record-cell ABI with fixed `int` fields, offsets derived from canonical field declaration order, and shared base-address handles for caller-visible mutation
- `DR-027` records that candidate contract, `OQ-006` is resolved into the narrower operationalization question `OQ-007`, and `Q-04-006` is closed with `Q-04-007` ready to define validator and preservation obligations before any implementation claim
- the candidate record-cell ABI now has explicit preconditions: canonical field-order offsets, fixed `int`-field records only, shared-handle callers only, and `P`/`P2` preservation with candidate-specific downgrade and evidence requirements
- `DR-028` records those validator and preservation obligations, `OQ-007` is resolved into the narrower implementation-credibility question `OQ-008`, and `Q-04-007` is closed with `Q-04-008` ready to assess whether bounded implementation is actually credible
- the repository now shows that bounded implementation of the record-cell ABI is credible without new `SCIR-L` semantics: the existing `field.addr`, `load`, `store`, comparison, and branch lowering surfaces were sufficient for the fixed Rust field-mutation case
- the helper-free Wasm backend now emits stable bounded WAT for `fixture.rust_importer.a_struct_field_borrow_mut` through module-owned linear memory, offset `0` for `Counter.value`, and shared base-address handles, while broader record layouts and Python field places remain explicitly out of scope
- `DR-029` records the bounded record-cell implementation, `OQ-008` is resolved into the narrower future-widening question `OQ-009`, and `Q-04-008` plus `Q-04-009` are closed with `Q-04-010` queued next as the next post-scalar Wasm decision boundary
- the active Wasm record-cell ABI is now explicitly frozen to the fixed Rust `a_struct_field_borrow_mut` slice rather than treated as a stepping stone toward broader record or Python field-place support
- `DR-030` records that freeze decision, `OQ-009` is resolved and removed, and `Q-04-010` is closed with any future Wasm widening treated as a deliberate reopen decision rather than an implied next step
- derived exports for the decision register, open questions, and execution queue were regenerated from their markdown sources
- TypeScript and broad tooling surfaces were kept in-place but downgraded to deferred status rather than active MVP claims
- passed `python scripts/validate_repo_contracts.py --mode validate`
- passed `python scripts/validate_repo_contracts.py --mode test`
- passed `python scripts/scir_bootstrap_pipeline.py --mode validate`
- passed `python scripts/scir_bootstrap_pipeline.py --language rust --mode validate`
- passed `python scripts/build_execution_queue.py --mode check`
- passed `python scripts/run_repo_validation.py`
- passed `python scripts/scir_bootstrap_pipeline.py --mode test`
- passed `python scripts/benchmark_contract_dry_run.py`
- passed `python scripts/scir_bootstrap_pipeline.py --language rust --mode test`
- passed `python scripts/run_repo_validation.py --require-rust`
