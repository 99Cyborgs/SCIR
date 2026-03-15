# TypeScript Frontend Local Rules
Status: Normative

Read first:

1. `frontend/README.md`
2. `frontend/typescript/IMPORT_SCOPE.md`
3. `docs/feature_tiering.md`
4. `docs/unsupported_cases.md`
5. `specs/type_effect_capability_model.md`

Local rules:

- keep structural typing and runtime semantics separate,
- do not treat decorators, proxies, or emit-dependent reflection as Tier `A` or `B`,
- represent host runtime obligations explicitly under profile `D`,
- do not claim native-performance semantics for host-object-heavy code.
