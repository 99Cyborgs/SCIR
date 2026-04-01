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

- active profile (`R`, `N`, `P`, `D-PY`, `D-JS`),
- preservation level ceiling (`P0`–`PX`),
- source tier distribution (`A`–`D`),
- opaque boundary fraction.

## Minimum success and kill rules

Canonical thresholds are defined in `benchmarks/success_failure_gates.md`.

For executable Track `A` automation:

- `S3` and `K2` are evaluated on median token ratios, not aggregate ratios,
- aggregate token ratios remain diagnostic only,
- automated benchmark status fails if an automated kill gate is hit, even if a separate success limb passes.

For executable Track `B` automation on the fixed bootstrap corpus:

- status is governed by `S1`, `S4`, `K3`, and `K4`,
- Tier `A` compile/test rates are the blocking fidelity signal,
- idiomaticity remains required evidence but is not a separate hard gate.

For executable Track `D` automation on the fixed bootstrap corpora:

- status is profile-separated and governed by `S5` and `K8`,
- Rust `N` and Python `D-PY` emit separate manifests and results,
- `D-JS` remains doctrine-only and must not emit executable result bundles,
- code size and memory remain required diagnostics, but are not blocking in the first Track `D` cut.

Repository-wide interpretation:

- continue on AI-facing path only if Track `C` shows a material win over the strongest baseline,
- continue on infrastructure path if Tracks `B` and `D` are useful but Track `C` is null,
- narrow or terminate if kill criteria are hit.

Rust Phase 6A adds no executable benchmark outputs. Phase 6B widens benchmark scope only to fixed Rust `N` and Python `D-PY` Track `D` slices; it does not make `D-JS` or witness-bearing second-language execution canonical.

The post-6B roadmap keeps this benchmark boundary explicit:

- Python Milestone 02B may widen importer evidence without widening executable benchmark corpora,
- the default Phase 7 TypeScript witness slice does not emit executable `D-JS` result bundles,
- a later milestone must publish explicit benchmark gates before any executable `D-JS` claim is valid.

Importer-only Python follow-on cases such as `b_if_else_return`, `b_direct_call`, `b_async_arg_await`, and `d_try_except` may emit canonical `SCIR-H`, but they remain outside the fixed executable Track `A`, `B`, and `D` corpora until lowering and reconstruction evidence exists for those cases.

## Command contract

`make benchmark` performs doctrine checks plus manifest-driven Track `A`, Track `B`, and fixed-corpus Track `D` execution. Track `A` emits both median and aggregate token-ratio diagnostics while applying success and kill gates against the median measures. Track `D` emits separate Rust `N` and Python `D-PY` result bundles and keeps `D-JS` doctrine-only. The command remains the single top-level benchmark entry point.

When `make` is unavailable, `python scripts/benchmark_contract_dry_run.py` is the direct executable fallback for the current Windows shell.

Generated Track `A`, Track `B`, and Track `D` benchmark bundles remain transient in this phase. Checked-in `reports/examples` fixtures remain illustrative schema examples only.
