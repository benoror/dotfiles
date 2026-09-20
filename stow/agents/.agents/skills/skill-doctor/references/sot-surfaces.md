# Skill and transcript surfaces

Source of truth for where this hub copy looks. Keep this next to `supported-harnesses.md`.

## Skill discovery

| Surface | When it is scanned |
| --- | --- |
| `<repo>/.agents/skills` | Always, for selected repos |
| `<repo>/.claude/skills` | Always, for selected repos |
| `<repo>/.codex/skills` | Always, for selected repos |
| `~/.agents/skills` | `--include-global-skills` and a coding harness (`auto` / `all` / coding id) |
| `~/.claude/skills` | same |
| `~/.codex/skills` | same |
| `~/.pi/agent/skills`, `~/.grok/skills`, `~/.zcode/skills` | same, when that home is set |
| `/home/box/agent-data/workflows` | `--include-global-skills` and `--harness grok_bot` only |
| `--skills-dir PATH` | User-asked extras, including a mix of hub and fleet workflows |

Do not scan `~/.cursor/plugins/**` (pstack). That plugin stays Cursor-local. See the agents REGISTRY.

## Transcript surfaces

| Collector | Default root | File pattern | Notes |
| --- | --- | --- | --- |
| `claude` | `~/.claude/projects` | `*/*.jsonl` | Sidechains under `*/subagents/` |
| `codex` | `~/.codex` | `sessions/**/rollout-*.jsonl` | Also `archived_sessions` |
| `warp` | OS channel data | `warp.sqlite` | Read-only |
| `pi` | `~/.pi/agent/sessions` | `*/*.jsonl` | No child sessions |
| `grok` | `~/.grok/sessions` | `*/*/chat_history.jsonl` | Grok Build, not grok_bot |
| `zcode` | `~/.zcode/cli/rollout` | `model-io-*.jsonl` | Last request window only |
| `cursor` | `~/.cursor/projects` | `*/agent-transcripts/**/*.jsonl` | Best-effort. See unknowns. |
| `grok_bot` | `/home/box/agent-data/agent-transcripts` | `<uuid>/<uuid>.jsonl` | Same stem as the directory. Stable. |

## Cursor path unknowns (best-effort, Mac-primary)

This cloud VM does not ship a live Mac Cursor layout. The adapter is locked with synthetic JSONL fixtures.

Probed, in order:

1. `--cursor-home` (default `CURSOR_CONFIG_DIR` or `~/.cursor`)
2. `~/.cursor/projects/<encoded-project>/agent-transcripts/<id>.jsonl`
3. `~/.cursor/projects/<encoded-project>/agent-transcripts/<id>/<id>.jsonl`
4. On Darwin: `~/Library/Application Support/Cursor/User/globalStorage`
5. On Linux: `~/.config/Cursor/User/globalStorage` (or `$XDG_CONFIG_HOME/Cursor/User/globalStorage`)

v1 reads JSONL only. It does **not** decode:

- `state.vscdb` / `cursorDiskKV` protobuf
- `~/.cursor/chats/*/store.db`
- `composerData` / `bubbleId` blobs

Published CLI JSONL (deja-vu, last verified 2026-07-17) uses `role` plus `message.content` parts. If files exist but the first records are not that shape, inventory `sources.cursor.status` is `format_unknown` and no sessions are scored.

Encoded project folders drop the leading slash and turn `/` into `-`. Hyphens that were already in the path cannot be recovered. Treat `cwd` as a hint.

Child transcripts are not a published Cursor contract. Paths whose names contain `subagent` are excluded unless `--include-subagents`.

## Grok Bot contract (verified 2026-09-20)

- Root: `/home/box/agent-data/agent-transcripts/`
- Pattern: `<uuid>/<uuid>.jsonl` (same stem as the directory)
- UUID folders are fleet bots. `sand-subagent-*` folders are child runs.
- Line schema: `{"role": "user"|"assistant"|"tool", "message": {"content": [{"type": ..., "text": ...}, ...]}}`
- Privacy: local only. Never upload transcripts. Tests use synthetic fixtures only.

## Privacy

Everything runs locally. Never upload transcripts, session files, or excerpts. The shareable artifact is the HTML report the user chooses to post.
