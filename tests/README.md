# Tests
Status: Informative

This directory holds checked-in golden corpora and conformance fixtures.

## Current contents

- `python_importer/cases/` fixture bundles for the Milestone 02 Python importer bootstrap floor plus importer-only 02B follow-on cases, including fixed-shape `while` loop slices and bounded class-field read/update slices
- `rust_importer/cases/` fixture bundles for the Phase 6A Rust safe-subset bootstrap slice
- `typescript_importer/cases/` reserved placeholder tree for the Phase 7 interface-witness slice; both the admitted `A`-case directories and the rejected `D`-case directories now carry non-live placeholder bundle files

## Rules

- Tier `A`, `B`, and `C` importer fixtures include canonical `SCIR-H` text targets
- Tier `C` importer fixtures include an explicit opaque boundary contract
- Tier `D` importer fixtures must not include canonical `SCIR-H`
- importer-only Tier `B` fixtures may stop at validated `SCIR-H` and need not participate in executable lowering, translation, or reconstruction
- Tier `A` Rust importer fixtures are single-crate Rust 2021 library fixtures with `input/Cargo.toml`, `input/src/lib.rs`, and `input/tests/smoke.rs`
- Tier `C` Rust importer fixtures include an explicit opaque boundary contract
- first-slice TypeScript fixture bundles must reuse the importer bundle model already used by Python and Rust: source text plus the required importer reports, with canonical `SCIR-H` present only on admitted cases
- first-slice TypeScript rejection fixtures must cover nearby unsupported constructs, including functions, `async`, classes, prototype behavior, decorators, proxies, and executable type-level semantics
- `make test` and `make validate` fail if the Python or Rust importer fixture corpora drift from their conformance rules

## TypeScript corpus

The first checked-in TypeScript placeholder corpus is:

- `tests/typescript_importer/cases/a_interface_decl/`
- `tests/typescript_importer/cases/a_interface_local_witness_use/`
- `tests/typescript_importer/cases/d_function_decl/`
- `tests/typescript_importer/cases/d_async_function/`
- `tests/typescript_importer/cases/d_class_implements_interface/`
- `tests/typescript_importer/cases/d_prototype_assignment/`
- `tests/typescript_importer/cases/d_decorator_class/`
- `tests/typescript_importer/cases/d_proxy_construct/`
- `tests/typescript_importer/cases/d_type_level_runtime_gate/`

Bundle contents are fixed as:

- admitted cases: `source.ts`, `expected.scirh`, `module_manifest.json`, `feature_tier_report.json`, `validation_report.json`
- rejected cases: `source.ts`, `module_manifest.json`, `feature_tier_report.json`, `validation_report.json`

Current on-disk placeholder state is:

- admitted first-slice TypeScript case directories now contain `README.md` plus placeholder `source.ts`, `expected.scirh`, `module_manifest.json`, `feature_tier_report.json`, and `validation_report.json`
- rejected first-slice TypeScript case directories now contain `README.md` plus placeholder `source.ts`, `module_manifest.json`, `feature_tier_report.json`, and `validation_report.json`
- rejected first-slice TypeScript case directories still intentionally omit `expected.scirh`
- none of these TypeScript placeholder files are live importer outputs
- repository validation now enforces the fixed nine-case TypeScript placeholder corpus shape, including admitted-vs-rejected file-presence rules, rejected-case `expected.scirh` absence, and placeholder report posture

## TypeScript conformance checker

The dormant TypeScript placeholder corpus is now paired with a language-local conformance checker that mirrors the existing Python and Rust pattern where the Phase 7 placeholder contract permits:

- `validate-fixtures` now checks corpus layout, placeholder text markers, schema-valid reports, and admitted-vs-rejected `expected.scirh` rules for the dormant corpus
- `test` remains reserved for future generated-vs-golden conformance against a live TypeScript importer implementation
- repository-contract validation remains the repo-level enforcement layer for the dormant TypeScript placeholder corpus even after `validate-fixtures` activation
