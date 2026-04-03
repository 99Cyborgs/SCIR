# SPEC_COMPLETENESS_CHECKLIST
Status: Normative

| construct | grammar | parser | validator | lowering | reconstruction | tests | MVP status | action taken |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| module header | yes | yes | yes | n/a | yes | yes | fully supported in MVP | kept as canonical root form |
| `import sym` | yes | yes | yes | importer-specific only | n/a | yes | fully supported in MVP | kept |
| `import type` | yes | yes | yes | n/a | n/a | minimal | fully supported in MVP | kept |
| record `type` declaration | yes | yes | yes | partial | Python and Rust surface only | yes | fully supported in MVP | kept |
| plain `fn` | yes | yes | yes | yes | yes | yes | fully supported in MVP | kept |
| `async fn` | yes | yes | yes | yes | yes for Python subset | yes | fully supported in MVP | kept |
| `var` | yes | yes | yes | yes | yes | yes | fully supported in MVP | kept |
| `set` local place | yes | yes | yes | yes | yes | yes | fully supported in MVP | kept |
| `set` field place | yes | yes | yes | yes | yes for bounded record-like shapes | yes | fully supported in MVP | kept |
| `return` | yes | yes | yes | yes | yes | yes | fully supported in MVP | kept |
| `if` / `else` | yes | yes | yes | Python proof loop yes; broader cases no | Python subset yes | yes | fully supported in MVP | kept with subset-bound lowering |
| `loop` | yes | yes | validator-only | no | no | yes | canonical parser/validator surface only | kept as importer-only `SCIR-H` surface beyond parser/validator |
| `break` | yes | yes | validator-only | no | no | yes | canonical parser/validator surface only | kept as importer-only `SCIR-H` surface beyond parser/validator |
| `continue` | yes | yes | validator-only | no | no | yes | canonical parser/validator surface only | kept as importer-only `SCIR-H` surface beyond parser/validator |
| single-handler `try` / `catch name Type` | yes | yes | validator-only | no | no | yes | canonical parser/validator surface only | kept as importer-only `SCIR-H` surface beyond parser/validator |
| direct call `f(args)` | yes | yes | yes | subset-bound yes | yes for Python subset | yes | fully supported in MVP | kept |
| `await` | yes | yes | yes | yes | yes for Python subset | yes | fully supported in MVP | kept |
| intrinsic scalar comparison | yes | yes | yes | yes | yes | yes | fully supported in MVP | kept |
| explicit field place `a.b` | yes | yes | yes | yes | yes for bounded record-like shapes | yes | fully supported in MVP | kept |
| opaque or unsafe boundary call | yes | importer-emitted only | yes | yes | Python opaque case only | yes | fully supported in MVP | kept as boundary-only surface |
| `iface` declarations | no | no | no | no | no | no | not MVP and removed from active claims | deferred |
| `witness` declarations | no | no | no | no | no | no | not MVP and removed from active claims | deferred |
| capability signatures and `using` clauses | no | no | no | no | no | no | not MVP and removed from active claims | deferred |
| importer-only `!throw` effect marker on bounded `try/catch` evidence | yes | yes | validator-only | no | no | yes | canonical parser/validator surface only | kept as an importer-only effect marker; standalone `throw` syntax remains deferred |
| `throw` expression or statement | no | no | no | no | no | no | not MVP and removed from active claims | deferred outside the importer-only `!throw` effect marker |
| `match` | no | no | no | no | no | no | not MVP and removed from active claims | deferred |
| `select` | no | no | no | no | no | no | not MVP and removed from active claims | deferred |
| `unsafe` suite block | no | no | no | no | no | no | not MVP and removed from active claims | deferred in favor of explicit boundary calls |
| `opaque` suite block | no | no | no | no | no | no | not MVP and removed from active claims | deferred in favor of explicit boundary calls |
| `borrow` / `borrow_mut` expressions | no | no | no | no | no | no | not MVP and removed from active claims | deferred; type-level borrow shapes remain |
| `invoke` witness dispatch | no | no | no | no | no | no | not MVP and removed from active claims | deferred |
| `spawn` / `send` / `recv` / channel types | no | no | no | no | no | no | not MVP and removed from active claims | deferred |
| standalone `SCIR-L` text parser | no | no | validator over structured data only | n/a | n/a | no | incomplete and deferred | active authority is renderer plus validator, not a standalone parser |
| `SCIR-L` provenance origin | n/a | n/a | yes | yes | n/a | yes | fully supported in MVP | strengthened with named lowering rules |
| `SCIR-L` lowering-rule coverage | n/a | n/a | yes | yes | n/a | yes | fully supported in MVP | added as blocking derivative check |
| Python reconstruction | n/a | n/a | report-checked | n/a | yes | yes | fully supported in MVP | kept |
| Rust reconstruction | n/a | n/a | legacy only | n/a | not active | legacy only | not MVP and removed from active claims | deferred |
| Wasm backend emission | helper-free WAT renderer only | no binary backend yet | yes for admitted subset | consumes the helper-free local-slot `SCIR-L` subset only | n/a | yes | partially supported in MVP | emitter-backed for `a_basic_function` and `a_mut_local`; `field.addr`, calls, async, and opaque lowering remain non-emittable |
