# Repository Reset Follow-Through

## Objective

Close the remaining post-reset gaps so `main` is the only credible operating authority and the public repo surface matches actual executable behavior.

## What changed

- deleted the stale local and remote `codex/02b-validation-closeout` and `codex/validation-hardening-worktree` branches after confirming they were obsolete
- split `scripts/validate_repo_contracts.py` into:
  - `--mode validate` for the default live blocking surface
  - `--mode audit` for retained placeholder, tooling, CI, and archival consistency checks
- replaced fake `make build` / `make lint` aliases with real command surfaces:
  - `scripts/run_repo_build.py`
  - `scripts/run_repo_lint.py`
- removed the nonexistent `runtime*` package claim from `pyproject.toml`
- added `_internal*` to the packaged Python surface because the repo’s executable scripts import it directly
- removed the `runtime/` working-surface claim from `REPO_MAP.md`
- changed default sweep and benchmark outputs to stable overwrite paths instead of timestamped accumulation:
  - `artifacts/validation/sweep-smoke`
  - `artifacts/validation/benchmark-smoke`
  - `artifacts/sweeps/latest`
  - `artifacts/benchmark_runs/latest`
  - `artifacts/benchmark_runs/claim`
- updated root and CI-facing docs to describe the live-surface gate, the retained-surface audit, the real build/lint commands, and the stable artifact retention behavior

## Branch cleanup outcome

- inspected `origin/main..origin/codex/validation-hardening-worktree`
- salvaged no additional changes from that branch
- reason:
  - the remaining branch-only delta was dominated by tracked artifacts, queue-era files, release-bundle machinery, exported reports, and broader governance/doc sprawl
  - none of that improved the narrow post-reset executable path enough to justify retaining the branch as authority
- local stale branches removed: yes
- remote stale branches removed: yes

## Default gate outcome

`python scripts/validate_repo_contracts.py --mode validate` now blocks on the real live surface:

- root operating docs
- active support docs under `docs/`
- normative `specs/`
- active `schemas/`
- executable scripts on the hot path
- `reports/examples/`
- active corpora, invalid manifests, and sweep manifests
- TypeScript quarantine markers that still matter to the live repo boundary

`python scripts/validate_repo_contracts.py --mode audit` now covers broader retained surfaces that stay on disk but are no longer part of the default blocking path:

- placeholder frontend docs
- retained benchmark/backend/tooling/CI docs
- retained TypeScript placeholder docs
- auxiliary repository navigation docs

## Command contract outcome

- `make build` now routes to `python scripts/run_repo_build.py` and produces a wheel under `artifacts/build`
- `make lint` now routes to `python scripts/run_repo_lint.py` and performs a real tracked-Python syntax/static check
- `make test`, `make validate`, `make benchmark`, and `make benchmark-claim` remain, but their documented behavior is now aligned to actual scripts rather than contract-check theater

## Package surface outcome

- removed `runtime*` from `pyproject.toml`
- kept `benchmarks*`, `scir*`, and `validators*`
- added `_internal*` because it is an actual importable source surface used by executable scripts
- no runtime package surface was created because the repo did not contain a legitimate runtime source module worth preserving

## Artifact hygiene outcome

- default repeated validation no longer creates a new timestamped sweep or benchmark directory on each run
- stable ignored output paths are overwritten unless an explicit `--output-dir` is requested
- retained per-run history is still available when the operator opts into an explicit output path

## Commands run

```bash
python scripts/run_repo_lint.py
python scripts/run_repo_build.py
python scripts/validate_repo_contracts.py --mode validate
python scripts/validate_repo_contracts.py --mode test
python scripts/validate_repo_contracts.py --mode audit
git branch -D codex/02b-validation-closeout codex/validation-hardening-worktree
git push origin --delete codex/02b-validation-closeout codex/validation-hardening-worktree
git fetch --prune origin
python scripts/run_repo_validation.py
```

`make` is not installed in this environment, so the real build/lint targets were validated by running their underlying scripts directly.

## Result

The repo is materially closer to a truthful implementation-led mainline than it was after the initial reset.
`main` is now the only credible operating authority, the default blocking repo-contract check matches the live surface much more closely, fake command/package claims were removed, and default validation no longer repollutes the workspace with unbounded timestamped sweep/benchmark directories.
