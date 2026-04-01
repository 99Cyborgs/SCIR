# TypeScript Import Scope
Status: Normative

## Phase 7 first-slice contract

The first admitted Phase 7 TypeScript slice is narrower than the long-run candidate subset:

- `interface` declarations are the only admitted witness-bearing surface
- admitted shapes are planning-only and importer-only
- the slice is limited to module-local interface consumption patterns that keep host assumptions explicit
- no executable `D-JS`, lowering, reconstruction, or benchmark claim is admitted for this slice

## First fixture bundle contract

The first checked-in TypeScript fixture corpus must reuse the existing importer bundle model:

- admitted cases include source text, canonical `SCIR-H`, `module_manifest.json`, `feature_tier_report.json`, and `validation_report.json`
- rejected first-slice boundary cases include source text, `module_manifest.json`, `feature_tier_report.json`, and `validation_report.json`, but no canonical `SCIR-H`
- no first-slice TypeScript fixture may include `SCIR-L`, translation, reconstruction, or benchmark artifacts
- fixture bundles must make witness semantics, host assumptions, tier classification, and non-executable status explicit in the checked-in reports

## Initial case matrix

Future initial TypeScript fixture bundles are fixed to the following case IDs:

### Admitted first-slice cases

- `a_interface_decl`
- `a_interface_local_witness_use`

### Rejected first-slice boundary cases

- `d_function_decl`
- `d_async_function`
- `d_class_implements_interface`
- `d_prototype_assignment`
- `d_decorator_class`
- `d_proxy_construct`
- `d_type_level_runtime_gate`

The initial corpus intentionally contains no first-slice `B` or `C` TypeScript case.

## Initial targeted subset

### Tier A first-slice constructs

- modules
- interfaces as explicit witnesses

### Deferred candidate constructs

- functions and `async` functions
- classes without proxy or decorator semantics
- promises normalized to async effects
- structured object and record-like patterns

### Tier B candidate constructs

- structural interface normalization with reduced idiomaticity
- selected prototype-based class behavior
- event-loop-sensitive async behavior where profile `D-JS` remains explicit

### Tier C constructs

- host runtime stubs
- dynamic property traps
- JS interop surfaces not semantically modeled

### Tier D constructs

- decorators that materially affect runtime semantics
- proxies
- emit-dependent reflection as semantic source of truth
- advanced type-level computation used as executable semantics

## Preservation expectations

- `D-JS` is usually the primary profile
- `R` is possible for structured subsets
- `N` claims are weak unless host semantics are removed

## Post-6B roadmap candidate

The default post-6B witness-bearing second-language slice is interface-shaped TypeScript witness evidence:

- interfaces remain the first-class witness surface,
- the first admitted slice is limited to interface declarations plus module-local witness consumption doctrine,
- host-runtime-sensitive semantics remain explicit under `D-JS`,
- importer and validator evidence may grow before executable lowering, reconstruction, or benchmark claims do,
- Rust trait/impl execution work does not supersede this candidate slice unless a later plan says so.

## Importer obligations

- keep structural typing explicit as witnesses or contracts,
- keep host-runtime assumptions explicit,
- keep the first admitted slice importer-only and non-executable,
- require a fixed fixture bundle and report package before importer implementation broadens,
- do not treat general functions, async behavior, classes, or prototype semantics as admitted in the first Phase 7 step,
- do not erase proxy or decorator behavior into fake support.
