#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scir.contract_docs import rendered_contract_documents


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check or rewrite metadata-rendered contract documents."
    )
    parser.add_argument(
        "--mode",
        choices=("check", "write"),
        default="check",
        help="Check for drift or rewrite the rendered contract documents in place.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    rendered_docs = rendered_contract_documents()
    drifted_paths: list[str] = []

    for rel_path, expected_text in rendered_docs.items():
        path = ROOT / rel_path
        actual_text = path.read_text(encoding="utf-8") if path.exists() else None
        if actual_text == expected_text:
            continue
        drifted_paths.append(rel_path)
        if args.mode == "write":
            path.write_text(expected_text, encoding="utf-8")

    if args.mode == "check":
        if drifted_paths:
            print("[check] rendered contract document drift detected")
            for rel_path in drifted_paths:
                print(f" - {rel_path}")
            return 1
        print("[check] rendered contract documents are in sync")
        return 0

    if drifted_paths:
        print("[write] refreshed rendered contract documents")
        for rel_path in drifted_paths:
            print(f" - {rel_path}")
    else:
        print("[write] rendered contract documents already in sync")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
