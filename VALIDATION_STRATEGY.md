# VALIDATION_STRATEGY
Status: Normative

## Objective

Validation keeps the Python-first MVP executable while preserving the retained derivative surfaces without letting governance artifacts dominate the default gate.

## Default validation order

1. repository contract validation
2. active and negative corpus manifest validation
3. sweep manifest validation
4. Python importer fixture validation
5. Rust importer fixture validation
6. seeded invalid `SCIR-H` rejection
7. seeded invalid `SCIR-L` rejection
8. canonical formatter and identity stability checks
9. `SCIR-H` validation
10. `SCIR-Hc` derivation and round-trip validation
11. `H -> L` provenance and lowering-rule validation
12. `SCIR-L` validation
13. sweep smoke over the frozen Tier `A` micro corpus
14. admitted helper-free Wasm emission validation
15. Python reconstruction validation
16. retained Track `A` / `B` benchmark validation

## Validator stack

| Validator | Input | Output | Blocking |
| --- | --- | --- | --- |
| repository contract checker | live root docs, active support docs, schemas, examples, manifests, and command surfaces | console report | yes |
| importer conformance checker | fixed source subset plus checked-in bundle | `module_manifest`, `feature_tier_report`, `validation_report` | yes |
| `SCIR-H` validator | canonical `SCIR-H` | `validation_report` | yes |
| `SCIR-Hc` validator | derived `SCIR-Hc` plus canonical round-trip target | `validation_report` | yes |
| translation validator | paired `SCIR-H` and `SCIR-L` artifacts | `preservation_report` | yes on active lowering paths |
| `SCIR-L` validator | structured lowered module | `validation_report` | yes |
| Wasm emitter checker | admitted `SCIR-L` subset plus bounded backend contract | WAT text plus `preservation_report` | yes on admitted Wasm cases |
| reconstruction validator | canonical `SCIR-H` plus reconstructed Python | `reconstruction_report`, `preservation_report` | yes on active Python round trips |
| benchmark checker | retained Track `A` / `B` harness | benchmark outputs | yes |

## Blocking rules

A change must not merge when any of the following is true:

- `SCIR-H` claims a construct the parser does not accept
- `SCIR-Hc` drifts from canonical `SCIR-H` or becomes semantic authority
- `SCIR-L` introduces semantics without validated `SCIR-H` origin and lowering rule
- active importer fixtures drift from their checked-in bundles
- archived TypeScript placeholders drift back toward live tier, profile, or `SCIR-H` implications
- active manifests drift from their schemas or file hashes
- active preservation reports omit required path/profile/preservation fields
- active `P2` or `P3` preservation reports omit required downgrade evidence for their bounded claim
- admitted proof-loop `H -> L` shapes or translation-report evidence drift from the fixed lowering contract
- admitted proof-loop exceptional `H -> L` invoke/catch shape drifts from the fixed `d_try_except` lowering contract
- deferred Track `D` executable residue re-enters the active bootstrap pipeline surface
- the default gate silently reactivates release-bundle machinery or queue-era exports
- tracked generated artifacts re-enter the live repository surface

## Command contract

`make validate` remains the top-level blocking validation command.

At minimum it must:

- verify required docs, specs, schemas, scripts, and focused plans exist
- validate checked-in example reports against their schemas
- validate active corpus, invalid-fixture, and sweep manifests
- validate the Python importer fixture corpus
- validate the Rust importer fixture corpus
- validate invalid canonical `SCIR-H` examples
- validate invalid derivative `SCIR-L` examples
- validate canonical formatter round-trip and identity stability
- validate the active Python proof loop and retained derivative surfaces
- reject default-gate dependence on tracked run outputs
- keep the blocking repository-contract check aligned to the live surface rather than placeholder or archival docs

## Optional deeper validation

`python scripts/validate_repo_contracts.py --mode audit` remains the optional retained-surface audit for broader placeholder, tooling, CI, and archival docs kept on disk outside the default blocking surface.

`python scripts/run_repo_validation.py --require-rust` remains the optional compatibility entrypoint for environments that require an explicit usable Rust toolchain before running the deeper Rust slice, including the retained Rust pipeline self-tests.

`python scripts/benchmark_contract_dry_run.py --claim-run` remains an explicit opt-in claim lane.
It must fail unless the active continuation decision is `SCIR_NECESSARY`.

Default sweep and benchmark runs must overwrite stable ignored output directories unless an explicit `--output-dir` is supplied.

## Evidence for done

A validation-sensitive task is not done unless:

- touched specs and docs agree
- relevant schemas are current
- checked-in examples remain schema-valid
- invalid fixtures still fail
- `make validate` passes
