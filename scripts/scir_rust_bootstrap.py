#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import dataclass

from scir_h_bootstrap_model import (
    AwaitExpr,
    CallExpr,
    FieldPlace,
    FunctionDecl,
    IfStmt,
    ImportDecl,
    IntExpr,
    IntrinsicExpr,
    Module,
    NameExpr,
    Param,
    PlaceExpr,
    ReturnStmt,
    SetStmt,
    TypeDecl,
    RecordType,
    FieldType,
    VarDecl,
    format_module,
    normalize_module,
)


SPEC_VERSION = "v0.1-draft"
VALIDATOR_NAME = "rust-bootstrap-importer"

CARGO_TOML = """[package]
name = "{crate_name}"
version = "0.1.0"
edition = "2021"

[lib]
path = "src/lib.rs"
"""

SOURCE_TEXTS = {
    "a_mut_local": """pub fn clamp_nonneg(x: i32) -> i32 {
    let mut y = x;
    if y < 0 {
        y = 0;
    }
    y
}
""",
    "a_struct_field_borrow_mut": """pub struct Counter {
    pub value: i32,
}

pub fn clamp_counter(counter: &mut Counter) -> i32 {
    if counter.value < 0 {
        counter.value = 0;
    }
    counter.value
}
""",
    "a_async_await": """async fn fetch_value() -> i32 {
    1
}

pub async fn load_once() -> i32 {
    fetch_value().await
}
""",
    "c_unsafe_call": """unsafe fn unsafe_ping() -> i32 {
    7
}

pub fn call_unsafe_ping() -> i32 {
    unsafe { unsafe_ping() }
}
""",
    "d_proc_macro": """#[derive(ExampleMacro)]
pub struct MacroDriven;
""",
    "d_self_ref_pin": """use std::marker::PhantomPinned;
use std::pin::Pin;

pub struct SelfRef {
    pub data: String,
    pub ptr: *const String,
    pub _pin: PhantomPinned,
}

pub fn make_self_ref(_data: String) -> Pin<Box<SelfRef>> {
    unimplemented!()
}
""",
}

TEST_TEXTS = {
    "a_mut_local": """use a_mut_local::clamp_nonneg;

#[test]
fn smoke() {
    assert_eq!(clamp_nonneg(-3), 0);
    assert_eq!(clamp_nonneg(4), 4);
}
""",
    "a_struct_field_borrow_mut": """use a_struct_field_borrow_mut::{clamp_counter, Counter};

#[test]
fn smoke() {
    let mut counter = Counter { value: -5 };
    assert_eq!(clamp_counter(&mut counter), 0);
    assert_eq!(counter.value, 0);
}
""",
    "a_async_await": """use a_async_await::load_once;
use std::future::Future;
use std::pin::Pin;
use std::task::{Context, Poll, RawWaker, RawWakerVTable, Waker};

fn noop_raw_waker() -> RawWaker {
    fn clone(_: *const ()) -> RawWaker {
        noop_raw_waker()
    }
    fn wake(_: *const ()) {}
    fn wake_by_ref(_: *const ()) {}
    fn drop(_: *const ()) {}
    RawWaker::new(
        std::ptr::null(),
        &RawWakerVTable::new(clone, wake, wake_by_ref, drop),
    )
}

fn block_on<F: Future>(future: F) -> F::Output {
    let waker = unsafe { Waker::from_raw(noop_raw_waker()) };
    let mut future = Pin::from(Box::new(future));
    loop {
        let mut context = Context::from_waker(&waker);
        match Future::poll(future.as_mut(), &mut context) {
            Poll::Ready(value) => return value,
            Poll::Pending => std::thread::yield_now(),
        }
    }
}

#[test]
fn smoke() {
    assert_eq!(block_on(load_once()), 1);
}
""",
}


class ImporterError(Exception):
    pass


@dataclass(frozen=True)
class Bundle:
    case_name: str
    files: dict[str, str]


