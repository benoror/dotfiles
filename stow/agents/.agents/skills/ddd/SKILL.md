---
name: ddd
description: Domain-driven design as a working checklist for agents. Decide which bounded context owns a use case, which layer the code goes in, and what everything is called, before writing it. Audit an existing codebase for leaked boundaries and product names in shared code. Use for /ddd, "where does this belong", "bounded context", "ubiquitous language", "aggregate", "domain model", "name this", or before adding a feature to a codebase with more than one business area.
---

# DDD

The codebase is the prompt. Agents navigate by directory names, file names, and type names. Domain-driven design gives those names one meaning each and puts every use case in one owner's folder. Evans wrote it for teams of humans. Agents need it more.

Three modes. Pick by what the user asks for.

| Mode | When | Output |
| --- | --- | --- |
| Place | Before new code | Placement table and glossary delta |
| Map | New codebase, or no context map exists | Context map and glossary |
| Audit | "Is this well structured", or after a large merge | Findings table |

## Place

Run before any new feature, endpoint, or command in a codebase with more than one business area.

1. Ask which business area owns the use case. Not which existing module has a similar route or a similar helper.
2. Name the entity. A product area is not an entity. A sidebar module, a report, or a page is a view onto entities. Find the noun with an id.
3. Pick the layer for each piece using [references/layout.md](references/layout.md). Entry point, controller, use case, repository, mapper.
4. Name everything in the domain's words. One name per concept. Use it in the directory, the type, the test, the URL, and the docs. If `GLOSSARY.md` exists, take names from it and add new ones there.
5. Decide what crosses the boundary. Other contexts reach this one only through its public use cases, wired in the composition root. No imports between context internals.
6. When URL ownership and implementation ownership differ, keep the implementation in the owning context and mount it under the other resource's prefix from the composition root.
7. If this is the first command (write) slice in the codebase, codify validation, idempotency, atomicity, audit logging, conflicts, and auth before the pattern spreads.

Output:

| Piece | Context | Layer | Name | Crosses boundary? |
| --- | --- | --- | --- | --- |
| `<what you add>` | `<owner>` | `<entry / controller / use case / repository / mapper>` | `<domain term>` | `<no / via use case X>` |

Plus a glossary delta: term, meaning, where it appears in code, conflicts with an existing name.

## Map

1. List the business areas the product has. Each becomes a bounded context, broad enough to match ownership, narrow enough that one team or one agent can hold it.
2. For each context, list what it owns (entities, use cases), what it exposes (public use cases, events), and what it needs from others.
3. Name the shared kernel. Only platform primitives go there: auth, errors, pagination, data clients, serialization. Nothing named after a product concept.
4. Name the composition root. One place wires contexts together, mounts routes, and builds dependencies.
5. Write the glossary. One entry per domain term. Mark synonyms as retired names.

Output a context map (table of contexts with owns, exposes, depends-on) and the glossary. Propose `docs/architecture/overview.md`, `docs/architecture/layers.md`, and `GLOSSARY.md` when the repo has none. Keep each under one screen.

## Audit

Look for these, in order of damage:

1. Cross-context imports outside the composition root.
2. Product concepts in the shared kernel. A helper whose name only makes sense in one context belongs in that context.
3. Store-specific shapes (rows, documents, API payloads) reaching controllers or wire schemas without a mapper.
4. Two names for one concept, or one name for two concepts. Check code, tests, URLs, and docs together.
5. Routes named after UI tabs, permissions, history, or implementation instead of the resource.
6. Sibling contracts that differ for no product reason (param names, envelopes, route shapes).
7. Business logic in entry points or controllers. Query composition in use cases.
8. An abstraction that serves one context. Collapse it into that context.

Output:

| Finding | Where | Rule broken | Fix |
| --- | --- | --- | --- |

For each rule the codebase keeps breaking, add a check from [references/checks.md](references/checks.md) so the structure enforces it.

## Rules that hold in every mode

- Ownership follows the business domain. URLs follow the resource. These can differ; the composition root bridges them.
- The shared kernel stays generic. Put shared code under the narrowest truthful namespace.
- Add an abstraction only when it removes duplication across two or more contexts without hiding the local use case. Prefer rollback to preserving an abstraction that raises reader load.
- Map at the repository boundary. Canonical domain models face the use case. Store-specific models stay inside repositories. Wire schemas face the client. A type that mirrors the wire contract is a schema, not a model.
- Keep analogous contracts homogeneous unless product semantics differ.
- Presentation resolves at the boundary. Codes and typed errors inside, localized strings and HTTP shapes at the edge.
- Cross-cutting checks (permissions, feature gates) stay declarative at the entry point. No per-context wrappers.

## Related skills

Use when installed. None is required.

- `grill-with-docs` (mattpocock) writes ADRs and a glossary while grilling a plan. Hand it the glossary delta.
- `improve-codebase-architecture` (mattpocock) finds shallow modules to deepen. Run it after Audit.
- pstack `principle-model-the-domain` and `principle-boundary-discipline` are the single-principle versions of steps 2 and 5 of Place.
- `five-step-simplify` cites bounded contexts as a pattern to apply where justified. This skill is the "how".

## Sources

- Eric Evans, Domain-Driven Design (2003). Ubiquitous language, bounded contexts, aggregates, context maps.
- Vaughn Vernon, Implementing Domain-Driven Design (2013). Layering and the composition root.
- Patterns distilled from a production admin backend migrated to bounded contexts in 2026. Structure only, no code.
