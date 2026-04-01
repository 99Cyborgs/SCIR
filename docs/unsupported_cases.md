# Unsupported Cases
Status: Normative

The following are explicitly outside the credible first-product scope unless a later decision overrides them.

| ID | Case | Handling |
| --- | --- | --- |
| U1 | Python `exec` / `eval` with ambient namespace dependence | reject or opaque host stub |
| U2 | Python metaclass, descriptor-mutation, import-hook heavy frameworks | opaque host stubs |
| U3 | Rust proc macros and build-script semantics | reject in Phase 6A or import post-expansion only in a later phase |
| U4 | Rust unsafe aliasing tricks and self-referential pin hacks | reject in Phase 6A unless explicitly downgraded to a Tier `C` opaque unsafe boundary |
| U5 | C++ macros as semantic source of truth | preprocess only with provenance loss or reject |
| U6 | C++ UB-dependent low-level tricks, inline assembly, pointer provenance games | unsafe boundary or reject |
| U7 | C++ unconstrained template metaprogramming as first-class source semantics | reject or import instantiated result only |
| U8 | TypeScript decorators, proxies, emit-dependent reflection | opaque host stubs |
| U9 | Go `cgo` and unsafe pointer choreography | opaque FFI boundary |
| U10 | Haskell Template Haskell, RULES, extension-heavy meta-level behavior | reject or opaque |
| U11 | exact cross-target scheduling equivalence | never above `P2` |
| U12 | exact cross-target floating-point reproducibility without strict contract | never above `P2` |
| U13 | Python broad exception surface (`raise`, `finally`, multiple handlers, named-handler fidelity) | reject outside the bounded importer-only `d_try_except` slice; only unnamed single-handler `except ValueError:` normalization is currently admitted, and only as Tier `B` `SCIR-H` import without executable downstream claims |
| U14 | Python broader follow-on expansion beyond the fixed importer-only `b_if_else_return`, `b_direct_call`, `b_async_arg_await`, `b_while_call_update`, `b_while_break_continue`, `b_class_init_method`, `b_class_field_update`, and `d_try_except` cases | reject outside named fixture-backed slices; broader class semantics, `for`, `while ... else`, broader loop families, comprehensions, and `raise` remain deferred |

## Handling rule

Unsupported is not failure to think harder. Unsupported is an explicit engineering boundary. Keep it explicit.
