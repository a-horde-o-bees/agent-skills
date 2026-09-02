# agent-skills

Curated agent skills in the open [Agent Skills](https://agentskills.io) format: each `skills/<name>/` folder is a self-contained `SKILL.md` plus its scripts and references, usable by any agent that supports the standard.

## Install

With the [skills CLI](https://github.com/vercel-labs/skills), into any supported agent:

```bash
npx skills add a-horde-o-bees/agent-skills --skill export-diff
```

Or copy a folder into your agent's skills directory (for Claude Code, `~/.claude/skills/`).

## Skills

- **export-diff** — renders two versions of a file or tree, or any unified diff, to a self-contained side-by-side HTML report that attributes moved, merged, and split content across line breaks, with word-level marks on only the real edits. Requires [uv](https://docs.astral.sh/uv/).

## Layout

Skills are mirrored here from a private authoring source by `scripts/sync_skills.py` per the allowlist in `.claude/skill-manifest.json`; `scripts/validate-skills.py` (run in CI) checks every published folder against the spec. Skill folders are the product — the rest is packaging.

## License

[MIT](LICENSE)
