# Success and Failure Gates
Status: Normative

## Success thresholds

| ID | Threshold |
| --- | --- |
| S1 | Tier A round-trip compile + test pass >= 95% on targeted corpora |
| S2 | SCIR-based AI workflows beat the strongest baseline by >= 10% absolute on at least two task families, or improve static-check-pass by >= 15 percentage points |
| S3 | `SCIR-H` median token count <= 1.10x canonical source or <= 0.75x typed AST while increasing semantic explicitness materially |
| S4 | Opaque or unsafe fallback remains < 15% of nodes in targeted subsets and < 25% in targeted repositories |
| S5 | Executable Track `D` fixed-corpus slices stay within their published direct-source performance ceilings with profile-qualified observable matching preserved |

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
| K8 | any executable Track `D` gating kernel exceeds 2.0x direct-source runtime or fails profile-qualified observable matching |

## Interpretation rule

If Track `C` fails while Track `B` and `D` are useful, narrow toward infrastructure rather than continuing to market SCIR as an AI substrate.

Track `A` automation evaluates `S3` and `K2` on median token ratios. Aggregate token ratios are diagnostic only, and any automated kill-gate hit forces a failing benchmark result.

For the current executable bootstrap harness:

- Track `A` automates `S3`, `S4`, `K2`, and `K4`,
- Track `B` automates `S1`, `S4`, `K3`, and `K4`,
- Track `B` idiomaticity is recorded for evidence and review but does not override those gates,
- Track `D` automates `S5` and `K8` on separate Rust `N` and Python `D-PY` slices,
- Rust `N` and Python `D-PY` use distinct published ceilings within `S5`,
- `D-JS` remains doctrine-only and does not feed executable gates.

Rust Phase 6A validation does not feed executable benchmark gates. Phase 6B is the first phase where canonical Rust `D`-track evidence exists, and that evidence is limited to the fixed Rust `N` slice plus the fixed Python `D-PY` slice.
