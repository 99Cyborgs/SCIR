# AGENTS.md
Status: Normative

## Project overview

SCIR is a two-layer semantic substrate.

- `SCIR-H`: canonical semantic authority
- `SCIR-L`: derivative lowering form justified by validated `SCIR-H`

## Source authority order

Use this order when files disagree:

1. `specs/`
2. `schemas/`
3. executable code under `scripts/`, `validators/`, `runtime/`, and `scir/`
4. root architecture and validation docs
5. benchmark and planning notes

Do not silently merge incompatible semantics. Record unresolved conflicts in `OPEN_QUESTIONS.md`.

## Read first

Always read these before coding:

1. `SYSTEM_BOUNDARY.md`
2. `CURRENT_FOCUS.md`
3. `ARCHITECTURE.md`
4. `README.md`
5. `specs/scir_h_spec.md`
6. `specs/scir_l_spec.md`
7. `specs/type_effect_capability_model.md`
8. `specs/ownership_alias_model.md`
9. `specs/interop_and_opaque_boundary_spec.md`
10. `specs/validator_invariants.md`
11. `docs/target_profiles.md`
12. `docs/preservation_contract.md`
13. `docs/feature_tiering.md`
14. `VALIDATION_STRATEGY.md`

Read the nearest local `AGENTS.md` before editing inside a subtree.

## Commands

Use the repository root.

Canonical Windows-safe validation entrypoint:

```bash
python scripts/run_repo_validation.py
```

Full Rust-inclusive validation entrypoint:

```bash
python scripts/run_repo_validation.py --require-rust
```

Top-level command contract:

```bash
make build
make lint
make test
make validate
make benchmark
make ci
```

Do not replace these commands without updating `README.md`, this file, and CI workflow docs.
`make build` must produce a real package-build sanity artifact under `artifacts/build`.
`make lint` must remain a real static check over tracked Python sources, not a repo-contract alias.

Optional retained-surface audit:

```bash
python scripts/validate_repo_contracts.py --mode audit
```

## When you must consult `IMPLEMENTATION_PLAN.md`

Consult it before:

- changing phase ordering
- reactivating or adding a frontend, backend, validator, or benchmark track
- widening scope beyond the current credible build path

## When you must consult `plans/PLANS.md`

Create or update a plan before work that:

- touches 3 or more files
- changes `specs/` or `schemas/`
- changes validator behavior
- changes target profiles, preservation levels, feature tiers, or unsupported-case handling
- changes benchmark manifests, gates, or baselines
- introduces a new directory or tool contract

Use the exact plan template in `plans/PLANS.md`.

## Hard constraints

- Do not invent unsupported semantics.
- Do not downgrade explicit unsupported cases into implicit support.
- Do not move semantics from `SCIR-H` into `SCIR-L` only.
- Do not claim preservation without a profile and preservation level.
- Do not hide unsafe, foreign, host, or opaque boundaries.
- Do not widen grammar without updating the normative specs first.
- Do not activate release-bundle machinery by default.

## Change discipline

Every architecture-affecting change must update the relevant set of files.

- `SCIR-H` semantics change:
  - `specs/scir_h_spec.md`
  - `docs/scir_h_overview.md`
  - `ARCHITECTURE.md`
  - `validators/validator_contracts.md`
  - `specs/validator_invariants.md`
  - `VALIDATION_STRATEGY.md`
  - `DECISION_REGISTER.md`
- `SCIR-L` semantics change:
  - `specs/scir_l_spec.md`
  - `docs/scir_l_overview.md`
  - `ARCHITECTURE.md`
  - `validators/validator_contracts.md`
  - `specs/validator_invariants.md`
  - `VALIDATION_STRATEGY.md`
  - `DECISION_REGISTER.md`
- target profiles or preservation change:
  - `docs/target_profiles.md`
  - `docs/preservation_contract.md`
  - `BENCHMARK_STRATEGY.md`
  - `benchmarks/success_failure_gates.md`
  - `DECISION_REGISTER.md`
- feature tier or unsupported-case change:
  - `docs/feature_tiering.md`
  - `docs/unsupported_cases.md`
  - relevant `frontend/*/IMPORT_SCOPE.md`
  - `BENCHMARK_STRATEGY.md`
  - `OPEN_QUESTIONS.md` if unresolved
- schema change:
  - changed file in `schemas/`
  - any markdown file that defines or consumes the schema
  - `VALIDATION_STRATEGY.md` or `BENCHMARK_STRATEGY.md`
  - CI if validation behavior changes

## Definition of done

A task is done only when all are true:

1. touched specs and docs agree
2. local `AGENTS.md` rules were followed
3. preservation/profile/tier implications are explicit
4. unsupported and opaque cases are explicit
5. required schemas or report contracts are updated
6. `make validate` passes
7. `DECISION_REGISTER.md` is updated if architecture changed
8. `OPEN_QUESTIONS.md` is updated if ambiguity remains
9. completion evidence is recorded in the active plan

## Default operating posture

Prefer the narrow credible path:

- Python subset importer first
- `SCIR-H` validator hardening before scope widening
- keep `SCIR-L` derivative and subset-bound
- treat Rust, Wasm, and benchmarks as maintained support surfaces unless `CURRENT_FOCUS.md` says otherwise

## Canonical labels

Preservation labels: `P0`, `P1`, `P2`, `P3`, `PX`.
Feature tiers: `Tier A`, `Tier B`, `Tier C`, `Tier D`.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **SCIR** (1835 symbols, 4270 relationships, 136 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/SCIR/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/SCIR/context` | Codebase overview, check index freshness |
| `gitnexus://repo/SCIR/clusters` | All functional areas |
| `gitnexus://repo/SCIR/processes` | All execution flows |
| `gitnexus://repo/SCIR/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
