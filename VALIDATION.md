# VALIDATION

## Canonical repo validation path

Use the Windows-safe validation runner:

```bash
python scripts/run_repo_validation.py
```

This runner is the canonical Windows-safe portfolio baseline for repo-local staging.
It always runs the repository contract, Python importer, Python bootstrap, and benchmark-contract checks.
The repository contract slice includes synchronized derived exports for the decision register, open questions, and autonomous execution queue.
On Windows, the runner probes whether the active Rust toolchain is actually usable and may apply a repo-local `RUSTUP_TOOLCHAIN` fallback to the installed MSVC toolchain for subprocesses only.
If no usable Rust toolchain is available, the Rust validation slice is reported as skipped rather than failing silently.

Use the full Rust-inclusive validation path when Rust work is in scope:

```bash
python scripts/run_repo_validation.py --require-rust
```

## Portfolio governance check

These governance notes are valid only if they remain consistent with:

- `SYSTEM_BOUNDARY.md`
- `ARCHITECTURE.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`

## Underlying validation commands

```bash
python scripts/validate_repo_contracts.py --mode validate
python scripts/build_execution_queue.py --mode check
python scripts/python_importer_conformance.py --mode validate-fixtures
python scripts/scir_bootstrap_pipeline.py --mode validate
python scripts/benchmark_contract_dry_run.py
```

Optional Rust slice:

```bash
python scripts/rust_importer_conformance.py --mode validate-fixtures
python scripts/scir_bootstrap_pipeline.py --language rust --mode validate
```

Direct benchmark validation still requires a usable Rust toolchain for the Rust Track `D` executable slice:

```bash
python scripts/benchmark_contract_dry_run.py
```

Do not treat SCIR as promotion-ready if those validation surfaces are not credible for the proposed extraction target.
