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
    "README.md",
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


class BuildExecutionQueueTests(unittest.TestCase):
    def make_repo_copy(self) -> Path:
        temp_root = Path(tempfile.mkdtemp(prefix="scir_queue_export_"))
        repo_root = temp_root / "repo"
        repo_root.mkdir(parents=True, exist_ok=True)
        for rel_path in FIXTURE_FILES:
            src = ROOT / rel_path
            dst = repo_root / rel_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

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
        return repo_root

    def test_write_then_check_is_deterministic(self) -> None:
        repo_root = self.make_repo_copy()

        write = run_cmd(repo_root, sys.executable, "scripts/build_execution_queue.py", "--mode", "write")
        self.assertEqual(write.returncode, 0, msg=f"{write.stdout}\n{write.stderr}")

        check = run_cmd(repo_root, sys.executable, "scripts/build_execution_queue.py", "--mode", "check")
        self.assertEqual(check.returncode, 0, msg=f"{check.stdout}\n{check.stderr}")

    def test_checkpoint_keeps_unrelated_dirty_files_only(self) -> None:
        repo_root = self.make_repo_copy()
        readme = repo_root / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n<!-- dirty -->\n", encoding="utf-8")

        write = run_cmd(repo_root, sys.executable, "scripts/build_execution_queue.py", "--mode", "write")
        self.assertEqual(write.returncode, 0, msg=f"{write.stdout}\n{write.stderr}")

        checkpoint_path = repo_root / "reports/exports/checkpoint_closeout.export.json"
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        status_lines = checkpoint["validation_context"]["working_tree_status"]

        self.assertTrue(checkpoint["validation_context"]["working_tree_dirty"])
        self.assertIn("M README.md", status_lines)
        self.assertFalse(
            any("reports/exports/execution_queue.export.json" in line for line in status_lines)
        )
        self.assertFalse(
            any("reports/exports/checkpoint_closeout.export.json" in line for line in status_lines)
        )


if __name__ == "__main__":
    unittest.main()
