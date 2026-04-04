from __future__ import annotations

import copy
import random
from dataclasses import dataclass
from typing import Any, Callable


class ScirRuntimeError(RuntimeError):
    """Raised when the bounded SCIR-L interpreter cannot execute an artifact."""


@dataclass(frozen=True)
class HostFunctionSpec:
    """Bounded host-call contract used by translation validation."""

    handler: Callable[..., Any]
    effects: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    io_events: tuple[str, ...] = ()
    deterministic: bool = True


def generate_inputs(scirl: dict, *, source_module=None) -> list[dict[str, Any]]:
    """Generate deterministic validation inputs for the active bounded subset."""

    source_functions = {
        function.name: function
        for function in getattr(source_module, "functions", ())
    }
    generated: list[dict[str, Any]] = []
    scalar_values = _scalar_input_values()

    for function in scirl["functions"]:
        name = function["name"]
        param_count = len(function["params"])
        source_function = source_functions.get(name)
        param_types = tuple(param.type_name for param in getattr(source_function, "params", ()))
        has_field_addr = any(
            instruction["op"] == "field.addr"
            for block in function["blocks"]
            for instruction in block["instructions"]
        )

        if param_count == 0:
            generated.append({"function": name, "args": [], "initial_memory": {}})
            continue

        if has_field_addr and param_count == 1:
            for value in scalar_values:
                generated.append(
                    {
                        "function": name,
                        "args": [0],
                        "initial_memory": {0: value},
                        "logical_inputs": {"counter.value": value},
                    }
                )
            continue

        if param_count == 1:
            for value in scalar_values:
                generated.append({"function": name, "args": [value], "initial_memory": {}})
            continue

        arg_space = []
        for index in range(param_count):
            type_name = param_types[index] if index < len(param_types) else "int"
            if type_name.startswith("borrow_mut<"):
                arg_space.append([0])
            else:
                arg_space.append([-1, 0, 1])
        generated.extend(_cross_product_inputs(name, arg_space))

    return generated


def run_scirl(
    scirl: dict,
    inputs: dict[str, Any],
    *,
    source_module=None,
    host_functions: dict[str, HostFunctionSpec] | None = None,
) -> dict[str, Any]:
    """Execute one bounded SCIR-L invocation and return a normalized trace."""

    host_functions = host_functions or {}
    function_name = inputs["function"]
    args = list(inputs.get("args", ()))
    memory = dict(copy.deepcopy(inputs.get("initial_memory", {})))
    trace = _make_trace(function_name, args, memory)
    functions = {function["name"]: function for function in scirl["functions"]}
    alloc_state = {"next_cell": 0, "next_mem_token": 1, "next_eff_token": 1}

    try:
        return_value = _execute_function(
            functions,
            functions[function_name],
            args,
            memory,
            trace,
            alloc_state,
            host_functions,
        )
    except Exception as exc:  # pragma: no cover - exercised through translation validator failure paths
        trace["error"] = f"{type(exc).__name__}: {exc}"
        trace["termination_kind"] = "trap"
        trace["events"].append({"kind": "error", "message": trace["error"]})
        return trace

    trace["return_value"] = copy.deepcopy(return_value)
    trace["termination_kind"] = "return"
    trace["events"].append({"kind": "return", "function": function_name, "value": copy.deepcopy(return_value)})
    trace["final_memory"] = _normalized_memory(memory)
    return trace


