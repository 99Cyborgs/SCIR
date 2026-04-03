# Benchmark Report

- run_id: `python-proof-loop-full-20260403T183642Z`
- corpus_manifest_hash: `sha256:0c3b78d3b092277d89bb79a7df485b3f794b3ae30668acbed4fba318b48e4398`
- claim_mode: `smoke`
- claim_class: `LEXICAL_COMPRESSION_ONLY`
- evidence_class: `['scirhc_lcr_vs_ast']`
- claim_gate: `supported`

## Representations

- explicit: `{'LCR': 1.6569, 'GR': 0.9545, 'SE': 0.213, 'SCPR': 1.0, 'round_trip': 1.0}`
- compressed: `{'LCR_scirhc': 1.8198, 'GR_scirhc': 0.9545, 'SCPR_scirhc': 1.0}`

## Claim Gate

- SCIR-Hc beats typed-AST on LCR. metric=`LCR_scirhc` delta=`-4.9474` threshold=`lt 0.0` passed=`True`

## Failure Attribution

- primary_cause=`unavoidable_explicitness`
- token_inflation=`0.0` structural_redundancy=`0.0` unavoidable_explicitness=`0.1611`

## Claims

- SCIR-Hc beats typed-AST on LCR. baseline=`typed-AST` metric=`LCR_scirhc` observed=`1.8198` delta=`-4.9474`

## Disclaimers

- Results are limited to the fixed Python proof-loop corpus and do not imply whole-language support.
- Wasm and reconstruction evidence remain profile-qualified and do not imply native or host parity.
- SCIR-Hc is a derived AI-facing form and must round-trip through canonical SCIR-H before downstream claims.
- Opaque or boundary-only cases remain present: fixture.python_importer.c_opaque_call
- Dataset split mode: simulated_no_training.
