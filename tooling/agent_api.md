# Agent API Contract
Status: Normative

This contract defines the minimum stable-ID-oriented workflow for agent tools.

## Required operations

### Slice request

Input:

- module IDs
- symbol IDs or stable node IDs
- active profile
- requested provenance depth

Output:

- canonical `SCIR-H` slice
- dependency summary
- relevant opaque boundary contracts

### Patch plan

Input:

- objective
- touched stable IDs
- claimed profile
- claimed preservation ceiling

Output:

- plan record
- validation obligations
- benchmark obligations if applicable

### Patch application

Input:

- stable-ID-addressed delta operations
- replacement declarations or bodies
- expected touched IDs

Output:

- updated `SCIR-H`
- changed-ID summary
- validator status

### Validation request

Input:

- artifact IDs
- validator set
- claimed preservation level

Output:

- `validation_report` and, if applicable, `preservation_report`

### Reconstruction request

Input:

- validated `SCIR-H`
- target language
- active profile

Output:

- reconstructed source
- `reconstruction_report`
- provenance map

## Delta discipline

Patch operations must target stable IDs, not raw line numbers, whenever the necessary provenance exists.
