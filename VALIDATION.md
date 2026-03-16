# VALIDATION

## Portfolio governance check

These governance notes are valid only if they remain consistent with:

- `SYSTEM_BOUNDARY.md`
- `ARCHITECTURE.md`
- `VALIDATION_STRATEGY.md`
- `BENCHMARK_STRATEGY.md`

## Existing repo validation path

```bash
make validate
make benchmark
```

Do not treat SCIR as promotion-ready if those validation surfaces are not credible for the proposed extraction target.
