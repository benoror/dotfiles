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
| `skill-doctor` | Maintained fork of Warp's skill-doctor (warpdotdev/common-skills); authors Warp / warpdotdev. |
| `product-description` | First-class hub copy. The upstream gist cannot be cloned with `npx skills`. |

## Symlink rule

Link only skills this repo owns or forks. Do **not** link pure upstream vendors:

- mattpocock pack
- ponytail pack
- anthropics `skill-creator`
- vercel-labs `find-skills`
- humanlayer `show-me`
- unmodified github `gh-stack` (the hub note stays in the Stow tree only)

```bash
cd ~/dotfiles
ln -sfn ../stow/agents/.agents/skills/<name> skills/<name>
```

Then add the slug (the `name` in `SKILL.md`) to [../skills.sh.json](../skills.sh.json).

## Install

Repo page (after skills.sh sees this tree):

```bash
npx skills add benoror/dotfiles --skill <name>
```

### Get indexed (FAQ)

skills.sh lists skills from anonymous CLI telemetry ([FAQ](https://www.skills.sh/docs/faq)). After this branch merges to the default branch, install with telemetry **on** (do not set `DISABLE_TELEMETRY` or `DO_NOT_TRACK`):

```bash
npx skills add benoror/dotfiles --skill skill-doctor
```

That install is what lets the leaderboard see `skill-doctor` from this repo. Visiting the GitHub page alone does not index it.

Pack [ben-orozcos-projects](https://www.skills.sh/packs/ben-orozcos-projects):

```bash
npx skills add https://skills.sh/p/<pack-id>
```

After this branch merges, set the pack’s GitHub source in the Vercel skills.sh UI to `benoror/dotfiles` and the `skills/` folder. The CLI cannot create or edit that pack when Vercel auth is required.

See [../stow/agents/REGISTRY.md](../stow/agents/REGISTRY.md).
