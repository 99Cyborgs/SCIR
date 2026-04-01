# OPEN_QUESTIONS
Status: Normative

Only unresolved items belong here. Do not convert an unresolved semantic question into hidden implementation behavior.

| ID | Question | Impact | Default until resolved | Blocker |
| --- | --- | --- | --- | --- |
| OQ-001 | Should profile `R` preserve stronger comment and provenance detail in v1? | reconstruction and audit tooling | comments remain out of canonical text; provenance sidecars remain allowed | no |
| OQ-003 | How much of `SCIR-H` should be user-visible versus tool-mediated? | UX and tooling design | `SCIR-H` remains inspectable text; no separate authoring language | no |
| OQ-005 | Can `SCIR-H` live inside MLIR infrastructure without losing normative status? | implementation architecture | treat MLIR as optional infrastructure, not the spec surface | no |
| OQ-006 | How much laziness, reflection, and template behavior can be captured without collapsing regularity? | source coverage and tiers | keep them outside Tier A unless explicitly proven otherwise | no |
| OQ-007 | Should generators remain first-class in `SCIR-H` or normalize to iterator/state-machine forms? | grammar and reconstruction | keep generators out of `SCIR-H` v0.1 core | no |
| OQ-010 | Should strict floating-point behavior be modeled as a separate profile facet? | preservation claims for native and portable backends | keep strict-fp as a contract-bounded note under `P2` | no |
| OQ-011 | How much analysis metadata should flow back from `SCIR-L` to `SCIR-H`? | tooling and debugging | provenance only; do not reflect optimizer-only facts back into `SCIR-H` yet | no |
| OQ-012 | Which trusted runtime services deserve first-class semantics rather than opaque boundaries? | interop and runtime scope | keep runtime services opaque unless they are required by the first targeted subset | no |
| OQ-013 | Which translation-validation obligations should land first? | trust reduction sequencing | start with `H -> L` preservation downgrades and provenance continuity checks | no |
| OQ-014 | Which intrinsic AI metrics actually predict repository repair success? | benchmark strategy | keep intrinsic metrics informative, not sufficient | no |
| OQ-015 | How much repository import should be eager versus slice-based on demand? | agent workflow scalability | default to slice-based import driven by impacted dependency cones | no |
| OQ-016 | How strict should versioning be before 1.0 while semantics are still moving? | release process | allow breaking changes only with migration notes and updated golden tests | no |
| OQ-017 | Which proof assistant split is appropriate: Lean, Coq, or both? | proof roadmap | proof work is non-blocking for phase 1 | no |
| OQ-018 | What is the minimum TypeScript interface-shaped witness slice that justifies a dedicated Phase 7 milestone without broadening host-runtime claims? | milestone scoping for witness-bearing second-language evidence | keep the slice limited to interface declarations plus module-local witness consumption with explicit host assumptions, importer-only evidence, and no executable `D-JS` claim | no |
| OQ-019 | Which downstream contracts must become blocking before TypeScript witness work can claim executable `D-JS` support? | validator and benchmark sequencing for `D-JS` | require explicit lowering, translation-validation, reconstruction, and benchmark gates, with report-visible witness semantics and profile-qualified downgrade obligations, before any executable `D-JS` claim | no |

## Resolution rule

When an item is resolved:

1. update the relevant spec,
2. add or update a decision register entry,
3. remove or downgrade the question here,
4. update any affected plan or benchmark doctrine.
