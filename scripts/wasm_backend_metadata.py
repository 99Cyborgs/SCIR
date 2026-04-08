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


def _python_non_emittable_wasm_cases() -> dict[str, dict]:
    blocked = {}
    for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items():
        if contract["wasm_emittable"]:
            continue
        if contract["requires_opaque_boundary"]:
            blocked[case_name] = {
                "module_id": f"fixture.python_importer.{case_name}",
                "blocking_lowering_rules": ["H_OPAQUE_CALL"],
                "exclusion_kind": "opaque_boundary",
                "reason": "opaque-boundary Python proof-loop case remains outside the helper-free Wasm subset",
            }
        else:
            blocked[case_name] = {
                "module_id": f"fixture.python_importer.{case_name}",
                "blocking_lowering_rules": ["H_AWAIT_RESUME"],
                "exclusion_kind": "await_boundary",
                "reason": "await-bearing Python proof-loop case remains outside the helper-free Wasm subset",
            }
    return blocked


def _rust_non_emittable_wasm_cases() -> dict[str, dict]:
    blocked = {}
    for case_name, contract in RUST_IMPORTER_METADATA["case_contracts"].items():
        if contract["wasm_emittable"]:
            continue
        if contract["requires_opaque_boundary"]:
            blocked[case_name] = {
                "module_id": f"fixture.rust_importer.{case_name}",
                "blocking_lowering_rules": ["H_OPAQUE_CALL"],
                "exclusion_kind": "opaque_boundary",
                "reason": "unsafe-boundary Rust importer case remains outside the helper-free Wasm subset",
            }
        else:
            blocked[case_name] = {
                "module_id": f"fixture.rust_importer.{case_name}",
                "blocking_lowering_rules": ["H_AWAIT_RESUME"],
                "exclusion_kind": "await_boundary",
                "reason": "await-bearing Rust importer case remains outside the helper-free Wasm subset",
            }
    return blocked


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
    "non_emittable_python_cases": _python_non_emittable_wasm_cases(),
    "non_emittable_rust_cases": _rust_non_emittable_wasm_cases(),
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


def wasm_non_emittable_module_contracts() -> dict[str, dict]:
    """Return supported-but-non-emittable Wasm cases keyed by module id."""

    contracts = {}
    for source_language, items in (
        ("python", WASM_BACKEND_METADATA["non_emittable_python_cases"]),
        ("rust", WASM_BACKEND_METADATA["non_emittable_rust_cases"]),
    ):
        for case_name, contract in items.items():
            contracts[contract["module_id"]] = {
                **contract,
                "case_name": case_name,
                "source_language": source_language,
            }
    return contracts


def _validate_wasm_backend_metadata():
    """Keep Wasm metadata synchronized with importer contracts so executable claims cannot silently widen."""

    expected_python_cases = [
        case_name
        for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items()
        if contract["wasm_emittable"]
    ]
    expected_python_non_emittable = [
        case_name
        for case_name, contract in PYTHON_PROOF_LOOP_METADATA["executable_case_contracts"].items()
        if not contract["wasm_emittable"]
    ]
    expected_rust_cases = [
        case_name
        for case_name, contract in RUST_IMPORTER_METADATA["case_contracts"].items()
        if contract["wasm_emittable"]
    ]
    expected_rust_non_emittable = [
        case_name
        for case_name, contract in RUST_IMPORTER_METADATA["case_contracts"].items()
        if not contract["wasm_emittable"]
    ]

    if WASM_BACKEND_METADATA["emittable_python_cases"] != expected_python_cases:
        raise ValueError("WASM_BACKEND_METADATA Python-emittable cases drifted from PYTHON_PROOF_LOOP_METADATA")
    if list(WASM_BACKEND_METADATA["non_emittable_python_cases"]) != expected_python_non_emittable:
        raise ValueError(
            "WASM_BACKEND_METADATA Python non-emittable cases drifted from PYTHON_PROOF_LOOP_METADATA"
        )
    if WASM_BACKEND_METADATA["emittable_rust_cases"] != expected_rust_cases:
        raise ValueError("WASM_BACKEND_METADATA Rust-emittable cases drifted from RUST_IMPORTER_METADATA")
    if list(WASM_BACKEND_METADATA["non_emittable_rust_cases"]) != expected_rust_non_emittable:
        raise ValueError(
            "WASM_BACKEND_METADATA Rust non-emittable cases drifted from RUST_IMPORTER_METADATA"
        )

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
    for group_name, expected_rule in (
        ("non_emittable_python_cases", {"await_boundary": "H_AWAIT_RESUME", "opaque_boundary": "H_OPAQUE_CALL"}),
        ("non_emittable_rust_cases", {"await_boundary": "H_AWAIT_RESUME", "opaque_boundary": "H_OPAQUE_CALL"}),
    ):
        for case_name, contract in WASM_BACKEND_METADATA[group_name].items():
            module_id = contract.get("module_id")
            if not isinstance(module_id, str) or not module_id.endswith(case_name):
                raise ValueError(f"WASM_BACKEND_METADATA {group_name}.{case_name} must publish a matching module_id")
            exclusion_kind = contract.get("exclusion_kind")
            if exclusion_kind not in expected_rule:
                raise ValueError(
                    f"WASM_BACKEND_METADATA {group_name}.{case_name} has invalid exclusion_kind {exclusion_kind!r}"
                )
            if contract.get("blocking_lowering_rules") != [expected_rule[exclusion_kind]]:
                raise ValueError(
                    f"WASM_BACKEND_METADATA {group_name}.{case_name} must publish blocking rule {expected_rule[exclusion_kind]!r}"
                )
            if not isinstance(contract.get("reason"), str) or not contract["reason"]:
                raise ValueError(f"WASM_BACKEND_METADATA {group_name}.{case_name} must publish a non-empty reason")


_validate_wasm_backend_metadata()
