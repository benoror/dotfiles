---
name: five-step-simplify
description: Step 3 of the five-step algorithm. Simplify and optimize what remains after deletion. DRY without premature abstraction, separation of concerns, cohesive boundaries, consistent contracts and error handling, naming, reader load, and data access. Use for /five-step-simplify, "simplify this", "reduce cognitive load", "DRY opportunities", "separation of concerns", or after five-step-delete.
---

# Five-step simplify

Step 3 of [five-step](../five-step/SKILL.md). Runs alone or after [five-step-delete](../five-step-delete/SKILL.md).

Prefer the simplest design that solves the actual problem. Do not add a pattern to show architectural skill.

## Gate

Delete before you simplify. If the ledger has no Delete section, run five-step-delete first, or confirm with the user that deletion is done.

## Input

Scope. The ledger.

## Procedure

Evaluate what remains against these questions. Record only findings that change a decision.

1. DRY. Where do two implementations repeat one decision? Merge them only when the shared code would have at least two real callers today.
2. Separation of concerns. Which module owns which decision? Where does one module reach into another's state?
3. Boundaries. Are modules, services, and domain contexts cohesive? Where justified, apply the patterns the codebase already uses (repository, query object, service object, adapter, gateway, bounded context, aggregate, ubiquitous language). Use the codebase's own domain terms.
4. Contracts. Are types, interfaces, and error handling consistent across similar code?
5. Reader load. Can a new reader answer "where does X come from" and "what can change X" in 30 seconds? If a question needs more than three files or layers, flatten. Collapse wrappers with one caller. Shrink mutable scope.
6. Data access and algorithms. Remove unnecessary computation, round trips, and N+1 patterns.
7. Consistency. Make similar implementations match the best existing one.

Optimize the system, not a component. Reject a local simplification that adds complexity elsewhere.

## Output

Append a Simplify section to the ledger:

| Change | Reader-load before | Reader-load after | Affected contracts | Tests |
| --- | --- | --- | --- | --- |
| `<what changes>` | `<layers, state, files to trace>` | `<same, after>` | `<none / list>` | `<existing / add / adapt>` |

## Stop rule

Ask the user when a simplification changes a public contract or intended behavior. Decide alone for internal structure with tests that specify the behavior.
