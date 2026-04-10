# Reports
Status: Informative

This directory is intentionally small.

## Current contents

- `examples/`: curated schema-valid example artifacts
- `repo_reset_report.md`: the current repository consolidation report
- `repo_reset_followthrough.md`: the follow-through pass that closed the remaining reset gaps

## Rules

- examples are illustrative fixtures, not breadth claims
- repeated run outputs belong under ignored `artifacts/`, not here
- default sweep and benchmark runs overwrite stable ignored paths unless an explicit `--output-dir` is requested
- derived exports are not part of the live repository surface
- release-oriented bundles remain opt-in only

Track `C` sample artifacts are illustrative only and do not belong to the default executable benchmark gate.
They support a retained diagnostic posture rather than a promotion claim.
Any non-editorial refresh to those Track `C` samples must cite the opt-in regeneration command, the matching opt-in validation command, the regenerated corpus hash, and the regenerated `run_id` plus `system_under_test`.

- `benchmark_report.example.json`
- `comparison_summary.example.json`
- `contamination_report.example.json`
