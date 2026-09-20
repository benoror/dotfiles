# Origin

Fork of **Warp's skill-doctor**. Upstream authors: Warp / [warpdotdev](https://github.com/warpdotdev).

Vendored from [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills)
at `.agents/skills/skill-doctor`.

- GitHub: https://github.com/warpdotdev/common-skills/tree/main/.agents/skills/skill-doctor
- skills.sh: https://www.skills.sh/warpdotdev/common-skills/skill-doctor

Pinned commit: `69b4753651ab7fab518c82be087b9f1d5b966631`

(`Add compliance scorers to skill-doctor (#101)`, 2026.)

The skill name stays `skill-doctor`. This is a maintained fork, not a Warp rebrand.

## Fork differences

- Multi-harness plugin API (`detect_runtime` / `list_sessions` / `parse_session` / `discover_skills`)
- Added `cursor` (best-effort) and `grok_bot` (Grok Bot v1)
- No Warp Factories CTA or marketing footer (attribution to warpdotdev/common-skills remains)
- skills.sh pack surface via `benoror/dotfiles` `skills/` (relative symlink into this hub skill)

Normalized transcripts, `inventory.json`, and `report.json` stay compatible with upstream scorers and the HTML renderer.

Never upload transcripts. Reports stay on the local machine.
