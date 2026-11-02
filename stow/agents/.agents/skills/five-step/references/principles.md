# Engineering principles for a five-step run

Apply these in every step.

- Correctness first. Preserve intended business behavior. Name every intentional behavior change.
- No backward compatibility by default. Keep a legacy contract only for an active external consumer the user names.
- Test behavior. Remove redundant tests. Never weaken coverage to make a refactor pass.
- Follow existing conventions. Prefer the best pattern already in the codebase over a new one.
- Consistency. Make similar implementations look the same. Lower the reader's load.
- Evidence over intuition. Check code, tests, callers, git history, and usage before you decide.
- Small changes. Atomic commits, each reviewable alone, ordered so the sequence proves itself.
- No speculative work. No abstraction, feature, or infrastructure for a hypothetical need.
- Human oversight. Surface consequential trade-offs and open decisions. Do not guess silently.
- Never delete input validation at a trust boundary, error handling that prevents data loss, security controls, accessibility basics, or anything the user asked to keep.
