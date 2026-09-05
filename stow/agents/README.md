# Agents stow package

Personal agent hub for coding tools.

Follow ASD-STE100 Simplified Technical English for technical text. These rules apply to all prose you write: docs, commit messages, PR descriptions, reports, replies, etc:
- Use approved words only. Each word has one meaning.
- Use one word for one idea. Do not use two words for the same thing.
- Write short sentences. Use 20 words or less for instructions.
- Use active voice. Write "Turn the switch", not "The switch must be turned".
- Write short paragraphs. Keep one topic in each paragraph.

`README.md`, `TODO.md`, `REGISTRY.md`, `links.registry`, and `skills-lock.json` stay in the package only (see [`.stow-local-ignore`](.stow-local-ignore)).

## Goal

One Stow package installs the hub and tool entrypoints.
No fan-out script. Bootstrap with Make on each machine.

**Skill map (sources → end locations):** [REGISTRY.md](REGISTRY.md).
**Make fan-out rows:** [links.registry](links.registry) (`make agents-link-sync`).

## Layout

| Path in package | After `make install-agents` | Role |
| --- | --- | --- |
| `.agents/AGENTS.md` | `~/.agents/AGENTS.md` | Canonical personal defaults |
| `.agents/RESOLVER.md` | `~/.agents/RESOLVER.md` | Discovery / precedence playbook |
| `.agents/skills/*` | `~/.agents/skills/*` | Global skills (mattpocock + find-skills + skill-creator + graduated) |
| `.claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | `@~/.agents/AGENTS.md` |
| `.codex/AGENTS.md` | `~/.codex/AGENTS.md` | Symlink → hub |
| `.config/opencode/AGENTS.md` | `~/.config/opencode/AGENTS.md` | Symlink → hub |
| `.config/agents/AGENTS.md` | `~/.config/agents/AGENTS.md` | Generic fallback symlink → hub |

`skills-lock.json` stays in the package (stow-ignored) for `npx skills experimental_install` restore.

Cursor is **not** part of this package. Use Cursor User Rules for global Cursor prefs. Install **pstack** with `/add-plugin pstack` on each Mac.

## Architecture

```mermaid
flowchart LR
  pkg["~/dotfiles/stow/agents"] -->|"make install-agents"| home["$HOME"]
  home --> hub["~/.agents/AGENTS.md"]
  home --> resolver["~/.agents/RESOLVER.md"]
  home --> claude["~/.claude/CLAUDE.md"]
  home --> codex["~/.codex/AGENTS.md"]
  home --> opencode["~/.config/opencode/AGENTS.md"]
  home --> generic["~/.config/agents/AGENTS.md"]
  claude -->|"@~/.agents/AGENTS.md"| hub
  codex -->|symlink| hub
  opencode -->|symlink| hub
  generic -->|symlink| hub
```

### Config layers

1. **Global personal** — this package.
2. **Project / team** — committed repo `AGENTS.md` / `CLAUDE.md` / rules.
3. **Local override** — gitignored `CLAUDE.local.md` / `AGENTS.override.md`.

## Bootstrap (new machine)

```bash
git clone <dotfiles-remote> ~/dotfiles
cd ~/dotfiles
make install-agents   # or: make agents-install
make agents-verify
```

Needs GNU Stow. Homebrew: `brew install stow`.

### Day-to-day

```bash
cd ~/dotfiles
make restow-agents    # after package edits
make agents-verify
make uninstall-agents # remove package links only
```


Dry-run before a risky restow:

```bash
stow -n -v -d ~/dotfiles/stow -t ~ agents
```

## Conflicts

If Stow reports a conflict, an existing file already sits at the destination.
Back it up or remove it, then `make agents-restow`.
Do not use `stow --adopt` unless you mean to pull that file into the package.

## Cursor

| Tool | Global mechanism |
| --- | --- |
| Claude Code | `~/.claude/CLAUDE.md` → `@~/.agents/AGENTS.md` |
| Codex | `~/.codex/AGENTS.md` → hub |
| OpenCode | `~/.config/opencode/AGENTS.md` → hub |
| Cursor | User Rules (not this package) |
| Generic | `~/.config/agents/AGENTS.md` → hub |

## Sources for AGENTS.md content

Patterns from:

- `mba15m4:~/code/**`
- `mbp14m4:~/code/**`

Keep the hub lean. Large team standards (e.g. Trivelta) stay in those repos; `RESOLVER.md` only points agents there.

Workflow modes mirror the vault Prompt Engineering Cheatsheet (`/research`, `/implement`, `/refactor`, `/test`, `/debug`, `/document`).

## Skills

Full inventory and end locations: **[REGISTRY.md](REGISTRY.md)**.

Vendored under `.agents/skills/` (universal agent path). After restow they appear at `~/.agents/skills/`.

| Source | Skills (summary) |
| --- | --- |
| [mattpocock/skills](https://www.skills.sh/mattpocock/skills) | grill / tdd / review / implement / handoff / … (see registry) |
| [vercel-labs/skills](https://www.skills.sh/vercel-labs/skills/find-skills) | find-skills |
| [anthropics/skills](https://www.skills.sh/anthropics/skills/skill-creator) | skill-creator |
| Graduated (Trivelta) | pr-description (generic) |
| [github/gh-stack](https://www.skills.sh/github/gh-stack/gh-stack) | gh-stack (stacked PRs; also `gh extension install github/gh-stack`) |
| [DietrichGebert/ponytail](https://www.skills.sh/dietrichgebert/ponytail/ponytail) | ponytail pack (YAGNI / lazy senior-dev) |
| [steveruizok gist](https://gist.github.com/steveruizok/83ae5c53f2784ebf8f5fe0a3fb94480f) | product-description (outside-in behavior spec) |
| [humanlayer/skills](https://www.skills.sh/humanlayer/skills/show-me) | show-me (diagrams and focused HTML) |

Per-skill sources and short summaries: [REGISTRY.md](REGISTRY.md).

Refresh / add:

```bash
cd ~/dotfiles/stow/agents
npx skills add mattpocock/skills -s <name> --copy -y -a universal
make -C ~/dotfiles agents-restow
# then update REGISTRY.md + skills-lock.json
```

The product-description gist has no GitHub clone for `npx skills`. Install it with the gist script:

```bash
cd ~/dotfiles/stow/agents
curl -fsSL https://gist.githubusercontent.com/steveruizok/83ae5c53f2784ebf8f5fe0a3fb94480f/raw/install.sh \
  | sh -s -- .agents/skills/product-description
```

### Vaults and code as consumers

Vault/code trees stay outside this repo. Link graduated hub skills into targets:

```bash
# One-shot
make agents-link-vault VAULT=~/vaults/personal
make agents-link-code CODE=~/code/solopreneur SKILLS='grill-me tdd ask-matt'

# Posterity (checked into package, stow-ignored):
#   REGISTRY.md     — human map
#   links.registry  — Make rows
make agents-link-sync          # re-link every row on a new machine
make agents-link-code CODE=~/code/foo APPEND=1   # link + append registry row
```

Defaults: vaults get `find-skills skill-creator pr-description`; code gets `grill-me tdd ask-matt pr-description` (override with `SKILLS=`). Does not overwrite existing non-symlink files.

`make verify` only checks SAFE stow package dirs exist. Use `agents-verify` for hub entrypoints — no per-package `verify-*` for zsh/nvim/etc.

## Related

- Skill / location map: [REGISTRY.md](REGISTRY.md)
- Make link rows: [links.registry](links.registry)
- Phased plan: [TODO.md](TODO.md)
- Make entrypoints: [../../Makefile](../../Makefile)
