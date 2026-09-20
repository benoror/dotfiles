# Supported harnesses

This file is the single source of truth for harness support in `skill-doctor`. Reference it instead of repeating harness lists in `SKILL.md`.

Based on / forked from [Warp's skill-doctor](https://github.com/warpdotdev/common-skills/tree/main/.agents/skills/skill-doctor)
in [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills).
This hub copy adds Cursor (`cursor`) and Grok Bot (`grok_bot`).

## Startup gate

| Harness | Collector ID | Local conversation source |
| --- | --- | --- |
| Warp | `warp` | Read-only Warp conversation databases |
| Claude Code | `claude` | Project-history JSONL |
| Codex | `codex` | Rollout JSONL |
| Pi | `pi` | Pi agent JSONL (`~/.pi/agent/sessions`) |
| Grok Build | `grok` | Grok Build chat_history JSONL (`~/.grok/sessions`) |
| ZCode | `zcode` | ZCode model-io rollout (`~/.zcode/cli/rollout`) |
| Cursor | `cursor` | Best-effort agent-transcript JSONL (see path discovery) |
| Grok Bot | `grok_bot` | `<uuid>/<uuid>.jsonl` under the Grok Bot transcript root |

At startup, identify the harness executing the skill from the runtime context. Do not infer it from conversation files found on disk.

Optional helper:

```bash
python3 "$SKILL_ROOT/scripts/collect_sessions.py" --detect-runtime
```

If the executing harness is not listed above, or cannot be identified confidently, stop before creating a report directory or reading conversation history. Tell the user:

> skill-doctor currently supports Warp, Claude Code, Codex, Pi, Grok Build, ZCode, Cursor, and Grok Bot. This run appears to be using an unsupported harness, so no conversations were read.

## Collector source selection

- `--harness auto` scans every locally available supported source and is the default.
- `--harness all` also requests every supported source.
- `--harness <collector-id>` restricts collection to one source from the table.
- A report containing one source uses its collector ID in `inventory.json`; a report containing multiple sources uses `mixed`.

Harness-specific source overrides:

- `--claude-home PATH` — nonstandard Claude Code configuration directory.
- `--codex-home PATH` — nonstandard Codex home.
- `--warp-db PATH` — explicit Warp database; repeatable.
- `--warp-data-dir PATH` — nonstandard Warp channel-data directory.
- `--pi-home PATH` — nonstandard Pi agent home (default `~/.pi/agent`).
- `--grok-home PATH` — nonstandard Grok Build home (default `~/.grok`).
- `--zcode-home PATH` — nonstandard ZCode home (default `~/.zcode`).
- `--cursor-home PATH` — Cursor config root (default `CURSOR_HOME` or `~/.cursor`).
- `--cursor-transcripts-dir PATH` — explicit Cursor transcript directory.
- `--grok-bot-home PATH` — Grok Bot transcript root (default `/home/box/agent-data/agent-transcripts`).
- `--grok-bot-workflows PATH` — Grok Stow skills root used with `--include-global-skills` (default `/home/box/agent-data/workflows`).

## Skill locations

Project skills are discovered from:

- `.agents/skills`
- `.claude/skills`
- `.codex/skills`
- `.cursor/skills`

Global skills are discovered from the corresponding directories under the user's home and configured harness homes when `--include-global-skills` is set:

- Coding hub: `~/.agents/skills` (this package after Stow)
- `~/.claude/skills`, `~/.codex/skills`
- Pi's skill directory under its agent home (default `~/.pi/agent/skills`)
- Grok Build's `~/.grok/skills`
- ZCode's `~/.zcode/skills`
- Cursor: `~/.cursor/skills` and `~/.cursor/skills-cursor`
- Grok Bot / Grok Stow: `/home/box/agent-data/workflows` (see [sot-surfaces.md](sot-surfaces.md))

## Cursor path discovery (best-effort)

Cursor does not publish a stable on-disk conversation schema. The `cursor` plugin scans, when present:

1. `$CURSOR_HOME/projects/*/agent-transcripts/**/*.jsonl` (default `~/.cursor`)
2. `$CURSOR_TRANSCRIPTS_DIR/**/*.jsonl` when that env var or `--cursor-transcripts-dir` is set
3. `/tmp/cursor/cloud-agent-transcripts/**/transcript.json` (cloud-agent dumps)

macOS `~/Library/Application Support/Cursor` composer data lives in sqlite (`state.vscdb`). This collector does **not** decode those databases.

On many CI or cloud VMs those paths are empty. Use `--cursor-transcripts-dir` with synthetic fixtures, or grade another harness. Never commit real Cursor transcripts.

## Grok Bot layout (v1, paths verified stable)

- Root default: `/home/box/agent-data/agent-transcripts/`
- Files: `<uuid>/<uuid>.jsonl` (directory name equals file stem)
- Skip `sand-subagent-*` unless `--include-subagents`
- JSONL lines: `{role: user|assistant|tool, message: {content: [{type, text}, ...]}}`
- `--include-global-skills` also scans `/home/box/agent-data/workflows` (Grok Stow skills)

`grok` (Grok Build) and `grok_bot` (Grok Bot) are different sources. Do not mix their homes.

## Plugin API

Each harness module under `scripts/harnesses/` implements:

| Method | Role |
| --- | --- |
| `detect_runtime` | Is this harness executing now? |
| `list_sessions` | Find session files/records in the lookback window |
| `parse_session` | Normalize one session to the shared transcript shape |
| `discover_skills` | Extra skill roots for this harness |

Normalized transcripts, `inventory.json`, and `report.json` stay compatible with the upstream scorers and HTML renderer.
