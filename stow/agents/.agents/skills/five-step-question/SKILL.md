---
name: five-step-question
description: Step 1 of the five-step algorithm. Challenge every requirement, constraint, abstraction, and design decision in a scope and record a keep, delete, or rethink verdict with evidence. Use for /five-step-question, "question the requirements", "do we still need this", "why does this exist", or before any deletion or refactor.
---

# Five-step question

Step 1 of [five-step](../five-step/SKILL.md). Runs alone or after [five-step-understand](../five-step-understand/SKILL.md).

Requirements from senior engineers and established conventions get the same scrutiny as everything else. A requirement with no identifiable owner is a candidate for deletion.

## Gate

Know how the code works first. If the ledger has no Understand section, run five-step-understand or read the scope before you start.

## Input

Scope. The ledger.

## Procedure

For each requirement, constraint, abstraction, and design decision in scope, answer:

1. What problem does it solve? Is that problem still real?
2. Who introduced it? Find the person or commit, not the team. Use `git log -S` and `git blame`.
3. Is it a real business, technical, security, regulatory, or operational constraint?
4. What evidence supports it? Or did an assumption become institutional?
5. What happens if we remove it or rethink it?
6. Is this the actual problem, or a historical solution we keep re-implementing?

Look hardest at:

- Backward compatibility and legacy behavior with no named consumer.
- Premature abstractions and speculative extensibility.
- Defensive code with no justified failure mode.
- Workarounds, historical requirements, and accumulated debt.
- Indirection, configuration, and options nobody sets.

## Output

Append a Question section to the ledger:

| Item | Problem it solves | Source | Evidence | Verdict |
| --- | --- | --- | --- | --- |
| `<requirement or abstraction>` | `<problem, or "none found">` | `<person, commit, doc>` | `<usage, test, caller count>` | keep / delete / rethink |

List the items with verdict `delete` or `rethink` first. They feed [five-step-delete](../five-step-delete/SKILL.md).

## Stop rule

Ask the user when a verdict depends on a business decision, a regulatory constraint, or an external consumer you cannot see. Decide alone when the code, tests, and history answer the question.
