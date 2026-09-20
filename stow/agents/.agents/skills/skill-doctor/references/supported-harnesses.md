# Supported harnesses

This file is the single source of truth for harness support in `skill-doctor`. Reference it instead of repeating harness lists in `SKILL.md`.

## Startup gate

| Harness | Collector ID | Local conversation source |
| --- | --- | --- |
| Warp | `warp` | Read-only Warp conversation databases |
| Claude Code | `claude` | Project-history JSONL |
| Codex | `codex` | Rollout JSONL |
| Pi | `pi` | Pi agent JSONL (`~/.pi/agent/sessions`) |
| Grok Build | `grok` | Grok Build chat_history JSONL (`~/.grok/sessions`) |
| ZCode | `zcode` | ZCode model-io rollout (`~/.zcode/cli/rollout`) |
| Cursor | `cursor` | Best-effort JSONL under `~/.cursor/projects/*/agent-transcripts` (Mac-primary) |
| Grok Bot | `grok_bot` | Fleet transcripts at `/home/box/agent-data/agent-transcripts/<uuid>/<uuid>.jsonl` |

At startup, identify the harness executing the skill from the runtime context. Do not infer it from conversation files found on disk.

If the executing harness is not listed above, or cannot be identified confidently, stop before creating a report directory or reading conversation history. Tell the user:

> skill-doctor currently supports Warp, Claude Code, Codex, Pi, Grok Build, ZCode, Cursor, and Grok Bot. This run appears to be using an unsupported harness, so no conversations were read.

## Collector source selection

- `--harness auto` scans every locally available supported source and is the default.
- `--harness all` also requests every supported source.
- `--harness <collector-id>` restricts collection to one source from the table.
- A report containing one source uses its collector ID in `inventory.json`; a report containing multiple sources uses `mixed`.

Harness-specific source overrides:

- `--claude-home PATH`: nonstandard Claude Code configuration directory.
- `--codex-home PATH`: nonstandard Codex home.
- `--warp-db PATH`: explicit Warp database; repeatable.
- `--warp-data-dir PATH`: nonstandard Warp channel-data directory.
- `--pi-home PATH`: nonstandard Pi agent home (default `~/.pi/agent`).
- `--grok-home PATH`: nonstandard Grok Build home (default `~/.grok`).
- `--zcode-home PATH`: nonstandard ZCode home (default `~/.zcode`).
- `--cursor-home PATH`: nonstandard Cursor config directory (default `CURSOR_CONFIG_DIR` or `~/.cursor`).
- `--grok-bot-home PATH`: Grok Bot transcript root (default `/home/box/agent-data/agent-transcripts`).

`--include-subagents` includes child runs. For Grok Bot, directories named `sand-subagent-*` are child runs and stay excluded unless this flag is set.

## Skill locations

Project skills are discovered from:

- `.agents/skills`
- `.claude/skills`
- `.codex/skills`

Global skills depend on the selected harness family when `--include-global-skills` is set:

- Coding harnesses (`auto`, `all`, or a coding collector): `~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills`, plus Pi / Grok Build / ZCode `*/skills` under their homes.
- `--harness grok_bot` only: `/home/box/agent-data/workflows`. Do not mix this with the coding hub unless the user passes `--skills-dir`.
- Cursor adds no extra global root. Project and hub skills cover it.
- pstack (`~/.cursor/plugins/**`) is out of band. Do not scan it.

See `sot-surfaces.md` for path unknowns and the Cursor probe list.
