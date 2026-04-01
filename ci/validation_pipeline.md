# Validation Pipeline
Status: Normative

## Required steps

1. verify required files exist
2. parse all JSON schemas
3. validate checked-in example report and manifest artifacts against their schemas
4. validate the checked-in decision-register export against `DECISION_REGISTER.md` and its schema
5. validate the checked-in open-questions export against `OPEN_QUESTIONS.md` and its schema
6. validate the checked-in Python importer fixture corpus and tier-specific required artifacts when that corpus exists
7. validate the checked-in TypeScript importer placeholder corpus through its active `validate-fixtures` checker
8. validate the checked-in Rust importer fixture corpus and tier-specific required artifacts when that corpus exists
9. require `rustc` and `cargo` before executing the Rust Phase 6A pipeline
10. validate the executable bootstrap importer, lowering, translation, and reconstruction path for the supported Python fixture slice
11. validate the executable Rust Phase 6A importer, lowering, translation, and Tier `A` reconstruction path
12. verify top-level doctrine files exist
13. verify benchmark doctrine files exist
14. verify workflow files exist
15. fail on missing or malformed contract files

## Blocking command

```bash
make validate
```

## Expansion rule

Executable validators and importer conformance checks already run under `make validate`, including the dormant TypeScript `validate-fixtures` gate. Further expansion must stay under the same top-level command contract rather than replacing the policy surface silently.
