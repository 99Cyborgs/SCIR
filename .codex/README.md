# SCIR Codex Surface

This repo-local `.codex` surface is a bounded execution harness for the admitted SCIR MVP.

## Tranche operator pack

Start new governed work with:

1. `scir-repo-contract-audit`
2. `scir-queue-reactivation` when queue or successor state is stale, empty, or contradictory
3. `scir-provenance-continuity` when the tranche touches `source -> SCIR-H -> SCIR-L -> reconstruction` lineage or translation evidence

These skills are not a general repo autopilot. They fail closed outside the current MVP boundary:

- `SCIR-H` is the only normative semantic authority
- `SCIR-L` is derivative-only
- queue re-entry must stay export-synchronized and fail-closed
- deferred frontend, backend, Track `D`, and broad platform work stay out of scope

## Related SCIR skills

Use the existing auditors when the tranche crosses their exact governed surface:

- `scir-proof-loop-guard`
- `scir-spec-sync`
- `scir-lowering-provenance-check`
- `scir-importer-boundary-auditor`
- `scir-benchmark-claim-auditor`
- `scir-tier-profile-auditor`

## Templates

`.codex/templates/` contains minimal report shells for tranche PRs, fail-closed stops, and closeouts.

These templates are operator aids only. They are not semantic authority and do not override root governance docs, specs, schemas, queue exports, or validator outputs.
