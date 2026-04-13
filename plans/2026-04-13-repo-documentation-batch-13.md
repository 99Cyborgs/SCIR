# Repo Documentation Batch 13

Status: complete
Owner: Codex
Date: 2026-04-13

## Objective

Add comment-only documentation to the Python bootstrap importer and its conformance checker so the fixed proof-loop corpus, admitted source shapes, and checked-in bundle contracts are locally readable.

## Scope

- Normalize the file headers in `scripts/scir_python_bootstrap.py` and `scripts/python_importer_conformance.py`
- Add function-level docstrings for the helper, validator, mutation, self-test, and CLI surfaces in both files
- Add only narrow inline comments where contract intent is hidden

## Non-goals

- No logic changes, refactors, renames, or parser-shape changes
- No widening of the admitted Python corpus or supported syntax
- No schema, validator, benchmark, or active proof-loop policy changes

## Touched files

- `plans/2026-04-13-repo-documentation-batch-13.md`
- `scripts/scir_python_bootstrap.py`
- `scripts/python_importer_conformance.py`

## Invariants that must remain true

- The Python bootstrap importer remains fixed-corpus and fixture-shaped, not general-purpose
- Conformance checks remain byte- and schema-exact governance checks over checked-in artifacts
- All edits remain comment-only and must preserve behavior exactly

## Risks

- GitNexus symbol lookup for shared names like `build_bundle`, `check_case`, and `main` is ambiguous across Python, Rust, and TypeScript importer surfaces, so file-scoped context must be used carefully
- These files feed the bootstrap pipeline, sweep, benchmark dry-run, and repo validation surfaces, so inaccurate comments would misstate retained importer doctrine

## Validation steps

- `python -m py_compile G:\GitHub\incubate\SCIR\scripts\scir_python_bootstrap.py`
- `python -m py_compile G:\GitHub\incubate\SCIR\scripts\python_importer_conformance.py`
- `python scripts/run_repo_lint.py`
- `python scripts/run_repo_validation.py`

## Rollback strategy

Revert only the documentation edits in the two importer files and this historical plan if review finds any prose that misstates the fixed-corpus or conformance contracts.

## Evidence required for completion

- Diff review confirmed comment-only edits in `scripts/scir_python_bootstrap.py` and `scripts/python_importer_conformance.py`
- GitNexus impact or context was recorded on 2026-04-13 for the Python importer batch, with explicit note that several symbol names were ambiguous across language-specific importer files
- `python -m py_compile G:\GitHub\incubate\SCIR\scripts\scir_python_bootstrap.py` passed on 2026-04-13
- `python -m py_compile G:\GitHub\incubate\SCIR\scripts\python_importer_conformance.py` passed on 2026-04-13
- `python scripts/run_repo_lint.py` passed on 2026-04-13
- `python scripts/run_repo_validation.py` passed on 2026-04-13
