# Reports
Status: Informative

This directory holds schema-valid example artifacts and derived exports.

## Current contents

- `examples/`: illustrative report and manifest fixtures
- `exports/`: derived exports whose source of truth remains markdown

`reports/exports/checkpoint_closeout.export.json` is the canonical machine-readable checkpoint snapshot for an empty-by-design queue. It binds queue state, decision refs, evidence refs, validation context, residual risks, and re-entry conditions into one auditable closeout artifact, and it supersedes any earlier dirty workspace capture only by preserving that prior checkpoint's provenance inside the canonical baseline export.

## Rule

Example artifacts are illustrative fixtures, not proof of implementation breadth. They must not overstate support, preservation, or benchmark success.

## Active preservation examples

- source to `SCIR-H`
- `SCIR-H` to `SCIR-L`
- `SCIR-H` to Python reconstruction
- `SCIR-L` to Wasm contract emission
- `SCIR-L` to backend translation validation

## Conditional benchmark examples

- `benchmark_track_c_manifest.example.json`
- `benchmark_track_c_result.example.json`
- `benchmark_track_c_refresh_provenance.example.md`

## Corpus and sweep examples

- `corpus_manifest.example.json`
- `sweep_manifest.example.json`
- `sweep_result.example.json`
- `sweep_summary.example.json`
- `regression_summary.example.json`
- `comparison_summary.example.json`
- `contamination_report.example.json`
- `benchmark_report.example.json`

`benchmark_report.example.json` now separates canonical explicit `SCIR-H` metrics from compressed `SCIR-Hc` metrics, records claim-gate evaluation plus failure attribution, and declares `claim_class` / `evidence_class` so compressed evidence cannot over-claim.

Track `C` benchmark samples are illustrative only and do not belong to the default executable benchmark gate.
They mirror the bounded output of the non-default executable pilot, remain outside the default benchmark bundle, and support a retained diagnostic posture rather than a promotion claim.
Any non-editorial refresh to those Track `C` samples must cite the opt-in regeneration command, the matching opt-in validation command, the regenerated corpus hash, and the regenerated `run_id` plus `system_under_test`.

Use this exact minimal note shape when recording that provenance:

```md
# Track C Sample Refresh Provenance
- regeneration_command: `python scripts/benchmark_contract_dry_run.py --include-track-c-pilot`
- validation_command: `python scripts/run_repo_validation.py --include-track-c-pilot`
- manifest_corpus_hash: `sha256:<regenerated-corpus-hash>`
- result_run_id: `<regenerated-run-id>`
- system_under_test: `<regenerated-system-under-test>`
```

The checked-in note for the retained sample bundle lives at `reports/examples/benchmark_track_c_refresh_provenance.example.md` so it remains adjacent to the Track `C` sample manifest and result.
Any non-editorial refresh replaces the entire checked-in note at that fixed path; it does not append historical entries or create sibling note variants for the retained sample bundle.
