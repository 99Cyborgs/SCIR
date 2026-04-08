from __future__ import annotations

import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from benchmark_contract_metadata import (
    BENCHMARK_CONTRACT_METADATA,
    benchmark_track_baselines,
    benchmark_track_contract,
    render_track_c_sample_refresh_note,
)
from scir_h_bootstrap_model import SCIR_H_KERNEL_METADATA
from scir_python_bootstrap import PYTHON_PROOF_LOOP_METADATA
from scir_rust_bootstrap import RUST_IMPORTER_METADATA
from wasm_backend_metadata import WASM_BACKEND_METADATA


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- `{item}`" for item in items)


def render_python_import_scope() -> str:
    return (
        "# Python Import Scope\n"
        "Status: Normative\n\n"
        "## Active corpus\n\n"
        "### Executable proof-loop cases\n\n"
        f"{_bullet_list(list(PYTHON_PROOF_LOOP_METADATA['executable_cases']))}\n\n"
        "### Importer-only canonical `SCIR-H` cases\n\n"
        f"{_bullet_list(list(PYTHON_PROOF_LOOP_METADATA['importer_only_cases']))}\n\n"
        "### Rejected cases\n\n"
        f"{_bullet_list(list(PYTHON_PROOF_LOOP_METADATA['rejected_cases']))}\n\n"
        "## Active executable path\n\n"
        "Only the executable proof-loop cases above are active end-to-end MVP claims.\n\n"
        "## Importer-only cases\n\n"
        "The importer-only cases above remain canonical `SCIR-H` evidence only. They do not imply active lowering or reconstruction support.\n\n"
        "## Unsupported\n\n"
        "- `exec` / `eval`\n"
        "- import hooks\n"
        "- metaclasses and descriptor mutation\n"
        "- broader exception control\n"
    )


def render_rust_import_scope() -> str:
    wasm_cases = [
        case_name
        for case_name, contract in RUST_IMPORTER_METADATA["case_contracts"].items()
        if contract["wasm_emittable"]
    ]
    await_cases = list(RUST_IMPORTER_METADATA["await_cases"])
    ownership_cases = list(RUST_IMPORTER_METADATA["ownership_boundary_cases"])
    unsafe_capability = RUST_IMPORTER_METADATA["case_contracts"]["c_unsafe_call"]["required_capabilities"][0]
    return (
        "# Rust Import Scope\n"
        "Status: Normative\n\n"
        "## Active scope\n\n"
        "The Rust MVP scope is importer-only safe-subset evidence.\n\n"
        "## Active corpus\n\n"
        "### Importer-first evidence cases\n\n"
        f"{_bullet_list(list(RUST_IMPORTER_METADATA['supported_cases']))}\n\n"
        "### Tier A importer-evidence cases\n\n"
        f"{_bullet_list(list(RUST_IMPORTER_METADATA['tier_a_cases']))}\n\n"
        "### Helper-free Wasm-emittable case\n\n"
        f"{_bullet_list(wasm_cases)}\n\n"
        "### Await-bearing cases\n\n"
        f"{_bullet_list(await_cases)}\n\n"
        "### Ownership-bearing and boundary-accounted cases\n\n"
        f"{_bullet_list(ownership_cases)}\n\n"
        "### Rejected cases\n\n"
        f"{_bullet_list(list(RUST_IMPORTER_METADATA['rejected_cases']))}\n\n"
        "## Supported shapes\n\n"
        "### Tier A active importer shapes\n\n"
        "- free functions\n"
        "- named record types\n"
        "- `borrow_mut` parameters\n"
        "- mutable locals\n"
        "- record field places in read and write positions\n"
        "- simple async functions with explicit `await`\n\n"
        "### Tier C active importer shape\n\n"
        "- explicit unsafe call boundary imported as an opaque boundary\n\n"
        "## Async contract\n\n"
        "- `a_async_await` is the admitted Tier `A` await-bearing Rust case. Its importer bundle must keep `async fn load_once -> int !await` explicit in canonical `SCIR-H`, keep `return await fetch_value()` visible, and keep the optional Rust `H -> L` validation lane preserving the await boundary without implying helper-free Wasm emission, Rust reconstruction, or broader backend claims.\n\n"
        "## Ownership and boundary contract\n\n"
        "- `a_struct_field_borrow_mut` is the admitted Tier `A` ownership-bearing Rust case. Its importer bundle must keep `borrow_mut<Counter>` explicit in canonical `SCIR-H`, keep `counter.value` field-place mutation visible, and keep the same contract through the optional Rust `H -> L` validation lane.\n"
        f"- `c_unsafe_call` is the admitted Tier `C` unsafe-boundary Rust case. Its importer bundle must keep the boundary explicit, keep `{unsafe_capability}` mirrored between `module_manifest.dependencies` and `opaque_boundary_contract.capabilities`, and keep the optional Rust `H -> L` validation lane boundary-accounting-only rather than implying Rust reconstruction, Wasm emission, or broader backend claims.\n\n"
        "### Tier D rejected shape classes\n\n"
        "- proc macros\n"
        "- build scripts\n"
        "- self-referential pin patterns\n"
        "- unsafe alias choreography beyond explicit boundary treatment\n\n"
        "## Claim boundary\n\n"
        "Rust importer evidence must not be presented as an active round-trip, backend, or benchmark claim unless the root roadmap and benchmark strategy are updated together.\n"
    )


