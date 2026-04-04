"""Validation for SCIR-Hc diff-audit artifacts."""
from __future__ import annotations

from scir_h_bootstrap_model import HcModule, HcVarDecl, IfStmt, LoopStmt, Module, TryStmt, normalize_hc_module, normalize_module

from validators.lineage_contract import assert_complete_lineage_binding


class DiffAuditValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DiffAuditValidationError(message)


def _walk_hc_statements(body):
    for stmt in body:
        yield stmt
        if isinstance(stmt, IfStmt):
            yield from _walk_hc_statements(stmt.then_body)
            yield from _walk_hc_statements(stmt.else_body)
        elif isinstance(stmt, LoopStmt):
            yield from _walk_hc_statements(stmt.body)
        elif isinstance(stmt, TryStmt):
            yield from _walk_hc_statements(stmt.try_body)
            yield from _walk_hc_statements(stmt.catch_body)


def expected_diff_audit_entry(module: Module, scirhc: HcModule) -> dict[str, object]:
    normalized = normalize_module(module)
    normalized_hc = normalize_hc_module(scirhc)
    dropped_fields: list[str] = []
    structural_diff = {
        "function_return_type_omissions": [],
        "function_effect_row_omissions": [],
        "local_type_omissions": [],
    }
    for scirh_function, scirhc_function in zip(normalized.functions, normalized_hc.functions):
        if scirhc_function.return_type is None:
            field_name = f"functions.{scirh_function.name}.return_type"
            dropped_fields.append(field_name)
            structural_diff["function_return_type_omissions"].append(field_name)
        if scirhc_function.effects is None:
            field_name = f"functions.{scirh_function.name}.effects"
            dropped_fields.append(field_name)
            structural_diff["function_effect_row_omissions"].append(field_name)
        for stmt_index, stmt in enumerate(scirhc_function.body):
            if not isinstance(stmt, HcVarDecl) or stmt.type_name is not None:
                continue
            field_name = f"functions.{scirh_function.name}.body[{stmt_index}].type_name"
            dropped_fields.append(field_name)
            structural_diff["local_type_omissions"].append(field_name)
    return {
        "module_id": normalized.module_id,
        "structural_diff": structural_diff,
        "dropped_fields": dropped_fields,
    }


def assert_diff_audit_entry(
    diff_audit: dict,
    *,
    module: Module,
    scirhc: HcModule,
    lineage_references: dict[str, dict[str, str]],
    compression_statistics: dict[str, int],
) -> None:
    _require(isinstance(diff_audit, dict), "SCIR-Hc diff audit must be an object")
    expected = expected_diff_audit_entry(module, scirhc)
    _require(diff_audit.get("module_id") == expected["module_id"], "SCIR-Hc diff audit module id mismatch")
    assert_complete_lineage_binding(
        diff_audit.get("lineage_references"),
        canonical_registry={module.module_id: module},
        required_modules={module.module_id},
        label="SCIR-Hc diff audit",
    )
    _require(
        diff_audit.get("lineage_references") == lineage_references,
        "SCIR-Hc diff audit lineage references drifted from the validated lineage binding",
    )
    _require(
        diff_audit.get("structural_diff") == expected["structural_diff"],
        "SCIR-Hc diff audit structural diff is incomplete or contains silent semantic changes",
    )
    _require(
        diff_audit.get("dropped_fields") == expected["dropped_fields"],
        "SCIR-Hc diff audit dropped_fields must exactly match the derived omission set",
    )
    _require(
        diff_audit.get("normalized_fields") == [],
        "SCIR-Hc diff audit normalized_fields must remain explicit even when empty",
    )
    _require(
        diff_audit.get("compression_statistics") == compression_statistics,
        "SCIR-Hc diff audit compression statistics drifted from the validated SCIR-Hc artifact",
    )


def assert_diff_audit_bundle(
    diff_audit_bundle: dict,
    *,
    expected_module_audits: dict[str, dict[str, object]],
) -> None:
    _require(isinstance(diff_audit_bundle, dict), "SCIR-Hc diff audit bundle must be an object")
    _require(diff_audit_bundle.get("representation") == "SCIR-Hc", "SCIR-Hc diff audit bundle must declare representation = SCIR-Hc")
    modules = diff_audit_bundle.get("modules")
    _require(isinstance(modules, dict) and modules, "SCIR-Hc diff audit bundle must declare module audits")
    _require(
        set(modules) == set(expected_module_audits),
        "SCIR-Hc diff audit bundle module coverage is incomplete",
    )
    for module_id, expected in expected_module_audits.items():
        _require(
            modules.get(module_id) == expected,
            f"SCIR-Hc diff audit bundle entry for {module_id!r} drifted from the validated module audit",
        )
