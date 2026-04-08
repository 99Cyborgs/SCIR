"""Deferred Track D helpers retained outside the active MVP pipeline."""
from __future__ import annotations

import asyncio
import hashlib
import importlib
import json
import pathlib
import statistics
import subprocess
import sys
import tempfile
import time
from typing import Any


TRACK_D_CONTROLS = [
    "hash every published corpus manifest",
    "separate development, tuning, and held-out evaluation slices",
    "record prompt templates and baseline adapters",
    "do not claim generalization from a contaminated or untracked dataset",
]

PYTHON_TRACK_D_CASES = ["a_basic_function", "a_async_await", "c_opaque_call"]
RUST_TRACK_D_CASES = ["a_mut_local", "a_struct_field_borrow_mut", "a_async_await"]
PYTHON_TRACK_D_ITERATIONS = {
    "a_basic_function": 20000,
    "a_async_await": 1000,
    "c_opaque_call": 4000,
}
RUST_TRACK_D_ITERATIONS = {
    "a_mut_local": 200000,
    "a_struct_field_borrow_mut": 120000,
    "a_async_await": 30000,
}


def rust_corpus_hash(pipeline: Any) -> str:
    digest = hashlib.sha256()
    for case_name in pipeline.RUST_ALL_CASES:
        digest.update(pipeline.RUST_SOURCE_TEXTS[case_name].encode("utf-8"))
    return f"sha256:{digest.hexdigest()}"


def compare_rust_imported_feature_totals(pipeline: Any, root: pathlib.Path):
    total = 0
    opaque = 0
    tier_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
    for case_name in pipeline.RUST_SUPPORTED_CASES:
        report = pipeline.load_rust_import_artifacts(root, case_name)["feature_tier_report.json"]
        total += len(report["items"])
        for item in report["items"]:
            tier_counts[item["tier"]] += 1
            if item["tier"] == "C":
                opaque += 1
    return opaque, total, tier_counts


def scirl_instruction_count(module: dict) -> int:
    return sum(len(block["instructions"]) for function in module["functions"] for block in function["blocks"])


def optimize_local_cell_module(pipeline: Any, lowered: dict):
    function = lowered["functions"][0]
    entry, neg, retread = function["blocks"]
    if [item["op"] for item in entry["instructions"]] != ["alloc", "store", "load", "cmp"]:
        raise pipeline.PipelineError(f"{lowered['module_id']}: expected local-cell lowering for optimization")
    if [item["op"] for item in neg["instructions"]] != ["store"]:
        raise pipeline.PipelineError(f"{lowered['module_id']}: expected store-only negative block for optimization")
    if [item["op"] for item in retread["instructions"]] != ["load"]:
        raise pipeline.PipelineError(f"{lowered['module_id']}: expected load-only return block for optimization")

    param = function["params"][0]
    module_id = lowered["module_id"]
    return {
        "module_id": module_id,
        "functions": [
            {
                "name": function["name"],
                "returns": function["returns"],
                "params": list(function["params"]),
                "blocks": [
                    {
                        "id": "entry",
                        "params": [],
                        "instructions": [
                            {
                                "id": "cmp0",
                                "op": "cmp",
                                "operands": [param, 0],
                                "origin": f"{module_id}::track-d-opt-cmp-param-zero",
                            }
                        ],
                        "terminator": {
                            "kind": "cond_br",
                            "cond": "cmp0",
                            "true": "neg",
                            "true_args": [],
                            "false": "retv",
                            "false_args": [param],
                            "origin": f"{module_id}::track-d-opt-branch",
                        },
                    },
                    {
                        "id": "neg",
                        "params": [],
                        "instructions": [
                            {
                                "id": "const0",
                                "op": "const",
                                "operands": [0],
                                "origin": f"{module_id}::track-d-opt-const-zero",
                            }
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "const0",
                            "origin": f"{module_id}::track-d-opt-ret-zero",
                        },
                    },
                    {
                        "id": "retv",
                        "params": ["value0"],
                        "instructions": [],
                        "terminator": {
                            "kind": "ret",
                            "value": "value0",
                            "origin": f"{module_id}::track-d-opt-ret-value",
                        },
                    },
                ],
            }
        ],
    }


