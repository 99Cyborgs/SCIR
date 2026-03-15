# Rust Frontend Local Rules
Status: Normative

Read first:

1. `frontend/README.md`
2. `frontend/rust/IMPORT_SCOPE.md`
3. `specs/ownership_alias_model.md`
4. `specs/type_effect_capability_model.md`
5. `docs/feature_tiering.md`

Local rules:

- prefer safe-subset import before any unsafe expansion,
- do not treat proc macros, build scripts, or unsafe aliasing tricks as Tier `A`,
- map ownership and borrow semantics explicitly; do not hide them in host helpers,
- keep witness lowering visible from traits and impls,
- reject or mark unsupported self-referential pin patterns explicitly.
