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
- [ ] Repo-local skills already used in `~/code/kamek-ai/.agents/skills` (react-best-practices, shadcn, …) — decide what belongs global vs project

## Repo packages under ~/code

- [ ] Optional opt-in personal overlays per repo (`CLAUDE.local.md`, gitignored `.agents` links).
- [ ] Do **not** blanket-stow into every `~/code/*` repo by default.
- [ ] Re-check remote `~/code/**` on `mbp14m4` when SSH works; merge any extra common rules into hub `AGENTS.md` if they stay lean.
  - 2026-08-09: Tailscale showed host active, but TCP/22 timed out (ping loss). Enable Remote Login / `sshd` on mbp14m4, then re-run review.

## Content seeding

- [ ] Grow `RESOLVER.md` rows as stable personal overrides appear.
- [ ] Keep hub `AGENTS.md` lean; push detail into skills and project guides.

## Explicitly out of scope

These earlier ideas stay dropped. The hub + fan-out script scales better:

- Stow-everything into `~/.claude` / `~/.cursor` trees
- Double hub at `~/code/agents/`
- `agents-stow` Make/just wrapper for many repo packages
