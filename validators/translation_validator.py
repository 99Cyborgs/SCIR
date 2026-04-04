from __future__ import annotations

import asyncio
import copy
import inspect
import re
import sys
from types import ModuleType
from typing import Any

from runtime.scirl_interpreter import HostFunctionSpec, generate_inputs, run_scirl
from validators.wasm_subset_classifier import classify_wasm_subset


TRANSLATION_VALIDATOR_NAME = "scir-l-backend-translation-validator"
EXECUTION_ORACLE = "scirl_bounded_interpreter"
OUTCOME_PASSED_FULL = "PASSED_FULL"
OUTCOME_PASSED_SUBSET = "PASSED_SUBSET"
OUTCOME_DOWNGRADED_UNSUPPORTED_SUBSET = "DOWNGRADED_UNSUPPORTED_SUBSET"
OUTCOME_DOWNGRADED_MISSING_ORACLE = "DOWNGRADED_MISSING_ORACLE"
OUTCOME_FAILED_MISMATCH = "FAILED_MISMATCH"
OUTCOME_FAILED_RUNTIME_ERROR = "FAILED_RUNTIME_ERROR"
ALL_OBSERVABLE_DIMENSIONS = (
    "returns",
    "traps_or_exceptions",
    "termination_kind",
    "call_trace",
    "branch_trace",
    "state_write_trace",
    "effect_trace",
    "capability_trace",
)
DEFAULT_OBSERVABLE_DIMENSIONS = {
    "wasm": list(ALL_OBSERVABLE_DIMENSIONS),
    "python": [
        "returns",
        "traps_or_exceptions",
        "termination_kind",
        "call_trace",
        "effect_trace",
        "capability_trace",
    ],
}


class TranslationValidationError(RuntimeError):
    """Raised when a backend artifact cannot be executed by the bounded validator."""


def default_observable_dimensions(backend_kind: str) -> list[str]:
    if backend_kind not in DEFAULT_OBSERVABLE_DIMENSIONS:
        raise TranslationValidationError(f"unsupported backend artifact kind {backend_kind!r}")
    return list(DEFAULT_OBSERVABLE_DIMENSIONS[backend_kind])


