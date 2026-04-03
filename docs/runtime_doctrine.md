# Runtime Doctrine
Status: Normative

## Active profiles

### `R`

- source-faithful regeneration and auditability
- active for Python reconstruction

### `P`

- safe portable execution through Wasm
- active as the first reference backend target
- success here does not imply native or host parity

### `D-PY`

- bounded Python-host interop for explicit opaque-boundary cases only

## Deferred profiles

### `N`

- reserved for future native backend work

### `D-JS`

- reserved for future JS/TS host work

## Rule

The MVP must not hide runtime assumptions in untracked helper layers. Any helper shim required by Wasm emission must remain explicit and report-visible.
