# Benchmark Tracks
Status: Normative

| Track | Question | Core metrics |
| --- | --- | --- |
| `A` | Is `SCIR-H` a regular, explicit, compact-enough representation? | lexical compression ratio, grammar regularity, semantic explicitness, canonical edit distance, context compression potential |
| `B` | Can supported subsets round-trip through import and reconstruction? | import success, validator pass, compile pass, test pass, reconstruction fidelity index, idiomaticity |
| `C` | Does SCIR beat strong baselines on generation, editing, or repair? | pass@k, static-check pass rate after generation, test pass, issue resolution, planning recall |
| `D` | Is the compiler/runtime path plausible for targeted subsets? | runtime, code size, compile time, memory, handler overhead, async overhead |

## Policy

Track `A` and `B` can start early. Track `C` and `D` require stronger harnessing but must be specified early.

For the current executable freeze:

- Track `A` runs on the fixed bootstrap corpus and records both median and aggregate token-ratio diagnostics, with status governed by the median-based `S3`/`K2` rules plus `S4`/`K4`,
- Track `B` runs on the fixed bootstrap corpus and is gated by Tier `A` compile/test rates plus opaque-fraction limits,
- Track `B` idiomaticity remains recorded evidence rather than a separate hard gate,
- Track `C` remains specified but does not emit executable result bundles,
- Track `D` emits separate executable result bundles for Rust `N` and Python `D-PY`,
- `D-JS` remains doctrine-only and emits no executable result bundle in Phase 6B.
