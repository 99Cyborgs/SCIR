# Ownership and Alias Model
Status: Normative

## Purpose

The MVP keeps ownership and alias semantics only where the active Python and Rust slices require them.

## Active modes

| Mode | Meaning | Active use |
| --- | --- | --- |
| plain value | normal value semantics | Python and Rust subset defaults |
| `borrow<T>` | read-only borrowed reference | Rust importer type surface |
| `borrow_mut<T>` | writable borrowed reference | Rust importer type surface |
| `opaque<T>` | boundary value with hidden internals | Python foreign and Rust unsafe boundaries |

## Rules

- mutation requires an explicit mutable place
- importer-visible borrow modes must remain explicit
- `borrow<T>` permits reads only and must not be used as a mutation root
- `borrow_mut<T>` is the only writable borrow mode in the active subset
- `opaque<T>` does not imply semantic understanding of the payload
- `opaque<T>` values must not be projected as record-like values inside the active subset
- no stronger alias guarantee may be invented during lowering

## Deferred from active use

- `own<T>`
- `share<T>`
- `gc<T>` as a first-class canonical commitment

These remain future design surfaces, not active MVP claims.
