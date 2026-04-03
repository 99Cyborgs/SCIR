# Unsupported Cases
Status: Normative

The following are explicitly outside the active MVP unless a later decision overrides them.

| ID | Case | Handling |
| --- | --- | --- |
| U1 | Python `exec` / `eval` | reject |
| U2 | Python import hooks, metaclass-driven rewrites, descriptor mutation, pervasive monkey patching | reject or explicit opaque boundary |
| U3 | Python exception control beyond the bounded importer-only single-handler slice | reject |
| U4 | Rust proc macros and build scripts | reject |
| U5 | Rust self-referential pin patterns and unsafe alias choreography beyond explicit boundary treatment | reject |
| U6 | TypeScript implementation work | deferred, not active |
| U7 | C++, Go, and Haskell implementation work | deferred, not active |
| U8 | active `D-JS` execution claims | deferred |
| U9 | benchmark Track `D` claims | deferred |
| U10 | any canonical `SCIR-H` construct outside `scripts/scir_h_bootstrap_model.py` | defer or reject explicitly |

## Handling rule

Unsupported is an explicit engineering boundary. It must not be hidden behind pseudo-support language.
