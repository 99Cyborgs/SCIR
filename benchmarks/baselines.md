# Baselines
Status: Normative

### Mandatory active baselines

- `direct source`
- `typed-AST`

### Track A additional executable baselines

- `lightweight regularized core or s-expression`

### Track C pilot baselines

- `direct source`
- `typed-AST`
- `lightweight regularized core or s-expression`

## Executable manifest labels

- `direct source`
- `typed-AST`
- `lightweight regularized core or s-expression`

## Adapter contract

- baseline adapters live under `benchmarks/baselines/source/`, `benchmarks/baselines/typed_ast/`, and `benchmarks/baselines/normalized/`
- the pluggable runner contract is `run_baseline(baseline_name, corpus_manifest)`
- every adapter must emit the same audit-row schema as SCIR sweep rows
- every adapter must run on the same corpus manifest and slice axes as SCIR
- every adapter must serialize deterministically

## Rule

Always interpret results against the strongest relevant baseline first. The active MVP must not compare SCIR only to weak baselines.
