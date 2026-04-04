# Validation Pipeline
Status: Normative

## Required steps

1. verify required files exist
2. parse all JSON schemas
3. validate checked-in example artifacts
4. validate derived exports
5. validate active and negative corpus manifests plus sweep manifests
6. validate the Python importer fixture corpus
7. validate the Rust importer fixture corpus
8. validate seeded invalid `SCIR-H` and `SCIR-L` examples
9. validate spec-completeness and identity checks
10. validate the active Python proof loop
11. run sweep smoke on the frozen Tier `A` micro corpus and compare against the latest successful baseline artifact when available
12. require `comparison_summary.json` and `contamination_report.json` for sweep smoke
13. fail on missing or malformed contract files
14. fail on regression deltas, preservation expectation drift, or unexpected diagnostic churn

## Blocking command

```bash
make validate
```

## Fast lanes

The quick gate is split into:

1. repo-contract checks
2. importer fixture conformance
3. bootstrap pipeline validation
4. sweep smoke plus regression, comparison, and contamination summaries

## SCIR-Hc Containment Lane

The dedicated containment lane must:

1. run `python -m unittest discover -s tests`
2. run `python scripts/scir_bootstrap_pipeline.py --mode validate`
3. run `python scripts/benchmark_contract_dry_run.py --claim-run`
4. run `python scripts/validate_repo_contracts.py --mode validate`
5. fail on unauthorized SCIR-Hc transform execution, incomplete lineage binding, invalid diff audit, metric-authority escalation, or missing containment artifacts
