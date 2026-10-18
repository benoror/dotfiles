# AGENTS.md

Instructions for coding agents that work in this repo. The global personal layer (`stow/agents/.agents/AGENTS.md`) also applies. Use its writing rules for all prose.

## This repo is public

Everything you commit is public forever. Git history, forks, mirrors, and skills.sh all keep a copy. A later delete does not remove it.

If you are in doubt, leave it out and ask. Do not commit:

- Secrets: API keys, tokens, passwords, `.env` files, cookies, session files, SSH or GPG private material, webhook URLs.
- Personal data: phone numbers, home addresses, family member names, health data, financial data, account numbers.
- Private notes: Obsidian vault content, vault file names, chat logs, memory files from AI assistants, and anything copied from the private bot hub or a work lane.
- Company data: employer or client source code and client data.

Internal names, repo paths, machine names, and tailnet names or IPs are OK. They are not credentials and do not give access.

A public email address in `stow/git/` and this README is OK.

Use placeholders instead: `$HOME` or `~` for paths, `example.com` for domains, environment variables for values. Keep machine-specific values in a gitignored local file or in a password manager.

## Before you commit

1. Read the full staged diff: `git diff --cached`.
2. Check it against the list above. Check new file names too.
3. If you are not sure that something is public-safe, stop and ask Ben. Do not commit it.

If you find a leak that is already pushed, do not try to hide it with a new commit. Tell Ben at once. A leaked secret must be rotated. A history rewrite needs Ben's approval.

## Repo defaults

- Packages live in `stow/<name>/` and link into `$HOME` with GNU Stow. Follow the existing package layout.
- Use the `Makefile` targets. Run `make help` to see them.
- Dry-run Stow before you link: `stow -n -v -d stow -t ~ <package>`.
- Run `make verify` after package changes. Run `make agents-verify` after changes in `stow/agents/` or `skills/`.
- `make install-secrets` is explicit. Do not add secret packages to the default `install` target.
- In `skills/`, link only skills this repo owns or forks. Read `skills/README.md` first.
- Keep the index table in `README.md` current when you add, move, or remove a top-level path or package.
- Work on a branch and open a pull request. Do not push to `master` without Ben's approval.
- Keep diffs small and focused. Do not change unrelated config.
- Make each commit atomic, with a clear message (`type(scope): summary`).
- Do not add a new dependency, plugin, or tool without a stated reason.
- For agent skills, use the layout in `stow/agents/README.md` and the list in `stow/agents/REGISTRY.md`. Do not repeat them here.
