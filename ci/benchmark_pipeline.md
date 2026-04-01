# Benchmark Pipeline
Status: Normative

## Current purpose

The current benchmark pipeline validates benchmark policy, schemas, contamination controls, gating documents, benchmark-checker self-tests, and executes manifest-driven Track `A`, Track `B`, Rust `N` Track `D`, and Python `D-PY` Track `D` runs for the fixed bootstrap corpus.

Track `A` automation records both median and aggregate token-ratio diagnostics, but benchmark status is governed by the published median-based success and kill gates.
Track `B` status is governed by Tier `A` compile/test gates plus opaque-fraction limits. Idiomaticity remains report evidence rather than an extra hard gate.
Track `D` status is governed by `S5` and `K8` on separate Rust `N` and Python `D-PY` slices. `D-JS` and Track `C` remain doctrine-only and do not emit executable result bundles in the current pipeline.

## Blocking command

```bash
make benchmark
```

Windows fallback:

```bash
python scripts/benchmark_contract_dry_run.py
```

## Future expansion

Further harness expansion must additionally:

- extend execution beyond the fixed bootstrap corpus without weakening the current doctrine checks,
- validate benchmark manifests for new tracks or corpora,
- validate result bundle structure,
- require named baselines,
- require contamination control metadata,
- decide explicitly whether generated bundles remain transient or are promoted into checked-in evidence.
