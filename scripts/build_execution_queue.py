from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE_DOC_REL = "EXECUTION_QUEUE.md"
OUTPUT_REL = "reports/exports/execution_queue.export.json"
SCHEMA_REL = "schemas/execution_queue.schema.json"
IMPLEMENTATION_PLAN_REL = "IMPLEMENTATION_PLAN.md"
ACTIVE_QUEUE_SOURCE_REL = "plans/2026-04-01-mvp-narrowing-and-contract-hardening.md"
CHECKPOINT_PLAN_REL = "plans/2026-04-07-q-06-012-checkpoint-integrity-and-governance-evidence-binding.md"
TRACK_C_CLOSEOUT_PLAN_REL = "plans/2026-04-07-q-06-011-lock-track-c-provenance-note-overwrite-semantics.md"
STATUS_REL = "STATUS.md"
OPEN_QUESTIONS_REL = "OPEN_QUESTIONS.md"
DECISION_EXPORT_REL = "reports/exports/decision_register.export.json"
CHECKPOINT_OUTPUT_REL = "reports/exports/checkpoint_closeout.export.json"
CHECKPOINT_SCHEMA_REL = "schemas/checkpoint_closeout.schema.json"

REQUIRED_SOURCE_DOCUMENTS = [
    IMPLEMENTATION_PLAN_REL,
    ACTIVE_QUEUE_SOURCE_REL,
    CHECKPOINT_PLAN_REL,
    OPEN_QUESTIONS_REL,
    STATUS_REL,
]

QUEUE_FIELD_LABELS = [
    "Queue ID",
    "Title",
    "Source milestone or phase",
    "Status",
    "Why now",
    "Prerequisites",
    "Work instructions",
    "Touched surfaces",
    "Validation",
    "Escalate only if",
    "Done evidence",
]

STATUS_VALUES = {"ready", "blocked", "in-progress", "done", "deferred"}
AUTONOMY_VALUES = {"high", "moderate", "conservative"}
QUEUE_VALIDATION_STATES = {"PENDING", "PASSED", "FAILED"}
QUEUE_STATE_VALUES = {"READY", "EMPTY_BY_DESIGN"}
COMMIT_HASH_BASIS_VALUES = {"current_head", "baseline_parent"}
CHECKPOINT_DECISION_RECORD_IDS = ["DR-040", "DR-041", "DR-042"]
REENTRY_RULE_MARKERS = [
    "roadmap selection is complete",
    "bounded next item is defined",
    "validator and export impact are assessed",
    "reports/exports/execution_queue.export.json",
    "reports/exports/checkpoint_closeout.export.json",
]
CHECKPOINT_PLAN_CLOSEOUTS = [
    ACTIVE_QUEUE_SOURCE_REL,
    TRACK_C_CLOSEOUT_PLAN_REL,
    CHECKPOINT_PLAN_REL,
]
MANAGED_EXPORT_STATUS_PATHS = {
    OUTPUT_REL.replace("\\", "/"),
    CHECKPOINT_OUTPUT_REL.replace("\\", "/"),
}
CHECKPOINT_SCHEMA_OR_CONTRACT_SURFACES = [
    QUEUE_DOC_REL,
    "DECISION_REGISTER.md",
    SCHEMA_REL,
    "schemas/decision_register.schema.json",
    CHECKPOINT_SCHEMA_REL,
    "VALIDATION.md",
    "VALIDATION_STRATEGY.md",
    "scripts/build_execution_queue.py",
    "scripts/validate_repo_contracts.py",
]


def split_inline_list(value: str) -> list[str]:
    if value.strip().lower() == "none":
        return []
    return [item.strip().strip("`") for item in value.split(";") if item.strip()]


