# ARCHITECTURE_SUMMARY

SCIR is a two-layer semantic system:

- `SCIR-H` is the canonical high-level semantic representation
- `SCIR-L` is the derivative lowered control/dataflow form

Its credible first product is importer + validator + lowering + reconstruction + benchmark harness. Portfolio governance should preserve that narrow path and avoid importing the full semantic surface into core prematurely.