CASE_CONFIG = {
    "a_mut_local": {
        "profiles": ["R"],
        "tier": "A",
        "dependencies": ["rust:std"],
        "exports": ["clamp_nonneg"],
        "status": "pass",
        "feature_items": [
            {
                "feature": "plain free function",
                "tier": "A",
                "rationale": "A direct Rust free function maps into the compact canonical SCIR-H function form.",
            },
            {
                "feature": "mutable local reassignment",
                "tier": "A",
                "rationale": "A Rust mutable local lowers into explicit var and set operations.",
            },
            {
                "feature": "scalar branch on intrinsic comparison",
                "tier": "A",
                "rationale": "The branch condition maps to the canonical lt intrinsic instead of a language-specific operator helper.",
            },
        ],
        "diagnostics": [],
        "opaque_boundary_contract": None,
    },
    "a_struct_field_borrow_mut": {
        "profiles": ["R"],
        "tier": "A",
        "dependencies": ["rust:std"],
        "exports": ["Counter", "clamp_counter"],
        "status": "pass",
        "feature_items": [
            {
                "feature": "named record type declaration",
                "tier": "A",
                "rationale": "A simple Rust struct lowers to a named record type declaration in the bootstrap slice.",
            },
            {
                "feature": "borrow_mut parameter",
                "tier": "A",
                "rationale": "A borrowed mutable parameter remains explicit through borrow_mut<T> in canonical SCIR-H.",
            },
            {
                "feature": "record field place read and write",
                "tier": "A",
                "rationale": "The bootstrap Rust slice uses explicit field places rather than hidden projection semantics.",
            },
        ],
        "diagnostics": [],
        "opaque_boundary_contract": None,
    },
    "a_async_await": {
        "profiles": ["R"],
        "tier": "A",
        "dependencies": ["rust:std"],
        "exports": ["load_once"],
        "status": "pass",
        "feature_items": [
            {
                "feature": "simple async function",
                "tier": "A",
                "rationale": "A structured async Rust function stays explicit in canonical SCIR-H.",
            },
            {
                "feature": "single await point",
                "tier": "A",
                "rationale": "A direct await lowers into the same explicit await expression used by the Python bootstrap slice.",
            },
        ],
        "diagnostics": [],
        "opaque_boundary_contract": None,
    },
    "c_unsafe_call": {
        "profiles": ["N"],
        "tier": "C",
        "dependencies": ["rust:std"],
        "exports": ["call_unsafe_ping"],
        "status": "warn",
        "feature_items": [
            {
                "feature": "plain free function wrapper",
                "tier": "A",
                "rationale": "The outer function structure itself remains regular.",
            },
            {
                "feature": "explicit unsafe call boundary",
                "tier": "C",
                "rationale": "The call into unsafe_ping remains bounded only by an explicit unsafe opaque boundary contract.",
                "fallback": "opaque_call",
            },
        ],
        "diagnostics": [
            {
                "code": "RS-C001",
                "severity": "warn",
                "message": "unsafe_ping remains an explicit Tier C opaque boundary in the Rust bootstrap slice.",
                "location": "input/src/lib.rs:6",
            }
        ],
        "opaque_boundary_contract": {
            "boundary_id": "fixture.rust_importer.c_unsafe_call.boundary.unsafe_ping",
            "kind": "opaque_call",
            "signature": "opaque.call unsafe_ping() -> int !opaque,unsafe",
            "effects": ["opaque", "unsafe"],
            "ownership_transfer": {
                "inbound": [],
                "outbound": ["int"],
            },
            "capabilities": [],
            "determinism": "unknown",
            "audit_note": "unsafe_ping is treated as a Tier C unsafe boundary rather than modeled Rust semantics in Phase 6A.",
        },
    },
    "d_proc_macro": {
        "profiles": ["R", "N"],
        "tier": "D",
        "dependencies": ["rust:std"],
        "exports": ["MacroDriven"],
        "status": "fail",
        "feature_items": [
            {
                "feature": "proc macro semantics",
                "tier": "D",
                "rationale": "Proc macro semantics are explicitly outside the first executable Rust bootstrap slice.",
                "fallback": "reject",
            }
        ],
        "diagnostics": [
            {
                "code": "RS-D001",
                "severity": "error",
                "message": "Proc macro semantics are rejected in the Rust bootstrap fixture subset.",
                "location": "input/src/lib.rs:1",
            }
        ],
        "opaque_boundary_contract": None,
    },
    "d_self_ref_pin": {
        "profiles": ["R", "N"],
        "tier": "D",
        "dependencies": ["rust:std"],
        "exports": ["SelfRef", "make_self_ref"],
        "status": "fail",
        "feature_items": [
            {
                "feature": "self-referential pin pattern",
                "tier": "D",
                "rationale": "Self-referential pin and alias-sensitive patterns are explicitly rejected in Phase 6A.",
                "fallback": "reject",
            }
        ],
        "diagnostics": [
            {
                "code": "RS-D002",
                "severity": "error",
                "message": "Self-referential pin patterns are rejected in the Rust bootstrap fixture subset.",
                "location": "input/src/lib.rs:1",
            }
        ],
        "opaque_boundary_contract": None,
    },
}


