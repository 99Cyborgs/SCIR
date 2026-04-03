# ROADMAP
Status: Normative

## Active direction

Continue, but narrow aggressively around:

- canonical `SCIR-H`
- derivative `SCIR-L`
- validators
- Python proof loop
- Rust importer evidence
- Wasm reference backend MVP
- Track `A` / `B` benchmark falsification

## Not on the active roadmap

- TypeScript implementation
- broad frontend expansion
- native backend breadth
- active `D-JS`
- Track `D`
- debugger, graph explorer, LSP, proof bridge, or agent patch platform work

## Ordered roadmap

1. lock the MVP boundary and remove contradictory claims
2. make `SCIR-H` the only normative semantic layer
3. harden identity, canonical storage, and non-canonical view separation
4. keep the Python import -> H -> L -> validate -> Python reconstruction loop healthy
5. keep Rust import evidence aligned with the same `SCIR-H` contract without widening round-trip claims
6. publish and validate the Wasm reference-backend MVP contract
7. keep Track `A` and Track `B` reproducible and baseline-strong
8. consider a minimal Track `C` pilot only if the earlier loop remains stable

## Active work surface

`MVP Kernel Hardening`

This work surface covers the current repository-alignment task:

- shrink the v0.1 kernel harder
- remove TypeScript and non-MVP tooling from active validation and roadmap claims
- align specs with the executable parser, validators, lowering, reconstruction, and tests
- make Wasm reference-target language explicit without overclaiming parity

## Re-entry conditions for deferred work

Deferred work can re-enter only when:

- the Python proof loop remains stable,
- Wasm contract and preservation reporting are explicit,
- Track `A` and `B` remain green,
- the boundary docs, decision register, and plans are updated together.
