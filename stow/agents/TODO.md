# Agents package TODO

Deferred work for `~/dotfiles/stow/agents`.
Not installed by Stow (see `.stow-local-ignore`).

## Skills / rules / memory

- [ ] Add personal skills under `.agents/skills/*/SKILL.md` (or hub-relative paths).
- [ ] Wire skills into Claude / Cursor / Codex skill directories (symlink or document load paths).
- [ ] Add shared rules under `.agents/rules/` when a rule applies across many repos.
- [ ] Decide memory location (Claude memory vs hub `memory/`) and document it.
- [ ] Port high-value prompts from [Prompt Engineering Cheatsheet](/Users/benoror/vaults/trivelta/Agentic%20Workflows/Prompt%20Engineering%20Cheatsheet.md) into skills where reuse pays off.

Candidate skill sources (from vault todos / repos):

- [ ] `/grill-me` and other [mattpocock/skills](https://github.com/mattpocock/skills)
- [ ] Anthropic / Cursor / skills.sh catalogs worth pinning personally
- [ ] Repo-local skills already used in `~/code/kamek-ai/.agents/skills` — decide global vs project

## Repo overlays

- [ ] Optional `make` target for personal `CLAUDE.local.md` / gitignored `.agents` links (opt-in only).
- [ ] Do **not** blanket-stow into every `~/code/*` repo by default.

## Done

- [x] Review `mba15m4:~/code/**` and `mbp14m4:~/code/**`; fold lean rules into hub — ✅ 2026-08-09
- [x] Migrate off `symlink-agents.sh` to Stow-owned tool entrypoints + root Makefile — ✅ 2026-08-09

## Explicitly out of scope

- Double hub at `~/code/agents/`
- Justfile (Make is enough for bootstrap)
- Required `~/.cursor/AGENTS.md` (use Cursor User Rules)
