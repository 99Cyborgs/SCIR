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
