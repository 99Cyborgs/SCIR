#!/usr/bin/env python3
"""Frozen metadata for the bounded Wasm reference-backend MVP slice.

This file records what the current helper-free Wasm path may emit and why that
path remains contract-bounded rather than semantically complete. Other scripts
consume it as the authoritative boundary for preservation wording and admitted
lowering rules.
"""
from __future__ import annotations

from scir_python_bootstrap import PYTHON_PROOF_LOOP_METADATA
from scir_rust_bootstrap import RUST_IMPORTER_METADATA


WASM_BACKEND_METADATA = {
    "report_path": "l_to_wasm",
    "profile": "P",
    "preservation_level": "P2",
    "emittable_python_cases": [
        "a_basic_function",
        "b_direct_call",
    ],
    "emittable_rust_cases": [
        "a_mut_local",
        "a_struct_field_borrow_mut",
    ],
    "admitted_lowering_rules": [
        "H_CONST_RET",
        "H_VAR_ALLOC",
        "H_SET_STORE",
        "H_PLACE_LOAD",
        "H_FIELD_ADDR",
        "H_INTRINSIC_CMP",
        "H_DIRECT_CALL",
        "H_BRANCH_COND",
        "H_BRANCH_JOIN",
        "H_RETURN",
    ],
    "non_emittable_lowering_rules": [
        "H_AWAIT_RESUME",
        "H_OPAQUE_CALL",
    ],
    "scalar_signature_constraint": "helper-free scalar Wasm emission remains limited to scalar int params and int returns with no record type declarations",
    "record_cell_shape_constraint": "the first post-scalar Wasm slice remains limited to the fixed record-cell ABI for a single borrowed mutable int-field record",
    "field_addr_blocker_reason": "field.addr remains non-emittable outside the bounded record-cell ABI because helper-free Wasm has no broader explicit record ABI/layout contract",
    "field_addr_blocked_observable": "caller-visible borrowed record field mutation semantics",
    "record_cell_layout_reason": "record-cell Wasm emission normalizes canonical field order into fixed module-owned linear-memory offsets",
    "shared_handle_reason": "record-cell Wasm emission preserves caller-visible mutation only for callers that share the same explicit record-cell ABI",
    "local_slot_reason": "helper-free Wasm emission lowers SCIR-L alloc/store/load into backend-local slot state",
    "cmp_reason": "cmp emission remains limited to the current less-than-zero bootstrap shape",
    "normalized_observable": "alloc/store/load lowered into backend-local slot operations",
    "record_cell_normalized_observable": "record field layout lowered into module-owned Wasm memory cells",
    "contract_bounded_observable": "cmp emitted only for the current less-than-zero bootstrap shape",
    "direct_call_observable": "same-module direct local call behavior",
    "shared_handle_contract_observable": "caller-visible record mutation preserved only for same-contract record-cell callers",
    "record_cell_evidence": [
        "field-offset-map: Counter.value->0",
        "shared-record-handle ABI: caller and callee must share the module-owned record-cell contract",
    ],
    "required_evidence": [
        "wasm-emitter-bootstrap-validator",
        "stable WAT emitted for the helper-free synchronous scalar subset",
        "no helper imports or runtime shims",
    ],
}


def wasm_emittable_module_ids() -> list[str]:
    """Return the exact fixture module ids admitted into the current Wasm slice."""

    return [
        *(f"fixture.python_importer.{case_name}" for case_name in WASM_BACKEND_METADATA["emittable_python_cases"]),
        *(f"fixture.rust_importer.{case_name}" for case_name in WASM_BACKEND_METADATA["emittable_rust_cases"]),
    ]


def _validate_wasm_backend_metadata():
    """Keep Wasm metadata synchronized with importer contracts so executable claims cannot silently widen."""

    expected_python_cases = [
        case_name
        for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items()
        if contract["wasm_emittable"]
    ]
    expected_rust_cases = [
        case_name
        for case_name, contract in RUST_IMPORTER_METADATA["case_contracts"].items()
        if contract["wasm_emittable"]
    ]

    if WASM_BACKEND_METADATA["emittable_python_cases"] != expected_python_cases:
        raise ValueError("WASM_BACKEND_METADATA Python-emittable cases drifted from PYTHON_PROOF_LOOP_METADATA")
    if WASM_BACKEND_METADATA["emittable_rust_cases"] != expected_rust_cases:
        raise ValueError("WASM_BACKEND_METADATA Rust-emittable cases drifted from RUST_IMPORTER_METADATA")

    admitted_rules = set(WASM_BACKEND_METADATA["admitted_lowering_rules"])
    non_emittable_rules = set(WASM_BACKEND_METADATA["non_emittable_lowering_rules"])
    if admitted_rules & non_emittable_rules:
        raise ValueError("WASM_BACKEND_METADATA lowering-rule classifications must be disjoint")

    if WASM_BACKEND_METADATA["report_path"] != "l_to_wasm":
        raise ValueError("WASM_BACKEND_METADATA report_path must remain l_to_wasm")
    if WASM_BACKEND_METADATA["profile"] != "P":
        raise ValueError("WASM_BACKEND_METADATA profile must remain P")
    if WASM_BACKEND_METADATA["preservation_level"] != "P2":
        raise ValueError("WASM_BACKEND_METADATA preservation_level must remain P2")


_validate_wasm_backend_metadata()
