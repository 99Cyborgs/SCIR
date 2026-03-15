# Preservation Contract
Status: Normative

Canonical preservation labels:

| Label | Alias | Meaning |
| --- | --- | --- |
| `P0` | exact | observable behavior preserved exactly under the active profile |
| `P1` | normalized | semantics preserved after declared normalizations |
| `P2` | contract-bounded | semantics preserved subject to explicit backend/runtime/host contract |
| `P3` | opaque-only | only boundary contract is preserved |
| `PX` | unsupported | no preservation claim |

## Rules

- A preservation claim is invalid without a profile.
- A preservation claim is invalid without named evidence.
- `P0` is not allowed across opaque or unsafe internals.
- `P2` must name the contract that bounds the claim.
- `P3` must reference an explicit opaque boundary contract.
- `PX` must map to an importer rejection or explicit unsupported marker.

## Path-specific ceilings

| Path | Typical ceiling |
| --- | --- |
| source -> `SCIR-H` | `P0/P1` for Tier A, `P2` for contract-sensitive cases, `P3` for opaque imports, `PX` otherwise |
| `SCIR-H -> SCIR-L` | `P0/P1` for structured subsets, `P2` when backend assumptions enter |
| `SCIR-H -> reconstructed source` | `P0/P1` for profile-matched targets, `P2` for profile shifts |
| `SCIR-L -> backend artifact` | `P0/P1` for restricted subsets, `P2` for runtime-sensitive code, `P3` through FFI or host stubs |

## Observation discipline

Observation is profile-qualified. Timing is not a default semantic observable. Scheduling is usually contract-bounded, not exact.
