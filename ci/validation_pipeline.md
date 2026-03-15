# Validation Pipeline
Status: Normative

## Required steps

1. verify required files exist
2. parse all JSON schemas
3. validate checked-in example report and manifest artifacts against their schemas
4. validate the checked-in decision-register export against `DECISION_REGISTER.md` and its schema
5. validate the checked-in open-questions export against `OPEN_QUESTIONS.md` and its schema
6. verify top-level doctrine files exist
7. verify benchmark doctrine files exist
8. verify workflow files exist
9. fail on missing or malformed contract files

## Blocking command

```bash
make validate
```

## Expansion rule

When executable validators land, they must be added under the same top-level command contract rather than replacing the policy surface silently.
