# BENCHMARK_STRATEGY
Status: Normative

## Objective

SCIR must be benchmarked against strong baselines before any AI-facing or performance claim is accepted.

## Mandatory benchmark tracks

- Track `A` — representation regularity and compression
- Track `B` — round-trip fidelity and reconstruction quality
- Track `C` — AI generation, editing, and repair
- Track `D` — compiler and runtime performance

See `benchmarks/tracks.md`.

## Mandatory baselines

At minimum every relevant benchmark must include:

- direct-source workflow baseline,
- canonical typed-AST baseline,
- SSA-like or backend-IR baseline where relevant,
- MLIR-style dialect-only baseline where relevant,
- lightweight regularized core or s-expression baseline where relevant.

See `benchmarks/baselines.md`.

## Benchmark rules

- Every run uses a `benchmark_manifest`.
- Every result bundle uses a `benchmark_result`.
- Every reported claim must reference a named baseline.
- Every benchmark must state the strongest baseline for that task family.
- Every benchmark must specify contamination controls.
- Every benchmark must state success gates and kill criteria.

## Required interpretation discipline

- If typed-AST or direct-source baselines match SCIR within confidence intervals, treat that as evidence against the AI-facing thesis.
- If Track `B` and Track `D` are positive but Track `C` is null, narrow toward compiler/tooling infrastructure.
- If Track `C` is positive only after manual curation unavailable in real repositories, do not claim general AI value.
- If opaque or unsupported fractions dominate the targeted corpus, treat benchmark wins as non-general.

## Profile and preservation discipline

Benchmark results must be annotated with:

- active profile (`R`, `N`, `P`, `D`),
- preservation level ceiling (`P0`–`PX`),
- source tier distribution (`A`–`D`),
- opaque boundary fraction.

## Minimum success and kill rules

Canonical thresholds are defined in `benchmarks/success_failure_gates.md`.

Repository-wide interpretation:

- continue on AI-facing path only if Track `C` shows a material win over the strongest baseline,
- continue on infrastructure path if Tracks `B` and `D` are useful but Track `C` is null,
- narrow or terminate if kill criteria are hit.

## Command contract

`make benchmark` currently performs a doctrine dry run. When the executable harness lands, the command must continue to be the single top-level benchmark entry point.
