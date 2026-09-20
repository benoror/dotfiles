# Origin

Based on / forked from [Warp's skill-doctor](https://github.com/warpdotdev/common-skills/tree/main/.agents/skills/skill-doctor)
in [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills).

Credit the upstream skill. This hub copy is not a Warp product page.

- GitHub: https://github.com/warpdotdev/common-skills/tree/main/.agents/skills/skill-doctor
- skills.sh: https://www.skills.sh/warpdotdev/common-skills/skill-doctor

Pinned commit: `69b4753651ab7fab518c82be087b9f1d5b966631`

(`Add compliance scorers to skill-doctor (#101)`, 2026.)

The skill name stays `skill-doctor`. This is a maintained multi-harness fork.

## Fork differences

- Multi-harness plugin API (`detect_runtime` / `list_sessions` / `parse_session` / `discover_skills`)
- Added `cursor` (best-effort) and `grok_bot` (Grok Bot v1)
- No product CTA or marketing footer
- Report footer still credits Warp's skill-doctor / warpdotdev/common-skills
- skills.sh pack surface via `benoror/dotfiles` `skills/` (relative symlink into this hub skill)

Normalized transcripts, `inventory.json`, and `report.json` stay compatible with upstream scorers and the HTML renderer.

Never upload transcripts. Reports stay on the local machine.