def _execute_function(
    functions: dict[str, dict[str, Any]],
    function: dict[str, Any],
    args: list[Any],
    memory: dict[Any, Any],
    trace: dict[str, Any],
    alloc_state: dict[str, int],
    host_functions: dict[str, HostFunctionSpec],
) -> Any:
    env = {param_name: copy.deepcopy(arg) for param_name, arg in zip(function["params"], args)}
    block_lookup = {block["id"]: block for block in function["blocks"]}
    current_block = block_lookup["entry"]
    entry_bindings = _fresh_entry_bindings(current_block["params"], alloc_state)
    env.update(entry_bindings)
    trace["events"].append({"kind": "enter_function", "function": function["name"], "args": copy.deepcopy(args)})

    while True:
        trace["events"].append({"kind": "enter_block", "function": function["name"], "block": current_block["id"]})
        for instruction in current_block["instructions"]:
            env[instruction["id"]] = _execute_instruction(
                functions,
                function["name"],
                instruction,
                env,
                memory,
                trace,
                alloc_state,
                host_functions,
            )

        terminator = current_block["terminator"]
        if terminator["kind"] == "ret":
            return _resolve_value(env, terminator["value"])

        if terminator["kind"] == "br":
            next_block = block_lookup[terminator["target"]]
            env = _merge_block_params(env, next_block["params"], terminator["args"])
            current_block = next_block
            continue

        if terminator["kind"] != "cond_br":
            raise ScirRuntimeError(f"unsupported terminator {terminator['kind']!r}")
        branch_taken = bool(_resolve_value(env, terminator["cond"]))
        trace["branches"].append(branch_taken)
        trace["events"].append({"kind": "branch", "block": current_block["id"], "taken": branch_taken})
        if branch_taken:
            next_block = block_lookup[terminator["true"]]
            env = _merge_block_params(env, next_block["params"], terminator["true_args"])
        else:
            next_block = block_lookup[terminator["false"]]
            env = _merge_block_params(env, next_block["params"], terminator["false_args"])
        current_block = next_block


def _execute_instruction(
    functions: dict[str, dict[str, Any]],
    function_name: str,
    instruction: dict[str, Any],
    env: dict[str, Any],
    memory: dict[Any, Any],
    trace: dict[str, Any],
    alloc_state: dict[str, int],
    host_functions: dict[str, HostFunctionSpec],
) -> Any:
    op = instruction["op"]
    operands = [_resolve_value(env, operand) for operand in instruction["operands"]]

    if op == "const":
        value = operands[0]
        trace["events"].append({"kind": "const", "value": value})
        return value

    if op == "alloc":
        cell_id = f"cell@{alloc_state['next_cell']}"
        alloc_state["next_cell"] += 1
        trace["events"].append({"kind": "alloc", "cell": cell_id})
        return cell_id

    if op == "field.addr":
        base, field_sym = operands
        field_name = _symbol_name(field_sym)
        address = ("field", base, field_name)
        trace["events"].append({"kind": "field.addr", "base": copy.deepcopy(base), "field": field_name})
        return address

    if op == "store":
        address, value = operands[0], copy.deepcopy(operands[1])
        memory[_normalize_address(address)] = value
        write_event = {
            "target_kind": _address_kind(address),
            "value": value,
        }
        trace["state_transitions"].append(write_event)
        trace["effects"].append({"effect": "write", "target_kind": write_event["target_kind"], "value": value})
        trace["events"].append({"kind": "store", **write_event})
        return _fresh_token("mem", alloc_state)

    if op == "load":
        address = operands[0]
        value = copy.deepcopy(memory.get(_normalize_address(address), 0))
        trace["events"].append({"kind": "load", "target_kind": _address_kind(address), "value": value})
        return value

    if op == "cmp":
        left, right = operands
        value = 1 if left < right else 0
        trace["events"].append({"kind": "cmp", "left": left, "right": right, "result": value})
        return value

    if op == "call":
        callee = _symbol_name(operands[0])
        call_args = operands[1:-1]
        trace["calls"].append({"kind": "call", "target": callee, "args": copy.deepcopy(call_args)})
        trace["events"].append({"kind": "call", "target": callee, "args": copy.deepcopy(call_args)})
        if callee not in functions:
            raise ScirRuntimeError(f"{function_name}: unknown callee {callee!r}")
        return _execute_function(functions, functions[callee], call_args, memory, trace, alloc_state, host_functions)

    if op == "async.resume":
        value = copy.deepcopy(operands[0])
        trace["effects"].append({"effect": "await", "target": function_name})
        trace["events"].append({"kind": "async.resume", "value": value})
        return value

    if op == "opaque.call":
        boundary = _symbol_name(operands[0])
        call_args = operands[1:-1]
        trace["calls"].append({"kind": "opaque.call", "target": boundary, "args": copy.deepcopy(call_args)})
        trace["effects"].append({"effect": "opaque", "target": boundary})
        trace["events"].append({"kind": "opaque.call", "target": boundary, "args": copy.deepcopy(call_args)})
        host = host_functions.get(boundary)
        if host is None:
            raise ScirRuntimeError(f"{function_name}: missing host function for boundary {boundary!r}")
        result = host.handler(*call_args)
        for effect in host.effects:
            trace["effects"].append({"effect": effect, "target": boundary})
        for capability in host.capabilities:
            trace["capabilities"].append(capability)
        for io_event in host.io_events:
            trace["io_events"].append({"event": io_event, "target": boundary})
        return copy.deepcopy(result)

    raise ScirRuntimeError(f"unsupported instruction op {op!r}")


