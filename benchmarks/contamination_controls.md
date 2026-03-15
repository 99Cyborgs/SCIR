# Contamination Controls
Status: Normative

## Rules

- hash every published corpus manifest,
- separate development, tuning, and held-out evaluation slices,
- record prompt templates and baseline adapters,
- avoid benchmark-specific prompt tuning that is unavailable to baselines,
- treat pretraining leakage risk as a reportable caveat, not a hidden variable,
- do not claim generalization from a contaminated or untracked dataset.

## Reporting minimum

Every benchmark result must record:

- corpus ID or hash,
- baseline set,
- tuning split if any,
- held-out evaluation split,
- known contamination caveats.
