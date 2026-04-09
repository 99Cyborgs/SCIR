from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_FILES = [
    "EXECUTION_QUEUE.md",
    "IMPLEMENTATION_PLAN.md",
    "OPEN_QUESTIONS.md",
    "STATUS.md",
    "DECISION_REGISTER.md",
    "VALIDATION.md",
    "VALIDATION_STRATEGY.md",
    "plans/2026-04-01-mvp-narrowing-and-contract-hardening.md",
    "plans/2026-04-07-q-06-011-lock-track-c-provenance-note-overwrite-semantics.md",
    "plans/2026-04-07-q-06-012-checkpoint-integrity-and-governance-evidence-binding.md",
    "reports/exports/decision_register.export.json",
    "reports/exports/execution_queue.export.json",
    "reports/exports/checkpoint_closeout.export.json",
    "schemas/execution_queue.schema.json",
    "schemas/decision_register.schema.json",
    "schemas/checkpoint_closeout.schema.json",
    "scripts/build_execution_queue.py",
    "scripts/progress_report.py",
    "scripts/validate_repo_contracts.py",
]


def run_cmd(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


class ProgressReportTests(unittest.TestCase):
    def make_repo_copy(self) -> Path:
        temp_root = Path(tempfile.mkdtemp(prefix="scir_progress_report_"))
        repo_root = temp_root / "repo"
        repo_root.mkdir(parents=True, exist_ok=True)
        for rel_path in FIXTURE_FILES:
            src = ROOT / rel_path
            dst = repo_root / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

        self._write_benchmark_fixture(repo_root)

        for command in (
            ("git", "init"),
            ("git", "config", "user.name", "Codex"),
            ("git", "config", "user.email", "codex@example.com"),
            ("git", "add", "."),
            ("git", "commit", "-m", "baseline"),
        ):
            completed = run_cmd(repo_root, *command)
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"{command!r} failed: {completed.stdout}\n{completed.stderr}",
            )

        rewrite = run_cmd(repo_root, sys.executable, "scripts/build_execution_queue.py", "--mode", "write")
        self.assertEqual(rewrite.returncode, 0, msg=f"{rewrite.stdout}\n{rewrite.stderr}")
        return repo_root

    def _write_benchmark_fixture(self, repo_root: Path) -> None:
        benchmark_root = repo_root / "artifacts" / "benchmark_runs"
        claim_dir = benchmark_root / "python-proof-loop-full-20260408T232025Z"
        smoke_dir = benchmark_root / "python-proof-loop-full-20260408T233646Z"
        claim_dir.mkdir(parents=True, exist_ok=True)
        smoke_dir.mkdir(parents=True, exist_ok=True)

        claim_report = {
            "run_id": "python-proof-loop-full-20260408T232025Z",
            "generated_at": "2026-04-08T23:20:25.615658+00:00",
            "claim_mode": "claim",
            "claim_class": "LEXICAL_COMPRESSION_ONLY",
            "evidence_class": ["scirhc_lcr_vs_ast"],
            "tracks": {"A": "pass", "B": "pass"},
            "explicit_representation_metrics": {"LCR": 1.6569},
            "compressed_representation_metrics": {"LCR_scirhc": 1.8198},
            "claim_gate": {
                "passed": True,
                "ai_thesis_status": "supported",
                "evaluated_conditions": [
                    {
                        "baseline_name": "typed-AST",
                        "baseline_value": 6.7672,
                    }
                ],
            },
        }
        smoke_report = {
            "run_id": "python-proof-loop-full-20260408T233646Z",
            "generated_at": "2026-04-08T23:36:46.695781+00:00",
            "claim_mode": "smoke",
            "claim_class": "LEXICAL_COMPRESSION_ONLY",
            "evidence_class": ["scirhc_lcr_vs_ast"],
            "tracks": {"A": "pass", "B": "pass"},
            "explicit_representation_metrics": {"LCR": 1.6569},
            "compressed_representation_metrics": {"LCR_scirhc": 1.8198},
            "claim_gate": {
                "passed": True,
                "ai_thesis_status": "supported",
                "evaluated_conditions": [
                    {
                        "baseline_name": "typed-AST",
                        "baseline_value": 6.7672,
                    }
                ],
            },
        }
        contamination = {
            "duplicates": [],
            "near_duplicates": [],
            "leakage_flags": [],
        }

        (claim_dir / "benchmark_report.json").write_text(json.dumps(claim_report, indent=2) + "\n", encoding="utf-8")
        (claim_dir / "contamination_report.json").write_text(json.dumps(contamination, indent=2) + "\n", encoding="utf-8")
        (smoke_dir / "benchmark_report.json").write_text(json.dumps(smoke_report, indent=2) + "\n", encoding="utf-8")
        (smoke_dir / "contamination_report.json").write_text(json.dumps(contamination, indent=2) + "\n", encoding="utf-8")

    def test_markdown_report_includes_queue_validation_and_benchmarks(self) -> None:
        repo_root = self.make_repo_copy()

        completed = run_cmd(
            repo_root,
            sys.executable,
            "scripts/progress_report.py",
            "--repo-root",
            str(repo_root),
            "--format",
            "markdown",
        )
        self.assertEqual(completed.returncode, 0, msg=f"{completed.stdout}\n{completed.stderr}")
        self.assertIn("# SCIR Progress Report", completed.stdout)
        self.assertIn("- queue state: `EMPTY_BY_DESIGN`", completed.stdout)
        self.assertIn("- current queue/export sync check: `passed`", completed.stdout)
        self.assertIn("- latest claim bundle: `python-proof-loop-full-20260408T232025Z`", completed.stdout)
        self.assertIn("- latest benchmark activity: `python-proof-loop-full-20260408T233646Z` (smoke)", completed.stdout)

    def test_json_report_prefers_latest_claim_bundle(self) -> None:
        repo_root = self.make_repo_copy()

        completed = run_cmd(
            repo_root,
            sys.executable,
            "scripts/progress_report.py",
            "--repo-root",
            str(repo_root),
            "--format",
            "json",
        )
        self.assertEqual(completed.returncode, 0, msg=f"{completed.stdout}\n{completed.stderr}")
        payload = json.loads(completed.stdout)
        self.assertEqual(
            payload["benchmarks"]["latest_claim"]["run_id"],
            "python-proof-loop-full-20260408T232025Z",
        )
        self.assertEqual(
            payload["benchmarks"]["latest_any"]["run_id"],
            "python-proof-loop-full-20260408T233646Z",
        )
        self.assertEqual(payload["queue_sync_check"]["status"], "passed")


if __name__ == "__main__":
    unittest.main()
