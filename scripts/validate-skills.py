#!/usr/bin/env python3
"""Validate skills/ against the Agent Skills spec and the manifest.

Hand-rolled shape checks over the published tree — no schema library, no
agent install needed on the CI runner (same rationale as the predecessor
repo's manifest validator). Enforces the agentskills.io frontmatter
constraints this repo relies on, manifest <-> tree agreement, and the
absence of cruft the sync should have excluded.

Exits non-zero on any failure with GitHub-Actions-annotated messages
(`::error::` prefix).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS = REPO_ROOT / "skills"
MANIFEST = REPO_ROOT / ".claude" / "skill-manifest.json"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CRUFT = ("__pycache__", "*.pyc")


def _frontmatter(text: str) -> dict[str, str] | None:
    """Parse the single-line `key: value` pairs of a SKILL.md frontmatter
    block. Returns None when the fences are missing."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        m = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip()
    return None


def check_skill(d: Path, errors: list[str]) -> None:
    rel = d.relative_to(REPO_ROOT)
    md = d / "SKILL.md"
    if not md.is_file():
        errors.append(f"{rel}: missing SKILL.md")
        return
    fm = _frontmatter(md.read_text())
    if fm is None:
        errors.append(f"{rel}/SKILL.md: missing or unterminated frontmatter block")
        return
    name = fm.get("name", "")
    desc = fm.get("description", "")
    if not name:
        errors.append(f"{rel}/SKILL.md: frontmatter missing name")
    elif name != d.name:
        errors.append(f"{rel}/SKILL.md: name '{name}' does not match directory")
    elif not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append(f"{rel}/SKILL.md: name '{name}' violates spec naming rules")
    if not desc:
        errors.append(f"{rel}/SKILL.md: frontmatter missing description")
    elif len(desc) > 1024:
        errors.append(f"{rel}/SKILL.md: description exceeds 1024 characters ({len(desc)})")
    compat = fm.get("compatibility")
    if compat is not None and not 1 <= len(compat) <= 500:
        errors.append(f"{rel}/SKILL.md: compatibility must be 1-500 characters")
    for pat in CRUFT:
        for hit in d.rglob(pat):
            errors.append(f"{hit.relative_to(REPO_ROOT)}: cruft in published tree")


def main() -> int:
    errors: list[str] = []

    try:
        declared = json.loads(MANIFEST.read_text())["skills"]
    except (OSError, ValueError, KeyError) as exc:
        print(f"::error::{MANIFEST.relative_to(REPO_ROOT)}: unreadable — {exc}", file=sys.stderr)
        return 1

    present = sorted(p.name for p in SKILLS.iterdir() if p.is_dir()) if SKILLS.is_dir() else []
    for name in sorted(set(declared) - set(present)):
        errors.append(f"manifest declares '{name}' but skills/{name}/ is absent")
    for name in sorted(set(present) - set(declared)):
        errors.append(f"skills/{name}/ exists but is not in the manifest")

    for name in present:
        check_skill(SKILLS / name, errors)

    if errors:
        for msg in errors:
            print(f"::error::{msg}", file=sys.stderr)
        return 1
    print(f"Validation passed — {len(present)} skill(s), manifest consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
