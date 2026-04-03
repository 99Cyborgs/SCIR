# TypeScript Importer Fixtures
Status: Informative

This subtree is an archived placeholder corpus from an earlier planning direction.

Current state:

- the corpus root remains on disk for historical reference only
- the fixed first-slice TypeScript case directories still contain placeholder bundle files only
- `scripts/typescript_importer_conformance.py` remains deferred and is not part of the active MVP gate
- no live TypeScript fixtures are checked in
- admitted placeholder cases carry `expected.scirh`; rejected placeholder cases intentionally omit `expected.scirh`
- the subtree is non-executable and non-authoritative

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

Bundle contents are historical residue only and do not imply an active roadmap commitment.