def sha256_bytes(payload: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(payload)
    return f"sha256:{digest.hexdigest()}"


def file_sha256(root: pathlib.Path, rel_path: str) -> str:
    return sha256_bytes((root / rel_path).read_bytes())


def run_git_stdout(root: pathlib.Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip()
        raise ValueError(f"git {' '.join(args)} failed: {stderr or completed.stdout.strip()}")
    return completed.stdout


def normalize_git_status_path(path_text: str) -> str:
    normalized = path_text.strip()
    if " -> " in normalized:
        normalized = normalized.split(" -> ", 1)[1]
    return normalized.replace("\\", "/")


def filtered_working_tree_status(root: pathlib.Path) -> list[str]:
    lines = [
        line.rstrip()
        for line in run_git_stdout(root, "status", "--short").splitlines()
        if line.strip()
    ]
    filtered = []
    for line in lines:
        candidate = normalize_git_status_path(line[3:] if len(line) > 3 else line)
        if candidate in MANAGED_EXPORT_STATUS_PATHS:
            continue
        filtered.append(line.strip())
    return filtered


def load_recorded_git_context(root: pathlib.Path) -> tuple[str, str, list[str]] | None:
    checkpoint_path = root / CHECKPOINT_OUTPUT_REL
    if not checkpoint_path.exists():
        return None
    checkpoint_payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    validation_context = checkpoint_payload.get("validation_context", {})
    head_commit_hash = validation_context.get("head_commit_hash")
    commit_hash_basis = validation_context.get("commit_hash_basis")
    working_tree_status = validation_context.get("working_tree_status", [])
    if (
        isinstance(head_commit_hash, str)
        and commit_hash_basis in COMMIT_HASH_BASIS_VALUES
        and isinstance(working_tree_status, list)
    ):
        return head_commit_hash, commit_hash_basis, [str(item) for item in working_tree_status]
    return None


def build_superseded_dirty_checkpoint(root: pathlib.Path) -> dict | None:
    checkpoint_path = root / CHECKPOINT_OUTPUT_REL
    if not checkpoint_path.exists():
        return None

    checkpoint_bytes = checkpoint_path.read_bytes()
    checkpoint_payload = json.loads(checkpoint_bytes.decode("utf-8"))

    carried_forward = checkpoint_payload.get("superseded_dirty_checkpoint")
    if isinstance(carried_forward, dict):
        return carried_forward

    validation_context = checkpoint_payload.get("validation_context", {})
    if validation_context.get("working_tree_dirty") is not True:
        return None

    generated_at = checkpoint_payload.get("generated_at")
    head_commit_hash = validation_context.get("head_commit_hash")
    commit_hash_basis = validation_context.get("commit_hash_basis", "current_head")
    working_tree_status = validation_context.get("working_tree_status", [])
    if not isinstance(generated_at, str):
        raise ValueError(f"{CHECKPOINT_OUTPUT_REL}: dirty checkpoint lineage missing generated_at")
    if not isinstance(head_commit_hash, str):
        raise ValueError(
            f"{CHECKPOINT_OUTPUT_REL}: dirty checkpoint lineage missing head_commit_hash"
        )
    if commit_hash_basis not in COMMIT_HASH_BASIS_VALUES:
        raise ValueError(
            f"{CHECKPOINT_OUTPUT_REL}: dirty checkpoint lineage has invalid commit_hash_basis"
        )
    if not isinstance(working_tree_status, list):
        raise ValueError(
            f"{CHECKPOINT_OUTPUT_REL}: dirty checkpoint lineage missing working_tree_status"
        )

    return {
        "generated_at": generated_at,
        "artifact_sha256": sha256_bytes(checkpoint_bytes),
        "head_commit_hash": head_commit_hash,
        "commit_hash_basis": commit_hash_basis,
        "working_tree_dirty": True,
        "working_tree_status": [str(item) for item in working_tree_status],
    }


def resolve_checkpoint_git_context(root: pathlib.Path) -> tuple[str, str, list[str]]:
    recorded_git_context = load_recorded_git_context(root)
    try:
        current_head = run_git_stdout(root, "rev-parse", "HEAD").strip()
        working_tree_status = filtered_working_tree_status(root)
    except ValueError:
        if recorded_git_context is None:
            raise
        return recorded_git_context

    if working_tree_status:
        return current_head, "current_head", working_tree_status

    if recorded_git_context is not None and recorded_git_context[1] == "baseline_parent":
        return recorded_git_context

    try:
        baseline_parent = run_git_stdout(root, "rev-parse", "HEAD^").strip()
    except ValueError:
        baseline_parent = current_head
        basis = "current_head"
    else:
        basis = "baseline_parent"
    return baseline_parent, basis, working_tree_status


def parse_current_queue_state(text: str) -> dict:
    section_match = re.search(
        r"^## CURRENT QUEUE STATE\s*$\n(?P<body>.*)$",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        raise ValueError(f"{QUEUE_DOC_REL}: missing CURRENT QUEUE STATE section")

    body = section_match.group("body")

    queue_state_match = re.search(r"^QUEUE STATE:\s*`([^`]+)`$", body, re.MULTILINE)
    if not queue_state_match:
        raise ValueError(f"{QUEUE_DOC_REL}: missing CURRENT QUEUE STATE queue-state line")
    queue_state = queue_state_match.group(1).strip().replace(" ", "_")
    if queue_state not in QUEUE_STATE_VALUES:
        raise ValueError(f"{QUEUE_DOC_REL}: invalid CURRENT QUEUE STATE queue_state {queue_state!r}")

    ready_match = re.search(r"^READY ITEMS:\s*(.+)$", body, re.MULTILINE)
    if not ready_match:
        raise ValueError(f"{QUEUE_DOC_REL}: missing CURRENT QUEUE STATE ready-items line")
    ready_value = ready_match.group(1).strip()
    if ready_value == "NONE":
        ready_items = []
    else:
        ready_items = [item.strip() for item in re.split(r"[;,]", ready_value) if item.strip()]

    last_completed_match = re.search(
        r"^LAST COMPLETED:\s*$\n^- (?P<queue_id>Q-[0-9]{2}-[0-9]{3}) \((?P<label>.+)\)$",
        body,
        re.MULTILINE,
    )
    if not last_completed_match:
        raise ValueError(f"{QUEUE_DOC_REL}: missing CURRENT QUEUE STATE last-completed entry")

    no_successor_match = re.search(
        r"^NO SUCCESSOR ITEM CREATED:\s*`([^`]+)`$",
        body,
        re.MULTILINE,
    )
    no_successor_item_reason = (
        no_successor_match.group(1).strip() if no_successor_match else None
    )

    synchronized_match = re.search(
        r"^- SYNCHRONIZED WITH WORKING TREE:\s*(TRUE|FALSE)$",
        body,
        re.MULTILINE,
    )
    if not synchronized_match:
        raise ValueError(
            f"{QUEUE_DOC_REL}: missing CURRENT QUEUE STATE synchronization status"
        )

    validation_match = re.search(
        r"^- VALIDATION STATE:\s*([A-Z]+)$",
        body,
        re.MULTILINE,
    )
    if not validation_match:
        raise ValueError(f"{QUEUE_DOC_REL}: missing CURRENT QUEUE STATE validation status")
    validation_state = validation_match.group(1).strip()
    if validation_state not in QUEUE_VALIDATION_STATES:
        raise ValueError(
            f"{QUEUE_DOC_REL}: invalid CURRENT QUEUE STATE validation status {validation_state!r}"
        )

    return {
        "queue_state": queue_state,
        "ready_items": ready_items,
        "last_completed": {
            "queue_id": last_completed_match.group("queue_id"),
            "label": last_completed_match.group("label").strip(),
        },
        "no_successor_item_reason": no_successor_item_reason,
        "queue_status": {
            "synchronized_with_working_tree": synchronized_match.group(1) == "TRUE",
            "validation_state": validation_state,
        },
    }


def parse_reentry_conditions(text: str) -> list[str]:
    section_match = re.search(
        r"^## QUEUE RE-ENTRY RULES\s*$\n(?P<body>.*?)(?=^## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        raise ValueError(f"{QUEUE_DOC_REL}: missing QUEUE RE-ENTRY RULES section")
    conditions = []
    for line in section_match.group("body").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.fullmatch(r"- `([^`]+)`", stripped)
        if not match:
            raise ValueError(
                f"{QUEUE_DOC_REL}: QUEUE RE-ENTRY RULES must use `- `...`` bullets only"
            )
        conditions.append(match.group(1))
    if not conditions:
        raise ValueError(f"{QUEUE_DOC_REL}: QUEUE RE-ENTRY RULES section has no bullets")
    return conditions


def parse_queue_markdown(root: pathlib.Path) -> dict:
    text = (root / QUEUE_DOC_REL).read_text(encoding="utf-8")

    metadata = {}
    metadata_patterns = {
        "generation_timestamp": r"- Queue snapshot:\s*`([^`]+)`",
        "active_milestone": r"- Active milestone:\s*`([^`]+)`",
        "autonomy_mode": r"- Autonomy mode:\s*`([^`]+)`",
        "escalation_threshold": r"- Escalation threshold:\s*`([^`]+)`",
    }
    for key, pattern in metadata_patterns.items():
        match = re.search(pattern, text)
        if not match:
            raise ValueError(f"{QUEUE_DOC_REL}: missing metadata field {key}")
        metadata[key] = match.group(1).strip()

    if metadata["autonomy_mode"] not in AUTONOMY_VALUES:
        raise ValueError(
            f"{QUEUE_DOC_REL}: invalid autonomy mode {metadata['autonomy_mode']!r}"
        )

    source_documents = re.findall(r"- `([^`]+)` for ", text.split("## Queue metadata")[0])
    if source_documents != REQUIRED_SOURCE_DOCUMENTS:
        raise ValueError(
            f"{QUEUE_DOC_REL}: expected source documents {REQUIRED_SOURCE_DOCUMENTS!r}"
        )

    item_pattern = re.compile(
        r"^### (?P<header>[^\n]+)\n(?P<body>.*?)(?=^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    items = []
    for match in item_pattern.finditer(text):
        body = match.group("body")
        fields = {}
        for label in QUEUE_FIELD_LABELS:
            field_match = re.search(
                rf"^- {re.escape(label)}:\s*(.+)$",
                body,
                re.MULTILINE,
            )
            if not field_match:
                raise ValueError(
                    f"{QUEUE_DOC_REL}: missing field {label!r} in item {match.group('header')!r}"
                )
            fields[label] = field_match.group(1).strip()

        status = fields["Status"].strip("`")
        if status not in STATUS_VALUES:
            raise ValueError(
                f"{QUEUE_DOC_REL}: invalid status {status!r} in item {fields['Queue ID']!r}"
            )

        items.append(
            {
                "queue_id": fields["Queue ID"].strip("`"),
                "title": fields["Title"].strip("`"),
                "source_milestone_or_phase": fields["Source milestone or phase"].strip("`"),
                "status": status,
                "why_now": fields["Why now"].strip("`"),
                "prerequisites": split_inline_list(fields["Prerequisites"]),
                "work_instructions": fields["Work instructions"].strip("`"),
                "touched_surfaces": split_inline_list(fields["Touched surfaces"]),
                "validation": split_inline_list(fields["Validation"]),
                "escalate_only_if": fields["Escalate only if"].strip("`"),
                "done_evidence": split_inline_list(fields["Done evidence"]),
                "blocking_open_questions": sorted(
                    set(re.findall(r"OQ-[0-9]{3}", fields["Escalate only if"]))
                ),
            }
        )

    if not items:
        raise ValueError(f"{QUEUE_DOC_REL}: no queue items found")

    current_queue_state = parse_current_queue_state(text)
    reentry_conditions = parse_reentry_conditions(text)
    ready_items = [item for item in items if item["status"] == "ready"]

    return {
        "generation_timestamp": metadata["generation_timestamp"],
        "active_milestone": metadata["active_milestone"],
        "autonomy_mode": metadata["autonomy_mode"],
        "source_documents": REQUIRED_SOURCE_DOCUMENTS,
        "queue_items": items,
        "current_queue_state": current_queue_state,
        "reentry_conditions": reentry_conditions,
        "blocking_open_questions": sorted(
            {oq for item in items for oq in item["blocking_open_questions"]}
        ),
        "next_action": (
            {
                "queue_id": ready_items[0]["queue_id"],
                "title": ready_items[0]["title"],
            }
            if ready_items
            else None
        ),
        "escalation_threshold": metadata["escalation_threshold"],
    }


def validate_queue_against_repo(root: pathlib.Path, payload: dict) -> None:
    implementation_plan = (root / IMPLEMENTATION_PLAN_REL).read_text(encoding="utf-8")
    active_queue_source = (root / ACTIVE_QUEUE_SOURCE_REL).read_text(encoding="utf-8")
    status_text = (root / STATUS_REL).read_text(encoding="utf-8")
    open_questions = (root / OPEN_QUESTIONS_REL).read_text(encoding="utf-8")

    if "mvp kernel hardening" not in implementation_plan.lower():
        raise ValueError(
            f"{IMPLEMENTATION_PLAN_REL}: missing MVP kernel hardening phase"
        )
    if "- activity: `active`" not in status_text:
        raise ValueError(f"{STATUS_REL}: expected active portfolio posture")
    if payload["active_milestone"] != "MVP Kernel Hardening":
        raise ValueError(
            f"{QUEUE_DOC_REL}: active milestone must remain 'MVP Kernel Hardening'"
        )

    queue_items = payload["queue_items"]
    if queue_items[0]["source_milestone_or_phase"] != "MVP Kernel Hardening":
        raise ValueError(
            f"{QUEUE_DOC_REL}: first queue item must come from MVP Kernel Hardening"
        )
    ready_items = [item for item in queue_items if item["status"] == "ready"]
    current_queue_state = payload["current_queue_state"]
    ready_queue_ids = [item["queue_id"] for item in ready_items]
    if current_queue_state["ready_items"] != ready_queue_ids:
        raise ValueError(
            f"{QUEUE_DOC_REL}: CURRENT QUEUE STATE ready items {current_queue_state['ready_items']!r} "
            f"do not match ready queue items {ready_queue_ids!r}"
        )
    if ready_items and current_queue_state["queue_state"] != "READY":
        raise ValueError(
            f"{QUEUE_DOC_REL}: CURRENT QUEUE STATE queue_state must be READY while ready items remain"
        )
    if not ready_items and current_queue_state["queue_state"] != "EMPTY_BY_DESIGN":
        raise ValueError(
            f"{QUEUE_DOC_REL}: CURRENT QUEUE STATE queue_state must be EMPTY_BY_DESIGN when no ready items remain"
        )

    last_completed_id = current_queue_state["last_completed"]["queue_id"]
    last_completed_item = next(
        (item for item in queue_items if item["queue_id"] == last_completed_id),
        None,
    )
    if last_completed_item is None:
        raise ValueError(
            f"{QUEUE_DOC_REL}: CURRENT QUEUE STATE references unknown last-completed item {last_completed_id}"
        )
    if last_completed_item["status"] != "done":
        raise ValueError(
            f"{QUEUE_DOC_REL}: CURRENT QUEUE STATE last-completed item {last_completed_id} must be marked done"
        )
    if not current_queue_state["queue_status"]["synchronized_with_working_tree"]:
        raise ValueError(
            f"{QUEUE_DOC_REL}: CURRENT QUEUE STATE must keep synchronized-with-working-tree true"
        )
    if not payload["reentry_conditions"]:
        raise ValueError(f"{QUEUE_DOC_REL}: reentry_conditions must not be empty")
    for marker in REENTRY_RULE_MARKERS:
        if not any(marker in condition for condition in payload["reentry_conditions"]):
            raise ValueError(
                f"{QUEUE_DOC_REL}: QUEUE RE-ENTRY RULES must mention {marker!r}"
            )

    if ready_items:
        if "Status: in-progress" not in active_queue_source:
            raise ValueError(
                f"{ACTIVE_QUEUE_SOURCE_REL}: expected active queue source to be in-progress while ready work remains"
            )
        if payload["next_action"] is None:
            raise ValueError(
                f"{QUEUE_DOC_REL}: next_action must name the first ready queue item while ready work remains"
            )
        if payload["next_action"]["queue_id"] != ready_items[0]["queue_id"]:
            raise ValueError(f"{QUEUE_DOC_REL}: next_action must point to the first ready queue item")
        if current_queue_state["no_successor_item_reason"] is not None:
            raise ValueError(
                f"{QUEUE_DOC_REL}: no-successor rationale must be absent while ready work remains"
            )
    else:
        if "Status: complete" not in active_queue_source:
            raise ValueError(
                f"{ACTIVE_QUEUE_SOURCE_REL}: expected active queue source to be complete when no ready work remains"
            )
        if payload["next_action"] is not None:
            raise ValueError(
                f"{QUEUE_DOC_REL}: next_action must be null when the queue is empty by design"
            )
        if not current_queue_state["no_successor_item_reason"]:
            raise ValueError(
                f"{QUEUE_DOC_REL}: empty-by-design queue state must record a no-successor rationale"
            )

    queue_ids = {item["queue_id"] for item in queue_items}
    for item in queue_items:
        for prerequisite in item["prerequisites"]:
            if prerequisite.startswith("Q-") and prerequisite not in queue_ids:
                raise ValueError(
                    f"{QUEUE_DOC_REL}: {item['queue_id']} references unknown prerequisite {prerequisite}"
                )

    for forbidden in ["TypeScript", "D-JS"]:
        if forbidden in (root / QUEUE_DOC_REL).read_text(encoding="utf-8"):
            raise ValueError(
                f"{QUEUE_DOC_REL}: queue must not reactivate deferred scope marker {forbidden!r}"
            )

    for open_question in payload["blocking_open_questions"]:
        if open_question not in open_questions:
            raise ValueError(
                f"{QUEUE_DOC_REL}: blocking open question {open_question} not found in {OPEN_QUESTIONS_REL}"
            )


def load_checkpoint_decision_records(root: pathlib.Path) -> list[dict]:
    export = json.loads((root / DECISION_EXPORT_REL).read_text(encoding="utf-8"))
    records = export.get("decision_records")
    if not isinstance(records, list):
        raise ValueError(f"{DECISION_EXPORT_REL}: missing decision_records array")
    by_id = {}
    for record in records:
        if not isinstance(record, dict) or "id" not in record:
            raise ValueError(f"{DECISION_EXPORT_REL}: malformed decision_record entry")
        by_id[record["id"]] = record
    missing = [record_id for record_id in CHECKPOINT_DECISION_RECORD_IDS if record_id not in by_id]
    if missing:
        raise ValueError(
            f"{DECISION_EXPORT_REL}: missing checkpoint decision records {', '.join(missing)}"
        )
    return [by_id[record_id] for record_id in CHECKPOINT_DECISION_RECORD_IDS]


def build_checkpoint_closeout_payload(root: pathlib.Path, queue_payload: dict, queue_serialized: str) -> dict:
    current_queue_state = queue_payload["current_queue_state"]
    last_completed = current_queue_state["last_completed"]
    last_completed_item = next(
        item for item in queue_payload["queue_items"] if item["queue_id"] == last_completed["queue_id"]
    )
    decision_records = load_checkpoint_decision_records(root)
    head_commit_hash, commit_hash_basis, working_tree_status = resolve_checkpoint_git_context(root)
    superseded_dirty_checkpoint = build_superseded_dirty_checkpoint(root)
    validation_outputs = [
        {
            "command": command,
            "status": "passed",
        }
        for command in last_completed_item["validation"]
    ]
    queue_export_sha = sha256_bytes(queue_serialized.encode("utf-8"))

    return {
        "generated_at": queue_payload["generation_timestamp"],
        "queue_state": {
            "status": current_queue_state["queue_state"],
            "ready_items": current_queue_state["ready_items"],
            "no_successor_item_reason": current_queue_state["no_successor_item_reason"],
        },
        "last_completed": {
            "queue_id": last_completed["queue_id"],
            "label": last_completed["label"],
            "title": last_completed_item["title"],
        },
        "next_action": queue_payload["next_action"],
        "validation_state": {
            "status": current_queue_state["queue_status"]["validation_state"],
            "synchronized_with_working_tree": current_queue_state["queue_status"][
                "synchronized_with_working_tree"
            ],
        },
        "decision_record_refs": [
            {
                "id": record["id"],
                "transition": record["transition"],
                "evidence_references": record["evidence_references"],
            }
            for record in decision_records
        ],
        "evidence_refs": {
            "queue_markdown": {
                "path": QUEUE_DOC_REL,
                "sha256": file_sha256(root, QUEUE_DOC_REL),
            },
            "queue_export": {
                "path": OUTPUT_REL,
                "generated_at": queue_payload["generation_timestamp"],
                "sha256": queue_export_sha,
            },
            "relevant_plan_closeouts": [
                {
                    "path": rel,
                    "section": "CLOSEOUT",
                    "sha256": file_sha256(root, rel),
                }
                for rel in CHECKPOINT_PLAN_CLOSEOUTS
            ],
            "validation_outputs": validation_outputs,
            "schema_or_contract_surfaces": [
                {
                    "path": rel,
                    "sha256": file_sha256(root, rel),
                }
                for rel in CHECKPOINT_SCHEMA_OR_CONTRACT_SURFACES
            ],
        },
        "validation_context": {
            "queue_snapshot": queue_payload["generation_timestamp"],
            "head_commit_hash": head_commit_hash,
            "commit_hash_basis": commit_hash_basis,
            "working_tree_dirty": bool(working_tree_status),
            "working_tree_status": working_tree_status,
            "validation_commands": last_completed_item["validation"],
            "schema_versions": [
                {
                    "path": rel,
                    "declared_version": None,
                    "sha256": file_sha256(root, rel),
                }
                for rel in [
                    SCHEMA_REL,
                    "schemas/decision_register.schema.json",
                    CHECKPOINT_SCHEMA_REL,
                ]
            ],
            "exported_artifacts": [
                {
                    "path": OUTPUT_REL,
                    "generated_at": queue_payload["generation_timestamp"],
                    "sha256": queue_export_sha,
                },
                {
                    "path": DECISION_EXPORT_REL,
                    "generated_at": None,
                    "sha256": file_sha256(root, DECISION_EXPORT_REL),
                },
            ],
        },
        "superseded_dirty_checkpoint": superseded_dirty_checkpoint,
        "residual_risks": [record["residual_risk"] for record in decision_records],
        "reentry_conditions": queue_payload["reentry_conditions"],
    }


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def matches_type(value, expected_type):
    if isinstance(expected_type, list):
        return any(matches_type(value, item) for item in expected_type)

    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": is_number(value),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
        "null": value is None,
    }.get(expected_type, True)


def normalize_for_uniqueness(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def resolve_local_schema_ref(schema_root, ref: str):
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported schema ref {ref!r}")
    target = schema_root
    for part in ref[2:].split("/"):
        target = target[part]
    return target


def collect_fallback_validation_errors(instance, schema, path="$", schema_root=None):
    if schema_root is None:
        schema_root = schema
    ref = schema.get("$ref")
    if ref is not None:
        resolved = resolve_local_schema_ref(schema_root, ref)
        return collect_fallback_validation_errors(instance, resolved, path, schema_root)

    failures = []
    expected_type = schema.get("type")
    if expected_type is not None and not matches_type(instance, expected_type):
        return [(path, f"expected type {expected_type!r}")]

    expected_enum = schema.get("enum")
    if expected_enum is not None and instance not in expected_enum:
        failures.append((path, f"expected one of {expected_enum!r}"))

    min_length = schema.get("minLength")
    if min_length is not None and isinstance(instance, str) and len(instance) < min_length:
        failures.append((path, f"expected string length >= {min_length}"))

    min_items = schema.get("minItems")
    if min_items is not None and isinstance(instance, list) and len(instance) < min_items:
        failures.append((path, f"expected at least {min_items} items"))

    pattern = schema.get("pattern")
    if pattern is not None and isinstance(instance, str) and re.fullmatch(pattern, instance) is None:
        failures.append((path, f"expected string matching {pattern!r}"))

    if schema.get("uniqueItems") and isinstance(instance, list):
        normalized = [normalize_for_uniqueness(item) for item in instance]
        if len(normalized) != len(set(normalized)):
            failures.append((path, "expected unique items"))

    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                failures.append((path, f"missing required property {key}"))

        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                failures.extend(
                    collect_fallback_validation_errors(
                        value, properties[key], child_path, schema_root
                    )
                )
            elif additional is False:
                failures.append((path, f"unexpected property {key}"))
            elif isinstance(additional, dict):
                failures.extend(
                    collect_fallback_validation_errors(
                        value, additional, child_path, schema_root
                    )
                )

    if isinstance(instance, list) and "items" in schema:
        for idx, item in enumerate(instance):
            failures.extend(
                collect_fallback_validation_errors(
                    item, schema["items"], f"{path}[{idx}]", schema_root
                )
            )

    return failures


def validate_against_schema(root: pathlib.Path, payload: dict, schema_rel: str) -> None:
    schema = json.loads((root / schema_rel).read_text(encoding="utf-8"))

    try:
        from jsonschema import Draft202012Validator
    except ImportError:  # pragma: no cover - optional dependency
        errors = collect_fallback_validation_errors(payload, schema)
        if errors:
            raise ValueError("; ".join(f"{path}: {message}" for path, message in errors))
        return

    errors = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda error: ([str(part) for part in error.absolute_path], error.message),
    )
    if errors:
        messages = []
        for error in errors:
            path = "$"
            for part in error.absolute_path:
                path += f"[{part}]" if isinstance(part, int) else f".{part}"
            messages.append(f"{path}: {error.message}")
        raise ValueError("; ".join(messages))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate the SCIR execution queue export."
    )
    parser.add_argument(
        "--mode",
        default="write",
        choices=["write", "check", "print"],
        help="write updates the checked-in export; check validates drift; print writes JSON to stdout.",
    )
    args = parser.parse_args()

    payload = parse_queue_markdown(ROOT)
    validate_queue_against_repo(ROOT, payload)
    validate_against_schema(ROOT, payload, SCHEMA_REL)

    output_path = ROOT / OUTPUT_REL
    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    checkpoint_payload = build_checkpoint_closeout_payload(ROOT, payload, serialized)
    validate_against_schema(ROOT, checkpoint_payload, CHECKPOINT_SCHEMA_REL)
    checkpoint_output_path = ROOT / CHECKPOINT_OUTPUT_REL
    checkpoint_serialized = json.dumps(checkpoint_payload, indent=2, ensure_ascii=False) + "\n"

    if args.mode == "write":
        output_path.write_text(serialized, encoding="utf-8")
        checkpoint_output_path.write_text(checkpoint_serialized, encoding="utf-8")
        print(f"[write] wrote {OUTPUT_REL}")
        print(f"[write] wrote {CHECKPOINT_OUTPUT_REL}")
    elif args.mode == "check":
        failures = []
        checked_in = output_path.read_text(encoding="utf-8")
        if checked_in != serialized:
            failures.append(f"[check] {OUTPUT_REL} is out of date")
        checked_in_checkpoint = checkpoint_output_path.read_text(encoding="utf-8")
        if checked_in_checkpoint != checkpoint_serialized:
            failures.append(f"[check] {CHECKPOINT_OUTPUT_REL} is out of date")
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1
        print(f"[check] {OUTPUT_REL} is synchronized")
        print(f"[check] {CHECKPOINT_OUTPUT_REL} is synchronized")
    else:
        sys.stdout.write(serialized)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
