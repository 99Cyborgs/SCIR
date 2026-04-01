# Milestone 07 - TypeScript Witness Slice

Status: in-progress

## Objective

Land the first witness-bearing second-language milestone after Phase 6B on the narrow credible path: TypeScript interface-shaped witness evidence with explicit validator, translation-validation, and report coverage, without widening executable `D-JS` claims.

## Scope

- TypeScript interface declarations as the only admitted witness-bearing surface for the first Phase 7 step
- module-local interface consumption shape for planning-only witness import doctrine under `frontend/typescript/*`
- a fixed checked-in fixture bundle and report package for admitted and rejected first-slice cases
- witness-focused validator and translation-validation obligations
- profile-qualified preservation and downgrade reporting for the admitted witness slice
- explicit non-executable `D-JS` boundary unless a later milestone adds downstream contracts

## Non-goals

- admitting functions, `async` functions, classes, prototype behavior, or structural record normalization into the first Phase 7 slice
- executable `D-JS` lowering or benchmark activation
- Rust trait/impl execution work
- new backend tracks
- widening the canonical `SCIR-L` opcode surface

## Touched files

- `frontend/typescript/IMPORT_SCOPE.md`
- `specs/type_effect_capability_model.md`
- `VALIDATION_STRATEGY.md`
- `validators/validator_contracts.md`
- `docs/runtime_doctrine.md`
- `plans/milestone_07_typescript_witness_slice.md`

## Invariants

- `SCIR-H` remains the semantic source of truth
- witness semantics stay explicit in `SCIR-H`
- `SCIR-L` remains derivative
- `D-JS` stays doctrine-only in this milestone
- no optimizer-only facts flow back into canonical `SCIR-H`
- host assumptions for the first TypeScript witness slice remain explicit and module-local

## Risks

- interface witnesses could overclaim executable host semantics
- `D-JS` doctrine-only status could blur if downstream artifacts appear without explicit gates
- witness semantics could drift into undocumented importer-specific behavior

## Validation steps

```bash
python scripts/validate_repo_contracts.py --mode validate
python scripts/run_repo_validation.py
```

## Rollback strategy

Narrow the TypeScript witness slice back to doctrine-only candidate status, remove unsupported downstream claims, and keep witness-bearing second-language execution deferred if validator/report obligations cannot be made explicit.

## Evidence required for completion

- admitted TypeScript witness slice is explicitly scoped as interface-shaped and planning-only
- the minimum checked-in fixture and report package for the first TypeScript slice is explicit
- validator and translation-validation obligations for the slice are documented
- executable `D-JS` remains disallowed without a superseding milestone
- repo contract validation passes

## Current handoff status

- Phase 7 is now the active planning source after Milestone 02B closeout
- the planning handoff contract for the first TypeScript interface-shaped witness slice is now explicit
- the first checked-in fixture and report evidence package is now explicit
- the initial TypeScript corpus layout and case matrix are now explicit
- the TypeScript conformance checker contract is now explicit and partially active
- the dormant TypeScript scaffold and reserved corpus root are now explicit
- the TypeScript `validate-fixtures` conformance entrypoint is now active for the dormant placeholder corpus
- the admitted TypeScript case directories now contain placeholder bundle files on disk and remain non-live
- the rejected TypeScript boundary case directories now contain placeholder bundle files on disk and continue to omit canonical `SCIR-H`
- repository validation now enforces the fixed dormant TypeScript placeholder corpus shape at the repo-contract layer
- TypeScript `test` mode remains reserved and non-live pending future generated-vs-golden activation
- `D-JS` remains doctrine-only and non-executable
- OQ-018 and OQ-019 remain open but non-blocking for planning-only handoff work

## Current slice contract

- the first admissible Phase 7 slice is limited to TypeScript `interface` declarations interpreted as explicit witness-bearing contracts in `SCIR-H`
- the planning handoff may describe only module-local interface consumption shapes that keep host assumptions explicit and do not imply general function, class, async, or prototype support
- the first Phase 7 slice remains importer-only and must not emit executable `SCIR-L`, translation, reconstruction, or benchmark artifacts
- any later executable `D-JS` claim must be gated by published lowering, translation-validation, reconstruction, and benchmark contracts rather than milestone prose alone

## First evidence package

- admitted first-slice fixtures must be checked in as fixed bundles under the TypeScript importer corpus rather than inferred from prose alone
- each admitted fixture bundle must include source text, canonical `SCIR-H`, `module_manifest`, `feature_tier_report`, and `validation_report`
- admitted placeholder bundles may exist on disk before importer implementation, but they remain non-live and do not constitute validated canonical output
- first-slice TypeScript fixtures must not include `SCIR-L`, translation, reconstruction, or benchmark artifacts
- rejected placeholder bundles may exist on disk before importer implementation, but they remain non-live and continue to omit canonical `SCIR-H`
- nearby rejected cases must still carry explicit `module_manifest`, `feature_tier_report`, and `validation_report`, but must not include canonical `SCIR-H`
- the first rejection boundary must cover at least functions, `async`, classes, prototype behavior, decorators, proxies, and executable type-level semantics

## Initial corpus layout and case matrix

- the corpus root is `tests/typescript_importer/cases/`
- admitted first-slice bundles use `source.ts`, `expected.scirh`, `module_manifest.json`, `feature_tier_report.json`, and `validation_report.json`
- rejected boundary bundles use `source.ts`, `module_manifest.json`, `feature_tier_report.json`, and `validation_report.json`, with no `expected.scirh`
- the initial admitted matrix is:
  `a_interface_decl`
  `a_interface_local_witness_use`
- the initial rejected boundary matrix is:
  `d_function_decl`
  `d_async_function`
  `d_class_implements_interface`
  `d_prototype_assignment`
  `d_decorator_class`
  `d_proxy_construct`
  `d_type_level_runtime_gate`
- the first TypeScript corpus intentionally starts with Tier `A` and Tier `D` only; no Tier `B` or `C` case is part of the initial matrix

## TypeScript conformance checker contract

- the TypeScript witness corpus is now paired with a language-local conformance checker that mirrors the Python and Rust conformance model where the placeholder corpus allows
- the active checker mode is `validate-fixtures` for checked-in dormant placeholder-corpus integrity
- `validate-fixtures` validates corpus layout, placeholder text markers, schema-valid importer reports, and admitted-vs-rejected `expected.scirh` rules without parsing admitted sentinel `expected.scirh` files as canonical `SCIR-H`
- `test` remains reserved for future generated-vs-golden conformance against live importer output and must fail clearly as non-live until the placeholder corpus is promoted to live goldens
- repository validation must continue to enforce the fixed dormant TypeScript placeholder corpus shape and must not be replaced by informal milestone prose
