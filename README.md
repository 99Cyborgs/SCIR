# SCIR

Status: Frozen and retired.

SCIR was a two-layer semantic substrate:

- `SCIR-H` was the only normative semantic authority.
- `SCIR-L` was derivative-only lowering justified by validated `SCIR-H`.

The repository is preserved as a historical record of a bounded semantic-substrate experiment that ended with a strong-baseline falsification result of `SCIR_USEFUL_BUT_UNNECESSARY`.

## Final status

SCIR is Frozen and retired.

The final repository phase was the frozen 11-case Python proof-loop strong-baseline falsification for Track `A` and Track `B`.
The project was retired because the final admitted-scope result did not justify further broadening:

- Track `A` showed some value on representation regularity and patch-composability surfaces.
- Track `B` only tied the strongest measured baseline on the admitted proof-loop round-trip surfaces.
- Under the repository doctrine, ties count against continuation.
- The final repository-level outcome was `SCIR_USEFUL_BUT_UNNECESSARY`, not `SCIR_NECESSARY`.

## What SCIR Was

SCIR attempted to provide:

- a canonical semantic authority in `SCIR-H`
- a derived compressed view in `SCIR-Hc`
- a derivative lowering form in `SCIR-L`
- validator-gated import, transformation, lowering, reconstruction, and benchmark claims
- explicit profile, preservation, and unsupported-case accounting
- bounded proof-loop evidence instead of whole-language overclaiming

The project did not aim to be:

- a new authoring language
- a broad whole-language importer suite
- a universal backend substrate
- an excuse for silent fallback or hidden semantics

## How The Project Got Here

1. It established a spec-first semantic doctrine with `SCIR-H` as the only normative authority and `SCIR-L` as derivative-only.
2. It built a bounded Python subset importer and refused to claim whole-language support outside the admitted subset.
3. It added validator-gated derivative surfaces: `SCIR-Hc`, `SCIR-L`, bounded Python reconstruction, bounded Wasm evidence, and bounded Rust importer-first evidence.
4. It froze the active executable evidence surface to the 11-case Python proof-loop corpus and made widening require explicit doctrine updates.
5. It hardened the benchmark doctrine around strong non-SCIR baselines: mandatory direct-source workflow baseline, mandatory typed-AST baseline, contamination reporting, reproducibility blocks, and strongest-baseline attribution.
6. It operationalized repository-level continuation outcomes and forced claim mode to fail unless SCIR was actually necessary.
7. It ran the strong-baseline falsification phase and landed on `SCIR_USEFUL_BUT_UNNECESSARY`.

## What We Ultimately Landed On

SCIR was viable on the admitted subset, but viability was not enough.

- The representation was internally coherent.
- The validator-first workflow was disciplined.
- Some benchmark surfaces showed value, especially on patch composability and representation regularity.
- But the project did not prove that SCIR was necessary relative to direct source plus typed-AST plus strong validation.

That was the stopping point.
The correct action was to freeze and retire the project rather than broaden semantics or protect the thesis from stronger baselines.

## Biggest Salvageable Parts

1. Explicit unsupportedness and boundary honesty.
   This repo learned to separate admitted executable subset, bounded support lanes, opaque or boundary-only cases, and deferred or unsupported cases without silent fallback.
2. Validator-first discipline.
   Import, transformation, lowering, reconstruction, and benchmark claims stayed gated by validators and contracts instead of impressionistic success.
3. Strong-baseline falsification doctrine.
   Mandatory direct-source and typed-AST baselines, explicit continuation outcomes, and claim-mode failure unless SCIR was necessary are worth preserving.
4. Benchmark artifact rigor.
   Manifest locks, reproducibility blocks, contamination reports, comparison summaries, strongest-baseline attribution, and repository-level continuation decisions are reusable infrastructure.
5. Patch-composability and representation-regularity metrics.
   These evaluation lenses were more durable than the full semantic-substrate thesis.
6. Subset-first, evidence-first engineering.
   Frozen corpus, admitted subset, explicit widening rules, and benchmark-before-broadening discipline were correct.
7. Claim and evidence separation.
   The repo learned to prevent compressed-representation evidence from leaking into broader semantic claims.

## Biggest Lessons Learned

1. Necessity is much harder than viability.
   A new representation has to beat strong simpler baselines, not just work.
2. Typed-AST plus strong validation is a stronger baseline than many architecture projects assume.
   If a substrate cannot clearly beat direct source and typed AST on the admitted tasks, it is probably too expensive.
3. Canonical semantic authority is expensive to maintain.
   The doctrinal and maintenance load of `SCIR-H`, `SCIR-Hc`, `SCIR-L`, validators, reconstruction, and benchmark governance is only justified if necessity is proven.
4. Good doctrine can outlive a failed thesis.
   Boundary honesty, validator-first gating, benchmark rigor, and falsification discipline remain valuable even though SCIR should not continue broadening.
5. Architecture should be cut where evidence says value actually exists.
   Future work should extract the mechanisms that proved useful rather than preserve the full SCIR architecture.

## Live surface

The repository remains on disk as a historical record and a source of reusable mechanisms.
The default working set is still:

- `README.md`
- `ARCHITECTURE.md`
- `CURRENT_FOCUS.md`
- `BACKLOG.md`
- `DECISION_REGISTER.md`
- `docs/`
- `specs/`
- `scir/`
- `scripts/`
- `tests/`
- `schemas/`
- `reports/examples/`

Tracked generated run outputs are intentionally excluded from the live surface.
The canonical gate still exercises the preserved bounded support lanes, but the repository no longer has an active widening target.
Helper-free Wasm remains retained backend evidence only for the MVP; it is not the next automatic implementation phase, and any future backend widening requires a fresh post-MVP reactivation decision.

## Historical Commands

```bash
python scripts/run_repo_validation.py
python scripts/run_repo_validation.py --require-rust
python scripts/validate_repo_contracts.py --mode audit
make build
make lint
make test
make validate
make benchmark
make benchmark-claim
```

`python scripts/run_repo_validation.py` remains the canonical repository-integrity check for the preserved historical state.
`make benchmark-claim` is expected to fail unless the repository-level continuation decision is `SCIR_NECESSARY`, which it is not.

## Historical Navigation

- [CURRENT_FOCUS.md](CURRENT_FOCUS.md) records the retirement state
- [ARCHITECTURE.md](ARCHITECTURE.md) preserves the final architecture and bounded implementation lane
- [SYSTEM_BOUNDARY.md](SYSTEM_BOUNDARY.md) preserves the supported-boundary rules that proved worth keeping
- [VALIDATION_STRATEGY.md](VALIDATION_STRATEGY.md) preserves the validator-first gate
- [BENCHMARK_STRATEGY.md](BENCHMARK_STRATEGY.md) preserves the strong-baseline falsification doctrine
