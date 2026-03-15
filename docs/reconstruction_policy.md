# Reconstruction Policy
Status: Normative

## Primary rule

Reconstruction is driven from validated `SCIR-H`. `SCIR-L` is diagnostic support, not the default reconstruction source.

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
- unsupported and opaque region accounting.

## Non-goals

Reconstruction is not obligated to preserve:

- original comments in canonical text,
- original local layout,
- accidental source idioms,
- exact runtime object identity across incompatible profiles.

## Failure conditions

Reconstruction work must stop and downgrade when:

- unsupported constructs enter the output path,
- opaque boundaries widen,
- preservation would be overstated,
- compile/test evidence is missing.
