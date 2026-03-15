# Project Overview
Status: Informative

SCIR is a semantic compression program with two explicit layers.

- `SCIR-H` is the canonical high-level form.
- `SCIR-L` is the lowered control and analysis form.

The first product question is not “can SCIR replace mainstream languages?”
The first product question is “can SCIR import a useful subset, validate it, lower it, reconstruct it, and benchmark it against strong baselines?”

## What is being built first

1. `SCIR-H` core
2. parser / formatter contract
3. `SCIR-H` validator
4. stable IDs and provenance
5. benchmark harness skeleton
6. Python subset importer
7. `SCIR-L` core and `H -> L`
8. reconstruction pipeline
9. Rust subset importer
10. initial optimization work

## What is not being built first

- new end-user syntax,
- broad C++ fidelity,
- backend sprawl,
- proof-heavy infrastructure before operational value,
- benchmark-free AI claims.

## Repository reading path

Read `AGENTS.md`, `SYSTEM_BOUNDARY.md`, `ARCHITECTURE.md`, then `specs/`.

## Project success test

SCIR survives as an AI-facing substrate only if it beats strong baselines on explicit tasks. Otherwise it may survive only as compiler and transformation infrastructure.
