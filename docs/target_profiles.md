# Target Profiles
Status: Normative

Every semantic, preservation, optimization, and benchmark claim must name its active target profile.

| Code | Name | Primary objective | Runtime stance | Reconstruction stance |
| --- | --- | --- | --- | --- |
| `R` | Reconstruction | source-faithful regeneration and auditability | helper runtime and provenance sidecars allowed | preserve source-visible ordering and shape when representable |
| `N` | Native performance | efficient native lowering | thin runtime only | idiomaticity may change when legal |
| `P` | Portable execution | safe portable execution through Wasm or equivalent | compact portable runtime allowed | reconstruction is secondary |
| `D` | Dynamic host | high-fidelity interop with Python/TS/JS hosts | host VM fully allowed | preserve host-visible identity and ordering where supported |

## Rules

- No unqualified claim is valid.
- A report may name multiple profiles only when evidence is profile-separated.
- Benchmark results must not mix incomparable profiles in one headline metric.
- Reconstruction claims default to `R` or `D`, not `N`.

## Default profile expectations

- Python subset importer work is usually `R` and `D`.
- Wasm work is usually `P`.
- Rust subset and layout-sensitive optimization work are usually `N`.
