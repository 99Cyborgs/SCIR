# Benchmark Report

- run_id: `python-proof-loop-full-20260403T193554Z`
- corpus_manifest_hash: `sha256:0c3b78d3b092277d89bb79a7df485b3f794b3ae30668acbed4fba318b48e4398`
- claim_mode: `smoke`
- representation: `SCIR-Hc`
- claim_class: `LEXICAL_COMPRESSION_ONLY`
- evidence_class: `['scirhc_lcr_vs_ast']`
- claim_gate: `supported`

## Representations

- explicit: `{'LCR': 1.6569, 'GR': 0.9545, 'SE': 0.213, 'SCPR': 1.0, 'round_trip': 1.0}`
- compressed: `{'LCR_scirhc': 1.8198, 'GR_scirhc': 0.9545, 'SCPR_scirhc': 1.0}`

## Canonical Lineage

- fixture.python_importer.a_async_await => `{'semantic_lineage_id': 'a98fe0c337795cf2ba3402bfbfa922b148e80c5523cb607e04b24d6ebc8c3621', 'normalized_canonical_hash': '6e8964fe70a9042ca8a380ae2368c8fb158f0d38961afecaeed7d9751f26a80d'}`
- fixture.python_importer.a_basic_function => `{'semantic_lineage_id': '3c587f53a4b9d222de6d7d030596f12f8a39099043b9ac1a71676944527aeeb4', 'normalized_canonical_hash': '86137dfe16e2e3c3adcaa519a6e3e4dadb1278c15d6312dc7d133057b73d8e8a'}`
- fixture.python_importer.b_direct_call => `{'semantic_lineage_id': '32009e343204bc239d85132dc1f12a65d5ea6a26142aea581aae370f373a1aa8', 'normalized_canonical_hash': '48439b8a2176c9799913384e0ec741f803c477532460174bea3b4c559098c7e2'}`
- fixture.python_importer.c_opaque_call => `{'semantic_lineage_id': '5c5cd930bece6767ffe7f7c773154b77e4c2f1a95d3c577a5dae9f7d5855e9f3', 'normalized_canonical_hash': '4e6709db6556d10523eb0c0ba9f6b6cf511c6795219650605071a7e007ac40d1'}`

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
