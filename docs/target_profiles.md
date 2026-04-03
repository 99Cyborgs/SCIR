# Target Profiles
Status: Normative

Every preservation or benchmark claim must name its active profile.

| Code | Name | MVP status | Notes |
| --- | --- | --- | --- |
| `R` | Reconstruction | active | Python reconstruction is the active proof loop |
| `P` | Portable execution | active | Wasm is the first reference backend target |
| `D-PY` | Dynamic host (Python) | active but bounded | only for the explicit Python opaque-boundary surface |
| `N` | Native performance | deferred | not an active backend target in the MVP |
| `D-JS` | Dynamic host (JS/TS) | deferred | no active implementation or executable claim |

## Rules

- no unqualified claim is valid
- a report may name multiple profiles only when evidence is separated
- Wasm emission uses `P`
- Python reconstruction uses `R`
- `N` and `D-JS` may remain in schemas and deferred docs without becoming active commitments
