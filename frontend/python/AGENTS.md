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
- keep host-sensitive claims profile-qualified, usually `R` or `D-PY`,
- emit explicit opaque boundaries for host objects or reflection-heavy surfaces,
- keep the bootstrap fixture corpus under `tests/python_importer/cases/` aligned with the accepted first-slice subset,
- keep the frozen 11-case executable Python proof loop executable end to end and do not reclassify any of those cases back to importer-only without synchronized spec, corpus, and decision updates,
- reject `raise` mapping in the bootstrap fixture slice rather than inventing partial support,
- if admitting minimal Python `try/except` in follow-on work, keep it Tier `B` and out of executable lowering, reconstruction, and benchmark claims until exception lowering exists,
- Tier `D` bootstrap fixtures must not emit canonical `SCIR-H`,
- produce module manifest and feature-tier outputs for every importer revision,
- record unresolved importer semantics in `OPEN_QUESTIONS.md`.
