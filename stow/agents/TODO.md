# Agents package TODO

Phased skill adoption for the global hub, `~/code`, vaults, and future Hermes/OpenClaw mastermind.
Not installed by Stow (see `.stow-local-ignore`).

Sources: [skills.sh](https://www.skills.sh/), [kau.sh AGENTS.md](https://kau.sh/blog/agents-md/), Trivelta scan on `mbp14m4` (2026-08-11).

## Vaults as maintenance targets?

**Yes as consumers, not as content inside this repo.**

- Do **not** copy vault notes into `dotfiles`.
- Do **graduate** portable skills/rules into `stow/agents/.agents/skills/` (or hub rules), then optionally symlink/copy into:
  - `~/vaults/personal/.agents/skills/`
  - `~/vaults/trivelta/.agents/skills/` (if/when present)
  - `~/vaults/openclaw/workspace/skills/`
- Human map of sources → end locations: [REGISTRY.md](REGISTRY.md)
- Make fan-out rows: [links.registry](links.registry) → `make agents-link-sync`

Personal vault skills (qmd, clip, kb-triage, …) stay vault-owned until intentionally graduated.

---

## Phase A — Global `stow/agents` (coding hub) — done 2026-08-11 (pstack Cursor install still manual)

### Matt Pocock ([skills.sh/mattpocock/skills](https://www.skills.sh/mattpocock/skills))

Install into `.agents/skills/` (vendor/copy; keep hub lean).

Core (recommended):

- [x] `grill-me` / `grilling` ✅ 2026-08-11
- [x] `grill-with-docs` ✅ 2026-08-11
- [x] `tdd` ✅ 2026-08-11
- [x] `diagnosing-bugs` ✅ 2026-08-11
- [x] `handoff` / `claude-handoff` ✅ 2026-08-11
- [x] `code-review` ✅ 2026-08-11
- [x] `improve-codebase-architecture` ✅ 2026-08-11
- [x] `writing-for-agents` ✅ 2026-08-11
- [x] `setup-matt-pocock-skills` (run per repo that needs tracker wiring) ✅ installed in hub 2026-08-11
- [x] `ask-matt` (router) ✅ 2026-08-11

Also popular / high-signal:

- [x] `implement` ✅ 2026-08-11
- [x] `to-spec` / `to-tickets` ✅ 2026-08-11
- [x] `prototype` ✅ 2026-08-11
- [x] `research` ✅ 2026-08-11
- [x] `wayfinder` (multi-session maps) ✅ 2026-08-11
- [x] `resolving-merge-conflicts` ✅ 2026-08-11
- [ ] `writing-great-skills` / `write-a-skill` — prefer anthropics `skill-creator` for now

### Cursor daily driver ([skills.sh/cursor/plugins](https://www.skills.sh/cursor/plugins))

Cursor plugins stay **Cursor-local** (not Stow-mirrored wholesale).

- [ ] Install **pstack**: `/add-plugin pstack` then `/setup-pstack` — [setup-pstack](https://www.skills.sh/cursor/plugins/setup-pstack) · [repo](https://github.com/cursor/plugins/tree/main/pstack)
- [ ] Default entry: `/poteto-mode` for non-trivial Cursor work
- [ ] REGISTRY “Cursor — pstack”: add 2 recommended skills after Ben confirms the names (tweet pending). Do not invent names.
- [ ] Skim other popular Cursor plugin skills for daily use:
  - [ ] `deslop` / `unslop`
  - [ ] `review-and-ship` / `make-pr-easy-to-review` / `get-pr-comments`
  - [ ] `fix-ci` / `loop-on-ci`
  - [ ] `fix-merge-conflicts`
  - [ ] `how` / `why` / `architect` / `interrogate` (if not covered by pstack mode)
  - [ ] `thermo-nuclear-code-quality-review` (heavy review; situational)

### Discovery / authoring (also feed Phase C)

- [x] [find-skills](https://www.skills.sh/vercel-labs/skills/find-skills) ✅ 2026-08-11
- [x] [skill-creator](https://www.skills.sh/anthropics/skills/skill-creator) ✅ 2026-08-11

### Graduated from Trivelta (`mbp14m4`)

- [x] **Graduate `pr-description`** → generic hub skill ✅ 2026-08-11  
  Source: `~/code/trivelta/trivelta-admin-services/services/admin_panel/admin_panel_v2/.agents/skills/pr-description`
- [ ] Steal idea (not full skill): **context pruning** from `pam-v2-context-pruning` → hub doc note (README prevails; agent artifacts stay non-duplicative)
- [x] Keep **project-local** (do not graduate) — decided 2026-08-11:
  - `pam-permissions` (PAM RBAC)
  - `athena-clickhouse-parity` (Rebet dbt)
  - `check-ci-status` / `check-sync` (ai-distribution)
  - FastAPI/typer vendor skills under `.venv`

### Hub wiring

- [x] After installs: `make agents-restow` + `make agents-verify` ✅ 2026-08-11
- [x] Document skill load paths in [README.md](README.md) ✅ 2026-08-11
- [x] Point `AGENTS.md` at skill discovery (progressive disclosure) ✅ 2026-08-11
- [x] `make agents-link-vault VAULT=~/vaults/personal` ✅ 2026-08-11

---

## Phase B — `~/code` pilots

### Frontend / design

- [x] [anthropics/frontend-design](https://www.skills.sh/anthropics/skills/frontend-design) — on kamek-ai ✅ 2026-08-11
- [x] [vercel-labs/web-design-guidelines](https://www.skills.sh/vercel-labs/agent-skills/web-design-guidelines) — on kamek-ai ✅ 2026-08-11

### React / Next (kamek and similar)

- [x] [vercel-react-best-practices](https://www.skills.sh/vercel-labs/agent-skills/vercel-react-best-practices) — already on kamek ✅
- [x] [vercel-composition-patterns](https://www.skills.sh/vercel-labs/agent-skills) — on kamek-ai ✅ 2026-08-11
- [ ] [vercel-react-view-transitions](https://www.skills.sh/vercel-labs/agent-skills) when shipping view transitions
- [ ] [vercel-react-native-skills](https://www.skills.sh/vercel-labs/agent-skills) only if RN work appears
- [ ] Optional deploy: `deploy-to-vercel` / `vercel-cli-with-tokens` / `vercel-optimize` (secrets via env/1Password)

### Backend / devops

- [x] Prefer **mattpocock** process skills (tdd, diagnose, implement, review) over new mega-packs ✅ hub Phase A
- [ ] Addy Osmani cherry-picks only if gaps remain after mattpocock ([skills.sh/addyosmani/agent-skills](https://www.skills.sh/addyosmani/agent-skills)):
  - [ ] `security-and-hardening`
  - [ ] `ci-cd-and-automation`
  - [ ] `observability-and-instrumentation`
  - [ ] `api-and-interface-design`
  - [ ] Skip duplicates of grill/tdd/review/planning already covered

### Anthropics other

- [x] [skill-creator](https://www.skills.sh/anthropics/skills/skill-creator) — in hub ✅ 2026-08-11 (also Phase C)
- [ ] `mcp-builder` when adding MCP servers
- [ ] `webapp-testing` for browser E2E-ish agent loops
- [ ] Skip Office doc skills (`pptx`/`pdf`/`docx`/`xlsx`) unless needed

### Pilot repos

- [x] `~/code/solopreneur` — thin AGENTS.md + grill-me/tdd via hub ✅ 2026-08-11
- [x] `~/code/kamek-ai` — vercel React + frontend-design + web-design-guidelines + composition-patterns ✅ 2026-08-11
- [ ] Opt-in `make agents-project dir=…` later (not blanket)

---

## Phase C — Future mastermind (Hermes / OpenClaw)

Direction: **gstack** as coding factory + ClawHub conversational slice; not gbrain unless vault+QMD fails.

- [x] Install gstack via upstream clone + `./setup` → `~/.claude/skills/gstack` ✅ 2026-08-11 (needs Bun; installed via Homebrew)
- [x] Wire OpenClaw workspace `AGENTS.md` “Coding Tasks” → Claude Code + gstack ✅ 2026-08-11
- [ ] Tell OpenClaw agent `install gstack for openclaw` if ACP spawn still needs host glue (artifacts generated; lite skills linked)
- [x] ClawHub lite first: `gstack-openclaw-office-hours`, `ceo-review`, `investigate`, `retro` ✅ linked 2026-08-11
- [x] Install [vercel-labs/skills/find-skills](https://www.skills.sh/vercel-labs/skills/find-skills) — also in coding hub ✅ 2026-08-11; skim [skills.sh](https://www.skills.sh/) before adding packs
- [x] Install [anthropics/skill-creator](https://www.skills.sh/anthropics/skills/skill-creator) — also in coding hub ✅ 2026-08-11
- [x] Reuse openclaw vault lessons (`SOUL`/`USER`/`MEMORY`/downshift/heavy-lift); do not replace with gbrain by default ✅ documented
- [ ] Revisit **gbrain** only if memory/search needs exceed Obsidian + QMD
- [ ] Optional: `./setup --host hermes` when Hermes is the daily mastermind runtime
---

## Cross-machine config sync

Do **not** Dropbox-sync whole `~/.cursor`, `~/.claude`, or `~/.codex` trees.

- [ ] Stow Cursor MCP: `.cursor/mcp.json` → `~/.cursor/mcp.json` (no secrets in git)
- [ ] Stow curated Claude Code `settings.json` (strip tokens)
- [ ] Optional: Claude Desktop MCP JSON under Application Support
- [ ] Optional: stable Codex config files only
- [ ] Cursor Settings Sync on each Mac
- [ ] Personal vs work account boundaries
- [ ] Optional: `make cursor-extensions` from a tracked list
- [ ] Perplexity PC caches local-only

---

## Hygiene

- [ ] Periodic: ask agent which instruction files it loaded; prune hub / RESOLVER
- [ ] Prefer nested package `AGENTS.md` over bloating repo roots
- [ ] Evaluate potential own skills to extract/graduate from `~/vaults/trivelta/Agentic Workflows/Prompt Engineering Cheatsheet.md` (modes already lean in hub AGENTS; look for skill-sized workflows beyond `/research`–`/document`)

## Done

- [x] Review `mba15m4:~/code/**` and `mbp14m4:~/code/**` for lean AGENTS rules — ✅ 2026-08-09
- [x] Migrate off `symlink-agents.sh` to Stow + Makefile — ✅ 2026-08-09
- [x] Evaluate gstack / gbrain / mattpocock / pstack + skills.sh catalogs — ✅ 2026-08-11
- [x] Scan Trivelta agentic artifacts on `mbp14m4` for graduation — ✅ 2026-08-11
- [x] Phase A: vendor mattpocock + find-skills + skill-creator + pr-description into hub — ✅ 2026-08-11
- [x] Vault maintenance: `make agents-link-vault` (consumers, not content dump) — ✅ 2026-08-11

## Explicitly out of scope

- Double hub at `~/code/agents/`
- Justfile (Make is enough)
- Required `~/.cursor/AGENTS.md`
- Dropbox-sync of live tool home dirs
- Whole gstack / gbrain inside the lean coding hub by default
- Graduating PAM/dbt/distribution-specific skills to global
