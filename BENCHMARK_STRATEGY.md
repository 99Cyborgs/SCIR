# BENCHMARK_STRATEGY
Status: Normative

## Objective

SCIR continues only if the narrow proof loop survives strong-baseline falsification.
Track `A` therefore measures both canonical explicit `SCIR-H` and compressed derived `SCIR-Hc` instead of collapsing them into one lexical score.

## Active benchmark tracks

- Track `A`: representation regularity and semantic explicitness
- Track `B`: Python proof-loop round-trip fidelity

Track `C` is conditional.
Track `D` is deferred.

See `benchmarks/tracks.md`.

The active executable benchmark corpus is frozen by the checked-in proof-loop corpus manifests under `tests/corpora/`.
Those manifests are governance artifacts, not benchmark result claims by themselves.
Sweep artifacts under `artifacts/sweeps/` are the historical comparison surface for those fixed corpora.

### Active executable benchmark cases

- `a_basic_function`
- `a_async_await`
- `b_direct_call`
- `c_opaque_call`

## Mandatory baselines

Every active benchmark must include:

- direct-source workflow baseline,
- typed-AST baseline.

The active MVP also carries the regularized-core comparison as the minimal third executable baseline through the active track-specific additions, not as an optional stretch goal.
See `benchmarks/baselines.md` for the adapter contract, including `run_baseline(baseline_name, corpus_manifest)`.

## Benchmark rules

- every run uses a `benchmark_manifest`
- every result bundle uses a `benchmark_result`
- every evaluation-lane sweep must emit `sweep_summary`, `regression_summary`, `comparison_summary.json`, and `contamination_report.json`
- every claim run must emit `benchmark_report.json`, `benchmark_report.md`, and `manifest_lock.json`
- every claim must name the strongest relevant baseline
- every claim must cite the corpus manifest hash and comparator metric
- every `benchmark_report` claim must declare `claim_class` and `evidence_class`
- every benchmark must state contamination controls
- every benchmark must carry a reproducibility block
- every benchmark must state success and kill gates

## Audit artifacts

The minimum externally defensible bundle for an active executable run now includes:

- `sweep_result.json`
- `sweep_summary.json`
- `comparison_summary.json`
- `contamination_report.json`
- `benchmark_report.json`
- `benchmark_report.md`
- `manifest_lock.json`

Claim-producing runs must fail if baseline results are missing, corpus hash mismatches are detected, a reproducibility block is missing, contamination is detected, or none of the approved claim-gate conditions hold for the declared `claim_class`.
They must also emit separate explicit and compressed representation metrics plus failure attribution for lexical inflation sources.
They must reject cross-class inference and any implicit generalization from `SCIR-Hc` evidence into semantic-preservation, reconstruction-fidelity, or cross-language claims.

## Interpretation discipline

- If direct source or typed AST matches SCIR on the active task family, treat that as evidence against continuing.
- If `SCIR-Hc` matches typed AST across the measured lexical and repair-composability signals, treat the AI-facing compression thesis as invalidated.
- If Track `A` looks acceptable but Track `B` is unstable, treat the representation as unproven.
- A Track `C` pilot is valid only after the fixed Python proof loop remains stable.
- Wasm success is backend evidence only; it does not validate broader semantics or benchmark claims by itself.
- `SCIR-Hc` evidence must stay inside the declared `claim_class` / `evidence_class` boundary for the benchmark report that cites it.

## Profile and preservation annotation

Benchmark results must report:

- active profile,
- preservation-level ceiling,
- tier distribution,
- explicit boundary-annotation fraction.

## Active success and kill rules

Canonical thresholds live in `benchmarks/success_failure_gates.md`.

For Track `A`:

- evaluate the source half of `S3` and `K2` on canonical `SCIR-H` median token ratios,
- evaluate the typed-AST half of `S3` on compressed `SCIR-Hc` median token ratios,
- keep aggregate ratios diagnostic only,
- keep structural-redundancy removal and patch-composability deltas diagnostic but published,
- fail the result if a kill gate triggers.

