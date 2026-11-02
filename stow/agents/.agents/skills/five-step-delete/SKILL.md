---
name: five-step-delete
description: Step 2 of the five-step algorithm. Find and remove what should not exist, with usage evidence, before any simplification. Dead code, unused dependencies, redundant tests, wrappers, layers, duplicated logic, compatibility shims, and unnecessary process. Use for /five-step-delete, "what can we delete", "remove dead code", "cut this down", or after five-step-question.
---

# Five-step delete

Step 2 of [five-step](../five-step/SKILL.md). Runs alone or after [five-step-question](../five-step-question/SKILL.md).

Bias toward subtraction. Prefer deleting a feature over preserving it through a more complex implementation. If you do not add back at least 10% of what you deleted, you did not delete enough.

## Gate

Delete only what step 1 marked `delete` or `rethink`, or what usage evidence shows is dead. Do not simplify or optimize here. That is step 3.

## Input

Scope. The ledger, with its Question section.

## Procedure

1. List candidates. Look for dead code, unused dependencies, redundant tests, obsolete config, wrappers and layers with one caller, duplicated logic, redundant state, unused parameters and conditionals, compatibility layers, and process steps nobody needs.
2. Prove each one is removable. Grep callers. Check git history, feature flags, telemetry, and external consumers. "It feels risky" is not evidence.
3. When a new path replaces an old one, migrate the callers and delete the old path in the same change. Keep no adapter without an owner and an end date.
4. Delete the test that only protected the deleted implementation. Keep the test that specifies behavior.
5. If a deletion leaves a real gap, add back the minimum.
6. Run the tests after each deletion.

Never delete input validation at a trust boundary, error handling that prevents data loss, security controls, accessibility basics, or anything the user asked to keep.

## Output

Append a Delete section to the ledger:

| Candidate | Evidence it is unneeded | Risk | Add-back (minimum) | Status |
| --- | --- | --- | --- | --- |
| `<path or symbol>` | `<0 callers, flag off since X, superseded by Y>` | `<none / contract Z>` | `<none, or the minimal replacement>` | proposed / done |

Record the line count and dependency count removed when you can measure them.

## Stop rule

Ask the user before you remove a contract an external consumer may use, or data. Decide alone for internal code with evidence of zero use.
