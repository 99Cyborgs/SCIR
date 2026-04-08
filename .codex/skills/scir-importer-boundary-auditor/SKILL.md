---
name: scir-importer-boundary-auditor
description: Audit SCIR importer and fixture changes when Python, Rust, or TypeScript frontend work touches import scope, fixture corpora, tier reports, opaque-boundary handling, or unsupported cases. Use when Codex must keep importer behavior inside the admitted subset and prevent importer-only evidence from silently becoming active proof-loop support.
---

# SCIR Importer Boundary Auditor

## Goal

Keep importer work explicitly bounded by the active corpus, feature tiers, and unsupported-case policy.

## Required context

Read `specs/scir_h_spec.md`, `VALIDATION_STRATEGY.md`, `docs/feature_tiering.md`, `docs/unsupported_cases.md`, and the relevant `frontend/*/IMPORT_SCOPE.md` file before editing importer behavior or fixture posture.

## Workflow

1. Identify the frontend and case family:
   - Python executable proof-loop case
   - Python importer-only case
   - Rust importer-first evidence case
   - TypeScript deferred placeholder surface
2. Classify each touched source shape as `Tier A`, `B`, `C`, or `D`.
3. Verify the importer outputs the required artifacts:
   - `module_manifest`
   - `feature_tier_report`
   - `validation_report`
   - `opaque_boundary_contract` for every `Tier C` region
4. Check that importer-only cases remain importer-only:
   - no automatic lowering promotion
   - no automatic reconstruction claim
   - no benchmark claim widening
5. Keep unsafe and opaque regions explicit. If the shape is not modeled, mark it `Tier C` or reject it as `Tier D`.
6. Sync importer scope docs, unsupported-case docs, and corpus manifests when the admitted boundary changes.
7. Select validation based on the touched importer surface, then run the smallest sufficient gate.

## Active boundary reminders

- Python proof-loop cases are `a_basic_function`, `a_async_await`, `b_direct_call`, and `c_opaque_call`.
- Python loop and `try/catch` cases are importer-only canonical `SCIR-H` evidence.
- Rust remains importer-first evidence and must not be described as active round-trip or benchmark support.
- Active TypeScript implementation work is deferred.

## Output contract

Always return:
1. `Frontend Surface`
2. `Tier / Boundary Outcome`
3. `Required Companion Updates`
4. `Required Validation`

## Hard invariants

- No silent fallback for unsupported source constructs.
- No importer-only evidence may be described as active proof-loop support.
- No hidden opaque or unsafe boundary is allowed.
- No deferred TypeScript surface may be restated as active implementation.
