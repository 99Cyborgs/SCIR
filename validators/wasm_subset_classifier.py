from __future__ import annotations

import re
from typing import Any


ADMITTED_WASM_SUBSET_REASON = "helper_free_bounded_subset"

_REFERENCE_TYPE_PATTERNS = (
    r"\bfuncref\b",
    r"\bexternref\b",
    r"\banyref\b",
    r"\beqref\b",
    r"\bi31ref\b",
    r"\bstructref\b",
    r"\barrayref\b",
    r"\bref\.",
    r"\btable\b",
)
_HELPER_NAME_PATTERN = re.compile(r"\(func\s+\$[^\s)]*(helper|trampoline|shim)", re.IGNORECASE)
_GLOBAL_MUT_PATTERN = re.compile(r"\(global(?:\s+\$[^\s)]*)?\s+\(mut\s", re.IGNORECASE)
_SECTION_PATTERN = re.compile(r"^\((type|table)\b", re.IGNORECASE)


def classify_wasm_subset(wat_text: str) -> dict[str, Any]:
    """Classify whether WAT stays inside the admitted helper-free Wasm subset."""

    unsupported_features: list[str] = []
    functions: dict[str, dict[str, Any]] = {}

    lines = [line.rstrip() for line in wat_text.splitlines() if line.strip()]
    if not lines or lines[0].strip() != "(module":
        unsupported_features.append("invalid_module_header")

    if "(import " in wat_text:
        unsupported_features.append("imports_outside_allowed_shims")
    if _HELPER_NAME_PATTERN.search(wat_text):
        unsupported_features.append("helper_trampolines")
    if "call_indirect" in wat_text:
        unsupported_features.append("indirect_calls")
    if _GLOBAL_MUT_PATTERN.search(wat_text):
        unsupported_features.append("mutable_globals")
    if "memory.grow" in wat_text:
        unsupported_features.append("memory_growth")
    if any(re.search(pattern, wat_text) for pattern in _REFERENCE_TYPE_PATTERNS):
        unsupported_features.append("reference_types")

    for line in lines:
        stripped = line.strip()
        if _SECTION_PATTERN.match(stripped):
            unsupported_features.append(f"unadmitted_module_section:{stripped.split()[0][1:]}")

    parsed_functions = _parse_wat_functions(wat_text)
    unsupported_features.extend(parsed_functions["unsupported_features_detected"])
    functions.update(parsed_functions["functions"])

    unsupported_features = _ordered_unique(unsupported_features)
    if unsupported_features:
        subset_class = "wasm_requires_helpers" if any(
            feature
            in {
                "imports_outside_allowed_shims",
                "helper_trampolines",
                "indirect_calls",
                "mutable_globals",
                "memory_growth",
                "reference_types",
            }
            for feature in unsupported_features
        ) else "unknown"
        return {
            "subset_admission_result": "rejected",
            "subset_admission_reason": _subset_rejection_reason(unsupported_features),
            "unsupported_features_detected": unsupported_features,
            "backend_subset_class": subset_class,
            "functions": functions,
        }

    return {
        "subset_admission_result": "admitted",
        "subset_admission_reason": ADMITTED_WASM_SUBSET_REASON,
        "unsupported_features_detected": [],
        "backend_subset_class": "wasm_helper_free_bounded",
        "functions": functions,
    }


def _parse_wat_functions(wat_text: str) -> dict[str, Any]:
    functions: dict[str, dict[str, Any]] = {}
    unsupported: list[str] = []
    current_name: str | None = None
    current_lines: list[str] = []

    for line in wat_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("(func $"):
            current_name = stripped.split("$", 1)[1].split()[0]
            current_lines = [stripped]
            continue
        if current_name is None:
            continue
        current_lines.append(stripped)
        if stripped == ")":
            try:
                functions[current_name] = _classify_wat_function(current_name, current_lines)
            except ValueError as exc:
                unsupported.append(str(exc))
            current_name = None
            current_lines = []

    if current_name is not None:
        unsupported.append(f"unterminated_function:{current_name}")

    return {
        "functions": functions,
        "unsupported_features_detected": _ordered_unique(unsupported),
    }


def _classify_wat_function(name: str, lines: list[str]) -> dict[str, Any]:
    body = [line for line in lines[1:-1] if line]
    tokens = []
    for line in body:
        if line.startswith("(local "):
            continue
        token = line.split()[0]
        tokens.append(token)

    if any(token in {"loop", "else", "br", "br_table", "return", "try", "catch", "throw"} for token in tokens):
        offending = next(
            token for token in tokens if token in {"loop", "else", "br", "br_table", "return", "try", "catch", "throw"}
        )
        raise ValueError(f"unsupported_control_construct:{offending}")

    allowed_tokens = {
        "block",
        "br_if",
        "call",
        "end",
        "i32.const",
        "i32.eqz",
        "i32.load",
        "i32.lt_s",
        "i32.store",
        "if",
        "local.get",
        "local.set",
    }
    for token in tokens:
        if token not in allowed_tokens:
            raise ValueError(f"unsupported_instruction:{token}")

    if len(body) == 1 and body[0].startswith("i32.const "):
        return {"kind": "const", "const": int(body[0].split()[-1])}

    if len(body) == 1 and body[0].startswith("local.get $"):
        return {"kind": "passthrough"}

    if any("call $" in line for line in body):
        if len([line for line in body if "call $" in line]) != 1:
            raise ValueError("unsupported_instruction:multiple_call_sites")
        call_target = next(line.split("$", 1)[1] for line in body if "call $" in line)
        unexpected = [token for token in tokens if token not in {"local.get", "call"}]
        if unexpected:
            raise ValueError(f"unsupported_instruction:{unexpected[0]}")
        return {"kind": "direct_call", "target": call_target}

    local_slot_pattern = [
        "local.get",
        "local.set",
        "block",
        "local.get",
        "i32.const",
        "i32.lt_s",
        "i32.eqz",
        "br_if",
        "i32.const",
        "local.set",
        "end",
        "local.get",
    ]
    if "(local $slot0 i32)" in body and tokens == local_slot_pattern:
        return {"kind": "local_slot"}

    record_cell_pattern = [
        "local.get",
        "i32.load",
        "i32.const",
        "i32.lt_s",
        "if",
        "local.get",
        "i32.const",
        "i32.store",
        "end",
        "local.get",
        "i32.load",
    ]
    if tokens == record_cell_pattern:
        load_ops = [line for line in body if line.startswith("i32.load")]
        store_ops = [line for line in body if line.startswith("i32.store")]
        if load_ops == ["i32.load offset=0", "i32.load offset=0"] and store_ops == ["i32.store offset=0"]:
            return {"kind": "record_cell"}
        raise ValueError("unsupported_instruction:record_cell_offset")

    raise ValueError(f"unsupported_instruction_shape:{name}")


def _subset_rejection_reason(features: list[str]) -> str:
    if any(feature in {"imports_outside_allowed_shims", "helper_trampolines"} for feature in features):
        return "helper_usage_outside_admitted_subset"
    if "indirect_calls" in features:
        return "indirect_calls_outside_admitted_subset"
    if "reference_types" in features:
        return "reference_types_outside_admitted_subset"
    if "memory_growth" in features:
        return "memory_growth_outside_admitted_subset"
    if "mutable_globals" in features:
        return "mutable_globals_outside_admitted_subset"
    return "unsupported_wasm_feature"


def _ordered_unique(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
