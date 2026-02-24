#!/usr/bin/env python3
"""Fail if plain-text `chat_once(...)` / `chat(...)` mentions are not links."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILES = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]

MENTIONS = (
    (
        re.compile(r"`chat_once\(\.\.\.\)`"),
        re.compile(r"\[`chat_once\(\.\.\.\)`\]\([^)]+\)"),
        "`chat_once(...)`",
    ),
    (
        re.compile(r"`chat\(\.\.\.\)`"),
        re.compile(r"\[`chat\(\.\.\.\)`\]\([^)]+\)"),
        "`chat(...)`",
    ),
)


def _scan_file(path: Path) -> list[str]:
    violations: list[str] = []
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith("#"):
            continue
        for mention_re, linked_re, label in MENTIONS:
            if mention_re.search(line) and not linked_re.search(line):
                violations.append(f"{path.relative_to(ROOT)}:{lineno}: unlinked {label}")
    return violations


def main() -> int:
    violations: list[str] = []
    for path in FILES:
        if path.exists():
            violations.extend(_scan_file(path))

    if not violations:
        print("method-link check passed")
        return 0

    print("method-link check failed:")
    for violation in violations:
        print(f"  - {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
