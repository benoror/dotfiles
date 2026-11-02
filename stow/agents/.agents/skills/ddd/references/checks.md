# Structural checks

Each rule the codebase keeps breaking becomes a test. The failure message says what to add. These are shapes, not copy-paste code. Match them to the repo's test runner.

## Import boundary

Fail when a file under `contexts/<a>/` imports from `contexts/<b>/` and the importing file is not the composition root.

Shape: walk every source file under `contexts/`, parse imports, assert the imported context equals the importing context. Allow-list the composition root files by path.

## Shared kernel naming

Fail when a file under `core/` contains a product term from the glossary or a context name.

Shape: load context names from the `contexts/` directory listing and product terms from `GLOSSARY.md`. Grep `core/` identifiers and module names for them. Keep a short allow-list for true primitives that happen to share a word.

## Route inventory

Fail when the set of mounted routes differs from a committed expected list.

Shape: build the app, enumerate routes (method, path), compare to `EXPECTED_ROUTES`. A new endpoint changes the list on purpose, in the same commit, and the diff shows the reviewer the new contract.

## Mapper boundary

Fail when a controller or schema module imports a store-specific model.

Shape: name store-specific model modules by convention (`*_doc.py`, `*_row.py`, `*_record.py`). Assert nothing under `controllers/` or `schemas/` imports them.

## Gate sites

Fail when a new inline permission or feature-gate call appears without a test that drives both truth values.

Shape: grep for the gate call outside the auth package, collect call sites, and compare to a baseline that shrinks only. A new site needs a matching test file before the baseline grows.

## Contract homogeneity

Fail when sibling endpoints of the same kind use different parameter names or envelope types.

Shape: group routes by kind (list, detail, export, dashboard). For each group, assert the shared query parameter names and the response envelope class match.

## When to add one

Add the check the second time the same review comment appears. One occurrence is a fix. Two is a structure gap.
