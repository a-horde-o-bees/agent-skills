# agent-skills

The public distribution mirror for skills authored in `~/.claude/skills/`. Each `skills/<name>/` folder follows the [Agent Skills](https://agentskills.io) open standard and must stay self-contained — no plugin machinery, no harness-specific assumptions, paths relative to the skill root. Everything else in the repo is the sync tooling that produces the mirror.

## `skills/` is generated — never edit it directly

`skills/` is regenerated from `~/.claude/skills/` per `.claude/skill-manifest.json`. Edit the live source at `~/.claude/skills/<skill>/`, then sync.

## sync-skills

When I say **"sync-skills"**:

1. `python3 scripts/reconcile_manifest.py` — diff the manifest against the live source. Present any **new** live skills not yet in the manifest and ask which to add (apply with `reconcile_manifest.py --add <names>`); surface **removed**/**changed** for awareness.
2. `python3 scripts/sync_skills.py` — regenerate `skills/` from `~/.claude/skills/` per the manifest.
3. Run the testing layers below (spec compliance + deterministic tests) against the regenerated mirror.

Then commit and push the updated mirror. (`main` is not currently branch-protected; CI re-runs the same checks on push.)

## Skill structure and testing

Three layers gate what this repo publishes; run 1 and 2 locally before any push — CI enforces the same two:

1. **Spec compliance** — `python3 scripts/validate-skills.py` (manifest ↔ tree agreement, cruft absence, frontmatter shape) plus the official reference validator, `uvx --from skills-ref agentskills validate skills/<name>` per skill.
2. **Deterministic tests** — a skill with executable scripts carries self-contained, LLM-free tests at `<skill>/tests/*.py` (stdlib-driven; fixtures inline; runnable from any cwd). CI runs every `skills/*/tests/*.py` with `python3`. Tests ship with the skill, so consumers can run them too.
3. **Behavioral evals** — for a skill whose value is agent behavior rather than script output, the convention is a per-skill `evals/` suite (representative task + expectation, executed through a headless agent and graded deterministically where possible). Adopted per skill at graduation when warranted; not wired into CI yet.

Skills are authored in `~/.claude/skills/<skill>/` and propagate here by sync — tests and evals live inside the skill folder there, never only in this repo. Authoring-time guidance for these layers (self-containment, test conventions, the evals decision) lives in the skill-authoring skill's Portability and tests section; this file owns only release-time enforcement.

## Graduating a skill

A skill enters the manifest only after a readiness pass: self-contained per the standard (relative paths, dependencies declared in `compatibility`, scripts runnable from the folder), no personal data or absolute paths anywhere in the folder, and testing layers 1–2 above passing (plus an `evals/` decision for behavior-shaped skills). One skill at a time — the manifest is the release gate, and an unready skill never blocks a ready one.
