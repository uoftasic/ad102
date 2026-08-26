#!/usr/bin/env python3
"""Replace course placeholders after creating a repo from the UofT ASIC template.

Fills ad102, AD102 — Linear Circuits & Fabrication, and Linear analysis, folded together with how passives are actually built on a chip. only.
Does not scaffold or remove docs pages — keep the published site barebones.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Org is fixed for this template; only course fields are fillable.
ORG = "uoftasic"

TOKENS = (
    "COURSE_ID",
    "COURSE_TITLE",
    "DESCRIPTION",
)

INCLUDE_SUFFIXES = {
    ".md",
    ".html",
    ".css",
    ".js",
    ".py",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".gitignore",
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "site",
    "_book",
}

COURSE_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,31}$")


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix and path.suffix not in INCLUDE_SUFFIXES:
            if path.name not in {".gitignore", "LICENSE"}:
                continue
        elif not path.suffix and path.name not in {".gitignore", "LICENSE", "Makefile"}:
            continue
        yield path


def replace_in_text(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    count = 0
    for key, value in mapping.items():
        token = "{{" + key + "}}"
        n = text.count(token)
        if n:
            text = text.replace(token, value)
            count += n
    return text, count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Rewrite course placeholders for a uoftasic repo "
            f"(org is always {ORG})."
        )
    )
    parser.add_argument(
        "--id",
        required=True,
        dest="course_id",
        help="Course / repo id (kebab-case), e.g. dd103 or serdes-intro",
    )
    parser.add_argument(
        "--title",
        required=True,
        help='Display title, e.g. "DD103 — RTL on FPGAs & ASICs"',
    )
    parser.add_argument(
        "--description",
        required=True,
        help="One-line blurb for the course",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report replacements without writing files",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root (default: parent of scripts/)",
    )
    args = parser.parse_args(argv)

    if not COURSE_ID_RE.match(args.course_id):
        print(
            f"Invalid --id {args.course_id!r}: use lowercase kebab-case "
            "(e.g. dd103, ic101, serdes-lab).",
            file=sys.stderr,
        )
        return 2

    mapping = {
        "COURSE_ID": args.course_id,
        "COURSE_TITLE": args.title,
        "DESCRIPTION": args.description,
    }

    total = 0
    touched = 0
    for path in sorted(iter_files(args.root)):
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated, n = replace_in_text(original, mapping)
        if n == 0:
            continue
        total += n
        touched += 1
        rel = path.relative_to(args.root)
        print(f"{rel}: {n} replacement(s)")
        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")

    action = "Would update" if args.dry_run else "Updated"
    print(f"{action} {touched} file(s), {total} token(s).")
    print(f"GitHub org is fixed: {ORG}")
    print(f"Expected Pages URL: https://{ORG}.github.io/{args.course_id}/")
    if total == 0:
        print("No placeholders found — already initialized?", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
