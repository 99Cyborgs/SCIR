# Tests
Status: Informative

This directory holds checked-in golden corpora and conformance fixtures.

## Current contents

- `python_importer/cases/` fixture bundles for the active Python importer proof loop and importer-only follow-on cases
- `rust_importer/cases/` fixture bundles for the bounded Rust safe-subset importer slice
- `corpora/` frozen machine-readable manifests for the active proof-loop corpora
- `sweeps/` slice definitions for sweep smoke and fuller proof-loop aggregation
- `invalid_scir_h/` seeded invalid canonical examples keyed to `SCIR-H` invariant codes
- `invalid_scir_l/` seeded invalid lowered examples keyed to `SCIR-L` invariant codes
- `typescript_importer/` archived placeholder corpus retained only as historical residue outside the active validation gate

## Rules

- Tier `A`, `B`, and `C` importer fixtures include canonical `SCIR-H` text targets
- Tier `C` importer fixtures include an explicit opaque boundary contract
- Tier `D` importer fixtures must not include canonical `SCIR-H`
- importer-only Tier `B` fixtures may stop at validated `SCIR-H` and need not participate in executable lowering, translation, or reconstruction
- Tier `A` Rust importer fixtures are single-crate Rust 2021 library fixtures with `input/Cargo.toml`, `input/src/lib.rs`, and `input/tests/smoke.rs`
- Tier `C` Rust importer fixtures include an explicit opaque boundary contract
- `make test` and `make validate` fail if the Python or Rust importer fixture corpora drift from their conformance rules
- `make validate` fails if the active corpus manifests, negative-fixture manifests, or sweep manifests drift from their schema or file hashes
- invalid `SCIR-H` and `SCIR-L` fixtures must continue to fail with their expected invariant codes

## Archived TypeScript corpus

The checked-in TypeScript placeholder tree is retained only as an archived, non-blocking historical surface.
It is marked with `tests/typescript_importer/NOT_ACTIVE.md` and remains outside the default gate.
It must not be treated as an active importer, lowering, reconstruction, benchmark, or CI commitment.

- `tests/typescript_importer/cases/a_interface_decl/`
- `tests/typescript_importer/cases/a_interface_local_witness_use/`
- `tests/typescript_importer/cases/d_function_decl/`
- `tests/typescript_importer/cases/d_async_function/`
- `tests/typescript_importer/cases/d_class_implements_interface/`
- `tests/typescript_importer/cases/d_prototype_assignment/`
- `tests/typescript_importer/cases/d_decorator_class/`
- `tests/typescript_importer/cases/d_proxy_construct/`
- `tests/typescript_importer/cases/d_type_level_runtime_gate/`

Active validation does not invoke the TypeScript placeholder checker.
