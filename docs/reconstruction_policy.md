# Reconstruction Policy
Status: Normative

## Primary rule

Reconstruction is driven from validated `SCIR-H`.
`SCIR-L` is diagnostic support, not the default reconstruction source.

## Active MVP reconstruction

Active proof-loop reconstruction is limited to Python.

## Active reconstruction cases

- `a_basic_function`
- `a_async_await`
- `b_direct_call`
- `c_opaque_call`

## Non-active cases

Importer-only or deferred cases may emit canonical `SCIR-H` but do not become reconstruction claims.

## Required outputs

- reconstructed source
- `reconstruction_report`
- `preservation_report`
- provenance map back to canonical `SCIR-H`

## Rules

- no reconstruction claim without compile and test evidence where the loop provides them
- no supported reconstruction may hide required boundary annotations
- pretty views do not count as reconstruction outputs