def build_supported_module(case_name: str) -> Module:
    module_id = f"fixture.rust_importer.{case_name}"
    if case_name == "a_mut_local":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="clamp_nonneg",
                        params=(Param("x", "int"),),
                        return_type="int",
                        effects=("write",),
                        body=(
                            VarDecl("y", "int", NameExpr("x")),
                            IfStmt(
                                condition=IntrinsicExpr("lt", (NameExpr("y"), IntExpr(0))),
                                then_body=(SetStmt("y", IntExpr(0)),),
                                else_body=(),
                            ),
                            ReturnStmt(NameExpr("y")),
                        ),
                    ),
                ),
            )
        )
    if case_name == "a_struct_field_borrow_mut":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(
                    TypeDecl(
                        name="Counter",
                        type_expr=RecordType((FieldType("value", "int"),)),
                    ),
                ),
                functions=(
                    FunctionDecl(
                        name="clamp_counter",
                        params=(Param("counter", "borrow_mut<Counter>"),),
                        return_type="int",
                        effects=("write",),
                        body=(
                            IfStmt(
                                condition=IntrinsicExpr(
                                    "lt",
                                    (PlaceExpr(FieldPlace("counter", "value")), IntExpr(0)),
                                ),
                                then_body=(
                                    SetStmt(FieldPlace("counter", "value"), IntExpr(0)),
                                ),
                                else_body=(),
                            ),
                            ReturnStmt(PlaceExpr(FieldPlace("counter", "value"))),
                        ),
                    ),
                ),
            )
        )
    if case_name == "a_async_await":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="fetch_value",
                        params=(),
                        return_type="int",
                        effects=(),
                        body=(ReturnStmt(IntExpr(1)),),
                        is_async=True,
                    ),
                    FunctionDecl(
                        name="load_once",
                        params=(),
                        return_type="int",
                        effects=("await",),
                        body=(ReturnStmt(AwaitExpr(CallExpr("fetch_value", ()))),),
                        is_async=True,
                    ),
                ),
            )
        )
    if case_name == "c_unsafe_call":
        return normalize_module(
            Module(
                module_id=module_id,
                imports=(ImportDecl("sym", "unsafe_ping", "rust:unsafe_ping"),),
                type_decls=(),
                functions=(
                    FunctionDecl(
                        name="call_unsafe_ping",
                        params=(),
                        return_type="int",
                        effects=("opaque", "unsafe"),
                        body=(ReturnStmt(CallExpr("unsafe_ping", ())),),
                    ),
                ),
            )
        )
    raise ImporterError(f"{case_name}: no supported module shape")


SCIRH_MODULES = {
    case_name: build_supported_module(case_name)
    for case_name in ("a_mut_local", "a_struct_field_borrow_mut", "a_async_await", "c_unsafe_call")
}


def make_summary(items: list[dict[str, str]]) -> dict[str, int]:
    summary = {"A": 0, "B": 0, "C": 0, "D": 0}
    for item in items:
        summary[item["tier"]] += 1
    return summary


def derive_case_name(source_path: pathlib.Path) -> str:
    if source_path.name != "lib.rs":
        raise ImporterError(f"{source_path}: expected a crate source file named lib.rs")
    try:
        case_name = source_path.parents[2].name
    except IndexError as exc:
        raise ImporterError(f"{source_path}: not part of the fixed Rust bootstrap corpus") from exc
    if case_name not in CASE_CONFIG:
        raise ImporterError(f"{source_path}: not part of the fixed Rust bootstrap corpus")
    return case_name


