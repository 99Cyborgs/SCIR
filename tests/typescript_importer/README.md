# TypeScript Importer Fixtures
Status: Informative

This subtree is reserved for the Phase 7 TypeScript interface-witness corpus.

Current state:

- the corpus root is checked in as a dormant placeholder corpus
- the fixed first-slice TypeScript case directories now contain placeholder bundle files only
- `python scripts/typescript_importer_conformance.py --mode validate-fixtures` is active for this dormant placeholder corpus
- `python scripts/typescript_importer_conformance.py --mode test` remains reserved and non-live
- no live TypeScript fixtures are checked in yet
- admitted placeholder cases carry `expected.scirh`; rejected placeholder cases intentionally omit `expected.scirh`
- the slice remains importer-only and non-executable

Future corpus root:

- `tests/typescript_importer/cases/`

Fixed first-slice case IDs:

- `a_interface_decl`
- `a_interface_local_witness_use`
- `d_function_decl`
- `d_async_function`
- `d_class_implements_interface`
- `d_prototype_assignment`
- `d_decorator_class`
- `d_proxy_construct`
- `d_type_level_runtime_gate`

Bundle expectations remain those published in `tests/README.md` and `plans/milestone_07_typescript_witness_slice.md`.
