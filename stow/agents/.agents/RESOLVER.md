# Resolver

When to load extra personal or domain guidance.
Keep paths short. Prefer project `AGENTS.md` over this file when both apply.
Work under `.worktrees/` still follows that repo’s root `AGENTS.md`.

## Frontend

When editing UI, React, Next.js App Router, CSS, or client components:

- Prefer the project frontend `AGENTS.md` or nearest package guide.
- Prefer shared UI packages when the project already uses them.
- Do not invent a second design system.
- Prefer project lint and typecheck (`yarn lint`, `tsc`, etc.) before you claim done.

<!-- Add personal includes later, e.g. @skills/frontend/SKILL.md -->

## Backend

When editing APIs, Rails, Python/FastAPI, DB, migrations, auth, or workers:

- Prefer the project backend `AGENTS.md` and docs under `docs/`.
- Preserve tenant, auth, and validation boundaries the project already uses.
- Add focused tests for model, policy, service, and endpoint changes.
- Prefer project lint/format (e.g. `ruff`) before you claim done.

<!-- Add personal includes later, e.g. @skills/backend/SKILL.md -->

## Language

| Signal | Prefer |
| --- | --- |
| `*.tsx`, `*.jsx`, Next app routes | Frontend rules above |
| `*.rb`, Rails `app/`, `db/` | Backend rules above |
| `*.py`, FastAPI, Alembic | Backend rules above + project Python guide |
| `*.ts` in packages/shared | Project package `AGENTS.md` / README |
| dbt / ClickHouse / Athena | Directory `AGENTS.md` + `ROUTER.md` first |
| Infra / Terraform / CI | Ask before production changes |

## Repos under ~/code

| Path pattern | Notes |
| --- | --- |
| `~/code/kamek-ai` | Read root `AGENTS.md` and app/package guides. |
| `~/code/spoint/*` | Follow each repo’s `AGENTS.md` / `.agents` router. |
| `~/code/techinmuebles114/*` | Prefer docs-first scaffolds; update docs with code. |
| `~/code/benoror/*` | Personal projects; still prefer each repo’s own guide. |
| `~/code/procevi/*` | Follow repo commit-cadence rules when the user asks for commits. |
| `~/code/trivelta/*` | Follow that repo’s `AGENTS.md` (shared Trivelta Engineering Standards: branches, PR size, lint, flags, tests). Do not copy those standards into this hub. |

Add a row when a repo needs a stable personal override.
Do not dump repo facts here — link out.