def render_benchmark_tracks_doc() -> str:
    track_c = benchmark_track_contract("C")
    return (
        "# Benchmark Tracks\n"
        "Status: Normative\n\n"
        "| Track | Question | MVP status |\n"
        "| --- | --- | --- |\n"
        "| `A` | Are canonical `SCIR-H` and compressed `SCIR-Hc` jointly explicit and compact enough to justify themselves? | active |\n"
        "| `B` | Can the Python proof loop round-trip through import, validation, lowering, and reconstruction? | active |\n"
        "| `C` | Does SCIR beat strong baselines on tightly controlled repair or editing tasks? | conditional pilot only |\n"
        "| `D` | Is runtime or backend performance competitive? | deferred |\n\n"
        "## Active executable tracks\n\n"
        f"{_bullet_list(BENCHMARK_CONTRACT_METADATA['active_tracks'])}\n\n"
        "## Conditional tracks\n\n"
        f"{_bullet_list(BENCHMARK_CONTRACT_METADATA['conditional_tracks'])}\n\n"
        "## Deferred tracks\n\n"
        f"{_bullet_list(BENCHMARK_CONTRACT_METADATA['deferred_tracks'])}\n\n"
        "## Track C pilot task family\n\n"
        f"{_bullet_list([track_c['task_family']])}\n\n"
        "## Track C executable pilot posture\n\n"
        f"{_bullet_list(track_c['execution_posture'])}\n\n"
        "## Track C disposition\n\n"
        f"{_bullet_list(track_c['disposition'])}\n\n"
        "## Track C sample synchronization\n\n"
        f"{_bullet_list(track_c['sample_sync_requirements'])}\n\n"
        "## Track C sample posture re-decision triggers\n\n"
        f"{_bullet_list(track_c['sample_posture_redecision_triggers'])}\n\n"
        "## Track C editorial-only sample refreshes\n\n"
        f"{_bullet_list(track_c['editorial_only_sample_refreshes'])}\n\n"
        "## Track C non-editorial sample refresh provenance\n\n"
        f"{_bullet_list(track_c['non_editorial_sample_refresh_provenance'])}\n\n"
        "## Track C non-editorial sample refresh provenance note format\n\n"
        f"{_bullet_list(track_c['non_editorial_sample_refresh_note_format'])}\n\n"
        "## Track C non-editorial sample refresh provenance note location\n\n"
        f"{_bullet_list(track_c['non_editorial_sample_refresh_note_location'])}\n\n"
        "## Track C non-editorial sample refresh provenance note overwrite semantics\n\n"
        f"{_bullet_list(track_c['non_editorial_sample_refresh_note_overwrite'])}\n\n"
        "## Rule\n\n"
        "Track `C` may not become active until the earlier proof loop remains stable.\n"
        "Track `D` is outside the active MVP.\n"
    )


