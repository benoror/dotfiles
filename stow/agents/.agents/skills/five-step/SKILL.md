---
name: five-step
description: Run a first-principles refactor with the five-step algorithm, in strict order. Understand, question every requirement, delete, simplify, accelerate, automate last, then review. Use for /five-step, "5-step refactor", "first-principles refactor", "cut complexity", or when the user wants to remove complexity from a codebase instead of reorganizing it.
disable-model-invocation: true
---

# Five-step

Act as a principal engineer. Remove unnecessary complexity. Do not move it. Challenge requirements, abstractions, implementations, and processes. Optimize for simplicity, correctness, maintainability, and development velocity.

Follow the steps in order. Do not optimize or automate a thing before you establish that it should exist.

Each step is its own skill. Run one alone when the user asks for only that step. The ledger (below) carries findings from one step to the next.

| Step | Skill | Question it answers |
| --- | --- | --- |
| 0 | [five-step-understand](../five-step-understand/SKILL.md) | How does it work today? |
| 1 | [five-step-question](../five-step-question/SKILL.md) | Should this exist? |
| 2 | [five-step-delete](../five-step-delete/SKILL.md) | What can go? |
| 3 | [five-step-simplify](../five-step-simplify/SKILL.md) | What is the simplest form of what remains? |
| 4 | [five-step-accelerate](../five-step-accelerate/SKILL.md) | How do we make it faster to change, test, and ship? |
| 5 | [five-step-automate](../five-step-automate/SKILL.md) | What is worth automating, now that it is small? |
| review | [five-step-review](../five-step-review/SKILL.md) | Did we remove complexity, or move it? |

If a step skill is not installed, follow the one-line summary in its row and the principles file.

## The ledger

One running document. Each step appends its own section. Keep it in chat. Write it to a file only when the user names one.

Sections, in order: Scope, Understand, Question, Delete, Simplify, Accelerate, Automate, Review, Report.

## Workflow

### Phase 1. Assess

Read only. No edits.

1. Record the scope (paths, module, feature) in the ledger.
2. Run step 0.
3. Run steps 1 to 5 as analysis. Each appends findings.

### Phase 2. Plan

Write an extremely concise phased plan, ordered by step. Sacrifice grammar for concision.

For each change: what changes, why, what gets removed, benefit, risk and affected contracts, tests required.

Prioritize the highest-impact simplifications. Leave trivial cleanup out.

End with unresolved questions and decisions that need the user. Stop and ask when a material requirement, business decision, or risk cannot be established. Otherwise decide and record the assumption.

Wait for approval before Phase 3.

### Phase 3. Execute

1. Keep the step order. Deletions land before simplifications.
2. One atomic, semantic change per commit.
3. When behavior changes, write the expectation first, then the test, then the code (BDD, then TDD).
4. Run the relevant tests after each change.
5. Do not stop at surface cleanup. Finish the agreed scope, or report a real blocker and stop.

### Phase 4. Review

Run [five-step-review](../five-step-review/SKILL.md). Fix every "fix now" finding before the report.

### Phase 5. Report

Fill [references/report-template.md](references/report-template.md). State measured results only. Never claim a performance gain without a number.

## Principles

Read [references/principles.md](references/principles.md) once per run. In short: correctness first, no backward compatibility by default, test behavior, follow existing conventions, evidence over intuition, small changes, no speculative work, surface trade-offs to the human.

## Related skills

Use these when installed. None is required.

- `ponytail-review` reviews a diff for over-engineering. Good after step 2.
- `improve-codebase-architecture` (mattpocock) finds deepening refactors. Overlaps step 3.
- pstack principle skills `subtract-before-you-add`, `migrate-callers-then-delete-legacy-apis`, `minimize-reader-load`, `sequence-verifiable-units`, and `build-the-lever` are single-principle versions of steps 2 to 5.

## Sources

- Elon Musk's five-step algorithm, as told in Walter Isaacson's biography (2023).
- Step 0 "read X in depth" prompt: [boristane.com/blog/how-i-use-claude-code](https://boristane.com/blog/how-i-use-claude-code/).
- Concise plans with unresolved questions: [aihero.dev](https://www.aihero.dev/my-agents-md-file-for-building-plans-you-actually-read).
- "Don't stop till X": [steipete](https://x.com/steipete/status/2040542898773762231).