def validate_translation(
    scirl: dict,
    backend_artifact: dict,
    target_profile: str,
    *,
    equivalence_mode: str = "contract_bounded",
    observable_dimensions: list[str] | None = None,
    allow_contract_bounded: bool | None = None,
) -> dict[str, Any]:
    """Execute bounded translation validation between `SCIR-L` and a backend artifact."""

    backend_kind = backend_artifact["kind"]
    contract = translation_contract(
        backend_artifact,
        target_profile,
        equivalence_mode=equivalence_mode,
        observable_dimensions=observable_dimensions,
        allow_contract_bounded=allow_contract_bounded,
    )
    subject = backend_artifact.get("subject") or backend_artifact.get("module_id") or scirl.get("module_id", "scirl-module")
    host_functions = _normalize_host_functions(backend_artifact.get("host_functions"))
    subset = classify_backend_subset(backend_artifact)
    contract_assumptions = build_contract_assumptions(backend_artifact, contract, subset)
    helper_free_subset_required = backend_kind == "wasm"

    report = {
        "report_id": f"translation-validation-{_slug(subject)}-{backend_kind}",
        "subject": subject,
        "backend_kind": backend_kind,
        "target_profile": target_profile,
        "preservation_level": contract["preservation_level"],
        "outcome": OUTCOME_DOWNGRADED_MISSING_ORACLE,
        "equivalence_mode": contract["equivalence_mode"],
        "observable_dimensions_checked": list(contract["observable_dimensions_checked"]),
        "backend_subset_class": subset["backend_subset_class"],
        "execution_oracle": EXECUTION_ORACLE,
        "validation_strength": "structural_only",
        "downgrade_reason": None,
        "subset_admission_result": subset["subset_admission_result"],
        "subset_admission_reason": subset["subset_admission_reason"],
        "unsupported_features_detected": list(subset["unsupported_features_detected"]),
        "helper_free_subset_required": helper_free_subset_required,
        "contract_assumptions": contract_assumptions,
        "dimension_results": {dimension: True for dimension in contract["observable_dimensions_checked"]},
        "violations": [],
        "findings": [],
        "validated_invocations": 0,
        "suspect_l_nodes": [],
        "suspect_h_nodes": [],
        "backend_regions": [],
        "origin_trace_links": [],
    }

    if subset["subset_admission_result"] != "admitted":
        report["outcome"] = OUTCOME_DOWNGRADED_UNSUPPORTED_SUBSET
        report["validation_strength"] = "unsupported"
        report["downgrade_reason"] = subset["subset_admission_reason"]
        report["violations"] = [
            f"{subject}: backend subset rejected: {subset['subset_admission_reason']}"
        ]
        report["backend_regions"] = [f"{backend_kind}.module"]
        return report

    if backend_kind == "python" and not backend_artifact.get("source_text"):
        report["outcome"] = OUTCOME_DOWNGRADED_MISSING_ORACLE
        report["validation_strength"] = "structural_only"
        report["downgrade_reason"] = "missing_python_execution_source"
        report["violations"] = [f"{subject}: missing Python source_text for bounded execution"]
        return report

    source_module = backend_artifact.get("source_module")
    input_cases = backend_artifact.get("inputs") or generate_inputs(scirl, source_module=source_module)
    if not input_cases:
        report["outcome"] = OUTCOME_DOWNGRADED_MISSING_ORACLE
        report["validation_strength"] = "structural_only"
        report["downgrade_reason"] = "missing_deterministic_inputs"
        report["violations"] = [f"{subject}: missing deterministic validation inputs"]
        return report

    report["validation_strength"] = validation_strength_for_backend(subset["backend_subset_class"])
    report["downgrade_reason"] = downgrade_reason_for_backend(backend_kind, subset["backend_subset_class"])

    provenance_index = build_provenance_index(scirl)
    declared_caps = declared_capabilities(scirl, backend_artifact)
    runtime_failures: list[str] = []
    all_findings: list[dict[str, Any]] = []

    for invocation in input_cases:
        report["validated_invocations"] += 1
        try:
            trace_l = run_scirl(
                scirl,
                invocation,
                source_module=source_module,
                host_functions=host_functions,
            )
            trace_backend = run_backend(
                backend_artifact,
                invocation,
                host_functions=host_functions,
                classified_functions=subset.get("functions"),
            )
        except TranslationValidationError as exc:
            runtime_failures.append(f"{_invocation_label(invocation)}: {exc}")
            continue

        oracle_observation = build_observation(trace_l)
        backend_observation = build_observation(trace_backend)
        comparison = compare_observations(
            oracle_observation,
            backend_observation,
            contract,
            declared_capabilities=declared_caps,
            provenance_index=provenance_index,
            invocation=invocation,
            backend_kind=backend_kind,
        )
        for dimension, matched in comparison["dimension_results"].items():
            report["dimension_results"][dimension] = report["dimension_results"].get(dimension, True) and matched
        all_findings.extend(comparison["findings"])
        report["violations"].extend(comparison["violations"])

    report["findings"] = all_findings
    report["suspect_l_nodes"] = _ordered_unique(
        [node for finding in all_findings for node in finding["suspect_l_nodes"]]
    )
    report["suspect_h_nodes"] = _ordered_unique(
        [node for finding in all_findings for node in finding["suspect_h_nodes"]]
    )
    report["backend_regions"] = _ordered_unique(
        [region for finding in all_findings for region in finding["backend_regions"]]
    )
    report["origin_trace_links"] = _ordered_unique_links(
        [link for finding in all_findings for link in finding["origin_trace_links"]]
    )

    if runtime_failures:
        report["outcome"] = OUTCOME_FAILED_RUNTIME_ERROR
        report["violations"].extend(runtime_failures)
        if report["downgrade_reason"] is None:
            report["downgrade_reason"] = "backend_execution_failed"
        return report

    if all_findings:
        report["outcome"] = OUTCOME_FAILED_MISMATCH
        return report

    report["outcome"] = OUTCOME_PASSED_SUBSET
    return report