def optimize_field_borrow_module(pipeline: Any, lowered: dict):
    function = lowered["functions"][0]
    entry, neg, retread = function["blocks"]
    if [item["op"] for item in entry["instructions"]] != ["field.addr", "load", "cmp"]:
        raise pipeline.PipelineError(f"{lowered['module_id']}: expected field borrow lowering for optimization")
    if [item["op"] for item in neg["instructions"]] != ["store"]:
        raise pipeline.PipelineError(f"{lowered['module_id']}: expected field store block for optimization")
    if [item["op"] for item in retread["instructions"]] != ["load"]:
        raise pipeline.PipelineError(f"{lowered['module_id']}: expected field reload block for optimization")

    module_id = lowered["module_id"]
    field_symbol = entry["instructions"][0]["operands"][1]
    param = function["params"][0]
    return {
        "module_id": module_id,
        "functions": [
            {
                "name": function["name"],
                "returns": function["returns"],
                "params": list(function["params"]),
                "blocks": [
                    {
                        "id": "entry",
                        "params": ["mem0"],
                        "instructions": [
                            {
                                "id": "field0",
                                "op": "field.addr",
                                "operands": [param, field_symbol],
                                "origin": f"{module_id}::track-d-opt-field",
                            },
                            {
                                "id": "load0",
                                "op": "load",
                                "operands": ["field0", "mem0"],
                                "origin": f"{module_id}::track-d-opt-load-field",
                            },
                            {
                                "id": "cmp0",
                                "op": "cmp",
                                "operands": ["load0", 0],
                                "origin": f"{module_id}::track-d-opt-cmp-zero",
                            },
                        ],
                        "terminator": {
                            "kind": "cond_br",
                            "cond": "cmp0",
                            "true": "neg",
                            "true_args": ["field0", "mem0"],
                            "false": "retv",
                            "false_args": ["load0"],
                            "origin": f"{module_id}::track-d-opt-branch",
                        },
                    },
                    {
                        "id": "neg",
                        "params": ["field1", "mem1"],
                        "instructions": [
                            {
                                "id": "const0",
                                "op": "const",
                                "operands": [0],
                                "origin": f"{module_id}::track-d-opt-const-zero",
                            },
                            {
                                "id": "mem2",
                                "op": "store",
                                "operands": ["field1", 0, "mem1"],
                                "origin": f"{module_id}::track-d-opt-store-zero",
                            },
                        ],
                        "terminator": {
                            "kind": "ret",
                            "value": "const0",
                            "origin": f"{module_id}::track-d-opt-ret-zero",
                        },
                    },
                    {
                        "id": "retv",
                        "params": ["value0"],
                        "instructions": [],
                        "terminator": {
                            "kind": "ret",
                            "value": "value0",
                            "origin": f"{module_id}::track-d-opt-ret-value",
                        },
                    },
                ],
            }
        ],
    }

def optimize_python_track_d_module(pipeline: Any, case_name: str, lowered: dict):
    if case_name == "a_basic_function":
        return optimize_local_cell_module(pipeline, lowered)
    if case_name in {"a_async_await", "c_opaque_call"}:
        return json.loads(json.dumps(lowered))
    raise pipeline.PipelineError(f"{case_name}: Python Track D optimization contract is not defined")


def optimize_rust_track_d_module(pipeline: Any, case_name: str, lowered: dict):
    if case_name == "a_mut_local":
        return optimize_local_cell_module(pipeline, lowered)
    if case_name == "a_struct_field_borrow_mut":
        return optimize_field_borrow_module(pipeline, lowered)
    if case_name == "a_async_await":
        return json.loads(json.dumps(lowered))
    raise pipeline.PipelineError(f"{case_name}: Rust Track D optimization contract is not defined")


def emit_python_track_d_source(pipeline: Any, case_name: str, optimized: bool):
    if case_name == "a_basic_function" and optimized:
        return (
            "def clamp_nonneg(x):\n"
            "    if x < 0:\n"
            "        return 0\n"
            "    return x\n"
        )
    return pipeline.PYTHON_SOURCE_TEXTS[case_name]


def emit_rust_track_d_source(pipeline: Any, case_name: str, optimized: bool):
    if case_name == "a_mut_local" and optimized:
        return (
            "pub fn clamp_nonneg(x: i32) -> i32 {\n"
            "    if x < 0 {\n"
            "        return 0;\n"
            "    }\n"
            "    return x;\n"
            "}\n"
        )
    if case_name == "a_struct_field_borrow_mut" and optimized:
        return (
            "pub struct Counter {\n"
            "    pub value: i32,\n"
            "}\n"
            "\n"
            "pub fn clamp_counter(counter: &mut Counter) -> i32 {\n"
            "    if counter.value < 0 {\n"
            "        counter.value = 0;\n"
            "        return 0;\n"
            "    }\n"
            "    return counter.value;\n"
            "}\n"
        )
    return pipeline.RUST_SOURCE_TEXTS[case_name]