def render_benchmark_baselines_doc() -> str:
    return (
        "# Baselines\n"
        "Status: Normative\n\n"
        "### Mandatory active baselines\n\n"
        f"{_bullet_list(BENCHMARK_CONTRACT_METADATA['mandatory_baselines'])}\n\n"
        "### Track A additional executable baselines\n\n"
        f"{_bullet_list(BENCHMARK_CONTRACT_METADATA['track_specific_additional_baselines']['A'])}\n\n"
        "### Track C pilot baselines\n\n"
        f"{_bullet_list(benchmark_track_baselines('C'))}\n\n"
        "## Executable manifest labels\n\n"
        f"{_bullet_list(benchmark_track_baselines('C'))}\n\n"
        "## Adapter contract\n\n"
        "- baseline adapters live under `benchmarks/baselines/source/`, `benchmarks/baselines/typed_ast/`, and `benchmarks/baselines/normalized/`\n"
        "- the pluggable runner contract is `run_baseline(baseline_name, corpus_manifest)`\n"
        "- every adapter must emit the same audit-row schema as SCIR sweep rows\n"
        "- every adapter must run on the same corpus manifest and slice axes as SCIR\n"
        "- every adapter must serialize deterministically\n\n"
        "## Rule\n\n"
        "Always interpret results against the strongest relevant baseline first. The active MVP must not compare SCIR only to weak baselines.\n"
    )


def render_benchmark_success_failure_gates_doc() -> str:
    track_a = benchmark_track_contract("A")
    track_b = benchmark_track_contract("B")
    track_c = benchmark_track_contract("C")
    return (
        "# Success and Failure Gates\n"
        "Status: Normative\n\n"
        "## Active success thresholds\n\n"
        "| ID | Threshold |\n"
        "| --- | --- |\n"
        "| S1 | Track `B` Tier `A` compile and test pass rate >= 95% on the fixed Python proof-loop corpus |\n"
        "| S2 | A Track `C` pilot may proceed only after Track `A` and Track `B` remain stable on the fixed proof-loop corpus |\n"
        "| S3 | canonical `SCIR-H` median token count <= 1.10x canonical source or compressed `SCIR-Hc` median token count <= 0.75x typed AST while canonical `SCIR-H` still increases semantic explicitness materially |\n"
        "| S4 | Explicit opaque fallback remains < 15% of nodes in the active proof-loop corpus |\n\n"
        "## Active kill criteria\n\n"
        "| ID | Condition |\n"
        "| --- | --- |\n"
        "| K1 | no evidence that the active proof loop is useful relative to direct source and typed AST on controlled tasks |\n"
        "| K2 | `SCIR-H` median token count > 1.5x source without compensating gains |\n"
        "| K3 | Track `B` Tier `A` compile and test pass rate stays < 90% after stabilization |\n"
        "| K4 | opaque fallback required for > 25% of the targeted proof-loop corpus |\n"
        "| K5 | Wasm success is being used to imply native or host parity |\n\n"
        "## Audit claim gates\n\n"
        "Explicit claim runs must fail when:\n\n"
        "- baseline results are missing\n"
        "- corpus hash mismatches are detected across the benchmark bundle\n"
        "- a reproducibility block is missing\n"
        "- contamination is detected\n"
        "- `claim_class` or `evidence_class` is missing from `benchmark_report`\n"
        "- `SCIR-Hc` evidence leaks across claim classes or implies semantic-preservation, reconstruction-fidelity, or cross-language claims\n"
        "- none of the active claim-gate conditions hold\n\n"
        "Active claim-gate conditions are:\n\n"
        "- `SCIR-Hc` beats typed-AST on `LCR`\n"
        "- canonical `SCIR-H` beats typed-AST on `SCPR` by at least 15 percentage points\n"
        "- canonical `SCIR-H` shows a positive typed-AST patch-composability gain\n\n"
        "Each `benchmark_report` may evaluate only the condition set admitted by its declared `claim_class`.\n"
        "Mixed-class claim reports are invalid even when multiple conditions happen to pass diagnostically.\n\n"
        "## Rule\n\n"
        "Track `A` and `B` are the only active executable benchmark gates in the MVP.\n\n"
        "### Track A success gates\n\n"
        f"{_bullet_list(track_a['success_gates'])}\n\n"
        "### Track A kill gates\n\n"
        f"{_bullet_list(track_a['kill_gates'])}\n\n"
        "### Track B success gates\n\n"
        f"{_bullet_list(track_b['success_gates'])}\n\n"
        "### Track B kill gates\n\n"
        f"{_bullet_list(track_b['kill_gates'])}\n\n"
        "### Conditional benchmark gate\n\n"
        f"{_bullet_list(BENCHMARK_CONTRACT_METADATA['conditional_success_gates'])}\n\n"
        "### Track C pilot success gates\n\n"
        f"{_bullet_list(track_c['success_gates'])}\n\n"
        "### Track C pilot kill gates\n\n"
        f"{_bullet_list(track_c['kill_gates'])}\n\n"
        "### Track C retention criteria\n\n"
        f"{_bullet_list(track_c['retention_criteria'])}\n\n"
        "### Track C retirement triggers\n\n"
        f"{_bullet_list(track_c['retirement_triggers'])}\n\n"
        "### Deferred benchmark misuse gate\n\n"
        f"{_bullet_list(BENCHMARK_CONTRACT_METADATA['deferred_kill_gates'])}\n"
    )


