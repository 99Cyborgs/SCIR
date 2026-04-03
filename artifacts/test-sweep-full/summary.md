# Sweep Summary: python-proof-loop-full

- run_id: `python-proof-loop-full-20260403T155418Z`
- corpus_id: `python-proof-loop-corpus`
- commit_sha: `427ecb865ab4184fbcb0014cd512d476fc4f124f`
- row_count: `22`

## Rankings

- most stable slice: `frontend=python|tier=A|profile=P|pipeline_stage=l_to_wasm|construct_family=branch-local-mutation|fixture_set=python-proof-loop` (score `100.0`)
- most failure-dense slice: `frontend=python|tier=C|profile=D-PY|pipeline_stage=source_to_h|construct_family=opaque-boundary|fixture_set=python-proof-loop` (density `1.0`)

## Stage Summary

- `h_to_l`: pass=4, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `h_to_python`: pass=4, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `l_to_wasm`: pass=2, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `scir_h_validation`: pass=4, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `scir_l_validation`: pass=4, warn=0, fail=0, skip=0; pass_rate=`1.0`; preservation_correctness=`1.0`
- `source_to_h`: pass=3, warn=1, fail=0, skip=0; pass_rate=`0.75`; preservation_correctness=`1.0`

## Diagnostic Codes

- `PY-C001`: `1`

## Preservation Breakdown

- `fixture.python_importer.a_async_await`: h_to_l=P1 (match), h_to_python=P1 (match), scir_h_validation=P1 (match), scir_l_validation=P1 (match), source_to_h=P1 (match)
- `fixture.python_importer.a_basic_function`: h_to_l=P1 (match), h_to_python=P1 (match), l_to_wasm=P2 (match), scir_h_validation=P1 (match), scir_l_validation=P1 (match), source_to_h=P1 (match)
- `fixture.python_importer.b_direct_call`: h_to_l=P1 (match), h_to_python=P1 (match), l_to_wasm=P2 (match), scir_h_validation=P1 (match), scir_l_validation=P1 (match), source_to_h=P1 (match)
- `fixture.python_importer.c_opaque_call`: h_to_l=P3 (match), h_to_python=P3 (match), scir_h_validation=P3 (match), scir_l_validation=P3 (match), source_to_h=P3 (match)