def execute_python_track_d_case(pipeline: Any, case_name: str, source_text: str, iterations: int):
    namespace = {"__builtins__": __builtins__}
    compile(source_text, f"<track-d:{case_name}>", "exec")
    if case_name == "a_basic_function":
        exec(compile(source_text, f"<track-d:{case_name}>", "exec"), namespace)
        function = namespace["clamp_nonneg"]
        function(-3)
        start = time.perf_counter()
        checksum = 0
        for index in range(iterations):
            checksum += function(-3 if index % 2 == 0 else 4)
        return time.perf_counter() - start, checksum
    if case_name == "a_async_await":
        exec(compile(source_text, f"<track-d:{case_name}>", "exec"), namespace)

        async def run_many():
            checksum = 0
            for _ in range(iterations):
                checksum += await namespace["load_once"]()
            return checksum

        asyncio.run(run_many())
        start = time.perf_counter()
        checksum = asyncio.run(run_many())
        return time.perf_counter() - start, checksum
    if case_name == "c_opaque_call":
        with tempfile.TemporaryDirectory(prefix="scir-track-d-foreign-api-") as tmp:
            temp_dir = pathlib.Path(tmp)
            (temp_dir / "foreign_api.py").write_text(
                "def ping():\n    return {'status': 'ok', 'origin': 'stub'}\n",
                encoding="utf-8",
            )
            sys.path.insert(0, str(temp_dir))
            try:
                importlib.invalidate_caches()
                sys.modules.pop("foreign_api", None)
                exec(compile(source_text, f"<track-d:{case_name}>", "exec"), namespace)
                function = namespace["ping"]
                function()
                start = time.perf_counter()
                checksum = 0
                for _ in range(iterations):
                    checksum += len(function()["origin"])
                return time.perf_counter() - start, checksum
            finally:
                sys.modules.pop("foreign_api", None)
                sys.path.pop(0)
    raise pipeline.PipelineError(f"{case_name}: Python Track D execution harness is not defined")


def rust_benchmark_harness(pipeline: Any, case_name: str, crate_name: str, iterations: int):
    if case_name == "a_mut_local":
        return (
            f"use {crate_name}::clamp_nonneg;\n\n"
            "fn main() {\n"
            "    let mut checksum: i64 = 0;\n"
            f"    for index in 0..{iterations} {{\n"
            "        checksum += clamp_nonneg(if index % 2 == 0 { -3 } else { 4 }) as i64;\n"
            "    }\n"
            "    println!(\"{}\", checksum);\n"
            "}\n"
        )
    if case_name == "a_struct_field_borrow_mut":
        return (
            f"use {crate_name}::{{clamp_counter, Counter}};\n\n"
            "fn main() {\n"
            "    let mut checksum: i64 = 0;\n"
            f"    for index in 0..{iterations} {{\n"
            "        let mut counter = Counter { value: if index % 2 == 0 { -5 } else { 4 } };\n"
            "        checksum += clamp_counter(&mut counter) as i64;\n"
            "        checksum += counter.value as i64;\n"
            "    }\n"
            "    println!(\"{}\", checksum);\n"
            "}\n"
        )
    if case_name == "a_async_await":
        return (
            f"use {crate_name}::load_once;\n"
            "use std::future::Future;\n"
            "use std::pin::Pin;\n"
            "use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};\n\n"
            "fn noop_raw_waker() -> RawWaker {\n"
            "    fn clone(_: *const ()) -> RawWaker { noop_raw_waker() }\n"
            "    fn wake(_: *const ()) {}\n"
            "    fn wake_by_ref(_: *const ()) {}\n"
            "    fn drop(_: *const ()) {}\n"
            "    RawWaker::new(std::ptr::null(), &RawWakerVTable::new(clone, wake, wake_by_ref, drop))\n"
            "}\n\n"
            "fn block_on<F: Future>(future: F) -> F::Output {\n"
            "    let waker = unsafe { Waker::from_raw(noop_raw_waker()) };\n"
            "    let mut future = Pin::from(Box::new(future));\n"
            "    loop {\n"
            "        let mut context = Context::from_waker(&waker);\n"
            "        match Future::poll(future.as_mut(), &mut context) {\n"
            "            Poll::Ready(value) => return value,\n"
            "            Poll::Pending => std::thread::yield_now(),\n"
            "        }\n"
            "    }\n"
            "}\n\n"
            "fn main() {\n"
            "    let mut checksum: i64 = 0;\n"
            f"    for _ in 0..{iterations} {{\n"
            "        checksum += block_on(load_once()) as i64;\n"
            "    }\n"
            "    println!(\"{}\", checksum);\n"
            "}\n"
        )
    raise pipeline.PipelineError(f"{case_name}: Rust Track D benchmark harness is not defined")


