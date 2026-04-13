# Backends
Status: Normative

Only Wasm is a retained backend surface in the MVP.

That surface remains bounded and validated on disk, but it is not an active scope-expansion lane.
Backend contracts must remain derivative of validated `SCIR-L` and must not be used to imply broader semantic support than the active subset justifies.
Any future Wasm widening or backend activation is a post-MVP reactivation decision that must update roadmap, profile/preservation doctrine, and repo-contract surfaces together.
