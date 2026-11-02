# skills.sh publish surface

This directory is the public [skills.sh](https://www.skills.sh/docs) / pack view of **own or forked** hub skills.

The Stow hub remains the source of truth:

```text
stow/agents/.agents/skills/<name>/   →   ~/.agents/skills/<name>/
```

Each entry here is a **relative symlink** into that hub tree. Do not copy skill files here.

## Linked now

| Skill | Why it is on this surface |
| --- | --- |
| `pr-description` | Graduated from Trivelta. Owned here. |
| `five-step`, `five-step-*` (7 steps) | Graduated from the vault prompt cheatsheet. Five-step algorithm for codebases. Owned here. |
| `ddd` | Domain-driven design checklist for agents. Owned here. |
| `skill-doctor` | Based on / forked from Warp's skill-doctor (warpdotdev/common-skills). Multi-harness grader owned here. |

## Symlink rule

Link only skills this repo owns or forks. Do **not** link pure upstream vendors
or hub-only copies:

- mattpocock pack
- ponytail pack
- anthropics `skill-creator`
- vercel-labs `find-skills`
- humanlayer `show-me`
- unmodified github `gh-stack` (the hub note stays in the Stow tree only)
- steveruizok gist `product-description` (hub copy only; `npx skills` cannot clone gists)

```bash
cd ~/dotfiles
ln -sfn ../stow/agents/.agents/skills/<name> skills/<name>
```

Then add the slug (the `name` in `SKILL.md` frontmatter) to [../skills.sh.json](../skills.sh.json).
The slug must match that `name`. `npx skills add` reads this folder, not the Stow hub path.

## Install

skills.sh does **not** crawl GitHub. It indexes from anonymous CLI install telemetry
when someone runs `npx skills add` ([FAQ](https://www.skills.sh/docs/faq)).
A push or a visit to the GitHub tree does not create the repo page.

After this branch merges to the default branch, run these with telemetry **on**
(do not set `DISABLE_TELEMETRY` or `DO_NOT_TRACK`). That create/refresh is what
makes [skills.sh/benoror/dotfiles](https://skills.sh/benoror/dotfiles) exist:

```bash
npx skills add benoror/dotfiles -s skill-doctor
npx skills add benoror/dotfiles -s pr-description
npx skills add benoror/dotfiles -s five-step
```

Install one skill later the same way. Always pass `-s <name>` so you get a
published slug, not every `SKILL.md` that happens to live in this repo:

```bash
npx skills add benoror/dotfiles -s <name>
```

A local list (no install) should show `skill-doctor` with the same `name`
as the SKILL.md frontmatter:

```bash
npx skills add ~/dotfiles -s skill-doctor --list
```

### Pack (Vercel UI)

The pack [skills.sh/p/HNXRLeUvoNFcf4jm](https://www.skills.sh/p/HNXRLeUvoNFcf4jm)
is separate from the repo page. Its entries are GitHub-sourced
(`benoror/dotfiles@master`, folder `skills/`), so edits to a listed skill reach
installers on the next install or `npx skills update`. The list itself is frozen
at creation: a new directory under `skills/` does not join an existing pack, and
the UI can only delete entries. The builder also rejects a checkout over 50 MB,
so keep large binaries out of the repo. The CLI cannot create or edit a pack.

Publishing a new skill therefore has two parts. The repo page picks it up after
one telemetry-on `npx skills add benoror/dotfiles -s <name>`, run from a scratch
directory so the CLI does not install copies into this repo. The pack picks it up
only when a new pack is created; do that per batch, not per skill, and keep old
pack ids alive for links already posted.

Install the pack (no CLI auth):

```bash
npx skills add https://skills.sh/p/HNXRLeUvoNFcf4jm
```

Pack history. `1sJwYsjYwfouBtEI` (Sep 2026) holds `pr-description` and
`skill-doctor` as file uploads. `HNXRLeUvoNFcf4jm` (Nov 2, 2026) holds those two
plus the eight `five-step` skills. `ddd` is on the repo page only until the next
pack. Both ids stay alive.

See [../stow/agents/REGISTRY.md](../stow/agents/REGISTRY.md).