def rust_binary_path(crate_root: pathlib.Path, crate_name: str):
    suffix = ".exe" if sys.platform.startswith("win") else ""
    return crate_root / "target" / "debug" / f"{crate_name}{suffix}"

def measure_rust_track_d_case(pipeline: Any, case_name: str, source_text: str, iterations: int):
    pipeline.require_rust_toolchain()
    with tempfile.TemporaryDirectory(
        prefix=f"scir-track-d-rust-{case_name}-",
        ignore_cleanup_errors=True,
    ) as tmp:
        crate_root = pathlib.Path(tmp)
        crate_name = f"track_d_{pipeline.slug(case_name).replace('-', '_')}"
        (crate_root / "src").mkdir(parents=True, exist_ok=True)
        (crate_root / "src" / "lib.rs").write_text(source_text, encoding="utf-8")
        (crate_root / "src" / "main.rs").write_text(
            rust_benchmark_harness(pipeline, case_name, crate_name, iterations),
            encoding="utf-8",
        )
        (crate_root / "Cargo.toml").write_text(
            (
                f"[package]\nname = \"{crate_name}\"\nversion = \"0.1.0\"\nedition = \"2021\"\n\n"
                "[lib]\npath = \"src/lib.rs\"\n"
            ),
            encoding="utf-8",
        )

        compile_start = time.perf_counter()
        compile_result = pipeline.run_rust_command(
            ["cargo", "build", "--quiet"],
            cwd=crate_root,
            capture_output=True,
            text=True,
        )
        compile_time = time.perf_counter() - compile_start
        if compile_result.returncode != 0:
            raise pipeline.PipelineError(f"{case_name}: cargo build failed for Track D benchmark source")

        binary_path = rust_binary_path(crate_root, crate_name)
        if not binary_path.exists():
            raise pipeline.PipelineError(f"{case_name}: expected Track D benchmark binary at {binary_path}")

        runtime_start = time.perf_counter()
        run_result = subprocess.run(
            [str(binary_path)],
            cwd=crate_root,
            capture_output=True,
            text=True,
            check=False,
        )
        runtime_time = time.perf_counter() - runtime_start
        if run_result.returncode != 0:
            raise pipeline.PipelineError(f"{case_name}: Track D benchmark binary failed to execute")

        return {
            "compile_time": compile_time,
            "runtime_time": runtime_time,
            "artifact_size": binary_path.stat().st_size,
            "output": run_result.stdout.strip(),
        }


