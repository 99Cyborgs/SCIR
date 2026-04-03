# OPEN_QUESTIONS
Status: Normative

Only unresolved items belong here. Do not convert an unresolved semantic question into hidden implementation behavior.

| ID | Question | Impact | Default until resolved | Blocker |
| --- | --- | --- | --- | --- |
| OQ-001 | How much comment and provenance detail should a future pretty-view retain by default? | review ergonomics and audit tooling | canonical storage stays comment-free; pretty-view may add only non-semantic annotations | no |
| OQ-003 | Should Rust remain importer-only in the MVP or grow into an active round-trip proof loop later? | roadmap scope and validation cost | keep Rust importer-first and do not widen reconstruction or benchmark claims | no |
| OQ-004 | Should persistent lineage later absorb a module-level dependency signature in addition to normalized declarations? | identity semantics across larger multi-module imports | keep lineage scoped to normalized module semantics only | no |

## Resolution rule

When an item is resolved:

1. update the relevant spec,
2. add or update a decision register entry,
3. remove or downgrade the question here,
4. update any affected plan or benchmark doctrine.