def render_benchmark_corpora_policy_doc() -> str:
    track_c = benchmark_track_contract("C")
    return (
        "# Corpora Policy\n"
        "Status: Normative\n\n"
        "## Active corpora\n\n"
        "- `python-bootstrap-fixtures` for Track `A`\n"
        "- `python-bootstrap-fixtures` for Track `B`\n"
        "- `tests/corpora/python_tier_a_micro_corpus.json` freezes the Tier `A` micro corpus used by sweep smoke\n"
        "- `tests/corpora/python_proof_loop_corpus.json` freezes the full active Python proof-loop benchmark corpus\n\n"
        "## Conditional Track C pilot corpus\n\n"
        "Track `C` reuses the fixed executable Python proof-loop corpus and reframes it as Python single-function repair tasks.\n"
        "It is not a new broad benchmark corpus and it does not widen the default executable gate.\n\n"
        "### Track C pilot cases\n\n"
        f"{_bullet_list(track_c['pilot_cases'])}\n\n"
        "## Rules\n\n"
        "- record dataset name and hash in the benchmark manifest\n"
        "- declare split membership in the checked-in `split_contract`\n"
        "- keep checked-in corpus manifests hash-locked to the exact fixture files they name\n"
        "- keep manifests immutable once a reporting run locks them in `manifest_lock.json`\n"
        "- record language and tier mix\n"
        "- keep contamination controls explicit\n"
        "- do not generalize from unsupported-heavy corpora\n"
        "- repository-scale issue corpora remain deferred until earlier loops are stable\n"
    )


