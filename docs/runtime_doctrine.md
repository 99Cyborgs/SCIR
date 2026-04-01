# Runtime Doctrine
Status: Normative

SCIR runtime expectations are profile-specific.

## Profile `R`

- helper runtime is allowed,
- provenance sidecars are allowed,
- source-visible ordering matters more than throughput,
- reconstruction clarity beats aggressive optimization.
- Rust Phase 6A Tier `A` round-trip evidence runs under this profile.

## Profile `N`

- thin runtime only,
- optimization aggressiveness may be high,
- scheduling exactness is not preserved,
- ABI or layout facts matter only when explicitly contracted.
- Rust Phase 6A unsafe boundary handling is validated under this profile.
- Phase 6B executable Rust Track `D` automation runs under this profile.

## Profile `P`

- compact portable runtime is allowed,
- capabilities must remain sandboxed,
- host-specific layout and identity are not default observables,
- portable correctness matters more than native parity.

## Profile `D-PY`

- Python VM is part of the active runtime model,
- Python-host-visible exceptions, identity, and event-loop order matter where supported,
- native-parity claims are invalid by default,
- opaque host stubs must be audited.
- Phase 6B executable Python Track `D` automation runs under this profile.

## Profile `D-JS`

- JS/TS VM is part of the active runtime model,
- JS/TS-host-visible exceptions, identity, and event-loop order matter where supported,
- native-parity claims are invalid by default,
- opaque host stubs must be audited,
- Phase 6B keeps this profile doctrine-only,
- the default post-6B witness milestone may admit only importer-only TypeScript interface-shaped evidence under this profile for its first slice,
- the first Phase 7 step is limited to interface declarations and module-local witness-consumption doctrine with explicit host assumptions,
- executable `D-JS` claims remain blocked until a later milestone publishes explicit lowering, reconstruction, validation, and benchmark gates.

## Performance doctrine

- do not claim universal zero-cost abstraction,
- measure witness dispatch, handler lowering, async state machines, channels, FFI, and host interop separately,
- `D-PY` and `D-JS` optimization may remove dead temporaries or trivial CFG structure, but must not reorder host-visible identity or event-loop observables,
- witness-bearing second-language work does not authorize a new native backend track,
- interpret performance only relative to the active profile and baseline.
