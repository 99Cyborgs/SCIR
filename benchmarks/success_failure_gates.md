# Success and Failure Gates
Status: Normative

## Success thresholds

| ID | Threshold |
| --- | --- |
| S1 | Tier A round-trip compile + test pass >= 95% on targeted corpora |
| S2 | SCIR-based AI workflows beat the strongest baseline by >= 10% absolute on at least two task families, or improve static-check-pass by >= 15 percentage points |
| S3 | `SCIR-H` median token count <= 1.10x canonical source or <= 0.75x typed AST while increasing semantic explicitness materially |
| S4 | Opaque or unsafe fallback remains < 15% of nodes in targeted subsets and < 25% in targeted repositories |

## Kill criteria

| ID | Condition |
| --- | --- |
| K1 | no material AI gain versus typed AST or direct source by month 12 |
| K2 | `SCIR-H` median token count > 1.5x source without compensating gains |
| K3 | Tier A round-trip compile + test pass stays < 90% after stabilization |
| K4 | opaque fallback required for > 25% of targeted subset constructs |
| K5 | native or portable profile remains slower than 2x direct baselines on core kernels by month 18 with no narrowing path |
| K6 | repeated silent miscompiles cannot be bounded by validation and differential testing |
| K7 | controlled human review finds `SCIR-H` materially less auditable than typed AST or source |

## Interpretation rule

If Track `C` fails while Track `B` and `D` are useful, narrow toward infrastructure rather than continuing to market SCIR as an AI substrate.
