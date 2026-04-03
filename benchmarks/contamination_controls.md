# Contamination Controls
Status: Normative

## Rules

- hash every published corpus manifest,
- enforce explicit train/dev/test membership with no overlap,
- record prompt templates and baseline adapters,
- avoid benchmark-specific prompt tuning that is unavailable to baselines,
- emit `duplicates`, `near_duplicates`, and `leakage_flags` in `contamination_report.json`,
- freeze manifests as immutable once a reporting run locks them in `manifest_lock.json`,
- treat pretraining leakage risk as a reportable caveat, not a hidden variable,
- do not claim generalization from a contaminated or untracked dataset.

## Reporting minimum

Every benchmark result must record:

- corpus ID or hash,
- baseline set,
- tuning split if any,
- held-out evaluation split,
- contamination report findings,
- known contamination caveats.

The current executable Track `A` and Track `B` manifests for the fixed bootstrap corpus must still carry explicit contamination-control metadata even though the corpus is intentionally small and fixed.
