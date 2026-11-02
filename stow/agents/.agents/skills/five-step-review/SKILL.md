---
name: five-step-review
description: Independent review after a five-step run or any refactor. A fresh reviewer on a different model checks whether complexity was removed or only moved, whether enough was deleted, and whether behavior held. Use for /five-step-review, "review this refactor", "did we actually simplify", or as phase 4 of a five-step run.
---

# Five-step review

Review phase of [five-step](../five-step/SKILL.md). Runs alone on any refactor diff.

The author must not grade their own work. Use a fresh context and a different model.

## Gate

A diff exists. The ledger exists, or the user names the refactor's intent.

## Input

Diff range (base and head, or PR). The ledger or the stated intent. File pointers, not inline content.

## Procedure

1. If the host can spawn subagents, spawn one read-only reviewer. Pick a model different from the one that wrote the change, and the strongest judgment model available. In Cursor with pstack, use the `judgment and prose` role from `~/.cursor/rules/pstack-models.mdc`. Give it the diff range, the ledger path, and the checklist below.
2. If the host cannot spawn subagents, run the checklist in a fresh session, or ask the user to open one.
3. The reviewer answers each checklist item with evidence from the diff, not from the ledger's claims.
4. The author triages the findings and fixes every "fix now" item before the report.

## Checklist

- Did we remove complexity, or move it? Apply the deletion test to each new unit. Would deleting it concentrate complexity, or just relocate it?
- Did we delete enough? Name what is still a candidate.
- Did we add an abstraction, layer, option, or parameter that one caller uses?
- Are responsibilities and contracts clearer? Can a new reader answer "where does X come from" in 30 seconds?
- Did we preserve intended behavior? Name every behavior change and check it is intentional and listed.
- Are redundant tests, code paths, or dependencies left? Scan the diff for repeated private functions and identical expressions. For each near-match the author kept, is the behavior that would change on merge named?
- Did we optimize or automate something that should not exist?
- Could the result be materially simpler? Say how.

## Output

Append a Review section to the ledger:

| Finding | Severity | Evidence | Action |
| --- | --- | --- | --- |
| `<one sentence>` | fix now / consider / note | `<file:line or command output>` | `<what the author does>` |

Severity rules. "fix now" means complexity was moved, behavior changed without record, or a deletion candidate is obvious. "consider" means a real concern with unclear cost. "note" means valid and low priority.

## Stop rule

The reviewer does not edit code. The author decides, and asks the user only when a "fix now" item needs a product or business call.
