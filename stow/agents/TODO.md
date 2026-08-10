# Agents package TODO

Deferred work for `~/dotfiles/stow/agents`.
Not installed by Stow (see `.stow-local-ignore`).

## Cross-machine config sync

Do **not** Dropbox-sync whole `~/.cursor`, `~/.claude`, or `~/.codex` trees (caches, locks, secrets, machine paths).

Rely on vendor accounts for chats/sessions (Claude, ChatGPT, Perplexity).
Ship textual config through this package + git.

- [ ] Stow Cursor MCP: `.cursor/mcp.json` → `~/.cursor/mcp.json` (no secrets in git; use 1Password / env where needed).
- [ ] Stow curated Claude Code settings: `.claude/settings.json` (strip tokens; document required local secrets).
- [ ] Optional: Stow Claude Desktop MCP JSON under `Library/Application Support/Claude/claude_desktop_config.json`.
- [ ] Optional: Stow stable Codex config files only — never the whole `~/.codex` SQLite/state tree.
- [ ] Enable Cursor Settings Sync on each Mac for IDE settings/keybindings/snippets/extensions UI.
- [ ] Keep Cursor User Rules as the global Cursor channel (do not require `~/.cursor/AGENTS.md`).
- [ ] Decide personal vs work account boundaries (shared login syncs sessions; isolate work if required).
- [ ] Optional later: `make cursor-extensions` from a tracked extension list (install missing; do not sync `~/.cursor/extensions/`).
- [ ] Leave Perplexity Personal Computer model/cache dirs local-only.

## Skills / commands / memory

Inspired by [kau.sh — Keep your AGENTS.md in sync](https://kau.sh/blog/agents-md/) (user-level SoT + thin project scaffolding).

- [ ] Add personal skills under `.agents/skills/*/SKILL.md` (highest-ROI next step).
- [ ] Add reusable commands under `.agents/commands/` (or tool-native command dirs wired from the hub).
- [ ] Wire hub skills/commands into Claude / Cursor / Codex / OpenCode load paths (Stow or documented symlinks).
- [ ] Keep global hub structure simple; do not mirror the full project `.agents/` layout at user level.
- [ ] Add shared rules under `.agents/rules/` only when a rule applies across many repos.
- [ ] Decide memory location (Claude memory vs hub `memory/`) and document it.
- [ ] Port high-value prompts from [Prompt Engineering Cheatsheet](/Users/benoror/vaults/trivelta/Agentic%20Workflows/Prompt%20Engineering%20Cheatsheet.md) into skills where reuse pays off.
- [ ] Optional skill: `/initialize` (or similar) to draft a first project `AGENTS.md` from repo analysis.
- [ ] Optional later: project `.agents/dox/` (or similar) with semantic prefixes (`plan-`, `spec-`, `handoff-`) for agent-authored artifacts — only if the need shows up.

Candidate skill sources (from vault todos / repos):

- [ ] `/grill-me` and other [mattpocock/skills](https://github.com/mattpocock/skills)
- [ ] Anthropic / Cursor / skills.sh catalogs worth pinning personally
- [ ] Repo-local skills already used in `~/code/kamek-ai/.agents/skills` — decide global vs project

## Tool entrypoints

- [ ] Optional: Stow Gemini CLI shim `.gemini/GEMINI.md` → hub (see [Zenn — reusing agent settings with dotfiles](https://zenn.dev/sotono/articles/3605803241a3e9?locale=en)) if Gemini CLI is in regular use.

## Repo overlays

- [ ] Opt-in `make agents-project dir=…` (kau.sh-style): local `CLAUDE.md` shim, `.agents/{skills,commands,…}` as needed — never blanket every `~/code/*` repo.
- [ ] Prefer nested/package `AGENTS.md` over bloating repo roots (keep roots lean).
- [ ] Do **not** blanket-stow into every `~/code/*` repo by default.

## Hygiene

- [ ] Periodic context audit: ask the agent which instruction files it is using; prune hub / `RESOLVER.md` / project guides for redundancy and ambiguity ([kau.sh](https://kau.sh/blog/agents-md/)).

## Done

- [x] Review `mba15m4:~/code/**` and `mbp14m4:~/code/**`; fold lean rules into hub — ✅ 2026-08-09
- [x] Migrate off `symlink-agents.sh` to Stow-owned tool entrypoints + root Makefile — ✅ 2026-08-09

## Explicitly out of scope

- Double hub at `~/code/agents/`
- Justfile (Make is enough for bootstrap)
- Required `~/.cursor/AGENTS.md` (use Cursor User Rules)
- Dropbox-sync of live tool home directories (`~/.cursor`, `~/.claude`, `~/.codex`, Perplexity caches)
- Mandatory project scaffolding on every repo
- Zenn-style `install.sh` with `rm -f` + `ln` (Stow + Make already covers this)