def render_wasm_backend_readme() -> str:
    admitted_python = [
        f"fixture.python_importer.{case}" for case in WASM_BACKEND_METADATA["emittable_python_cases"]
    ]
    admitted_rust = [
        f"fixture.rust_importer.{case}" for case in WASM_BACKEND_METADATA["emittable_rust_cases"]
    ]
    blocked_python = [
        contract["module_id"] for contract in WASM_BACKEND_METADATA["non_emittable_python_cases"].values()
    ]
    blocked_rust = [
        contract["module_id"] for contract in WASM_BACKEND_METADATA["non_emittable_rust_cases"].values()
    ]
    return (
        "# Wasm Backend MVP\n"
        "Status: Normative\n\n"
        "## Purpose\n\n"
        "Wasm is the first reference execution target for the SCIR MVP.\n\n"
        "## Active scope\n\n"
        "The active Wasm backend is limited to helper-free stable WAT emission for the smallest admitted `SCIR-L` subset:\n\n"
        "- synchronous `int -> int` or `() -> int` functions in the scalar slice, plus the fixed `borrow_mut<Counter> -> int` record-cell slice\n"
        "- `const`\n"
        "- local-slot `alloc`, `store`, and `load`\n"
        "- bounded module-owned record-cell memory for the fixed Rust `borrow_mut<Counter>` field-mutation shape\n"
        "- same-module direct local call only in the fixed `identity` / `call_identity` scalar shape\n"
        "- `cmp` only in the current less-than-zero bootstrap shape\n"
        "- `ret`, `br`, and `cond_br` only in the current clamp-style control shape\n"
        "- explicit profile `P`\n"
        "- explicit `P2` ceiling\n"
        "- explicit downgrade and boundary reporting\n"
        "- execution-backed translation validation against the paired `SCIR-L` artifact\n\n"
        "### Admitted Python emitted modules\n\n"
        f"{_bullet_list(admitted_python)}\n\n"
        "### Admitted Rust emitted modules\n\n"
        f"{_bullet_list(admitted_rust)}\n\n"
        "### Supported but non-emittable Python modules\n\n"
        f"{_bullet_list(blocked_python)}\n\n"
        "### Supported but non-emittable Rust modules\n\n"
        f"{_bullet_list(blocked_rust)}\n\n"
        "### Admitted lowering rules\n\n"
        f"{_bullet_list(list(WASM_BACKEND_METADATA['admitted_lowering_rules']))}\n\n"
        "### Non-emittable lowering rules\n\n"
        f"{_bullet_list(list(WASM_BACKEND_METADATA['non_emittable_lowering_rules']))}\n\n"
        "### Additional non-emittable backend shapes\n\n"
        "Not emittable in this slice:\n\n"
        "- supported await-bearing modules that lower through `H_AWAIT_RESUME`\n"
        "- supported opaque or unsafe boundary modules that lower through `H_OPAQUE_CALL`\n"
        "- `field.addr` outside the bounded record-cell ABI\n"
        "- imported, indirect, recursive, or broader direct-call shapes\n"
        "- `async.resume`\n"
        "- `opaque.call`\n"
        "- record-layout widening beyond the fixed record-cell ABI\n"
        "- helper imports, runtime shims, imported memory, or hidden linear-memory conventions\n\n"
        "### Active record-cell ABI slice\n\n"
        "The first post-scalar Wasm slice is now active only for `fixture.rust_importer.a_struct_field_borrow_mut`.\n"
        "That ABI is frozen at this exact slice until a later recorded contract decision widens it.\n\n"
        "Active constraints:\n\n"
        "- one named record type only: `Counter { value: int }`\n"
        "- field offsets derived from canonical field declaration order\n"
        "- `borrow_mut<Counter>` lowered as an `i32` base-address handle into module-owned linear memory\n"
        "- `field.addr` admitted only for the fixed `Counter.value` projection at offset `0`\n"
        "- caller-visible mutation preserved only for callers that explicitly share the same record-cell ABI\n\n"
        "Still blocked:\n\n"
        "- Python field-place Wasm emission\n"
        "- non-`int` record fields\n"
        "- multi-record layouts\n"
        "- imported memory\n"
        "- host ABI claims\n"
        "- GC or object-model semantics\n"
        "- broader field-place shapes beyond the fixed record-cell case\n\n"
        "## Storage model\n\n"
        "- `alloc` lowers to backend-local slot assignment\n"
        "- no helper imports or runtime shims are permitted\n\n"
        "## Claim boundary\n\n"
        "Wasm emission does not imply:\n\n"
        "- native parity\n"
        "- host-runtime parity\n"
        "- support for deferred constructs\n\n"
        "## Validation boundary\n\n"
        "Admitted Wasm output now requires both:\n\n"
        "- stable helper-free WAT inside this bounded backend contract\n"
        "- a passing `translation_validation_report` that compares backend behavior against bounded `SCIR-L` execution under profile `P`\n\n"
        "## Required report path\n\n"
        "`l_to_wasm`\n"
    )


