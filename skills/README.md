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

Pack [ben-orozcos-projects](https://www.skills.sh/packs/ben-orozcos-projects) is
separate from the repo page. After merge, set the pack GitHub source in the
Vercel skills.sh UI to `benoror/dotfiles` and folder `skills/`. The CLI cannot
create or edit that pack when Vercel sign-in is required.

Install the pack (no CLI auth):

```bash
npx skills add https://skills.sh/p/<pack-id>
```

See [../stow/agents/REGISTRY.md](../stow/agents/REGISTRY.md).
