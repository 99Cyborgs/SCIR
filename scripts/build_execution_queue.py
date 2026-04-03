from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE_DOC_REL = "EXECUTION_QUEUE.md"
OUTPUT_REL = "reports/exports/execution_queue.export.json"
SCHEMA_REL = "schemas/execution_queue.schema.json"
IMPLEMENTATION_PLAN_REL = "IMPLEMENTATION_PLAN.md"
ACTIVE_QUEUE_SOURCE_REL = "plans/2026-04-01-mvp-narrowing-and-contract-hardening.md"
STATUS_REL = "STATUS.md"
OPEN_QUESTIONS_REL = "OPEN_QUESTIONS.md"

REQUIRED_SOURCE_DOCUMENTS = [
    IMPLEMENTATION_PLAN_REL,
    ACTIVE_QUEUE_SOURCE_REL,
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


def split_inline_list(value: str) -> list[str]:
    if value.strip().lower() == "none":
        return []
    return [item.strip().strip("`") for item in value.split(";") if item.strip()]


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

    ready_items = [item for item in items if item["status"] == "ready"]
    if not ready_items:
        raise ValueError(f"{QUEUE_DOC_REL}: no ready queue item found")

    return {
        "generation_timestamp": metadata["generation_timestamp"],
        "active_milestone": metadata["active_milestone"],
        "autonomy_mode": metadata["autonomy_mode"],
        "source_documents": REQUIRED_SOURCE_DOCUMENTS,
        "queue_items": items,
        "blocking_open_questions": sorted(
            {oq for item in items for oq in item["blocking_open_questions"]}
        ),
        "next_action": {
            "queue_id": ready_items[0]["queue_id"],
            "title": ready_items[0]["title"],
        },
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
    if "Status: in-progress" not in active_queue_source:
        raise ValueError(
            f"{ACTIVE_QUEUE_SOURCE_REL}: expected active queue source to be in-progress"
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
    if not ready_items:
        raise ValueError(f"{QUEUE_DOC_REL}: expected at least one ready queue item")
    if payload["next_action"]["queue_id"] != ready_items[0]["queue_id"]:
        raise ValueError(f"{QUEUE_DOC_REL}: next_action must point to the first ready queue item")

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


def collect_fallback_validation_errors(instance, schema, path="$"):
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
                    collect_fallback_validation_errors(value, properties[key], child_path)
                )
            elif additional is False:
                failures.append((path, f"unexpected property {key}"))
            elif isinstance(additional, dict):
                failures.extend(
                    collect_fallback_validation_errors(value, additional, child_path)
                )

    if isinstance(instance, list) and "items" in schema:
        for idx, item in enumerate(instance):
            failures.extend(
                collect_fallback_validation_errors(item, schema["items"], f"{path}[{idx}]")
            )

    return failures


def validate_against_schema(root: pathlib.Path, payload: dict) -> None:
    schema = json.loads((root / SCHEMA_REL).read_text(encoding="utf-8"))

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
    validate_against_schema(ROOT, payload)

    output_path = ROOT / OUTPUT_REL
    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

    if args.mode == "write":
        output_path.write_text(serialized, encoding="utf-8")
        print(f"[write] wrote {OUTPUT_REL}")
    elif args.mode == "check":
        checked_in = output_path.read_text(encoding="utf-8")
        if checked_in != serialized:
            print(f"[check] {OUTPUT_REL} is out of date", file=sys.stderr)
            return 1
        print(f"[check] {OUTPUT_REL} is synchronized")
    else:
        sys.stdout.write(serialized)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
