# Python Frontend Local Rules
Status: Normative

Read first:

1. `frontend/README.md`
2. `frontend/python/IMPORT_SCOPE.md`
3. `docs/feature_tiering.md`
4. `docs/unsupported_cases.md`
5. `specs/scir_h_spec.md`

Local rules:

- do not treat `exec`, `eval`, import hooks, metaclasses, descriptor mutation, or monkey patching as Tier `A` or `B`,
- keep host-sensitive claims profile-qualified, usually `R` or `D`,
- emit explicit opaque boundaries for host objects or reflection-heavy surfaces,
- produce module manifest and feature-tier outputs for every importer revision,
- record unresolved importer semantics in `OPEN_QUESTIONS.md`.