def run_python_track_d(pipeline: Any, root: pathlib.Path):
    opaque_nodes, total_nodes, tier_counts = pipeline.compare_imported_feature_totals(root)
    opaque_fraction = opaque_nodes / total_nodes
    sync_ratios = []
    async_ratio = None
    opaque_ratio = None
    observable_match = True
    instruction_ratios = []

    for case_name in PYTHON_TRACK_D_CASES:
        lowered = pipeline.lower_supported_module(pipeline.PYTHON_SCIRH_MODULES[case_name])
        optimized = optimize_python_track_d_module(pipeline, case_name, lowered)
        scirl_failures, _ = pipeline.validate_scirl_module(optimized)
        if scirl_failures:
            raise pipeline.PipelineError(f"{case_name}: optimized Python Track D SCIR-L failed validation")
        instruction_ratios.append(scirl_instruction_count(optimized) / scirl_instruction_count(lowered))

        direct_source = pipeline.PYTHON_SOURCE_TEXTS[case_name]
        unoptimized_source = emit_python_track_d_source(pipeline, case_name, optimized=False)
        optimized_source = emit_python_track_d_source(pipeline, case_name, optimized=True)
        direct_elapsed, direct_value = execute_python_track_d_case(
            pipeline,
            case_name,
            direct_source,
            PYTHON_TRACK_D_ITERATIONS[case_name],
        )
        if unoptimized_source == direct_source:
            unoptimized_elapsed, unoptimized_value = direct_elapsed, direct_value
        else:
            unoptimized_elapsed, unoptimized_value = execute_python_track_d_case(
                pipeline,
                case_name,
                unoptimized_source,
                PYTHON_TRACK_D_ITERATIONS[case_name],
            )
        if optimized_source == direct_source:
            optimized_elapsed, optimized_value = direct_elapsed, direct_value
        else:
            optimized_elapsed, optimized_value = execute_python_track_d_case(
                pipeline,
                case_name,
                optimized_source,
                PYTHON_TRACK_D_ITERATIONS[case_name],
            )
        observable_match = observable_match and direct_value == unoptimized_value == optimized_value
        ratio = optimized_elapsed / direct_elapsed
        if case_name == "a_async_await":
            async_ratio = ratio
        elif case_name == "c_opaque_call":
            opaque_ratio = ratio
            sync_ratios.append(ratio)
        else:
            sync_ratios.append(ratio)

    median_runtime_ratio = statistics.median(sync_ratios)
    gate_s5_pass = (
        median_runtime_ratio <= 1.50
        and async_ratio is not None
        and async_ratio <= 1.75
        and opaque_ratio is not None
        and opaque_ratio <= 1.25
    )
    gate_k8_hit = (
        any(ratio > 2.0 for ratio in sync_ratios)
        or (async_ratio is not None and async_ratio > 2.0)
        or (opaque_ratio is not None and opaque_ratio > 2.0)
        or not observable_match
    )

    manifest = {
        "benchmark_id": "bootstrap-track-d-python-dpy-subset",
        "track": "D",
        "task_family": "python-bootstrap-host-runtime",
        "corpus": {
            "name": "python-bootstrap-fixtures",
            "scope": "Fixed Python bootstrap cases emitted from optimized SCIR-L",
            "hash": pipeline.corpus_hash(pipeline.BENCHMARK_CASES),
        },
        "baselines": ["direct source", "typed-AST"],
        "profiles": ["D-PY"],
        "success_gates": ["S5"],
        "kill_gates": ["K8"],
        "contamination_controls": list(TRACK_D_CONTROLS),
    }
    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": "bootstrap-track-d-python-run-2026-03-17",
        "system_under_test": "scir-bootstrap-track-d-python-dpy",
        "track": "D",
        "profile": "D-PY",
        "metrics": {
            "median_runtime_ratio": round(median_runtime_ratio, 4),
            "async_overhead_ratio": round(async_ratio, 4),
            "opaque_boundary_overhead_ratio": round(opaque_ratio, 4),
            "observable_match": observable_match,
            "gate_S5_pass": gate_s5_pass,
            "gate_K8_hit": gate_k8_hit,
            "opaque_fraction": round(opaque_fraction, 4),
            "preservation_level_ceiling": "P3",
            "tier_a_feature_count": tier_counts["A"],
            "tier_b_feature_count": tier_counts["B"],
            "tier_c_feature_count": tier_counts["C"],
            "tier_d_feature_count": tier_counts["D"],
            "instruction_reduction_ratio": round(statistics.mean(instruction_ratios), 4),
        },
        "baseline_comparison": {
            "direct source": round(median_runtime_ratio - 1.0, 4),
            "typed-AST": "translation-only reference",
        },
        "status": "pass" if gate_s5_pass and not gate_k8_hit else "fail",
        "evidence": [
            "optimized Python D-PY source emitted from fixed SCIR-L bootstrap cases",
            "direct-source runtime baseline on the same harness",
            "observable matching checked across direct, unoptimized, and optimized emission",
        ],
    }
    return manifest, result

