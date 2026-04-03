# Benchmark Tracks
Status: Normative

| Track | Question | MVP status |
| --- | --- | --- |
| `A` | Are canonical `SCIR-H` and compressed `SCIR-Hc` jointly explicit and compact enough to justify themselves? | active |
| `B` | Can the Python proof loop round-trip through import, validation, lowering, and reconstruction? | active |
| `C` | Does SCIR beat strong baselines on tightly controlled repair or editing tasks? | conditional pilot only |
| `D` | Is runtime or backend performance competitive? | deferred |

## Active executable tracks

- `A`
- `B`

## Conditional tracks

- `C`

## Deferred tracks

- `D`

## Track C pilot task family

- `python-single-function-repair`

## Track C executable pilot posture

- `non-default executable pilot only`
- `opaque-boundary cases remain boundary-accounting-only`

## Track C disposition

- `retain bounded diagnostic pilot`
- `do not promote to default executable gate`
- `keep c_opaque_call boundary-accounting-only`

## Track C sample synchronization

- `checked-in sample manifest must equal the current opt-in pilot manifest`
- `checked-in sample result must equal the current opt-in pilot result`
- `checked-in sample result must keep accepted_case_count 3 and boundary_only_case_count 1`
- `checked-in sample result must keep gate_S2_ready true, gate_K1_hit false, and status mixed or pass`

## Track C sample posture re-decision triggers

- `changing checked-in sample status from mixed requires a new decision-register entry and queue update`
- `changing checked-in sample evidence or retained-diagnostic wording requires a new decision-register entry and queue update`
- `changing checked-in sample task family, case set, or boundary-accounting posture requires a new decision-register entry and queue update`
- `changing checked-in sample default-gate or promotion posture requires a new decision-register entry and queue update`

## Track C editorial-only sample refreshes

- `json whitespace, indentation, and trailing-newline normalization that preserves parsed sample content`
- `json key-order normalization that preserves parsed sample content`

## Track C non-editorial sample refresh provenance

- `cite python scripts/benchmark_contract_dry_run.py --include-track-c-pilot as the regeneration command`
- `cite python scripts/run_repo_validation.py --include-track-c-pilot as the confirming validation command`
- `cite the regenerated manifest corpus hash`
- `cite the regenerated result run_id and system_under_test`

## Rule

Track `C` may not become active until the earlier proof loop remains stable.
Track `D` is outside the active MVP.
