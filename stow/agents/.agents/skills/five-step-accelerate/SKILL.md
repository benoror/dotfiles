---
name: five-step-accelerate
description: Step 4 of the five-step algorithm. Make the system and its workflow faster to understand, change, test, review, and deploy. Coupling, dependency chains, feedback loops, test isolation, atomic reviewable changes, build and CI overhead. Use for /five-step-accelerate, "speed up the dev loop", "cycle time", "why is this slow to change", or after five-step-simplify.
---

# Five-step accelerate

Step 4 of [five-step](../five-step/SKILL.md). Runs alone or after [five-step-simplify](../five-step-simplify/SKILL.md).

Cycle time means the time from idea to verified change in production. Improve both runtime and engineering throughput, when evidence justifies it.

## Gate

Accelerate only what survived steps 1 to 3. A fast path through code that should not exist is waste.

## Input

Scope. The ledger.

## Procedure

Measure first. Record the current numbers you can get (test time, build time, CI time, review size, files touched per typical change).

Then look for:

1. Shorter implementation paths. Fewer hops from request to effect.
2. Less coupling. Shorter dependency chains, fewer modules a change must touch.
3. Faster, more focused feedback. Unit checks that run in seconds. Fewer slow end-to-end tests covering what a unit test proves.
4. Test isolation. Tests that fail for one reason and need no shared state.
5. Atomic, independently reviewable changes. Order commits so the sequence proves itself (failing test first, then the fix; subtraction before the reshape).
6. Build, test, and deploy overhead you can remove.

Do not trade correctness, reliability, or meaningful coverage for speed.

## Output

Append an Accelerate section to the ledger:

| Change | Metric | Before | After or expected | Evidence |
| --- | --- | --- | --- | --- |
| `<what changes>` | `<test time, CI time, files per change>` | `<number>` | `<number>` | `<measurement or "not measured">` |

## Stop rule

Ask the user before you change CI, deploy, or release process shared with other teams. Decide alone for test structure and local tooling.
