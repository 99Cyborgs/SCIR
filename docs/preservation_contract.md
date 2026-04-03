# Preservation Contract
Status: Normative

## Canonical labels

| Label | Meaning |
| --- | --- |
| `P0` | exact semantic and observable preservation under the active profile |
| `P1` | normalized preservation under the active profile |
| `P2` | contract-bounded preservation |
| `P3` | boundary annotation only |
| `PX` | unsupported |

## Operator-facing report surface

Every preservation report must expose:

- `path`
- `profile`
- `preservation_level`
- `status`
- `downgrades`
- `boundary_annotations`
- `evidence`

Detailed observable buckets may exist for debugging, but they are not the required operator surface.

## Active paths

- `source_to_h`
- `h_to_l`
- `h_to_python`
- `l_to_wasm`

## Rules

- no preservation claim is valid without path and profile
- `P3` means boundary annotation, not semantic understanding
- active corpus fixtures must declare `expected_preservation_ceiling` and `expected_preservation_stage_behavior`
- a stage must not claim stronger preservation than its declared ceiling
- a stage that reports weaker preservation than expected must carry diagnostics, downgrade evidence, boundary annotations, or a non-pass status
- downgrade reasons must be machine-generated and explicit
- Wasm success does not imply native or host parity

## Active bounded Wasm record-cell ABI obligations

The active post-scalar Wasm record-cell slice for `fixture.rust_importer.a_struct_field_borrow_mut` remains profile `P` with a `P2` ceiling and must report at least:

- one downgrade for record-cell layout normalization from canonical field order into Wasm field offsets,
- one downgrade for the shared-handle caller contract that bounds caller-visible mutation to same-ABI callers,
- evidence containing the field-offset map and the bounded shared-caller assumption,
- explicit unsupported treatment for non-`int` record fields, imported-memory variants, and broader host/object layouts.

Those obligations define the current executable boundary for the fixed Rust record-cell slice only. They do not activate broader post-scalar Wasm support.