EXTRA_CHECKLIST_ROWS = [
    {
        "construct": "`iface` declarations",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred",
    },
    {
        "construct": "`witness` declarations",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred",
    },
    {
        "construct": "capability signatures and `using` clauses",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred",
    },
    {
        "construct": "importer-only `!throw` effect marker on bounded `try/catch` evidence",
        "grammar": "yes",
        "parser": "yes",
        "validator": "validator-only",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "yes",
        "MVP status": "canonical parser/validator surface only",
        "action taken": "kept as an importer-only effect marker; standalone `throw` syntax remains deferred",
    },
    {
        "construct": "`throw` expression or statement",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred outside the importer-only `!throw` effect marker",
    },
    {
        "construct": "`match`",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred",
    },
    {
        "construct": "`select`",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred",
    },
    {
        "construct": "`unsafe` suite block",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred in favor of explicit boundary calls",
    },
    {
        "construct": "`opaque` suite block",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred in favor of explicit boundary calls",
    },
    {
        "construct": "`borrow` / `borrow_mut` expressions",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred; type-level borrow shapes remain",
    },
    {
        "construct": "`invoke` witness dispatch",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred",
    },
    {
        "construct": "`spawn` / `send` / `recv` / channel types",
        "grammar": "no",
        "parser": "no",
        "validator": "no",
        "lowering": "no",
        "reconstruction": "no",
        "tests": "no",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred",
    },
    {
        "construct": "standalone `SCIR-L` text parser",
        "grammar": "no",
        "parser": "no",
        "validator": "validator over structured data only",
        "lowering": "n/a",
        "reconstruction": "n/a",
        "tests": "no",
        "MVP status": "incomplete and deferred",
        "action taken": "active authority is renderer plus validator, not a standalone parser",
    },
    {
        "construct": "`SCIR-L` provenance origin",
        "grammar": "n/a",
        "parser": "n/a",
        "validator": "yes",
        "lowering": "yes",
        "reconstruction": "n/a",
        "tests": "yes",
        "MVP status": "fully supported in MVP",
        "action taken": "strengthened with named lowering rules",
    },
    {
        "construct": "`SCIR-L` lowering-rule coverage",
        "grammar": "n/a",
        "parser": "n/a",
        "validator": "yes",
        "lowering": "yes",
        "reconstruction": "n/a",
        "tests": "yes",
        "MVP status": "fully supported in MVP",
        "action taken": "added as blocking derivative check",
    },
    {
        "construct": "Python reconstruction",
        "grammar": "n/a",
        "parser": "n/a",
        "validator": "report-checked",
        "lowering": "n/a",
        "reconstruction": "yes",
        "tests": "yes",
        "MVP status": "fully supported in MVP",
        "action taken": "kept",
    },
    {
        "construct": "Rust reconstruction",
        "grammar": "n/a",
        "parser": "n/a",
        "validator": "legacy only",
        "lowering": "n/a",
        "reconstruction": "not active",
        "tests": "legacy only",
        "MVP status": "not MVP and removed from active claims",
        "action taken": "deferred",
    },
    {
        "construct": "Wasm backend emission",
        "grammar": "helper-free WAT renderer only",
        "parser": "no binary backend yet",
        "validator": "yes for admitted subset",
        "lowering": "consumes the helper-free local-slot `SCIR-L` subset only",
        "reconstruction": "n/a",
        "tests": "yes",
        "MVP status": "partially supported in MVP",
        "action taken": "emitter-backed for `a_basic_function` and `a_mut_local`; `field.addr`, calls, async, and opaque lowering remain non-emittable",
    },
]


def render_spec_completeness_checklist() -> str:
    rows = []
    for construct in SCIR_H_KERNEL_METADATA["constructs"]:
        checklist = construct["checklist"]
        rows.append(
            {
                "construct": construct["construct"],
                "grammar": checklist["grammar"],
                "parser": checklist["parser"],
                "validator": checklist["validator"],
                "lowering": checklist["lowering"],
                "reconstruction": checklist["reconstruction"],
                "tests": checklist["tests"],
                "MVP status": checklist["mvp_status"],
                "action taken": checklist["action_taken"],
            }
        )
    rows.extend(EXTRA_CHECKLIST_ROWS)
    lines = [
        "# SPEC_COMPLETENESS_CHECKLIST",
        "Status: Normative",
        "",
        "| construct | grammar | parser | validator | lowering | reconstruction | tests | MVP status | action taken |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {construct} | {grammar} | {parser} | {validator} | {lowering} | {reconstruction} | {tests} | {MVP status} | {action taken} |".format(
                **row
            )
        )
    return "\n".join(lines) + "\n"


def rendered_contract_documents() -> dict[str, str]:
    manifest = {
        "corpus": {
            "hash": benchmark_track_contract("C")["sample_manifest_hash"],
        }
    }
    result = {
        "run_id": benchmark_track_contract("C")["sample_run_id"],
        "system_under_test": benchmark_track_contract("C")["sample_system_under_test"],
    }
    return {
        "frontend/python/IMPORT_SCOPE.md": render_python_import_scope(),
        "frontend/rust/IMPORT_SCOPE.md": render_rust_import_scope(),
        "benchmarks/tracks.md": render_benchmark_tracks_doc(),
        "benchmarks/baselines.md": render_benchmark_baselines_doc(),
        "benchmarks/success_failure_gates.md": render_benchmark_success_failure_gates_doc(),
        "benchmarks/corpora_policy.md": render_benchmark_corpora_policy_doc(),
        "backends/wasm/README.md": render_wasm_backend_readme(),
        "SPEC_COMPLETENESS_CHECKLIST.md": render_spec_completeness_checklist(),
        benchmark_track_contract("C")["sample_provenance_note_path"]: render_track_c_sample_refresh_note(manifest, result),
    }
