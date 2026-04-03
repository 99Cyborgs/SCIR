# Success and Failure Gates
Status: Normative

## Active success thresholds

| ID | Threshold |
| --- | --- |
| S1 | Track `B` Tier `A` compile and test pass rate >= 95% on the fixed Python proof-loop corpus |
| S2 | A Track `C` pilot may proceed only after Track `A` and Track `B` remain stable on the fixed proof-loop corpus |
| S3 | canonical `SCIR-H` median token count <= 1.10x canonical source or compressed `SCIR-Hc` median token count <= 0.75x typed AST while canonical `SCIR-H` still increases semantic explicitness materially |
| S4 | Explicit opaque fallback remains < 15% of nodes in the active proof-loop corpus |

## Active kill criteria

| ID | Condition |
| --- | --- |
| K1 | no evidence that the active proof loop is useful relative to direct source and typed AST on controlled tasks |
| K2 | `SCIR-H` median token count > 1.5x source without compensating gains |
| K3 | Track `B` Tier `A` compile and test pass rate stays < 90% after stabilization |
| K4 | opaque fallback required for > 25% of the targeted proof-loop corpus |
| K5 | Wasm success is being used to imply native or host parity |

## Audit claim gates

Explicit claim runs must fail when:

- baseline results are missing
- corpus hash mismatches are detected across the benchmark bundle
- a reproducibility block is missing
- contamination is detected
- `claim_class` or `evidence_class` is missing from `benchmark_report`
- `SCIR-Hc` evidence leaks across claim classes or implies semantic-preservation, reconstruction-fidelity, or cross-language claims
- none of the active claim-gate conditions hold

Active claim-gate conditions are:

- `SCIR-Hc` beats typed-AST on `LCR`
- canonical `SCIR-H` beats typed-AST on `SCPR` by at least 15 percentage points
- canonical `SCIR-H` shows a positive typed-AST patch-composability gain

Each `benchmark_report` may evaluate only the condition set admitted by its declared `claim_class`.
Mixed-class claim reports are invalid even when multiple conditions happen to pass diagnostically.

## Rule

Track `A` and `B` are the only active executable benchmark gates in the MVP.

### Track A success gates

- `S3`
- `S4`

### Track A kill gates

- `K2`
- `K4`

### Track B success gates

- `S1`
- `S4`

### Track B kill gates

- `K3`
- `K4`

### Conditional benchmark gate

- `S2`

### Track C pilot success gates

- `S2`

### Track C pilot kill gates

- `K1`

### Track C retention criteria

- `gate_S2_ready must remain true`
- `gate_K1_hit must remain false`
- `accepted_case_count must remain 3`
- `boundary_only_case_count must remain 1`
- `status must remain mixed or pass`

### Track C retirement triggers

- `retire if gate_S2_ready becomes false`
- `retire if gate_K1_hit becomes true`
- `retire if accepted_case_count drops below 3`
- `retire if boundary_only_case_count differs from 1`
- `retire if status becomes fail`

### Deferred benchmark misuse gate

- `K5`