def translation_contract(
    backend_artifact: dict,
    target_profile: str,
    *,
    equivalence_mode: str,
    observable_dimensions: list[str] | None,
    allow_contract_bounded: bool | None,
) -> dict[str, Any]:
    contract = {
        "preservation_level": "P1",
        "allowed_scheduling_variation": False,
        "allowed_allocation_variation": False,
        "fp_tolerance": 0.0,
    }
    contract.update(copy.deepcopy(backend_artifact.get("preservation_contract", {})))
    contract["target_profile"] = target_profile
    contract["equivalence_mode"] = equivalence_mode
    if allow_contract_bounded is None:
        allow_contract_bounded = equivalence_mode == "contract_bounded"
    contract["allow_contract_bounded"] = bool(allow_contract_bounded)
    if equivalence_mode == "contract_bounded" and not contract["allow_contract_bounded"]:
        raise TranslationValidationError("contract_bounded mode requires allow_contract_bounded=True")
    if equivalence_mode != "contract_bounded" and contract["allow_contract_bounded"]:
        raise TranslationValidationError("allow_contract_bounded cannot be enabled outside contract_bounded mode")

    backend_kind = backend_artifact["kind"]
    resolved_dimensions = observable_dimensions or default_observable_dimensions(backend_kind)
    unsupported_dimensions = sorted(set(resolved_dimensions) - set(default_observable_dimensions(backend_kind)))
    if unsupported_dimensions:
        raise TranslationValidationError(
            f"{backend_kind}: unsupported observable dimensions {unsupported_dimensions!r}"
        )
    contract["observable_dimensions_checked"] = list(resolved_dimensions)
    return contract


def classify_backend_subset(backend_artifact: dict) -> dict[str, Any]:
    kind = backend_artifact["kind"]
    if kind == "wasm":
        return classify_wasm_subset(backend_artifact["text"])
    if kind == "python":
        return {
            "subset_admission_result": "admitted",
            "subset_admission_reason": "python_bounded_execution",
            "unsupported_features_detected": [],
            "backend_subset_class": "python_bounded",
            "functions": {},
        }
    return {
        "subset_admission_result": "rejected",
        "subset_admission_reason": "unsupported_backend_kind",
        "unsupported_features_detected": [f"unsupported_backend_kind:{kind}"],
        "backend_subset_class": "unknown",
        "functions": {},
    }


def build_contract_assumptions(
    backend_artifact: dict,
    contract: dict[str, Any],
    subset: dict[str, Any],
) -> list[str]:
    assumptions = list(backend_artifact.get("contract_assumptions", ()))
    backend_kind = backend_artifact["kind"]
    if backend_kind == "wasm":
        assumptions.append("helper-free Wasm subset execution only")
        if any(function.get("kind") == "record_cell" for function in subset.get("functions", {}).values()):
            assumptions.append("record-cell ABI limited to the fixed offset=0 shared-handle slice")
    if contract["equivalence_mode"] == "contract_bounded":
        assumptions.append("contract-bounded normalization is explicitly enabled")
    if contract.get("allowed_allocation_variation"):
        assumptions.append("allocation variation normalizes local and cell writes into state-write observations")
    return _ordered_unique(assumptions)


def validation_strength_for_backend(backend_subset_class: str) -> str:
    if backend_subset_class in {"wasm_helper_free_bounded", "python_bounded"}:
        return "execution_backed_subset"
    return "structural_only"


def downgrade_reason_for_backend(backend_kind: str, backend_subset_class: str) -> str | None:
    if backend_subset_class == "wasm_helper_free_bounded":
        return "helper_free_subset_bounded_execution"
    if backend_subset_class == "python_bounded":
        return "experimental_python_bounded_execution"
    if backend_kind == "wasm":
        return "unsupported_wasm_subset"
    return None


