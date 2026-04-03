# Benchmark Report

- run_id: `python-proof-loop-full-20260403T165339Z`
- corpus_manifest_hash: `sha256:0c3b78d3b092277d89bb79a7df485b3f794b3ae30668acbed4fba318b48e4398`
- claim_mode: `smoke`

## Claims

- Aggregate LCR delta vs direct source was measured for the fixed proof-loop corpus. baseline=`direct source` metric=`LCR` observed=`1.6569` delta=`0.6569`
- Aggregate round-trip delta vs direct source was measured for the fixed proof-loop corpus. baseline=`direct source` metric=`round_trip` observed=`1.0` delta=`0.0`
- Aggregate LCR delta vs typed-AST was measured for the fixed proof-loop corpus. baseline=`typed-AST` metric=`LCR` observed=`1.6569` delta=`-5.1103`
- Aggregate round-trip delta vs typed-AST was measured for the fixed proof-loop corpus. baseline=`typed-AST` metric=`round_trip` observed=`1.0` delta=`0.0`
- Aggregate LCR delta vs lightweight regularized core or s-expression was measured for the fixed proof-loop corpus. baseline=`lightweight regularized core or s-expression` metric=`LCR` observed=`1.6569` delta=`0.6569`
- Aggregate round-trip delta vs lightweight regularized core or s-expression was measured for the fixed proof-loop corpus. baseline=`lightweight regularized core or s-expression` metric=`round_trip` observed=`1.0` delta=`0.0`

## Disclaimers

- Results are limited to the fixed Python proof-loop corpus and do not imply whole-language support.
- Wasm and reconstruction evidence remain profile-qualified and do not imply native or host parity.
- Opaque or boundary-only cases remain present: fixture.python_importer.c_opaque_call
- Dataset split mode: simulated_no_training.
