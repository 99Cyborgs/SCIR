# Target Profiles
Status: Normative

Every semantic, preservation, optimization, and benchmark claim must name its active target profile.

| Code | Name | Primary objective | Runtime stance | Reconstruction stance |
| --- | --- | --- | --- | --- |
| `R` | Reconstruction | source-faithful regeneration and auditability | helper runtime and provenance sidecars allowed | preserve source-visible ordering and shape when representable |
| `N` | Native performance | efficient native lowering | thin runtime only | idiomaticity may change when legal |
| `P` | Portable execution | safe portable execution through Wasm or equivalent | compact portable runtime allowed | reconstruction is secondary |
| `D-PY` | Dynamic host (Python) | high-fidelity interop with Python hosts | Python VM fully allowed | preserve Python-host-visible identity and ordering where supported |
| `D-JS` | Dynamic host (JS/TS) | high-fidelity interop with JS/TS hosts | JS/TS VM fully allowed | preserve JS/TS-host-visible identity and ordering where supported |

## Rules

- No unqualified claim is valid.
- A report may name multiple profiles only when evidence is profile-separated.
- Benchmark results must not mix incomparable profiles in one headline metric.
- Reconstruction claims default to `R`, `D-PY`, or `D-JS`, not `N`.

## Default profile expectations

- Python subset importer work is usually `R` and `D-PY`.
- Wasm work is usually `P`.
- Rust subset and layout-sensitive optimization work are usually `N`.
- TypeScript structured-host work is usually `D-JS` and `R`.

## Current executable exceptions

- Python bootstrap opaque-boundary evidence is fixed at profile `D-PY`.
- Rust Phase 6A Tier `A` round-trip evidence is fixed at profile `R`.
- Rust Phase 6A explicit unsafe boundaries are fixed at profile `N`.
- Rust `N` and Python `D-PY` executable Track `D` claims begin in Phase 6B.
- `D-JS` remains doctrine-only until a later frontend milestone lands.
