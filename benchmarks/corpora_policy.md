# Corpora Policy
Status: Normative

## Active corpora

- `python-bootstrap-fixtures` for Track `A`
- `python-bootstrap-fixtures` for Track `B`
- `tests/corpora/python_tier_a_micro_corpus.json` freezes the Tier `A` micro corpus used by sweep smoke
- `tests/corpora/python_proof_loop_corpus.json` freezes the full active Python proof-loop benchmark corpus

## Conditional Track C pilot corpus

Track `C` reuses the fixed executable Python proof-loop corpus and reframes it as Python single-function repair tasks.
It is not a new broad benchmark corpus and it does not widen the default executable gate.

### Track C pilot cases

- `a_basic_function`
- `a_async_await`
- `b_direct_call`
- `c_opaque_call`

## Rules

- record dataset name and hash in the benchmark manifest
- declare split membership in the checked-in `split_contract`
- keep checked-in corpus manifests hash-locked to the exact fixture files they name
- keep manifests immutable once a reporting run locks them in `manifest_lock.json`
- record language and tier mix
- keep contamination controls explicit
- do not generalize from unsupported-heavy corpora
- repository-scale issue corpora remain deferred until earlier loops are stable
