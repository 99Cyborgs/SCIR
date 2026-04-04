---
name: scir-proof-loop-guard
description: Use when changing SCIR specs, schemas, validators, importers, lowering, reconstruction, or benchmark harnesses so SCIR-H remains the only semantic authority and the bounded proof loop stays honest. Do not use for generic frontend or tooling edits that do not affect semantic or validation contracts.
---

# SCIR Proof Loop Guard

## Purpose
Protect the SCIR doctrine: `SCIR-H` is authoritative, `SCIR-Hc` is derived, and `SCIR-L` is derivative-only. Keep the proof loop and importer evidence bounded.

## When to use
Use this skill when touching:
- `specs/`
- `schemas/`
- `validators/`
- importer or frontend conformance paths
- lowering, reconstruction, or backend contracts
- benchmark harness scripts or manifests

## Required inputs
- repo root
- changed paths

## Operating procedure
1. Read the root `AGENTS.md` read order before coding.
2. Run `scripts/check_scir_proof_loop.py --repo-root <repo-root> --changed <paths...>`.
3. Preserve `SCIR-H` as the only normative semantic representation.
4. Treat Rust, TypeScript, and Wasm surfaces as bounded evidence layers unless the specs admit more.
5. Use the repo validation runner first, then the narrower importer or benchmark checks indicated by the touched surface.

## Output contract
Always return:
1. `Semantic Authority Impact`
2. `Proof Loop Impact`
3. `Importer / Backend Impact`
4. `Required Validation`

## Hard invariants
- Do not silently widen the admitted subset.
- Do not let `SCIR-L` or backend artifacts become semantic authority.
- Do not claim round-trip or benchmark coverage broader than the current admitted loop.
- Track `A` and Track `B` reproducibility outrank speculative widening.

## Failure handling
If a change pressures the admitted boundary:
- mark it as a boundary change, not a routine implementation change
- point to the governing spec that would need revision
- avoid shipping the wider claim under old validation language
