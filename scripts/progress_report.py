from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STATUS_REL = "STATUS.md"
QUEUE_EXPORT_REL = "reports/exports/execution_queue.export.json"
CHECKPOINT_EXPORT_REL = "reports/exports/checkpoint_closeout.export.json"
BENCHMARK_RUNS_REL = "artifacts/benchmark_runs"


@dataclass
class GitState:
    branch: str | None
    head: str | None
    dirty: bool
    working_tree_status: list[str]


def run_git_stdout(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout


def load_json(root: Path, rel_path: str) -> dict[str, Any]:
    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def parse_status_markdown(root: Path) -> dict[str, Any]:
    lines = (root / STATUS_REL).read_text(encoding="utf-8").splitlines()
    summary_lines: list[str] = []
    blockers: list[str] = []
    section: str | None = None

    for line in lines:
        stripped = line.strip()
        if stripped == "## Summary":
            section = "summary"
            continue
        if stripped == "## Current blockers":
            section = "blockers"
            continue
        if stripped.startswith("## "):
            section = None
            continue
        if section == "summary":
            if stripped:
                summary_lines.append(stripped)
        elif section == "blockers" and stripped.startswith("- "):
            blockers.append(stripped[2:].strip())

    return {
        "summary": " ".join(summary_lines).strip(),
        "blockers": blockers,
    }


def collect_git_state(root: Path) -> GitState:
    try:
        branch = run_git_stdout(root, "branch", "--show-current").strip() or None
        head = run_git_stdout(root, "rev-parse", "HEAD").strip() or None
        status_lines = [line.rstrip() for line in run_git_stdout(root, "status", "--short").splitlines() if line.strip()]
    except ValueError:
        return GitState(branch=None, head=None, dirty=False, working_tree_status=[])
    return GitState(
        branch=branch,
        head=head,
        dirty=bool(status_lines),
        working_tree_status=status_lines,
    )


def parse_iso_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.min
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_benchmark_report(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    report["_path"] = str(path)
    report["_generated_at"] = report.get("generated_at")
    contamination_path = path.with_name("contamination_report.json")
    if contamination_path.exists():
        contamination = json.loads(contamination_path.read_text(encoding="utf-8"))
        report["_contamination_flag_count"] = (
            len(contamination.get("duplicates", []))
            + len(contamination.get("near_duplicates", []))
            + len(contamination.get("leakage_flags", []))
        )
    else:
        report["_contamination_flag_count"] = None
    return report


def find_latest_benchmark_reports(root: Path) -> dict[str, dict[str, Any] | None]:
    benchmark_root = root / BENCHMARK_RUNS_REL
    if not benchmark_root.exists():
        return {"latest_any": None, "latest_claim": None}

    reports: list[dict[str, Any]] = []
    for report_path in benchmark_root.glob("*/benchmark_report.json"):
        try:
            reports.append(load_benchmark_report(report_path))
        except json.JSONDecodeError:
            continue

    if not reports:
        return {"latest_any": None, "latest_claim": None}

    reports.sort(key=lambda report: parse_iso_timestamp(report.get("_generated_at")), reverse=True)
    latest_any = reports[0]
    latest_claim = next((report for report in reports if report.get("claim_mode") == "claim"), None)
    return {"latest_any": latest_any, "latest_claim": latest_claim}


def check_queue_sync(root: Path) -> dict[str, Any]:
    script_path = root / "scripts" / "build_execution_queue.py"
    if not script_path.exists():
        return {
            "checked": False,
            "status": "unavailable",
            "output": [],
        }

    completed = subprocess.run(
        [sys.executable, str(script_path), "--mode", "check"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    output_lines = [
        line
        for line in (completed.stdout.splitlines() + completed.stderr.splitlines())
        if line.strip()
    ]
    return {
        "checked": True,
        "status": "passed" if completed.returncode == 0 else "failed",
        "output": output_lines,
    }


def summarize_benchmark(report: dict[str, Any] | None) -> dict[str, Any] | None:
    if report is None:
        return None
    claim_gate = report.get("claim_gate", {})
    return {
        "path": report["_path"],
        "run_id": report.get("run_id"),
        "generated_at": report.get("generated_at"),
        "claim_mode": report.get("claim_mode"),
        "claim_class": report.get("claim_class"),
        "evidence_class": report.get("evidence_class"),
        "tracks": report.get("tracks"),
        "claim_gate_passed": claim_gate.get("passed"),
        "ai_thesis_status": claim_gate.get("ai_thesis_status"),
        "explicit_lcr": report.get("explicit_representation_metrics", {}).get("LCR"),
        "compressed_lcr": report.get("compressed_representation_metrics", {}).get("LCR_scirhc"),
        "typed_ast_baseline_lcr": _extract_typed_ast_baseline(report),
        "contamination_flag_count": report.get("_contamination_flag_count"),
    }


def _extract_typed_ast_baseline(report: dict[str, Any]) -> float | None:
    for condition in report.get("claim_gate", {}).get("evaluated_conditions", []):
        if condition.get("baseline_name") == "typed-AST":
            return condition.get("baseline_value")
    return None


def build_report(root: Path, *, include_sync_check: bool) -> dict[str, Any]:
    status = parse_status_markdown(root)
    queue_export = load_json(root, QUEUE_EXPORT_REL)
    checkpoint_export = load_json(root, CHECKPOINT_EXPORT_REL)
    benchmark_reports = find_latest_benchmark_reports(root)
    git_state = collect_git_state(root)

    report = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "repository": {
            "root": str(root),
            "git": asdict(git_state),
        },
        "status": status,
        "queue": {
            "active_milestone": queue_export.get("active_milestone"),
            "queue_state": queue_export.get("current_queue_state", {}).get("queue_state"),
            "last_completed": queue_export.get("current_queue_state", {}).get("last_completed"),
            "next_action": queue_export.get("next_action"),
            "no_successor_item_reason": queue_export.get("current_queue_state", {}).get("no_successor_item_reason"),
        },
        "checkpoint": {
            "generated_at": checkpoint_export.get("generated_at"),
            "validation_state": checkpoint_export.get("validation_state"),
            "validation_commands": checkpoint_export.get("validation_context", {}).get("validation_commands", []),
            "recorded_head_commit_hash": checkpoint_export.get("validation_context", {}).get("head_commit_hash"),
            "recorded_working_tree_dirty": checkpoint_export.get("validation_context", {}).get("working_tree_dirty"),
            "recorded_working_tree_status": checkpoint_export.get("validation_context", {}).get("working_tree_status", []),
        },
        "benchmarks": {
            "latest_any": summarize_benchmark(benchmark_reports["latest_any"]),
            "latest_claim": summarize_benchmark(benchmark_reports["latest_claim"]),
        },
    }
    if include_sync_check:
        report["queue_sync_check"] = check_queue_sync(root)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# SCIR Progress Report")
    lines.append("")
    lines.append(f"- generated_at: `{report['generated_at']}`")
    lines.append(f"- repo_root: `{report['repository']['root']}`")

    git_state = report["repository"]["git"]
    lines.append(f"- branch: `{git_state['branch'] or 'unknown'}`")
    lines.append(f"- head: `{git_state['head'] or 'unknown'}`")
    lines.append(f"- working_tree_dirty: `{str(git_state['dirty']).lower()}`")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append(report["status"]["summary"] or "No summary available.")
    lines.append("")

    lines.append("## Queue")
    lines.append("")
    queue = report["queue"]
    lines.append(f"- active milestone: `{queue['active_milestone']}`")
    lines.append(f"- queue state: `{queue['queue_state']}`")
    last_completed = queue["last_completed"] or {}
    lines.append(
        f"- last completed: `{last_completed.get('queue_id', 'unknown')}`"
        + (f" ({last_completed.get('label')})" if last_completed.get("label") else "")
    )
    if queue["next_action"] is None:
        lines.append("- next action: `none`")
    else:
        lines.append(
            f"- next action: `{queue['next_action'].get('queue_id')}` ({queue['next_action'].get('title')})"
        )
    if queue.get("no_successor_item_reason"):
        lines.append(f"- no successor rationale: {queue['no_successor_item_reason']}")
    lines.append("")

    lines.append("## Validation")
    lines.append("")
    checkpoint = report["checkpoint"]
    validation_state = checkpoint.get("validation_state") or {}
    lines.append(f"- checkpoint generated_at: `{checkpoint.get('generated_at')}`")
    lines.append(f"- checkpoint validation status: `{validation_state.get('status')}`")
    lines.append(
        f"- checkpoint synchronized_with_working_tree: `{str(validation_state.get('synchronized_with_working_tree')).lower()}`"
    )
    if "queue_sync_check" in report:
        lines.append(f"- current queue/export sync check: `{report['queue_sync_check']['status']}`")
        for output_line in report["queue_sync_check"]["output"]:
            lines.append(f"  - {output_line}")
    if checkpoint.get("validation_commands"):
        lines.append("- recorded validation commands:")
        for command in checkpoint["validation_commands"]:
            lines.append(f"  - `{command}`")
    lines.append("")

    lines.append("## Benchmarks")
    lines.append("")
    latest_claim = report["benchmarks"]["latest_claim"]
    latest_any = report["benchmarks"]["latest_any"]
    if latest_claim is None:
        lines.append("- latest claim bundle: `none found`")
    else:
        lines.append(f"- latest claim bundle: `{latest_claim['run_id']}`")
        lines.append(f"- claim path: `{latest_claim['path']}`")
        lines.append(f"- claim class: `{latest_claim['claim_class']}`")
        lines.append(f"- evidence class: `{latest_claim['evidence_class']}`")
        lines.append(f"- tracks: `{latest_claim['tracks']}`")
        lines.append(f"- claim gate passed: `{str(latest_claim['claim_gate_passed']).lower()}`")
        lines.append(f"- explicit LCR: `{latest_claim['explicit_lcr']}`")
        lines.append(f"- compressed LCR: `{latest_claim['compressed_lcr']}`")
        lines.append(f"- typed-AST baseline LCR: `{latest_claim['typed_ast_baseline_lcr']}`")
        lines.append(f"- contamination flags: `{latest_claim['contamination_flag_count']}`")
    if latest_any is not None and (latest_claim is None or latest_any["run_id"] != latest_claim["run_id"]):
        lines.append(f"- latest benchmark activity: `{latest_any['run_id']}` ({latest_any['claim_mode']})")
    lines.append("")

    lines.append("## Blockers")
    lines.append("")
    blockers = report["status"]["blockers"]
    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none listed")
    lines.append("")

    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an automated SCIR progress report.")
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root to inspect. Defaults to the current SCIR repository.",
    )
    parser.add_argument(
        "--skip-queue-sync-check",
        action="store_true",
        help="Skip the live execution-queue export synchronization check.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    root = Path(args.repo_root).resolve()
    report = build_report(root, include_sync_check=not args.skip_queue_sync_check)

    if args.format == "json":
        sys.stdout.write(json.dumps(report, indent=2) + "\n")
    else:
        sys.stdout.write(render_markdown(report))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
