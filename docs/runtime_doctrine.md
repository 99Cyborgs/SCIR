# Runtime Doctrine
Status: Normative

SCIR runtime expectations are profile-specific.

## Profile `R`

- helper runtime is allowed,
- provenance sidecars are allowed,
- source-visible ordering matters more than throughput,
- reconstruction clarity beats aggressive optimization.

## Profile `N`

- thin runtime only,
- optimization aggressiveness may be high,
- scheduling exactness is not preserved,
- ABI or layout facts matter only when explicitly contracted.

## Profile `P`

- compact portable runtime is allowed,
- capabilities must remain sandboxed,
- host-specific layout and identity are not default observables,
- portable correctness matters more than native parity.

## Profile `D`

- host VM is part of the active runtime model,
- host-visible exceptions, identity, and event-loop order matter where supported,
- native-parity claims are invalid by default,
- opaque host stubs must be audited.

## Performance doctrine

- do not claim universal zero-cost abstraction,
- measure witness dispatch, handler lowering, async state machines, channels, FFI, and host interop separately,
- interpret performance only relative to the active profile and baseline.
