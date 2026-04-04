# SCIR
Status: Informative

SCIR is a two-layer semantic compression substrate.

## Goal

- make `SCIR-H` the only normative semantic representation
- keep `SCIR-L` derivative-only for lowering, validation, backend preparation, and reference emission
- prove the narrowed MVP is worth continuing through validator-enforced preservation, a credible Python proof loop, bounded Rust importer evidence, a subset-bound Wasm reference backend, and strong-baseline Track `A` / Track `B` benchmarks

## Current State

- the active MVP is limited to canonical `SCIR-H`, derived `SCIR-Hc`, derivative `SCIR-L`, their validators, Python subset import, Rust safe-subset import evidence, Python reconstruction from validated `SCIR-H`, the Wasm reference-backend MVP contract, and Track `A` / Track `B` benchmark harnesses
- the confirmed executable proof loop is Python import -> `SCIR-H` -> `SCIR-H` validation -> `SCIR-Hc` derivation and validation -> `SCIR-H -> SCIR-L` lowering -> `SCIR-L` validation -> Python reconstruction -> Track `A` / Track `B` benchmark checks
- the active backend path additionally validates emitted Wasm against bounded `SCIR-L` execution traces before accepting `l_to_wasm` success, and that translation-validation report now makes claim strength, subset admission, equivalence mode, observable set, downgrade reason, and provenance-linked findings explicit
- helper-free Wasm execution is now fail-closed on unsupported surface: imports, helper trampolines, indirect calls, mutable globals, memory growth, reference types, unsupported instructions, and unsupported control constructs are classified before execution rather than being attempted implicitly
- the active Wasm lane remains an `execution_backed_subset` claim only; it does not claim full backend equivalence beyond the admitted helper-free bounded subset
- an opt-in experimental Python translation-validation lane exists to keep bounded backend execution support alive without changing the default Wasm-first backend contract or the `SCIR-H -> Python` reconstruction contract
- Rust is active at the importer-evidence layer and optional bounded validation slice only; Rust reconstruction, active TypeScript implementation, Track `D`, native-backend breadth, and broad runtime or tooling claims remain deferred
- the current operator entrypoints remain:

```bash
python scripts/run_repo_validation.py
python scripts/validate_translation.py
python scripts/validate_translation.py --include-experimental-python
python scripts/benchmark_contract_dry_run.py --claim-run
python scripts/benchmark_repro.py --run-id <run-id>
python scripts/sync_python_proof_loop_artifacts.py --mode check
python scripts/sync_python_proof_loop_artifacts.py --mode write
python scripts/benchmark_contract_dry_run.py --include-track-c-pilot
python scripts/run_repo_validation.py --include-track-c-pilot
python scripts/run_repo_validation.py --include-experimental-python-translation
```

## Next Steps

1. keep the Python proof loop healthy without widening beyond the admitted subset
2. keep Rust importer evidence aligned to the same `SCIR-H` contract without widening round-trip or benchmark claims
3. harden identity, canonical-storage, and derived-view boundaries so `SCIR-H` remains the only semantic authority
4. keep the Wasm reference backend explicit, profile-qualified, subset-classified, and bounded to the currently admitted emission surface
5. keep Track `A` and Track `B` reproducible and baseline-strong
6. only expand execution-backed backend surface when subset-classifier support, bounded-oracle support, adversarial tests, updated examples, and explicit governance updates land together
7. consider the minimal opt-in Track `C` pilot only if the earlier loop remains stable
