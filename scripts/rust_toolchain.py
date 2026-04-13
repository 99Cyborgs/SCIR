"""File: scripts/rust_toolchain.py
Purpose: Resolve a usable Rust toolchain for the repo's preserved optional Rust validation surfaces.
Role in system: This module centralizes Rust toolchain discovery so validation and pipeline scripts share one probe policy.
Key dependencies: rustup, cargo, rustc, tempfile, subprocess, and the local process environment.
Side effects: Spawns probe commands, creates a temporary Cargo project for compile validation, and caches the selected toolchain decision.
"""
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
    """Purpose: Snapshot the current environment before adding toolchain-specific overrides.

    Inputs:
      - None.
    Outputs:
      - dict[str, str] shallow copy of the current process environment.
    Side Effects:
      - None.
    Assumptions:
      - Probe helpers should start from the caller's real environment instead of constructing one from scratch.
    Failure Modes:
      - None.
    """
    return os.environ.copy()


def _candidate_env(toolchain: str | None) -> dict[str, str]:
    """Purpose: Build an environment for probing one specific Rust toolchain candidate.

    Inputs:
      - toolchain: str | None toolchain name to force via RUSTUP_TOOLCHAIN, or None for the active environment.
    Outputs:
      - dict[str, str] environment for subprocess probes.
    Side Effects:
      - None.
    Assumptions:
      - Toolchain selection is controlled only through the environment variable expected by rustup-aware tools.
    Failure Modes:
      - None.
    """
    env = _base_env()
    if toolchain:
        env["RUSTUP_TOOLCHAIN"] = toolchain
    return env


def _run_probe(command: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Purpose: Execute one Rust probe command with captured output for later diagnostics.

    Inputs:
      - command: list[str] argv for the probe.
      - env: dict[str, str] environment for the probe.
    Outputs:
      - subprocess.CompletedProcess[str] captured result.
    Side Effects:
      - Spawns a subprocess.
    Assumptions:
      - Probe commands should never raise directly because callers need the stderr or stdout text for the final reason string.
    Failure Modes:
      - Returns non-zero subprocess results instead of raising.
    """
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _probe_version(command: list[str], env: dict[str, str]) -> tuple[bool, str]:
    """Purpose: Check whether a version probe succeeded and extract the most relevant message text.

    Inputs:
      - command: list[str] version probe command such as cargo --version.
      - env: dict[str, str] environment for the probe.
    Outputs:
      - tuple[bool, str] success flag plus the probe message.
    Side Effects:
      - Spawns a subprocess through _run_probe.
    Assumptions:
      - Successful and failed probes both need a concise textual summary for downstream reasoning.
    Failure Modes:
      - None beyond _run_probe behavior.
    """
    result = _run_probe(command, env)
    message = (result.stdout or result.stderr).strip()
    return result.returncode == 0, message


def _summarize_error(text: str) -> str:
    """Purpose: Collapse multi-line probe output into the first non-empty diagnostic line.

    Inputs:
      - text: str stderr or stdout content from a failed probe.
    Outputs:
      - str concise failure summary.
    Side Effects:
      - None.
    Assumptions:
      - The first populated line is the most useful short explanation for operator-facing output.
    Failure Modes:
      - Returns a generic fallback when no non-empty line exists.
    """
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return "probe failed"


def _probe_compile(env: dict[str, str]) -> tuple[bool, str]:
    """Purpose: Verify that the candidate toolchain can actually compile a minimal Cargo project.

    Inputs:
      - env: dict[str, str] environment configured for the candidate toolchain.
    Outputs:
      - tuple[bool, str] success flag plus a short probe summary.
    Side Effects:
      - Creates a temporary Cargo package on disk.
      - Runs `cargo test --no-run` inside that package.
    Assumptions:
      - Version probes alone are insufficient; the repo wants a toolchain that can compile, not merely identify itself.
    Failure Modes:
      - Returns a summarized compilation failure instead of raising.
    """
    with tempfile.TemporaryDirectory(
        prefix="scir-rust-toolchain-probe-",
        ignore_cleanup_errors=True,
    ) as tmp:
        root = pathlib.Path(tmp)
        (root / "src").mkdir(parents=True, exist_ok=True)
        (root / "tests").mkdir(parents=True, exist_ok=True)
        # Build the smallest possible crate so toolchain resolution includes a
        # real compile step rather than trusting version banners alone.
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
    """Purpose: List rustup-managed toolchains that are available for fallback probing.

    Inputs:
      - None.
    Outputs:
      - list[str] installed rustup toolchain names.
    Side Effects:
      - Runs `rustup toolchain list` when rustup is available.
    Assumptions:
      - Fallback selection is only meaningful when rustup is installed.
    Failure Modes:
      - Returns an empty list when rustup is missing or the listing probe fails.
    """
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
    """Purpose: Determine the active Rust toolchain name seen by the current environment.

    Inputs:
      - None.
    Outputs:
      - str | None active toolchain name, or None when it cannot be determined.
    Side Effects:
      - Runs `rustup show active-toolchain` when rustup is available.
    Assumptions:
      - The environment variable fallback is the best available signal when rustup is absent or fails.
    Failure Modes:
      - Returns None when no active toolchain can be inferred.
    """
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
    """Purpose: Order the toolchain candidates that resolve_rust_toolchain should probe.

    Inputs:
      - None.
    Outputs:
      - list[tuple[str, str | None]] ordered `(selection_source, toolchain)` candidates.
    Side Effects:
      - Reads the active toolchain and installed fallback list.
    Assumptions:
      - On Windows, the preferred MSVC stable toolchain is the only meaningful fallback if the active one is unusable.
    Failure Modes:
      - None.
    """
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
    """Purpose: Select one usable Rust toolchain and explain why it was or was not accepted.

    Inputs:
      - None.
    Outputs:
      - dict[str, object] resolution payload describing availability, selection source, versions, and reason text.
    Side Effects:
      - Probes rustup, cargo, rustc, and compilation viability.
      - Caches the result for the lifetime of the Python process.
    Assumptions:
      - A toolchain is usable only when cargo and rustc are on PATH and a minimal Cargo compile succeeds.
    Failure Modes:
      - Returns an unavailable payload with detailed reasons instead of raising.
    """
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
    """Purpose: Produce the environment that downstream commands should use for the resolved toolchain.

    Inputs:
      - None.
    Outputs:
      - dict[str, str] environment copy with RUSTUP_TOOLCHAIN set when selection succeeded.
    Side Effects:
      - Reads the cached toolchain resolution result.
    Assumptions:
      - Downstream callers should not reimplement toolchain selection logic once a resolution has been computed.
    Failure Modes:
      - Returns the base environment unchanged when no usable toolchain was found.
    """
    resolution = resolve_rust_toolchain()
    env = _base_env()
    selected = resolution.get("selected_toolchain")
    if isinstance(selected, str) and selected:
        env["RUSTUP_TOOLCHAIN"] = selected
    return env
