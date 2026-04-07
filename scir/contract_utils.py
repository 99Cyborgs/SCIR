from __future__ import annotations

import json
import re

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - optional dependency
    Draft202012Validator = None


CAPABILITY_DEPENDENCY_PREFIX = "capability:"


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def matches_type(value, expected_type):
    if isinstance(expected_type, list):
        return any(matches_type(value, item) for item in expected_type)
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": is_number(value),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected_type, True)


def normalize_for_uniqueness(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def collect_fallback_validation_errors(instance, schema, path="$"):
    failures = []
    expected_type = schema.get("type")
    if expected_type is not None and not matches_type(instance, expected_type):
        return [(path, f"expected type {expected_type!r}")]

    expected_enum = schema.get("enum")
    if expected_enum is not None and instance not in expected_enum:
        failures.append((path, f"expected one of {expected_enum!r}"))

    min_length = schema.get("minLength")
    if min_length is not None and isinstance(instance, str) and len(instance) < min_length:
        failures.append((path, f"expected string length >= {min_length}"))

    min_items = schema.get("minItems")
    if min_items is not None and isinstance(instance, list) and len(instance) < min_items:
        failures.append((path, f"expected at least {min_items} items"))

    pattern = schema.get("pattern")
    if pattern is not None and isinstance(instance, str) and re.fullmatch(pattern, instance) is None:
        failures.append((path, f"expected string matching {pattern!r}"))

    if schema.get("uniqueItems") and isinstance(instance, list):
        normalized = [normalize_for_uniqueness(item) for item in instance]
        if len(normalized) != len(set(normalized)):
            failures.append((path, "expected unique items"))

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                failures.append((path, f"missing required property {key}"))
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                failures.extend(
                    collect_fallback_validation_errors(value, properties[key], child_path)
                )
            elif additional is False:
                failures.append((path, f"unexpected property {key}"))
            elif isinstance(additional, dict):
                failures.extend(
                    collect_fallback_validation_errors(value, additional, child_path)
                )

    if isinstance(instance, list) and "items" in schema:
        for idx, item in enumerate(instance):
            failures.extend(
                collect_fallback_validation_errors(item, schema["items"], f"{path}[{idx}]")
            )

    return failures


def collect_instance_validation_errors(instance, schema):
    if Draft202012Validator is None:
        return collect_fallback_validation_errors(instance, schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(instance),
        key=lambda error: ([str(part) for part in error.absolute_path], error.message),
    )
    failures = []
    for error in errors:
        path = "$"
        for part in error.absolute_path:
            path += f"[{part}]" if isinstance(part, int) else f".{part}"
        failures.append((path, error.message))
    return failures


def capability_dependency_entries(module_manifest: dict | None):
    if not isinstance(module_manifest, dict):
        return set()
    dependencies = module_manifest.get("dependencies", [])
    if not isinstance(dependencies, list):
        return set()
    return {
        dependency
        for dependency in dependencies
        if isinstance(dependency, str) and dependency.startswith(CAPABILITY_DEPENDENCY_PREFIX)
    }


def boundary_capability_entries(boundary_contract: dict | None):
    if not isinstance(boundary_contract, dict):
        return set(), []
    capability_entries = set()
    failures = []
    for entry in boundary_contract.get("capabilities", []):
        if not isinstance(entry, str) or not entry:
            failures.append("capabilities entries must be non-empty strings")
            continue
        if not entry.startswith(CAPABILITY_DEPENDENCY_PREFIX):
            failures.append(
                f"capability entry {entry!r} must use the {CAPABILITY_DEPENDENCY_PREFIX}<name> form"
            )
            continue
        capability_entries.add(entry)
    return capability_entries, failures


def validate_boundary_capability_contract(
    module_manifest: dict | None,
    boundary_contract: dict | None,
    *,
    label: str,
    allow_capabilities: bool,
):
    """Require Tier C capability accounting to stay mirrored between manifests and boundary contracts."""

    failures = []
    capability_imports = capability_dependency_entries(module_manifest)
    boundary_capabilities, capability_failures = boundary_capability_entries(boundary_contract)
    for item in capability_failures:
        failures.append(f"{label}: {item}")

    if not allow_capabilities:
        if boundary_capabilities:
            failures.append(f"{label}: non-boundary fixtures must not declare capability requirements")
        if capability_imports:
            failures.append(
                f"{label}: non-boundary fixtures must not declare capability imports {sorted(capability_imports)!r}"
            )
        return failures

    missing_capabilities = sorted(boundary_capabilities - capability_imports)
    if missing_capabilities:
        failures.append(
            f"{label}: missing capability imports for boundary requirements {missing_capabilities!r}"
        )

    unused_capabilities = sorted(capability_imports - boundary_capabilities)
    if unused_capabilities:
        failures.append(
            f"{label}: unused capability imports not referenced by the boundary contract {unused_capabilities!r}"
        )

    return failures
