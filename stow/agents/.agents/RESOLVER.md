# Resolver

How to find and prefer instructions. Keep this short.
Imported content still uses context — do not turn this into a dump of repo facts.

## Playbook

Before large changes:

1. Find the repository root (`git rev-parse --show-toplevel` when in a git work tree).
2. Load project instructions in order when present:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `CLAUDE.local.md` (personal, gitignored)
   - nested guides near the files you edit (package/app `AGENTS.md`, `ROUTER.md`, `docs/`)
3. Prefer project facts over these personal defaults when they conflict.
4. Prefer deeper, nearer guides over higher, broader ones.
5. Prefer the explicit user task over defaults.
6. Work under `.worktrees/` still follows that repo’s root guides.
7. Before editing, name which instruction files and domain rules apply.

## Domain signals

| Signal | Prefer |
| --- | --- |
| UI, `*.tsx` / `*.jsx`, Next App Router | Frontend project guide; shared UI packages; lint/typecheck |
| APIs, Rails, Python/FastAPI, DB, workers | Backend project guide; tenant/auth boundaries; focused tests; lint/format |
| `*.ts` shared packages | Nearest package `AGENTS.md` / README |
| dbt / ClickHouse / Athena | Directory `AGENTS.md` + `ROUTER.md` first |
| Infra / Terraform / CI | Ask before production changes |

## Repos under ~/code

Hints only — always open that repo’s own `AGENTS.md`:

| Path pattern | Notes |
| --- | --- |
| `~/code/kamek-ai` | Root + app/package guides |
| `~/code/spoint/*` | Repo `AGENTS.md` / `.agents` router |
| `~/code/techinmuebles114/*` | Docs-first scaffolds |
| `~/code/benoror/*` | Personal; prefer each repo guide |
| `~/code/procevi/*` | Commit cadence when the user asks for commits |
| `~/code/trivelta/*` | In-repo Engineering Standards (branches, PR size, lint, flags, tests) |

Do not copy team standards into the personal hub.
