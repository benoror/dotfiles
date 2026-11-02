---
name: five-step-understand
description: Step 0 of the five-step algorithm. Study a scope in depth before any change. Trace flow, callers, contracts, tests, and conventions, and separate intentional behavior from accidental complexity. Delegates to an installed how or research skill when one fits. Use for /five-step-understand, "understand X before we change it", "read X in depth", or as the first step of a five-step run.
---

# Five-step understand

Step 0 of [five-step](../five-step/SKILL.md). Runs alone or as the first step of a run.

Do not make changes. The output is a mental model the next steps can act on.

## Gate

None. This step starts a run.

## Input

Scope (paths, module, feature, or a runtime flow). The ledger if one exists.

## Delegate when a fitting skill is installed

Check for these skills, in this order:

1. `how` (pstack; `pstack-how` outside Cursor) for a subsystem or runtime trace.
2. `research` (mattpocock) for a question that needs primary sources outside the codebase.

If exactly one fits, use it and tell the user which. If both fit, ask which one. If none is installed, follow the procedure below. In every case, end with the Output section.

## Procedure

1. Read the implementation, its dependencies, callers, contracts, and tests. Read the code. Do not guess from file names.
2. Trace the complete execution flow from entry to effect. Stop when you can describe every step without hand-waving.
3. Find the existing patterns. Compare similar implementations across the codebase and name the best one.
4. Establish the current behavior. Separate intentional behavior from accidental complexity. Use git history and tests as evidence.
5. Note what a newcomer would get wrong.
6. Keep researching until the flow is clear. Do not stop early.

## Output

Append an Understand section to the ledger:

- Architecture and execution flow, in prose, with file and function names.
- Key types and contracts, and who consumes them.
- Intentional behavior, with the evidence.
- Accidental complexity and historical workarounds, with the evidence.
- Existing patterns worth adopting, with the best example.
- Test coverage and gaps.
- Open questions you could not settle from the code.

## Stop rule

Ask the user only for facts the code cannot show (ownership, business intent, active external consumers). Everything observable, observe.