For Track `B`:

- evaluate `S1`, `S4`, `K3`, and `K4`,
- treat Tier `A` compile and test rates as the blocking signal,
- keep idiomaticity as supporting evidence, not a separate hard gate.

## Conditional Track `C`

Track `C` may exist only as a minimal pilot after:

- Track `A` remains stable,
- Track `B` remains stable,
- contamination controls and baselines stay fixed.

The first Track `C` pilot is restricted to Python single-function repair over the fixed executable Python proof-loop cases.
It remains non-default, and the checked-in sample artifacts stay outside the default executable benchmark gate.

### Conditional Track C pilot task family

- `python-single-function-repair`

### Conditional Track C pilot cases

- `a_basic_function`
- `a_async_await`
- `b_direct_call`
- `c_opaque_call`

### Conditional Track C artifact posture

- `illustrative sample only`
- `outside default executable benchmark gate`

### Conditional Track C executable pilot posture

- `non-default executable pilot only`
- `opaque-boundary cases remain boundary-accounting-only`

### Conditional Track C disposition

- `retain bounded diagnostic pilot`
- `do not promote to default executable gate`
- `keep c_opaque_call boundary-accounting-only`

### Conditional Track C retention criteria

- `gate_S2_ready must remain true`
- `gate_K1_hit must remain false`
- `accepted_case_count must remain 3`
- `boundary_only_case_count must remain 1`
- `status must remain mixed or pass`

### Conditional Track C retirement triggers

- `retire if gate_S2_ready becomes false`
- `retire if gate_K1_hit becomes true`
- `retire if accepted_case_count drops below 3`
- `retire if boundary_only_case_count differs from 1`
- `retire if status becomes fail`

### Conditional Track C sample synchronization

- `checked-in sample manifest must equal the current opt-in pilot manifest`
- `checked-in sample result must equal the current opt-in pilot result`
- `checked-in sample result must keep accepted_case_count 3 and boundary_only_case_count 1`
- `checked-in sample result must keep gate_S2_ready true, gate_K1_hit false, and status mixed or pass`

### Conditional Track C sample posture re-decision triggers

- `changing checked-in sample status from mixed requires a new decision-register entry and queue update`
- `changing checked-in sample evidence or retained-diagnostic wording requires a new decision-register entry and queue update`
- `changing checked-in sample task family, case set, or boundary-accounting posture requires a new decision-register entry and queue update`
- `changing checked-in sample default-gate or promotion posture requires a new decision-register entry and queue update`

### Conditional Track C editorial-only sample refreshes

- `json whitespace, indentation, and trailing-newline normalization that preserves parsed sample content`
- `json key-order normalization that preserves parsed sample content`

### Conditional Track C non-editorial sample refresh provenance

- `cite python scripts/benchmark_contract_dry_run.py --include-track-c-pilot as the regeneration command`
- `cite python scripts/run_repo_validation.py --include-track-c-pilot as the confirming validation command`
- `cite the regenerated manifest corpus hash`
- `cite the regenerated result run_id and system_under_test`

## Deferred Track `D`

Runtime and backend performance claims are not active MVP evidence.
No Track `D` result bundle is part of the default benchmark gate.

## Command contract

`make benchmark` performs doctrine checks plus executable Track `A` and Track `B` validation on the fixed Python proof-loop corpus.

`make benchmark-claim` performs the same executable run in explicit claim mode and fails when audit claim gates fire.

`make benchmark-repro RUN_ID=<run-id>` replays a locked claim run from `manifest_lock.json`.

When `make` is unavailable, use:

```bash
python scripts/benchmark_contract_dry_run.py
python scripts/benchmark_contract_dry_run.py --claim-run
python scripts/benchmark_repro.py --run-id <run-id>
```

Checked-in `reports/examples` benchmark artifacts remain illustrative examples, not proof of benchmark breadth.

The non-default Track `C` pilot is available only via:

```bash
python scripts/benchmark_contract_dry_run.py --include-track-c-pilot
```
