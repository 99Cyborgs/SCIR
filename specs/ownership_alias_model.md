# Ownership and Alias Model
Status: Normative

## Purpose

SCIR uses a hybrid model because a single memory discipline does not cover the targeted language set.

## Canonical modes

| Mode | Meaning | Typical use |
| --- | --- | --- |
| `own<T>` | unique owning value | native-style explicit ownership |
| `borrow<T>` | shared read-only alias | temporary shared access |
| `borrow_mut<T>` | unique mutable alias | temporary unique mutation |
| `share<T>` | shareable synchronized or explicit-shared value | concurrency-safe shared state |
| `gc<T>` | host or GC-managed value | dynamic-host interop |
| `opaque<T>` | boundary value with hidden internals | FFI, host, unsafe, unsupported internals |

## Rules

- mutation requires an explicit mutable place or alias mode,
- alias rules are part of validator obligations for modeled subsets,
- `gc<T>` and `opaque<T>` weaken static alias guarantees,
- `opaque<T>` does not imply semantic understanding of the payload.

## Importer expectations

- Rust safe subsets should map cleanly into `own`, `borrow`, and `borrow_mut` where possible,
- Python and TypeScript host objects usually land in `gc` or `opaque`,
- FFI-heavy or unsafe constructs remain `opaque` or explicit unsafe regions,
- C++-style layout-sensitive code must not be over-claimed as `own`-safe unless the subset contract supports it.

## Lowering expectations

`SCIR-L` may refine region or memory token structure, but it must not strengthen alias guarantees silently.

## Invalid claims

The following are invalid without explicit evidence:

- claiming race freedom over `opaque` shared state,
- claiming native ownership safety for `gc` host objects,
- claiming `borrow_mut` legality when live aliases are not discharged.
