# Reports
Status: Informative

This directory holds schema-valid example artifacts and derived exports.

## Current contents

- `examples/`: illustrative report and manifest fixtures
- `exports/`: derived exports whose source of truth remains markdown

## Rule

Example artifacts are illustrative fixtures, not proof of implementation breadth. They must not overstate support, preservation, or benchmark success.

## Active preservation examples

- source to `SCIR-H`
- `SCIR-H` to `SCIR-L`
- `SCIR-H` to Python reconstruction
- `SCIR-L` to Wasm contract emission

## Conditional benchmark examples

- `benchmark_track_c_manifest.example.json`
- `benchmark_track_c_result.example.json`

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
