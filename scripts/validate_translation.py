#!/usr/bin/env python3
"""Run execution-backed backend translation validation for active SCIR paths."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from runtime.scirl_interpreter import HostFunctionSpec  # noqa: E402
from scir_bootstrap_pipeline import (  # noqa: E402
    PipelineError,
    RECONSTRUCTION_EXPECTATIONS,
    lower_supported_module,
    parse_observable_set_arg,
    resolve_translation_validation_options,
    run_pipeline,
    run_rust_pipeline,
)
from scir_python_bootstrap import SCIRH_MODULES as PYTHON_SCIRH_MODULES  # noqa: E402
from validators.translation_validator import default_observable_dimensions, validate_translation  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root")
    parser.add_argument("--require-rust", action="store_true")
    parser.add_argument(
        "--equivalence-mode",
        choices=["deterministic_observational", "sequential_trace", "contract_bounded"],
    )
    parser.add_argument("--observable-set")
    parser.add_argument("--target-profile", choices=["R", "N", "P", "D-PY", "D-JS"])
    parser.add_argument("--allow-contract-bounded", dest="allow_contract_bounded", action="store_true")
    parser.add_argument("--disallow-contract-bounded", dest="allow_contract_bounded", action="store_false")
    parser.add_argument("--include-experimental-python", action="store_true")
    parser.set_defaults(allow_contract_bounded=None)
    return parser.parse_args()


def summarize_wasm(outputs: dict) -> dict[str, int]:
    summary: dict[str, int] = {}
    for payload in outputs.get("wasm_reports", {}).values():
        report = payload.get("translation_validation_report")
        if report is None:
            continue
        summary[report["outcome"]] = summary.get(report["outcome"], 0) + 1
    return summary


def summarize_reports(reports: list[dict]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for report in reports:
        summary[report["outcome"]] = summary.get(report["outcome"], 0) + 1
    return summary


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_experimental_python_backend_artifact(root: pathlib.Path, case_name: str, source_text: str) -> dict:
    module = PYTHON_SCIRH_MODULES[case_name]
    artifact = {
        "kind": "python",
        "subject": module.module_id,
        "module_id": module.module_id,
        "source_text": source_text,
        "filename": f"<experimental-python-translation:{case_name}>",
        "source_module": module,
        "preservation_contract": {
            "preservation_level": RECONSTRUCTION_EXPECTATIONS[case_name]["preservation_level"],
            "allowed_allocation_variation": False,
            "allowed_scheduling_variation": False,
            "fp_tolerance": 0.0,
        },
    }
    if case_name == "c_opaque_call":
        boundary_contract = load_json(
            root / "tests" / "python_importer" / "cases" / "c_opaque_call" / "opaque_boundary_contract.json"
        )
        host_spec = HostFunctionSpec(
            handler=lambda: {"status": "ok"},
            capabilities=("capability:foreign_api_ping",),
        )
        artifact["host_functions"] = {
            "foreign_api_ping": host_spec,
        }
        artifact["host_modules"] = {
            "foreign_api": {
                "ping": host_spec,
            }
        }
        artifact["boundary_contracts"] = boundary_contract
    return artifact


def run_experimental_python_translation(
    root: pathlib.Path,
    outputs: dict,
    *,
    equivalence_mode: str | None,
    observable_dimensions: list[str] | None,
    allow_contract_bounded: bool | None,
) -> list[dict]:
    reports = []
    supported_python_observables = set(default_observable_dimensions("python"))
    if observable_dimensions is not None:
        unsupported = sorted(set(observable_dimensions) - supported_python_observables)
        if unsupported:
            raise PipelineError(f"experimental Python translation does not admit observables {unsupported!r}")
    lane_inputs = {
        "a_basic_function": [{"function": "clamp_nonneg", "args": [value], "initial_memory": {}} for value in [-7, -1, 0, 1, 7]],
        "a_async_await": [{"function": "load_once", "args": [], "initial_memory": {}}],
        "b_direct_call": [{"function": "call_identity", "args": [value], "initial_memory": {}} for value in [-7, -1, 0, 1, 7]],
        "c_opaque_call": [{"function": "ping", "args": [], "initial_memory": {}}],
    }
    lane_observables = {
        "a_basic_function": ["returns", "traps_or_exceptions", "termination_kind"],
        "a_async_await": ["returns", "traps_or_exceptions", "termination_kind", "call_trace", "effect_trace"],
        "b_direct_call": ["returns", "traps_or_exceptions", "termination_kind", "call_trace"],
        "c_opaque_call": ["returns", "traps_or_exceptions", "termination_kind", "effect_trace", "capability_trace"],
    }

    for case_name, payload in outputs.get("reconstruction_reports", {}).items():
        module = PYTHON_SCIRH_MODULES[case_name]
        lowered = lower_supported_module(module)
        backend_artifact = build_experimental_python_backend_artifact(root, case_name, payload["source"])
        target_profile = RECONSTRUCTION_EXPECTATIONS[case_name]["profile"]
        backend_artifact["inputs"] = lane_inputs[case_name]
        report = validate_translation(
            lowered,
            backend_artifact,
            target_profile,
            equivalence_mode=equivalence_mode or "sequential_trace",
            observable_dimensions=observable_dimensions or lane_observables[case_name],
            allow_contract_bounded=allow_contract_bounded,
        )
        reports.append(report)
    return reports


def ensure_successful_outcomes(prefix: str, summary: dict[str, int], reports: list[dict] | None = None) -> None:
    failing = {outcome: count for outcome, count in summary.items() if not outcome.startswith("PASSED_")}
    if not failing:
        return
    print(f"[translation] {prefix} failed")
    if reports is not None:
        for report in reports:
            if report["outcome"].startswith("PASSED_"):
                continue
            print(f" - {report['subject']}: {report['outcome']}")
            for violation in report["violations"]:
                print(f"   * {violation}")
    raise SystemExit(1)


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.root).resolve() if args.root else ROOT
    observable_dimensions = parse_observable_set_arg(args.observable_set)

    if args.include_experimental_python and args.target_profile is not None:
        print(
            "[translation] experimental Python validation uses case-qualified reconstruction profiles; "
            "--target-profile is not valid with --include-experimental-python"
        )
        return 1

    translation_options = resolve_translation_validation_options(
        backend_kind="wasm",
        target_profile=args.target_profile,
        equivalence_mode=args.equivalence_mode,
        observable_dimensions=observable_dimensions,
        allow_contract_bounded=args.allow_contract_bounded,
    )

    try:
        failures, outputs = run_pipeline(root, translation_validation_options=translation_options)
    except PipelineError as exc:
        print(f"[translation] Python pipeline failed: {exc}")
        return 1
    if failures:
        print("[translation] Python pipeline translation validation failed")
        for failure in failures:
            print(f" - {failure}")
        return 1

    python_wasm_summary = summarize_wasm(outputs)
    ensure_successful_outcomes("Python Wasm lane", python_wasm_summary)
    print(
        "[translation] Python Wasm lane "
        f"profile={translation_options['target_profile']} "
        f"equivalence_mode={translation_options['equivalence_mode']} "
        f"allow_contract_bounded={translation_options['allow_contract_bounded']} "
        f"outcomes={python_wasm_summary}"
    )

    if args.include_experimental_python:
        experimental_reports = run_experimental_python_translation(
            root,
            outputs,
            equivalence_mode=args.equivalence_mode,
            observable_dimensions=observable_dimensions,
            allow_contract_bounded=args.allow_contract_bounded,
        )
        experimental_summary = summarize_reports(experimental_reports)
        ensure_successful_outcomes("Experimental Python lane", experimental_summary, experimental_reports)
        print(
            "[translation] Experimental Python lane "
            f"equivalence_mode={args.equivalence_mode or 'sequential_trace'} "
            f"outcomes={experimental_summary}"
        )

    if not args.require_rust:
        return 0

    try:
        rust_failures, rust_outputs = run_rust_pipeline(root, translation_validation_options=translation_options)
    except PipelineError as exc:
        print(f"[translation] Rust pipeline failed: {exc}")
        return 1
    if rust_failures:
        print("[translation] Rust pipeline translation validation failed")
        for failure in rust_failures:
            print(f" - {failure}")
        return 1

    rust_summary = summarize_wasm(rust_outputs)
    ensure_successful_outcomes("Rust Wasm lane", rust_summary)
    print(
        "[translation] Rust Wasm lane "
        f"profile={translation_options['target_profile']} "
        f"equivalence_mode={translation_options['equivalence_mode']} "
        f"allow_contract_bounded={translation_options['allow_contract_bounded']} "
        f"outcomes={rust_summary}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
