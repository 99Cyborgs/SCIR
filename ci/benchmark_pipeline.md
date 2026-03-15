# Benchmark Pipeline
Status: Normative

## Current purpose

The current benchmark pipeline is a doctrine dry run. It validates that benchmark policy, schemas, contamination controls, gating documents, and benchmark-checker self-tests are present and passing.

## Blocking command

```bash
make benchmark
```

## Future expansion

When executable harness code lands, the pipeline must additionally:

- validate benchmark manifests,
- validate result bundle structure,
- require named baselines,
- require contamination control metadata.
