---
name: pr-description
description: Draft concise PR descriptions from branch context. Use when the user asks for /pr-description, a PR description, pull request summary, or branch change summary — especially when API or client contracts may change.
disable-model-invocation: true
---

# PR Description

Focus on the latest changes for the current Git branch, unless the user asks for a different range.

Graduated from Trivelta PAM v2; keep this skill generic across backend/frontend/monorepo work.

## Workflow

1. Gather branch context: current branch, recent commits, changed files, and diff from the branch base (`main`/`origin/main` unless the user specifies otherwise).
2. Separate implementation details from user/API behavior. Keep notes skimmable for reviewers who need a quick implementation read.
3. Identify contract changes: routes, methods, params, response shape, status/error codes, auth, pagination/filter/sort, OpenAPI/docs, CLI flags, or E2E cases.
4. Include frontend/client notes only when contracts or consumer-facing behavior changed.
5. Keep wording concise. Prefer bullets, concrete file/module names, and outcomes over a file-by-file changelog.

## Output Template

```markdown
## Summary
- <Primary outcome or feature/fix>
- <Secondary notable change, if useful>

## Implementation Notes
- <Architecture/flow detail reviewers should know>
- <Data/schema/service behavior worth calling out>

## API Contract / Frontend Notes
- <Only include when contracts or client-facing behavior changed>
- <Call out endpoint/method/params/response/auth/errors/pagination changes>

## Testing
- <Commands run or focused test coverage>
- <Known gaps or commands not run, if any>
```

Omit `API Contract / Frontend Notes` when there are no API or client-facing contract changes.

## Style

- Lead with what changed and why it matters.
- Keep the summary at 1-3 bullets.
- Keep implementation notes high-signal.
- For frontend notes, write as a quick handoff: exact contract change, migration concern, and anything the client must display/send differently.
- Do not invent tests. If evidence is missing, say what was not run.
- Prefer ASD-STE100 short sentences when writing the final description.