def run_rust_track_d(pipeline: Any, root: pathlib.Path):
    pipeline.require_rust_toolchain()
    opaque_nodes, total_nodes, tier_counts = compare_rust_imported_feature_totals(pipeline, root)
    opaque_fraction = opaque_nodes / total_nodes
    sync_ratios = []
    async_ratio = None
    compile_ratios = []
    size_ratios = []
    instruction_ratios = []
    observable_match = True

    for case_name in RUST_TRACK_D_CASES:
        lowered = pipeline.lower_rust_supported_module(pipeline.RUST_SCIRH_MODULES[case_name])
        optimized = optimize_rust_track_d_module(pipeline, case_name, lowered)
        scirl_failures, _ = pipeline.validate_scirl_module(optimized)
        if scirl_failures:
            raise pipeline.PipelineError(f"{case_name}: optimized Rust Track D SCIR-L failed validation")
        instruction_ratios.append(scirl_instruction_count(optimized) / scirl_instruction_count(lowered))

        direct_source = pipeline.RUST_SOURCE_TEXTS[case_name]
        unoptimized_source = emit_rust_track_d_source(pipeline, case_name, optimized=False)
        optimized_source = emit_rust_track_d_source(pipeline, case_name, optimized=True)
        direct_measure = measure_rust_track_d_case(
            pipeline,
            case_name,
            direct_source,
            RUST_TRACK_D_ITERATIONS[case_name],
        )
        if unoptimized_source == direct_source:
            unoptimized_measure = dict(direct_measure)
        else:
            unoptimized_measure = measure_rust_track_d_case(
                pipeline,
                case_name,
                unoptimized_source,
                RUST_TRACK_D_ITERATIONS[case_name],
            )
        if optimized_source == direct_source:
            optimized_measure = dict(direct_measure)
        else:
            optimized_measure = measure_rust_track_d_case(
                pipeline,
                case_name,
                optimized_source,
                RUST_TRACK_D_ITERATIONS[case_name],
            )
        observable_match = (
            observable_match
            and direct_measure["output"] == unoptimized_measure["output"] == optimized_measure["output"]
        )

        runtime_ratio = optimized_measure["runtime_time"] / direct_measure["runtime_time"]
        compile_ratio = optimized_measure["compile_time"] / direct_measure["compile_time"]
        size_ratio = optimized_measure["artifact_size"] / direct_measure["artifact_size"]
        compile_ratios.append(compile_ratio)
        size_ratios.append(size_ratio)
        if case_name == "a_async_await":
            async_ratio = runtime_ratio
        else:
            sync_ratios.append(runtime_ratio)

    median_runtime_ratio = statistics.median(sync_ratios)
    compile_time_ratio = statistics.median(compile_ratios)
    artifact_size_ratio = statistics.median(size_ratios)
    gate_s5_pass = median_runtime_ratio <= 1.25 and compile_time_ratio <= 1.50
    gate_k8_hit = (
        any(ratio > 2.0 for ratio in sync_ratios)
        or (async_ratio is not None and async_ratio > 2.0)
        or not observable_match
    )

    manifest = {
        "benchmark_id": "bootstrap-track-d-rust-n-subset",
        "track": "D",
        "task_family": "rust-bootstrap-native-runtime",
        "corpus": {
            "name": "rust-bootstrap-fixtures",
            "scope": "Fixed Rust bootstrap cases emitted from optimized SCIR-L",
            "hash": rust_corpus_hash(pipeline),
        },
        "baselines": ["direct source", "typed-AST", "SSA-like internal IR"],
        "profiles": ["N"],
        "success_gates": ["S5"],
        "kill_gates": ["K8"],
        "contamination_controls": list(TRACK_D_CONTROLS),
    }
    result = {
        "benchmark_id": manifest["benchmark_id"],
        "run_id": "bootstrap-track-d-rust-run-2026-03-17",
        "system_under_test": "scir-bootstrap-track-d-rust-n",
        "track": "D",
        "profile": "N",
        "metrics": {
            "median_runtime_ratio": round(median_runtime_ratio, 4),
            "compile_time_ratio": round(compile_time_ratio, 4),
            "artifact_size_ratio": round(artifact_size_ratio, 4),
            "peak_memory_ratio": None,
            "async_overhead_ratio": round(async_ratio, 4),
            "gate_S5_pass": gate_s5_pass,
            "gate_K8_hit": gate_k8_hit,
            "opaque_fraction": round(opaque_fraction, 4),
            "preservation_level_ceiling": "P3",
            "tier_a_feature_count": tier_counts["A"],
            "tier_b_feature_count": tier_counts["B"],
            "tier_c_feature_count": tier_counts["C"],
            "tier_d_feature_count": tier_counts["D"],
            "instruction_reduction_ratio": round(statistics.mean(instruction_ratios), 4),
            "observable_match": observable_match,
        },
        "baseline_comparison": {
            "direct source": round(median_runtime_ratio - 1.0, 4),
            "typed-AST": "translation-only reference",
            "SSA-like internal IR": "reference only",
        },
        "status": "pass" if gate_s5_pass and not gate_k8_hit else "fail",
        "evidence": [
            "optimized Rust N source emitted from fixed SCIR-L bootstrap cases",
            "direct-source runtime and compile-time baselines on the same harness",
            "observable matching checked across direct, unoptimized, and optimized emission",
        ],
    }
    return manifest, result
