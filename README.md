# SCIR

SCIR is a two-layer semantic substrate.

- `SCIR-H` is the only normative semantic authority.
- `SCIR-L` is derivative-only lowering justified by validated `SCIR-H`.

## Active MVP lane

The live implementation target is:

`Python subset importer -> canonical SCIR-H -> validator hardening`

Maintained but frozen support surfaces remain on disk:

- bounded `SCIR-H -> SCIR-L` lowering
- bounded Rust importer evidence
- bounded Wasm reference backend
- Track `A` and Track `B` benchmark harnesses

Those surfaces are retained, but they are not the current scope-expansion target.

## Live surface

The default working set is:

- `README.md`
- `ARCHITECTURE.md`
- `CURRENT_FOCUS.md`
- `BACKLOG.md`
- `DECISION_REGISTER.md`
- `docs/`
- `specs/`
- `scir/`
- `scripts/`
- `tests/`
- `schemas/`
- `reports/examples/`

Tracked generated run outputs are intentionally excluded from the live surface.
The canonical gate still exercises retained Rust, Wasm, and benchmark support lanes, but broader placeholder, tooling, CI, and archival consistency checks now live behind `python scripts/validate_repo_contracts.py --mode audit`.

## Commands

```bash
python scripts/run_repo_validation.py
python scripts/run_repo_validation.py --require-rust
python scripts/validate_repo_contracts.py --mode audit
make build
make lint
make test
make validate
make benchmark
make benchmark-claim
```

`python scripts/run_repo_validation.py` is the canonical default gate.
Default validation and benchmark runs overwrite stable ignored output paths under `artifacts/validation/`, `artifacts/sweeps/latest`, and `artifacts/benchmark_runs/latest`; pass `--output-dir` when a run needs its own retained directory.

## Operating rules

- widen grammar only through spec-first changes
- keep release-bundle machinery opt-in only
- keep `SCIR-H` normative and `SCIR-L` derivative
- prefer modifying existing architecture over adding new control surfaces

## Current navigation

- [CURRENT_FOCUS.md](CURRENT_FOCUS.md) names the one active bounded item
- [BACKLOG.md](BACKLOG.md) ranks deferred work
- [ARCHITECTURE.md](ARCHITECTURE.md) defines the stable system shape
- [VALIDATION_STRATEGY.md](VALIDATION_STRATEGY.md) defines the default gate
- [reports/repo_reset_report.md](reports/repo_reset_report.md) records the consolidation decisions for this reset
- [reports/repo_reset_followthrough.md](reports/repo_reset_followthrough.md) records the post-reset cleanup that closed the remaining gaps