def compare_observations(
    oracle: dict[str, Any],
    backend: dict[str, Any],
    contract: dict[str, Any],
    *,
    declared_capabilities: set[str],
    provenance_index: dict[str, list[dict[str, str]]],
    invocation: dict[str, Any],
    backend_kind: str,
) -> dict[str, Any]:
    dimension_results = {
        dimension: True for dimension in contract["observable_dimensions_checked"]
    }
    findings: list[dict[str, Any]] = []
    violations: list[str] = []

    for dimension in contract["observable_dimensions_checked"]:
        if dimension == "returns":
            expected = oracle["returns"]
            observed = backend["returns"]
            matched = _values_equivalent(expected, observed, contract)
        elif dimension == "capability_trace":
            expected = oracle["capability_trace"]
            observed = backend["capability_trace"]
            missing = sorted(set(expected) - set(observed))
            extra = sorted(set(observed) - declared_capabilities)
            matched = expected == observed and not missing and not extra
            if not matched:
                details = []
                if expected != observed:
                    details.append(f"expected {expected!r} observed {observed!r}")
                if missing:
                    details.append(f"missing {missing!r}")
                if extra:
                    details.append(f"undeclared {extra!r}")
                message = f"capability_trace mismatch ({'; '.join(details)})"
                finding = build_finding(
                    dimension,
                    invocation,
                    expected,
                    observed,
                    message,
                    provenance_index,
                    backend_kind,
                )
                findings.append(finding)
                violations.append(f"{_invocation_label(invocation)}: {message}")
                dimension_results[dimension] = False
                continue
        else:
            expected = _project_observation_dimension(dimension, oracle, contract)
            observed = _project_observation_dimension(dimension, backend, contract)
            matched = expected == observed

        if matched:
            continue
        message = f"{dimension} mismatch: expected {expected!r} observed {observed!r}"
        finding = build_finding(
            dimension,
            invocation,
            expected,
            observed,
            message,
            provenance_index,
            backend_kind,
        )
        findings.append(finding)
        violations.append(f"{_invocation_label(invocation)}: {message}")
        dimension_results[dimension] = False

    return {
        "dimension_results": dimension_results,
        "findings": findings,
        "violations": violations,
    }


def build_finding(
    dimension: str,
    invocation: dict[str, Any],
    expected: Any,
    observed: Any,
    message: str,
    provenance_index: dict[str, list[dict[str, str]]],
    backend_kind: str,
) -> dict[str, Any]:
    origin_links = [dict(link) for link in provenance_index.get(dimension, [])]
    suspect_l_nodes = _ordered_unique([link["l_node"] for link in origin_links if link.get("l_node")])
    suspect_h_nodes = _ordered_unique([link["h_origin"] for link in origin_links if link.get("h_origin")])
    backend_regions = infer_backend_regions(backend_kind, invocation, dimension)
    return {
        "invocation": _invocation_label(invocation),
        "dimension": dimension,
        "message": message,
        "expected": copy.deepcopy(expected),
        "observed": copy.deepcopy(observed),
        "suspect_l_nodes": suspect_l_nodes,
        "suspect_h_nodes": suspect_h_nodes,
        "backend_regions": backend_regions,
        "origin_trace_links": origin_links,
    }


def infer_backend_regions(backend_kind: str, invocation: dict[str, Any], dimension: str) -> list[str]:
    function_name = invocation["function"]
    regions = [f"{backend_kind}.function:{function_name}"]
    if backend_kind == "wasm" and dimension in {"state_write_trace", "effect_trace"}:
        if invocation.get("initial_memory"):
            regions.append("wasm.memory")
    return regions


