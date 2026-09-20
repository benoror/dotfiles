# Origin

Vendored from [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills)
at `.agents/skills/skill-doctor`.

Pinned commit: `69b4753651ab7fab518c82be087b9f1d5b966631`

(`Add compliance scorers to skill-doctor (#101)`, 2026.)

This hub copy is a generic multi-harness skill grader. It keeps the upstream
transcript, `inventory.json`, and `report.json` shapes so scorers and the HTML
renderer stay compatible. Collector code is split into a harness plugin API.
Cursor and Grok Bot (`grok_bot`) are added here.

Never upload transcripts. Reports stay on the local machine.

Upstream: https://github.com/warpdotdev/common-skills/tree/main/.agents/skills/skill-doctor
