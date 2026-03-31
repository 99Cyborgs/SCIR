from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache


PREFERRED_WINDOWS_TOOLCHAIN = "stable-x86_64-pc-windows-msvc"


def _base_env() -> dict[str, str]:
    return os.environ.copy()


def _candidate_env(toolchain: str | None) -> dict[str, str]:
    env = _base_env()
    if toolchain:
        env["RUSTUP_TOOLCHAIN"] = toolchain
    return env


def _run_probe(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _probe_version(command: list[str], env: dict[str, str]) -> tuple[bool, str]:
    result = _run_probe(command, env)
    message = (result.stdout or result.stderr).strip()
    return result.returncode == 0, message


def _summarize_error(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return "probe failed"


def _probe_compile(env: dict[str, str]) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(
        prefix="scir-rust-toolchain-probe-",
        ignore_cleanup_errors=True,
    ) as tmp:
        root = pathlib.Path(tmp)
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "tests").mkdir(parents=True, exist_ok=True)
        (root / "src" / "lib.rs").write_text(
            "pub fn ping() -> i32 {\n    1\n}\n",
            encoding="utf-8",
        )
        (root / "tests" / "smoke.rs").write_text(
            "use rust_probe::ping;\n\n#[test]\nfn smoke() {\n    assert_eq!(ping(), 1);\n}\n",
            encoding="utf-8",
        )
        (root / "Cargo.toml").write_text(
            "[package]\nname = \"rust_probe\"\nversion = \"0.1.0\"\nedition = \"2021\"\n\n[lib]\npath = \"src/lib.rs\"\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            ["cargo", "test", "--quiet", "--no-run"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        if result.returncode == 0:
            return True, "cargo test --no-run succeeded"
        return False, _summarize_error(result.stderr or result.stdout)


def _list_installed_toolchains() -> list[str]:
    if shutil.which("rustup") is None:
        return []
    result = subprocess.run(
        ["rustup", "toolchain", "list"],
        capture_output=True,
        text=True,
        check=False,
        env=_base_env(),
    )
    if result.returncode != 0:
        return []
    toolchains = []
    for line in result.stdout.splitlines():
        name = line.split("(", 1)[0].strip()
        if name:
            toolchains.append(name)
    return toolchains


def _active_toolchain_name() -> str | None:
    if shutil.which("rustup") is None:
        return os.environ.get("RUSTUP_TOOLCHAIN")
    result = subprocess.run(
        ["rustup", "show", "active-toolchain"],
        capture_output=True,
        text=True,
        check=False,
        env=_base_env(),
    )
    if result.returncode != 0:
        return os.environ.get("RUSTUP_TOOLCHAIN")
    line = result.stdout.strip()
    if not line:
        return os.environ.get("RUSTUP_TOOLCHAIN")
    return line.split()[0]


def _candidate_toolchains() -> list[tuple[str, str | None]]:
    active = _active_toolchain_name()
    candidates: list[tuple[str, str | None]] = [("active", None)]
    if (
        sys.platform.startswith("win")
        and PREFERRED_WINDOWS_TOOLCHAIN != active
        and PREFERRED_WINDOWS_TOOLCHAIN in _list_installed_toolchains()
    ):
        candidates.append(("fallback", PREFERRED_WINDOWS_TOOLCHAIN))
    return candidates


@lru_cache(maxsize=1)
def resolve_rust_toolchain() -> dict[str, object]:
    rustup_available = shutil.which("rustup") is not None
    cargo_on_path = shutil.which("cargo") is not None
    rustc_on_path = shutil.which("rustc") is not None

    if not cargo_on_path or not rustc_on_path:
        missing = [name for name, present in (("cargo", cargo_on_path), ("rustc", rustc_on_path)) if not present]
        return {
            "available": False,
            "selected_toolchain": None,
            "selection_source": None,
            "reason": f"missing executables: {', '.join(missing)}",
            "cargo_version": None,
            "rustc_version": None,
            "rustup_available": rustup_available,
        }

    probe_failures = []
    for selection_source, toolchain in _candidate_toolchains():
        env = _candidate_env(toolchain)
        cargo_ok, cargo_message = _probe_version(["cargo", "--version"], env)
        rustc_ok, rustc_message = _probe_version(["rustc", "--version"], env)
        compile_ok, compile_message = _probe_compile(env) if cargo_ok and rustc_ok else (False, "version probe failed")
        if cargo_ok and rustc_ok and compile_ok:
            selected = toolchain or _active_toolchain_name() or "active"
            reason = (
                "active toolchain is usable"
                if toolchain is None
                else f"active toolchain unusable; using fallback {toolchain}"
            )
            return {
                "available": True,
                "selected_toolchain": selected,
                "selection_source": selection_source,
                "reason": reason,
                "cargo_version": cargo_message,
                "rustc_version": rustc_message,
                "rustup_available": rustup_available,
            }
        label = toolchain or (_active_toolchain_name() or "active")
        failure_bits = []
        if not cargo_ok:
            failure_bits.append(f"cargo: {cargo_message or 'probe failed'}")
        if not rustc_ok:
            failure_bits.append(f"rustc: {rustc_message or 'probe failed'}")
        if cargo_ok and rustc_ok and not compile_ok:
            failure_bits.append(f"compile: {compile_message}")
        probe_failures.append(f"{label} ({selection_source}) -> {'; '.join(failure_bits)}")

    return {
        "available": False,
        "selected_toolchain": None,
        "selection_source": None,
        "reason": "; ".join(probe_failures) if probe_failures else "no usable Rust toolchain found",
        "cargo_version": None,
        "rustc_version": None,
        "rustup_available": rustup_available,
    }


def rust_toolchain_env() -> dict[str, str]:
    resolution = resolve_rust_toolchain()
    env = _base_env()
    selected = resolution.get("selected_toolchain")
    if isinstance(selected, str) and selected:
        env["RUSTUP_TOOLCHAIN"] = selected
    return env
