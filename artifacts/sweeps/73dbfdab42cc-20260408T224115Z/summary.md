# Sweep Summary: python-proof-loop-smoke

- run_id: `python-proof-loop-smoke-20260408T224115Z`
- corpus_id: `python-tier-a-micro-corpus`
- commit_sha: `73dbfdab42ccd9e9ee4e9d2ac4678ca22b394d1b`
- row_count: `15`

## Rankings

- most stable slice: `frontend=python|tier=A|split=test|profile=R|pipeline_stage=h_to_l|construct_family=async-await|fixture_set=python-tier-a` (score `100.0`)
- most failure-dense slice: `frontend=python|tier=A|split=test|profile=R|pipeline_stage=h_to_l|construct_family=async-await|fixture_set=python-tier-a` (density `0.0`)

## Stage Summary

- `h_to_l`: pass=3, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `h_to_python`: pass=3, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `scir_h_validation`: pass=3, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `scir_l_validation`: pass=3, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `source_to_h`: pass=3, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`

## Diagnostic Codes

- none

## Preservation Breakdown

- `fixture.python_importer.a_async_await`: h_to_l=P1 (match), h_to_python=P1 (match), scir_h_validation=P1 (match), scir_l_validation=P1 (match), source_to_h=P1 (match)
- `fixture.python_importer.a_basic_function`: h_to_l=P1 (match), h_to_python=P1 (match), scir_h_validation=P1 (match), scir_l_validation=P1 (match), source_to_h=P1 (match)
- `fixture.python_importer.b_direct_call`: h_to_l=P1 (match), h_to_python=P1 (match), scir_h_validation=P1 (match), scir_l_validation=P1 (match), source_to_h=P1 (match)
