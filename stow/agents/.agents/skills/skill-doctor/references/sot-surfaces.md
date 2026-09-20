# Source-of-truth surfaces

Map skill-doctor conversation and skill scopes to the coding hub, project trees, and Grok Stow workflows.

Doctor never writes into these trees. It only reads skills and local transcripts, then writes a scratch report directory.

## Conversation scope (what to grade)

Chosen at skill startup, then passed to `collect_sessions.py`:

| Startup choice | Collector flags | Meaning |
| --- | --- | --- |
| Conversations in this repository | `--repo $REPO` | Sessions whose cwd belongs to the current git root |
| Choose projects | `--repo PATH` (repeat) | Combined report across those git roots |
| All conversations | `--all-conversations` | Do not filter by project |

Project matching uses the session cwd when present. `cursor`, `grok_bot`, and `zcode` may omit cwd; those sessions still count for project-scoped runs (`cwd_optional`).

## Skill scope (what to evaluate)

| Startup choice | Collector flags | Roots |
| --- | --- | --- |
| Project skills only | (default) | Skills under each in-scope repo |
| Project + global skills | `--include-global-skills` | Project roots plus the global trees below |

## Where skills live

| Surface | End location | Doctor role |
| --- | --- | --- |
| Coding hub | `~/.agents/skills/<name>/` (Stow from `stow/agents/.agents/skills/`) | Global skills for every harness. Always this hub path; not Grok Stow. |
| Project | `<repo>/.agents/skills`, `<repo>/.claude/skills`, `<repo>/.codex/skills`, `<repo>/.cursor/skills` | Project skills for `--repo` / inferred repos |
| Claude / Codex / Pi / Grok Build / ZCode homes | `~/.claude/skills`, `~/.codex/skills`, `~/.pi/agent/skills`, `~/.grok/skills`, `~/.zcode/skills` | Extra global roots when `--include-global-skills` |
| Cursor (best-effort) | `~/.cursor/skills`, `~/.cursor/skills-cursor` | Extra global roots when `--include-global-skills` |
| Grok Stow workflows | `/home/box/agent-data/workflows` | Extra global roots **only for `grok_bot`** when `--include-global-skills` |

`--skills-dir PATH` adds more roots for any harness.

## Grok Bot vs coding hub

Grok Bot transcripts default to `/home/box/agent-data/agent-transcripts/`.

Grok Stow skills default to `/home/box/agent-data/workflows`. Those are fleet/workflow skills on the box. They are **not** the coding hub.

The coding hub stays `~/.agents/skills` (this package). A `grok_bot` run with `--include-global-skills` scans both: hub first (shared `discover_skills`), then workflows via the `grok_bot` plugin.

Override with `--grok-bot-home` and `--grok-bot-workflows`.

## Do not upload

Transcripts, session files, and excerpts stay on the local machine. The only shareable artifact is the HTML report the user chooses to keep or post.