def _merge_block_params(env: dict[str, Any], params: list[str], args: list[Any]) -> dict[str, Any]:
    next_env = dict(env)
    for name, value in zip(params, args):
        next_env[name] = _resolve_value(env, value)
    return next_env


def _resolve_value(env: dict[str, Any], operand: Any) -> Any:
    if isinstance(operand, int):
        return operand
    if isinstance(operand, tuple):
        return operand
    if isinstance(operand, str):
        if operand.startswith("sym:"):
            return operand
        if operand in env:
            return env[operand]
    return operand


def _fresh_entry_bindings(params: list[str], alloc_state: dict[str, int]) -> dict[str, Any]:
    bindings = {}
    for param in params:
        prefix = param[:3]
        if prefix == "mem":
            bindings[param] = _fresh_token("mem", alloc_state)
        elif prefix == "eff":
            bindings[param] = _fresh_token("eff", alloc_state)
    return bindings


def _fresh_token(prefix: str, alloc_state: dict[str, int]) -> str:
    key = "next_mem_token" if prefix == "mem" else "next_eff_token"
    token = f"{prefix}#{alloc_state[key]}"
    alloc_state[key] += 1
    return token


def _scalar_input_values() -> list[int]:
    values = [-2147483648, -7, -1, 0, 1, 7, 2147483647]
    seeded = random.Random(0)
    values.extend([seeded.randint(-9, 9) for _ in range(3)])
    deduped = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def _cross_product_inputs(function_name: str, arg_space: list[list[Any]]) -> list[dict[str, Any]]:
    results = [{"function": function_name, "args": [], "initial_memory": {}}]
    for candidates in arg_space:
        next_results = []
        for result in results:
            for candidate in candidates:
                next_results.append(
                    {
                        "function": function_name,
                        "args": [*result["args"], candidate],
                        "initial_memory": dict(result["initial_memory"]),
                    }
                )
        results = next_results
    return results


def _symbol_name(value: Any) -> str:
    if not isinstance(value, str):
        raise ScirRuntimeError(f"expected symbolic operand, got {value!r}")
    return value.split(":", 1)[1] if value.startswith("sym:") else value


def _normalize_address(address: Any) -> Any:
    if isinstance(address, tuple) and address and address[0] == "field":
        return address[1]
    if isinstance(address, tuple):
        return address
    return address


def _address_kind(address: Any) -> str:
    if isinstance(address, tuple) and address and address[0] == "field":
        return "field"
    if isinstance(address, str) and address.startswith("cell@"):
        return "cell"
    return "memory"


def _normalized_memory(memory: dict[Any, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in memory.items():
        normalized[repr(key)] = copy.deepcopy(value)
    return normalized


def _make_trace(function_name: str, args: list[Any], initial_memory: dict[Any, Any]) -> dict[str, Any]:
    return {
        "function": function_name,
        "args": copy.deepcopy(args),
        "initial_memory": _normalized_memory(initial_memory),
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
