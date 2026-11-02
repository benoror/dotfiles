# Context layout and layer rules

A layout that has held up in production. Adapt directory names to the language and framework. Keep the rules.

```text
contexts/
  orders/
    entry.py            # routes, handlers, CLI commands, or consumers
    controllers/        # translate transport input into use-case calls
    services/           # use cases, business rules, orchestration
    repositories/       # persistence and queries
      mappers/          # store shape -> canonical model (optional)
      query_builders/   # query composition for complex reads (optional)
    models/             # canonical domain models and store-specific shapes
    schemas/            # wire DTOs: requests, responses, filters, envelopes
  billing/
    ...
core/                   # shared kernel: auth, errors, pagination, data clients
  auth/
  errors/
  data/
composition root        # app factory, router mounting, dependency container, settings
docs/
  architecture/         # overview, layers, contracts
  orders/               # per-context notes
GLOSSARY.md
```

## Flow

```text
entry -> controller -> service (use case) -> repository -> infrastructure client
```

Every request walks this path. No layer skips one.

## Per layer: owns, must not

**Entry point.** Owns paths, status codes, binding, pagination and filter dependencies, auth and gate dependencies, and delegating at once to a controller. Must not contain business logic, persistence, or query composition.

**Controller.** Owns converting transport input to typed use-case arguments, calling one or more use cases, and shaping the response with shared helpers. Must not touch repositories, infrastructure clients, or raw backend payloads.

**Service (use case).** Owns validation beyond boundary parsing, business rules, choosing which repositories take part, and composing results for the controller. Must not build raw SQL, search bodies, or store expressions.

**Repository.** Owns translating use-case intent into store operations, backend pagination and sorting, and mapping store responses into canonical models. Must not leak store details upward.

**Mappers and query builders.** Repository support, not layers. Add them when extraction improves readability or reuse. Mappers make no network calls. Query builders hold no business logic.

## Models vs schemas

- `schemas/` holds HTTP-facing or message-facing DTOs. If a type mirrors the wire contract, it is a schema.
- `models/` holds canonical domain models the use case reasons about, and store-specific shapes repositories use internally. This is the stricter bucket.
- Controllers and schemas never depend on store-specific models. The repository maps.

## Shared kernel

`core/` holds platform primitives only. Auth dependencies, error and response envelopes, data clients, generic pagination, filtering, and sorting helpers. Put each under the narrowest truthful namespace (`core/auth`, `core/data`). A helper named after a product concept, a single report, or one context's quirk belongs in that context.

## Composition root

One place builds the app, mounts each context's router, constructs dependencies, and reads settings. It may mount one context's router under another resource's prefix when URL ownership and implementation ownership differ. No alternate registries or hidden construction paths.

## Naming

- Directory, type, test, URL, and doc use the same domain term.
- Route shape names the resource, not the UI tab, the permission, or the history: `/{context}/{resource}[/{facet}]`.
- A product area or page is a module, not an entity. Nest the entity's collection under the module.
- Constants that define request or response vocabulary live next to the schemas that use them.