def build_provenance_index(scirl: dict) -> dict[str, list[dict[str, str]]]:
    index = {dimension: [] for dimension in ALL_OBSERVABLE_DIMENSIONS}
    for function in scirl["functions"]:
        for block in function["blocks"]:
            for instruction in block["instructions"]:
                l_node = f"{function['name']}::{block['id']}::{instruction['id']}"
                origin = instruction.get("origin")
                op = instruction["op"]
                if op == "store":
                    _append_origin(index, "state_write_trace", l_node, origin)
                    _append_origin(index, "effect_trace", l_node, origin)
                elif op == "call":
                    _append_origin(index, "call_trace", l_node, origin)
                elif op == "opaque.call":
                    _append_origin(index, "call_trace", l_node, origin)
                    _append_origin(index, "effect_trace", l_node, origin)
                    _append_origin(index, "capability_trace", l_node, origin)
                elif op == "async.resume":
                    _append_origin(index, "effect_trace", l_node, origin)
            terminator = block["terminator"]
            l_node = f"{function['name']}::{block['id']}::terminator"
            origin = terminator.get("origin")
            if terminator["kind"] == "ret":
                _append_origin(index, "returns", l_node, origin)
                _append_origin(index, "termination_kind", l_node, origin)
                _append_origin(index, "traps_or_exceptions", l_node, origin)
            elif terminator["kind"] == "cond_br":
                _append_origin(index, "branch_trace", l_node, origin)
    return index


def build_observation(trace: dict[str, Any]) -> dict[str, Any]:
    return {
        "returns": copy.deepcopy(trace["return_value"]),
        "traps_or_exceptions": trace["error"],
        "termination_kind": trace["termination_kind"],
        "call_trace": copy.deepcopy(trace["calls"]),
        "branch_trace": copy.deepcopy(trace["branches"]),
        "state_write_trace": copy.deepcopy(trace["state_transitions"]),
        "effect_trace": _build_effect_trace(trace),
        "capability_trace": copy.deepcopy(trace["capabilities"]),
    }


def _project_observation_dimension(dimension: str, observation: dict[str, Any], contract: dict[str, Any]) -> Any:
    value = copy.deepcopy(observation[dimension])
    if contract["equivalence_mode"] != "contract_bounded":
        return value
    if dimension == "state_write_trace" and contract.get("allowed_allocation_variation"):
        return _normalized_state_transitions(value)
    if dimension == "effect_trace" and contract.get("allowed_allocation_variation"):
        return _normalized_effects(value)
    return value


