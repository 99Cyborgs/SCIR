# VALIDATION

## Canonical MVP validation path

Use the Windows-safe MVP runner:

```bash
python scripts/run_repo_validation.py
```

This command validates:

- repository contracts
- derived exports
- Python importer fixture integrity
- Rust importer fixture integrity
- active and negative corpus manifest integrity
- seeded invalid `SCIR-H` and `SCIR-L` invariant corpora
- slice-based sweep smoke over the fixed Python Tier `A` corpus with persisted artifacts, summaries, and regression comparison when a baseline is available
- the admitted helper-free Wasm emitter slice
- execution-backed translation validation for the admitted helper-free Wasm slice
- the active Python proof loop
- the active Track `A` / Track `B` benchmark harness

## Underlying validation commands

```bash
python scripts/validate_repo_contracts.py --mode validate
python scripts/build_execution_queue.py --mode check
python scripts/python_importer_conformance.py --mode validate-fixtures
python scripts/rust_importer_conformance.py --mode validate-fixtures
python scripts/scir_bootstrap_pipeline.py --mode validate
python scripts/validate_translation.py
python scripts/scir_sweep.py --manifest tests/sweeps/python_proof_loop_smoke.json
python scripts/benchmark_contract_dry_run.py
python scripts/benchmark_contract_dry_run.py --claim-run
python scripts/benchmark_repro.py --run-id <run-id>
```

## Generated artifact synchronization

When Python proof-loop metadata or bounded Track `C` sample-producing logic changes, refresh the checked-in generated artifacts before rerunning validation:

```bash
python scripts/sync_python_proof_loop_artifacts.py --mode check
python scripts/sync_python_proof_loop_artifacts.py --mode write
```

## Optional importer-first Rust validation

The default MVP gate does not require a Rust toolchain.
When a usable toolchain is available, the optional Rust slice validates the importer-first Rust path only:

- Rust fixture import
- canonical `SCIR-H` validation
- bounded `SCIR-H -> SCIR-L` lowering
- `SCIR-L` validation
- helper-free Wasm emission for the admitted Rust local-mutation case
- execution-backed translation validation for the admitted Rust helper-free Wasm slice
- path-qualified Rust `H -> L` preservation reporting

Command:

```bash
python scripts/run_repo_validation.py --require-rust
```

## Optional non-default Track C validation

The default MVP gate still stops at executable Track `A` and Track `B`.
When explicitly requested, the bounded Track `C` pilot runs over the same fixed Python repair cases without changing the default gate:

```bash
python scripts/benchmark_contract_dry_run.py --include-track-c-pilot
python scripts/run_repo_validation.py --include-track-c-pilot
```

That opt-in pilot keeps `c_opaque_call` boundary-accounting-only and leaves `make benchmark` unchanged.

Explicit benchmark claims still require the dedicated claim lane:

```bash
python scripts/benchmark_contract_dry_run.py --claim-run
```

Deferred or archived surfaces that stay on disk are marked with `NOT_ACTIVE.md` and remain outside the default gate.
