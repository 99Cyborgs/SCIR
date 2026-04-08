---
name: scir-lowering-provenance-check
description: Audit SCIR-H to SCIR-L lowering work when code or docs change lowering rules, SCIR-L validation, backend preparation, translation validation, or provenance-bearing artifacts. Use when Codex must verify every meaningful SCIR-L op keeps a valid origin, named lowering_rule, admitted op pairing, and derivative-only discipline.
---

# SCIR Lowering Provenance Check

## Goal

Keep `SCIR-L` derivative, auditable, and unable to acquire semantics that do not come from validated `SCIR-H`.

## Required context

Read `LOWERING_CONTRACT.md`, `specs/scir_l_spec.md`, `specs/validator_invariants.md`, `validators/validator_contracts.md`, and any touched lowering or backend files.

## Workflow

1. Enumerate every changed `SCIR-L` op, terminator, validator rule, or backend assumption.
2. For each changed op, identify:
   - the `SCIR-H` source shape
   - the required lowering rule
   - the expected `origin`
   - the active subset status
3. Verify the op/rule pairing remains one of the admitted rules in `LOWERING_CONTRACT.md`.
4. Confirm every semantically meaningful op still carries both `origin` and `lowering_rule`.
5. Check that provenance roots back into the emitting `SCIR-H` module rather than a synthesized backend-only abstraction.
6. Reject any attempt to:
   - add `SCIR-L`-only semantics
   - hide boundary calls without `opaque.call`
   - lower direct `SCIR-Hc`
   - widen the active Wasm-emittable subset without the required classifier, oracle, report, and decision updates
7. If backend emission is touched, separate lowering correctness from backend admissibility and preservation claims.

## Active checks

- `const`, `cmp`, `alloc`, `store`, `load`, `field.addr`, `call`, `async.resume`, and `opaque.call` are the active op set.
- `ret`, `br`, and `cond_br` are the active terminators.
- `H_AWAIT_RESUME` and `H_OPAQUE_CALL` are not Wasm-emittable in the active helper-free subset.
- `field.addr` is backend-executable only inside the frozen record-cell ABI slice.

## Output contract

Always return:
1. `Lowering Surface`
2. `Origin / Rule Coverage`
3. `Backend Subset Impact`
4. `Required Validation`

## Hard invariants

- `SCIR-H` remains the only semantic authority.
- No active `SCIR-L` op may exist without `origin` and `lowering_rule`.
- No backend contract may be mistaken for a new semantic admission.
- No new Wasm surface may enter the active path without doctrine, validator, and report sync.