def relative_source_path(root: pathlib.Path, source_path: pathlib.Path) -> str:
    try:
        return source_path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ImporterError(f"{source_path}: source must live under {root}") from exc


def expected_cargo_text(case_name: str) -> str:
    return CARGO_TOML.format(crate_name=case_name)


def build_bundle(root: pathlib.Path, source_path: pathlib.Path) -> Bundle:
    source_text = source_path.read_text(encoding="utf-8")
    case_name = derive_case_name(source_path)
    if source_text != SOURCE_TEXTS[case_name]:
        raise ImporterError(f"{source_path}: source does not match the checked-in bootstrap fixture text")

    cargo_path = source_path.parents[1] / "Cargo.toml"
    if not cargo_path.exists():
        raise ImporterError(f"{cargo_path}: missing crate manifest for Rust bootstrap case")
    cargo_text = cargo_path.read_text(encoding="utf-8")
    if cargo_text != expected_cargo_text(case_name):
        raise ImporterError(f"{cargo_path}: crate manifest does not match the checked-in bootstrap fixture text")

    test_path = source_path.parents[1] / "tests" / "smoke.rs"
    if case_name in TEST_TEXTS:
        if not test_path.exists():
            raise ImporterError(f"{test_path}: missing smoke test for supported Rust bootstrap case")
        if test_path.read_text(encoding="utf-8") != TEST_TEXTS[case_name]:
            raise ImporterError(f"{test_path}: smoke test does not match the checked-in bootstrap fixture text")
    elif test_path.exists():
        raise ImporterError(f"{test_path}: unexpected smoke test for unsupported Rust bootstrap case")

    source_rel = relative_source_path(root, source_path)
    module_id = f"fixture.rust_importer.{case_name}"
    config = CASE_CONFIG[case_name]
    summary = make_summary(config["feature_items"])
    validation_slug = case_name.replace("_", "-")

    module_manifest = {
        "module_id": module_id,
        "layer": "scir_h",
        "source_language": "rust",
        "source_path": source_rel,
        "declared_profiles": config["profiles"],
        "declared_tier": config["tier"],
        "dependencies": config["dependencies"],
        "exports": config["exports"],
        "opaque_boundary_count": 1 if config["opaque_boundary_contract"] else 0,
    }
    feature_tier_report = {
        "report_id": f"fixture-feature-tier-{validation_slug}",
        "subject": module_id,
        "source_language": "rust",
        "summary": summary,
        "items": config["feature_items"],
    }
    validation_report = {
        "report_id": f"fixture-validation-{validation_slug}",
        "artifact": module_id,
        "layer": "scir_h",
        "validator": VALIDATOR_NAME,
        "spec_version": SPEC_VERSION,
        "status": config["status"],
        "diagnostics": config["diagnostics"],
    }

    files = {
        "module_manifest.json": json.dumps(module_manifest, indent=2) + "\n",
        "feature_tier_report.json": json.dumps(feature_tier_report, indent=2) + "\n",
        "validation_report.json": json.dumps(validation_report, indent=2) + "\n",
    }
    if case_name in SCIRH_MODULES:
        files["expected.scirh"] = format_module(SCIRH_MODULES[case_name])
    opaque_contract = config["opaque_boundary_contract"]
    if opaque_contract is not None:
        files["opaque_boundary_contract.json"] = json.dumps(opaque_contract, indent=2) + "\n"
    return Bundle(case_name=case_name, files=files)


def write_bundle(bundle: Bundle, output_dir: pathlib.Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, contents in bundle.files.items():
        (output_dir / name).write_text(contents, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--root")
    return parser.parse_args()


def main():
    args = parse_args()
    root = pathlib.Path(args.root).resolve() if args.root else pathlib.Path(__file__).resolve().parents[1]
    source_path = pathlib.Path(args.source).resolve()
    output_dir = pathlib.Path(args.output_dir).resolve()

    try:
        bundle = build_bundle(root, source_path)
    except ImporterError as exc:
        print(f"[import] failed: {exc}")
        sys.exit(1)

    write_bundle(bundle, output_dir)
    print(f"[import] wrote {len(bundle.files)} artifact files for {bundle.case_name} to {output_dir}")
    sys.exit(0)


if __name__ == "__main__":
    main()