def run_backend(
    backend_artifact: dict,
    invocation: dict[str, Any],
    *,
    host_functions: dict[str, HostFunctionSpec],
    classified_functions: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    kind = backend_artifact["kind"]
    if kind == "wasm":
        return run_backend_wasm(backend_artifact, invocation, classified_functions=classified_functions)
    if kind == "python":
        return run_backend_python(backend_artifact, invocation, host_functions=host_functions)
    raise TranslationValidationError(f"unsupported backend artifact kind {kind!r}")


def run_backend_wasm(
    backend_artifact: dict,
    invocation: dict[str, Any],
    *,
    classified_functions: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    functions = classified_functions or classify_wasm_subset(backend_artifact["text"]).get("functions", {})
    function_name = invocation["function"]
    args = list(invocation.get("args", ()))
    memory = dict(copy.deepcopy(invocation.get("initial_memory", {})))
    trace = _make_backend_trace(function_name, args, memory)
    try:
        return_value = _execute_wasm_function(functions, function_name, args, memory, trace)
    except Exception as exc:  # pragma: no cover - exercised through failure paths
        trace["error"] = f"{type(exc).__name__}: {exc}"
        trace["termination_kind"] = "trap"
        trace["events"].append({"kind": "error", "message": trace["error"]})
        return trace
    trace["return_value"] = return_value
    trace["termination_kind"] = "return"
    trace["events"].append({"kind": "return", "function": function_name, "value": copy.deepcopy(return_value)})
    trace["final_memory"] = {repr(key): copy.deepcopy(value) for key, value in memory.items()}
    return trace


def run_backend_python(
    backend_artifact: dict,
    invocation: dict[str, Any],
    *,
    host_functions: dict[str, HostFunctionSpec],
) -> dict[str, Any]:
    source_text = backend_artifact["source_text"]
    function_name = invocation["function"]
    args = list(invocation.get("args", ()))
    filename = backend_artifact.get("filename", f"<translation:{function_name}>")
    trace = _make_backend_trace(function_name, args, {})
    namespace = {"__builtins__": __builtins__}
    installed_modules: list[str] = []

    for module_name, exports in backend_artifact.get("host_modules", {}).items():
        module = ModuleType(module_name)
        for export_name, export_value in exports.items():
            host = export_value
            if isinstance(export_value, HostFunctionSpec):
                host = _wrap_host_callable(trace, f"{module_name}.{export_name}", export_value)
            setattr(module, export_name, host)
        sys.modules[module_name] = module
        installed_modules.append(module_name)

    def profiler(frame, event, arg):
        if frame.f_code.co_filename != filename:
            return profiler
        if event == "call":
            callee = frame.f_code.co_name
            if callee not in {function_name, "<module>"}:
                trace["calls"].append({"kind": "call", "target": callee, "args": _frame_call_args(frame)})
        return profiler

    try:
        compiled = compile(source_text, filename, "exec")
        exec(compiled, namespace)
        target = namespace[function_name]
        sys.setprofile(profiler)
        if inspect.iscoroutinefunction(target):
            trace["effects"].append({"effect": "await", "target": function_name})
            return_value = asyncio.run(target(*args))
        else:
            return_value = target(*args)
    except Exception as exc:
        trace["error"] = f"{type(exc).__name__}: {exc}"
        trace["termination_kind"] = "trap"
        trace["events"].append({"kind": "error", "message": trace["error"]})
        return trace
    finally:
        sys.setprofile(None)
        for module_name in installed_modules:
            sys.modules.pop(module_name, None)

    trace["return_value"] = copy.deepcopy(return_value)
    trace["termination_kind"] = "return"
    trace["events"].append({"kind": "return", "function": function_name, "value": copy.deepcopy(return_value)})
    return trace


def declared_capabilities(scirl: dict, backend_artifact: dict) -> set[str]:
    del scirl
    boundary_contracts = backend_artifact.get("boundary_contracts")
    if boundary_contracts is None:
        return set()
    if isinstance(boundary_contracts, dict):
        boundary_contracts = [boundary_contracts]
    capabilities = set()
    for contract in boundary_contracts:
        capabilities.update(contract.get("capabilities", ()))
    return capabilities


def _execute_wasm_function(
    functions: dict[str, dict[str, Any]],
    function_name: str,
    args: list[Any],
    memory: dict[Any, Any],
    trace: dict[str, Any],
) -> Any:
    if function_name not in functions:
        raise TranslationValidationError(f"unknown Wasm export {function_name!r}")
    function = functions[function_name]
    trace["events"].append({"kind": "enter_function", "function": function_name, "args": copy.deepcopy(args)})
    kind = function["kind"]

    if kind == "const":
        return function["const"]
    if kind == "passthrough":
        return args[0]
    if kind == "direct_call":
        trace["calls"].append({"kind": "call", "target": function["target"], "args": copy.deepcopy(args)})
        return _execute_wasm_function(functions, function["target"], args, memory, trace)
    if kind == "local_slot":
        value = args[0]
        trace["state_transitions"].append({"target_kind": "local", "value": value})
        trace["effects"].append({"effect": "write", "target_kind": "local", "value": value})
        if value < 0:
            trace["branches"].append(True)
            trace["state_transitions"].append({"target_kind": "local", "value": 0})
            trace["effects"].append({"effect": "write", "target_kind": "local", "value": 0})
            return 0
        trace["branches"].append(False)
        return value
    if kind == "record_cell":
        address = args[0]
        current = copy.deepcopy(memory.get(address, 0))
        if current < 0:
            trace["branches"].append(True)
            memory[address] = 0
            trace["state_transitions"].append({"target_kind": "field", "value": 0})
            trace["effects"].append({"effect": "write", "target_kind": "field", "value": 0})
            current = 0
        else:
            trace["branches"].append(False)
        return copy.deepcopy(current)
    raise TranslationValidationError(f"unsupported Wasm execution kind {kind!r}")


def _wrap_host_callable(trace: dict[str, Any], target: str, host_spec: HostFunctionSpec):
    def wrapped(*args):
        normalized_target = _normalize_backend_symbol(target)
        trace["calls"].append({"kind": "opaque.call", "target": normalized_target, "args": copy.deepcopy(list(args))})
        trace["effects"].append({"effect": "opaque", "target": normalized_target})
        for effect in host_spec.effects:
            trace["effects"].append({"effect": effect, "target": normalized_target})
        for capability in host_spec.capabilities:
            trace["capabilities"].append(capability)
        for io_event in host_spec.io_events:
            trace["io_events"].append({"event": io_event, "target": normalized_target})
        return host_spec.handler(*args)

    return wrapped


def _normalize_host_functions(
    host_functions: dict[str, Any] | None,
) -> dict[str, HostFunctionSpec]:
    normalized: dict[str, HostFunctionSpec] = {}
    for name, value in (host_functions or {}).items():
        if isinstance(value, HostFunctionSpec):
            normalized[name] = value
        else:
            normalized[name] = HostFunctionSpec(handler=value)
    return normalized


def _normalized_state_transitions(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for event in events:
        normalized_kind = event["target_kind"]
        if normalized_kind in {"cell", "local"}:
            normalized_kind = "state"
        normalized.append({"target_kind": normalized_kind, "value": copy.deepcopy(event["value"])})
    return normalized


def _normalized_effects(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for event in events:
        normalized_event = copy.deepcopy(event)
        if normalized_event.get("effect") == "write" and normalized_event.get("target_kind") in {"cell", "local"}:
            normalized_event["target_kind"] = "state"
        normalized.append(normalized_event)
    return normalized


def _values_equivalent(left: Any, right: Any, contract: dict[str, Any]) -> bool:
    tolerance = float(contract.get("fp_tolerance", 0.0) or 0.0)
    if isinstance(left, float) or isinstance(right, float):
        return abs(float(left) - float(right)) <= tolerance
    return left == right


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _invocation_label(invocation: dict[str, Any]) -> str:
    return f"{invocation['function']}({', '.join(repr(arg) for arg in invocation.get('args', []))})"


def _append_origin(index: dict[str, list[dict[str, str]]], dimension: str, l_node: str, origin: str | None) -> None:
    if origin is None:
        return
    index[dimension].append({"dimension": dimension, "l_node": l_node, "h_origin": origin})


def _build_effect_trace(trace: dict[str, Any]) -> list[dict[str, Any]]:
    effect_trace = [copy.deepcopy(event) for event in trace["effects"]]
    for io_event in trace["io_events"]:
        effect_trace.append({"effect": "io", "event": io_event["event"], "target": io_event["target"]})
    return effect_trace


def _ordered_unique(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def _ordered_unique_links(items: list[dict[str, str]]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (item.get("dimension", ""), item.get("l_node", ""), item.get("h_origin", ""))
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _frame_call_args(frame) -> list[Any]:
    arg_names = frame.f_code.co_varnames[:frame.f_code.co_argcount]
    return [copy.deepcopy(frame.f_locals[name]) for name in arg_names if name in frame.f_locals]


def _normalize_backend_symbol(target: str) -> str:
    if "." not in target:
        return target
    return target.replace(".", "_")


def _make_backend_trace(function_name: str, args: list[Any], initial_memory: dict[Any, Any]) -> dict[str, Any]:
    return {
        "function": function_name,
        "args": copy.deepcopy(args),
        "initial_memory": {repr(key): copy.deepcopy(value) for key, value in initial_memory.items()},
        "return_value": None,
        "error": None,
        "termination_kind": None,
        "calls": [],
        "effects": [],
        "capabilities": [],
        "io_events": [],
        "branches": [],
        "state_transitions": [],
        "events": [],
        "final_memory": {},
    }
