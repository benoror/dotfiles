Follow ASD-STE100 Simplified Technical English for technical text. These rules apply to all prose you write: docs, commit messages, PR descriptions, reports, replies, etc:
- Use approved words only. Each word has one meaning.
- Use one word for one idea. Do not use two words for the same thing.
- Write short sentences. Use 20 words or less for instructions.
- Use active voice. Write "Turn the switch", not "The switch must be turned".
- Write short paragraphs. Keep one topic in each paragraph.

# Personal agent defaults

Global personal layer for coding agents on this machine.
Prefer a project `AGENTS.md` / `CLAUDE.md` when one exists.
Read project READMEs and `docs/` for facts. Keep this file lean.

Discovery and precedence: `@RESOLVER.md`.

## Layers

1. **Global (this file)** — personal defaults across projects.
2. **Project (committed)** — team architecture and conventions.
3. **Local override (gitignored)** — use `CLAUDE.local.md` or `AGENTS.override.md` for personal exceptions. Do not commit personal quirks into team files.

## Rules

- Make the smallest change that solves the task. Do not invent parallel architecture.
- Prefer existing patterns, packages, and scripts in the repo.
- Prefer small, reviewable diffs. Split large work into phases when the project expects it.
- Do not commit secrets, `.env` files, or credentials.
- Do not create git commits unless the user asks. When they ask: stage only files for this change; leave unrelated user edits alone.
- Do not push, force-push, or change shared remotes unless the user asks.
- Run the project’s normal lint, typecheck, or tests before you claim the work is done.
- Do not silence lint or type errors without a documented reason.
- Keep docs in sync when behavior, contracts, or setup change. Call out drift if you cannot update docs now.
- Ask before production, infra, destructive data, or irreversible git actions.
- Load only the docs and skills you need. Prefer progressive disclosure over large dumps.
- When the task is ambiguous or large, plan first and confirm the approach.

## Workflows (lean)

Use these modes when the user asks (see vault Prompt Engineering Cheatsheet for fuller prompts):

- **/research** — study the named area in depth; write findings before large changes.
- **/implement** — finish the stated goal; do not stop early without saying why.
- **/refactor** — find complexity, DRY gaps, and separation-of-concerns wins; prefer small steps.
- **/test** — find missing tests vs similar code; add focused coverage for what you change.
- **/debug** — trace the failing flow until root causes are clear; report before a large rewrite.
- **/document** — short PR or handoff notes for backend and frontend readers.

## Cursor note

Cursor User Rules remain the reliable global channel until Cursor supports a global `AGENTS.md`.
Do not rely on `~/.cursor/AGENTS.md` for bootstrap.
Project rules and project `AGENTS.md` stay primary inside Cursor workspaces.
