#!/usr/bin/env python3
"""Deterministic contract test: render a fixture change set and hold the
pipeline to SPEC.md's observable promises — no LLM, no network.

Run from anywhere: `python3 tests/test_contract.py` (or via `uv run`).
The fixture moves one long sentence and edits one word, so a pass requires
diff acquisition, move attribution, and a page that survives the I17 lint.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent

OLD = """The quick brown fox jumps over the lazy dog near the river bank.

Section one keeps its original wording here.
Section two also keeps wording, mostly stable text.
"""

NEW = """Section one keeps its modified wording here.
Section two also keeps wording, mostly stable text.

The quick brown fox jumps over the lazy dog near the river bank.
"""


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", *args], cwd=SKILL_ROOT, capture_output=True, text=True
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "old.txt").write_text(OLD)
        (t / "new.txt").write_text(NEW)

        render = run(
            "scripts/render_diff.py",
            "--old", str(t / "old.txt"),
            "--new", str(t / "new.txt"),
            "--out", str(t / "out"),
        )
        out = render.stdout + render.stderr
        failures = []
        if render.returncode != 0:
            failures.append(f"render exited {render.returncode}")
        if not (t / "out" / "index.html").is_file():
            failures.append("no index.html produced")
        if "LINT" in out:
            failures.append("render output contains LINT defects")
        m = re.search(r"(\d+) moved runs", out)
        if not m:
            failures.append("summary line missing 'moved runs'")
        elif int(m.group(1)) < 1:
            failures.append("fixture move not attributed (0 moved runs)")

        if (t / "out" / "index.html").is_file():
            lint = run("scripts/lint_diff.py", str(t / "out" / "index.html"))
            if lint.returncode != 0:
                failures.append(
                    f"lint_diff failed on rendered page:\n{lint.stdout}{lint.stderr}"
                )

        if failures:
            print("FAIL: " + "; ".join(failures))
            print(out)
            return 1
        print("contract test passed:", out.strip().splitlines()[-1])
        return 0


if __name__ == "__main__":
    sys.exit(main())
