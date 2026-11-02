---
name: five-step-automate
description: Step 5 of the five-step algorithm. Automate last, and only what survived the first four steps. Repetitive dev tasks, manual verification, boilerplate, lint, static analysis, CI, maintenance and sync chores. Use for /five-step-automate, "what should we automate", "script this", or after five-step-accelerate.
---

# Five-step automate

Step 5 of [five-step](../five-step/SKILL.md). Runs alone or after [five-step-accelerate](../five-step-accelerate/SKILL.md).

Prefer removing a process over automating it. Automation that nobody maintains becomes the next thing to delete.

## Gate

Steps 1 to 4 are done for this scope. If the ledger lacks them, say so and run them first, or get the user's explicit go-ahead to skip.

## Input

Scope. The ledger.

## Procedure

1. List the manual steps that remain. For each, ask first whether it can go away. A deleted step beats an automated one.
2. Keep candidates that are repetitive, error-prone, or block verification. Typical ones: repeated edits, manual checks, boilerplate, lint and format, static analysis, CI stages, sync and maintenance chores.
3. For each kept candidate, build the smallest script, check, codemod, or generator that does the job and reruns safely. Do the first unit by hand, then prove the tool reproduces it.
4. Count the maintenance cost. Skip the automation when it adds more surface than it removes.
5. Commit the tool. A reviewer reruns it instead of trusting you.

If you cite this step and the diff has no script, check, or generator, you did not automate. You wrote a note.

## Output

Append an Automate section to the ledger:

| Manual step | Removed instead? | Tool | Reruns safely | Maintenance cost |
| --- | --- | --- | --- | --- |
| `<what a human did>` | yes / no | `<path to script or check>` | yes / no | `<low / medium / high, and why>` |

## Stop rule

Ask the user before you add a dependency, a CI stage, or a scheduled job. Decide alone for a repo-local script.
