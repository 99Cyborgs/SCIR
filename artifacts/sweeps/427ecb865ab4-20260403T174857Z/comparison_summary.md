# Comparison Summary

- run_id: `python-proof-loop-smoke-20260403T174857Z`
- corpus_manifest_hash: `sha256:71b2ed0546551abf292b4ad1ee5912546386936f547c4925a856f6488dbd22a4`
- metrics: `LCR, GR, SE, SCPR, round_trip, LCR_scirhc, GR_scirhc, SCPR_scirhc`

## Aggregate Deltas

- `delta_vs_source`: `{'LCR': 0.4912, 'GR': 0.0, 'SE': 0.0779, 'SCPR': 0.0, 'round_trip': 0.0, 'LCR_scirhc': 0.3158, 'GR_scirhc': 0.0, 'SCPR_scirhc': 0.0}`
- `delta_vs_ast`: `{'LCR': -5.4035, 'GR': 0.0, 'SE': 0.1475, 'SCPR': 0.0, 'round_trip': 0.0, 'LCR_scirhc': -5.5789, 'GR_scirhc': 0.0, 'SCPR_scirhc': 0.0}`
- `delta_vs_normalized`: `{'LCR': 0.4912, 'GR': 0.0, 'SE': 0.0428, 'SCPR': 0.0, 'round_trip': 0.0, 'LCR_scirhc': 0.3158, 'GR_scirhc': 0.0, 'SCPR_scirhc': 0.0}`

## Tolerance Failures

- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=async-await|fixture_set=python-tier-a` vs `direct source` metric `LCR`: delta `0.4737` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=async-await|fixture_set=python-tier-a` vs `direct source` metric `LCR_scirhc`: delta `0.1053` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=async-await|fixture_set=python-tier-a` vs `lightweight regularized core or s-expression` metric `LCR`: delta `0.4737` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=async-await|fixture_set=python-tier-a` vs `lightweight regularized core or s-expression` metric `LCR_scirhc`: delta `0.1053` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=branch-local-mutation|fixture_set=python-tier-a` vs `direct source` metric `LCR`: delta `0.4737` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=branch-local-mutation|fixture_set=python-tier-a` vs `direct source` metric `LCR_scirhc`: delta `0.4211` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=branch-local-mutation|fixture_set=python-tier-a` vs `lightweight regularized core or s-expression` metric `LCR`: delta `0.4737` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=branch-local-mutation|fixture_set=python-tier-a` vs `lightweight regularized core or s-expression` metric `LCR_scirhc`: delta `0.4211` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=direct-call|fixture_set=python-tier-a` vs `direct source` metric `LCR`: delta `0.5263` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=direct-call|fixture_set=python-tier-a` vs `direct source` metric `LCR_scirhc`: delta `0.4211` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=direct-call|fixture_set=python-tier-a` vs `lightweight regularized core or s-expression` metric `LCR`: delta `0.5263` beyond tolerance `0.1`
- `frontend=python|tier=A|split=test|profile=R|pipeline_stage=source_to_h|construct_family=direct-call|fixture_set=python-tier-a` vs `lightweight regularized core or s-expression` metric `LCR_scirhc`: delta `0.4211` beyond tolerance `0.1`

## Contamination Flags

- none
