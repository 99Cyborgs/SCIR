# ARCHITECTURE
Status: Normative

## Core doctrine

SCIR is a two-layer system.

| Layer | Normative status | Purpose | Current MVP role |
| --- | --- | --- | --- |
| `SCIR-H` | normative | canonical semantics for inspection, transformation, validation, reconstruction, and stable identity | source of truth |
| `SCIR-L` | derivative | lowered control/dataflow form for validation, backend preparation, and reference emission | derived only |

`SCIR-H` is the only semantic source of truth.
`SCIR-Hc` is a derived compressed view of validated `SCIR-H`, not a third semantic layer.
`SCIR-L` is valid only when it can be justified by validated `SCIR-H` plus a named lowering rule.

## Active MVP boundary

The active MVP contains:

- a compact canonical `SCIR-H` subset,
- a bounded derived `SCIR-Hc` view for AI-facing compression and benchmark comparison,
- a compact derivative `SCIR-L` subset,
- `SCIR-H`, `SCIR-Hc`, and `SCIR-L` validators,
- Python subset import,
- Rust safe-subset import,
- Python reconstruction from validated `SCIR-H`,
- Wasm reference-backend contract,
- Track `A` and Track `B` benchmark harnesses.

Deferred from the MVP:

- broad second-language work,
- active `D-JS` execution,
- native backend performance work,
- broad runtime/tooling surfaces,
- benchmark Track `D`.

## Implementation posture

Implemented now:

- canonical `SCIR-H` parser/formatter plus invariant-coded validation
- `SCIR-H -> SCIR-Hc` compression, round-trip validation, and normalization statistics
- bounded derivative `SCIR-L` lowering and validation for the active Python proof loop
- execution-backed translation validation for the admitted `SCIR-L -> Wasm` backend path
- fixed proof-loop corpus manifests and slice-based sweep smoke

Partially implemented:

- importer-only Tier `B` `SCIR-H` evidence beyond the executable proof loop
- Rust importer-first evidence and bounded optional Rust validation
- helper-free Wasm emission only for the admitted fixed cases

Planned next:

- additional hardening inside the existing bounded proof loop without widening frontend or backend scope

Unsupported or deferred:

- standalone `throw` syntax, active TypeScript execution, Track `D`, and broader backend/runtime parity claims

## Active proof loop

```text
python source
  -> Python importer
  -> canonical SCIR-H
  -> SCIR-H validation
  -> derived SCIR-Hc validation
  -> derivative SCIR-L lowering
  -> SCIR-L validation
  -> Python reconstruction from SCIR-H
  -> Track A / Track B benchmark checks
```

Rust is active at the importer layer and must remain semantically aligned with the same `SCIR-H` contract, but Rust round-trip and benchmark work are not part of the MVP gate.

## Implemented canonical `SCIR-H` subset

The executable bootstrap parser/formatter currently supports:

- `module`
- `import sym` and `import type`
- `type` declarations for record shapes
- `fn` and `async fn`
- `var`
- `set`
- `return`
- `if` / `else`
- `loop`
- `break`
- `continue`
- single-handler `try` / `catch name Type`
- importer-only `!throw` effect markers on the bounded Tier `B` `try/catch` slice
- direct calls `f(args)`
- `await`
- explicit field places such as `counter.value`
- intrinsic scalar comparisons `lt`, `le`, `eq`, `ne`, `gt`, `ge`

Anything broader is deferred or unsupported until the parser, validator, lowering, reconstruction, and tests all agree.

## Implemented derived `SCIR-Hc` view

`SCIR-Hc` is a machine-generated compression of validated `SCIR-H` for AI-facing lexical efficiency work.
It must preserve `P1` semantic equivalence back to canonical `SCIR-H`.
It now also carries a derived-only authority marker plus omission provenance so it cannot silently become semantic authority.

The active executable compression path may:

- omit effect rows that are fully inferable from the function body,
- omit local binding type markers when they are inferable from the assigned expression,
- omit explicit return types when they are inferable from the function body,
- compress repeated boundary capability metadata outside canonical syntax,
- leave witness compression as a reserved no-op while canonical witness syntax remains deferred.

No downstream lowering, reconstruction, or preservation claim may consume `SCIR-Hc` directly without first round-tripping back through canonical `SCIR-H`.
The bootstrap pipeline must hard-stop any direct `SCIR-Hc` attempt to enter lowering, reconstruction, or backend emission.

## Implemented derivative `SCIR-L` subset

The executable lowering and validator currently admit:

- value ops: `const`, `cmp`
- memory ops: `alloc`, `store`, `load`
- place projection: `field.addr`
- effect and boundary ops: `call`, `async.resume`, `opaque.call`
- terminators: `ret`, `br`, `cond_br`
- provenance plus named lowering-rule coverage on semantically meaningful ops

`SCIR-L` may not add semantics absent from `SCIR-H`.

## Identity and canonical storage

Identity is split into:

- persistent semantic lineage identity,
- canonical content hash,
- local or revision-scoped node identity.

Spec version is not part of persistent semantic lineage identity.

Canonical storage is deterministic and machine-facing.
Human-facing views are non-canonical and must not affect canonical hashes or lineage identifiers.

See `IDENTITY_MODEL.md`.

## Preservation reporting

Operator-facing preservation claims are generated around:

- explicit path,
- explicit profile,
- preservation ceiling,
- downgrade reasons,
- boundary annotations,
- evidence.

This repository does not treat Wasm emission, Python reconstruction, or lowering success as interchangeable claims.

## Backend stance

Wasm is the first reference backend target because it exercises `SCIR-L` emission discipline without implying native or host-runtime parity.
Active Wasm acceptance is now two-part:

- shape validation for the bounded helper-free WAT contract
- execution-backed translation validation that compares emitted backend behavior against bounded `SCIR-L` traces under the declared preservation contract

The active helper-free Wasm backend now contains two bounded slices:

- the original scalar subset,
- the fixed Rust record-cell slice for `a_struct_field_borrow_mut`.

That record-cell slice uses module-owned linear memory, fixed-size records with `int` fields only, offsets derived from canonical field declaration order, `borrow_mut<T>` record parameters represented as base-address handles, and caller-visible mutation preserved only for callers that explicitly share the same contract.
That record-cell ABI is now frozen to the fixed Rust slice rather than treated as a stepping stone toward implicit general record support.
Broader record, borrow, Python field-place, async, opaque, imported, or host-facing backend shapes still require further explicit backend-contract decisions rather than incremental emitter widening.

Wasm success means only:

- the active `SCIR-L` subset can be emitted to the published Wasm MVP contract,
- the published profile and downgrade rules were respected.

It does not imply:

- native parity,
- `D-PY` parity,
- `D-JS` parity,
- support for deferred language constructs.

## Architecture change protocol

No architecture change is complete until:

- the root boundary docs are current,
- affected normative specs are current,
- validator implications are current,
- benchmark implications are current,
- decision register entries are updated,
- unresolved ambiguity is recorded in `OPEN_QUESTIONS.md`.
