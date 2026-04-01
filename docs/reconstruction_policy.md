# Reconstruction Policy
Status: Normative

## Primary rule

Reconstruction is driven from validated `SCIR-H`. `SCIR-L` is diagnostic support, not the default reconstruction source.

## Bootstrap Phase 4 freeze

The executable bootstrap reconstruction contract is fixed to the current supported subset:

- `a_basic_function`: `python -> SCIR-H -> python`, profile `R`, preservation `P1`
- `a_async_await`: `python -> SCIR-H -> python`, profile `R`, preservation `P1`
- `b_if_else_return`: importer may emit Tier `B` canonical `SCIR-H`, but no reconstruction output is valid until the executable follow-on contract exists
- `b_direct_call`: importer may emit Tier `B` canonical `SCIR-H`, but no reconstruction output is valid until the executable follow-on contract exists
- `b_async_arg_await`: importer may emit Tier `B` canonical `SCIR-H`, but no reconstruction output is valid until the executable follow-on contract exists
- `c_opaque_call`: `python -> SCIR-H -> python`, profile `D-PY`, preservation `P3`, explicit opaque boundary accounting required
- `d_exec_eval`: no reconstruction output; importer rejection remains the only valid path
- `d_try_except`: importer may emit Tier `B` canonical `SCIR-H`, but no reconstruction output is valid until exception lowering and reconstruction contracts exist

## Goals

- regenerate source for supported subsets,
- preserve source-visible behavior according to profile-qualified preservation claims,
- keep idiomaticity acceptable for human review,
- emit provenance sidecars when exact source trivia is not preserved.

## Required reconstruction outputs

- reconstructed target source,
- `reconstruction_report`,
- `preservation_report`,
- provenance map back to `SCIR-H`,
- explicit downgrade notes for any `P2`, `P3`, or `PX` region.

## Acceptance rules

A reconstruction claim is incomplete without:

- compile result,
- test result,
- preservation level,
- active profile,
- idiomaticity assessment,
- provenance completeness status,
- unsupported and opaque region accounting.

For the bootstrap Phase 4 slice:

- compile and test evidence are mandatory and blocking for every supported reconstruction,
- idiomaticity remains mandatory evidence but not a hard pass/fail threshold,
- Tier `A` reconstructions must not introduce opaque accounting,
- the opaque case must retain explicit opaque boundary accounting,
- reconstruction claims may match or downgrade prior stage ceilings, but the frozen bootstrap path currently emits only the fixed `R/P1` and `D-PY/P3` case matrix,
- line-granular provenance is complete only when every non-empty canonical `SCIR-H` line has a corresponding provenance entry.

## Non-goals

Reconstruction is not obligated to preserve:

- original comments in canonical text,
- original local layout,
- accidental source idioms,
- exact runtime object identity across incompatible profiles.

For the bootstrap slice, exact comments, local layout, and other trivia remain explicitly out of scope even when the reconstructed source is textually close to the checked-in fixture.

## Failure conditions

Reconstruction work must stop and downgrade when:

- unsupported constructs enter the output path,
- opaque boundaries widen,
- preservation would be overstated,
- compile/test evidence is missing,
- provenance is incomplete,
- a non-executable importer-only or rejected case produces a reconstruction artifact.
