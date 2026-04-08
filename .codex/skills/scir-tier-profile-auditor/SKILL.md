---
name: scir-tier-profile-auditor
description: Audit SCIR coverage and preservation claims when work changes feature admission, unsupported handling, benchmark wording, preservation reports, or profile labels. Use when Codex must verify valid use of Tier A-D, P0-PX, active profiles, boundary annotations, downgrade reasons, and explicit unsupported posture.
---

# SCIR Tier Profile Auditor

## Goal

Prevent claim inflation by forcing every changed surface to use valid SCIR tier, profile, and preservation labels.

## Required context

Read `docs/feature_tiering.md`, `docs/target_profiles.md`, `docs/preservation_contract.md`, `docs/unsupported_cases.md`, `specs/validator_invariants.md`, and any touched benchmark or report schema.

## Workflow

1. Inventory every claim surface touched by the change:
   - tier labels
   - profile labels
   - preservation paths
   - preservation levels
   - downgrade reasons
   - boundary annotations
   - evidence wording
2. Check each label against the active doctrine:
   - `Tier A`: validator-understood semantics with active proof-loop evidence
   - `Tier B`: validator-understood semantics without active downstream proof-loop evidence
   - `Tier C`: opaque or unsafe boundary only
   - `Tier D`: rejected or unsupported
3. Verify every preservation claim names both `path` and `profile`, and that the chosen `P0/P1/P2/P3/PX` level matches the declared ceiling.
4. Apply the conservative rule from `docs/feature_tiering.md`: choose the lower tier when uncertain.
5. Treat `P3` as boundary annotation only, never as semantic understanding.
6. Reject unqualified "support," "fidelity," "parity," or "works" language unless the exact tier, profile, and preservation path are explicit.
7. Ensure unsupported shapes remain explicit in `docs/unsupported_cases.md` or the relevant importer scope file.

## Common failure patterns

- importer-only evidence presented as active lowering, reconstruction, or benchmark support
- Wasm success described as native or host-runtime parity
- `Tier C` wording presented as semantic support
- `P2` or `P3` cases summarized as if they were `P0` or `P1`
- profile `D-JS` or Track `D` treated as active

## Output contract

Always return:
1. `Claim Surface Inventory`
2. `Valid Labels`
3. `Required Replacements`
4. `Blocking Overclaims`

## Hard invariants

- No SCIR claim is valid without the canonical labels.
- No preservation claim is valid without `path` and `profile`.
- No benchmark or backend wording may imply native, `D-JS`, or whole-language parity.
- No uncertain case may be rounded up to a stronger tier.
