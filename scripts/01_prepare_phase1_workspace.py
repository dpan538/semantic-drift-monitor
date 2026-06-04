#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DIRECTORIES = [
    "data/raw",
    "data/raw/html",
    "data/raw/image_ocr",
    "data/raw/creator_posts",
    "data/raw/qa",
    "data/interim",
    "data/interim/cleaned_text",
    "data/interim/extracted_claims",
    "data/interim/annotations",
    "data/processed",
    "outputs",
    "outputs/phase1",
    "reports",
    "reports/phase1",
    "logs",
]


def main() -> int:
    for relative_path in DIRECTORIES:
        path = ROOT / relative_path
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
        print(f"prepared {relative_path}")

    notes = ROOT / "data/raw/README.local.md"
    if not notes.exists():
        notes.write_text(
            "# Local Raw Data\n\n"
            "This directory is ignored by git. Store permitted local imports here:\n\n"
            "- products.csv\n"
            "- snapshots.csv\n"
            "- reviews.csv\n"
            "- collection_targets.csv\n"
            "- source_registry.csv\n\n"
            "Do not store credentials, cookies, private user identifiers, or prohibited exports.\n",
            encoding="utf-8",
        )
    print("Phase 1 workspace is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

