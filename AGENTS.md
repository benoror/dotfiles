# AGENTS.md

Instructions for coding agents that work in this repo. The global personal layer (`stow/agents/.agents/AGENTS.md`) also applies. Use its writing rules for all prose.

## This repo is public

Everything you commit is public forever. Git history, forks, mirrors, and skills.sh all keep a copy. A later delete does not remove it.

Do not commit:

- Secrets: API keys, tokens, passwords, `.env` files, cookies, session files, SSH or GPG private material, webhook URLs.
- Personal data: phone numbers, home addresses, family member names, health data, financial data, account numbers.
- Private notes: Obsidian vault content, vault file names, chat logs, memory files from AI assistants.
- Company data: employer or client code, internal system names, internal URLs, client names, private repo contents.
- Private network details: Tailscale or other private DNS names, private IP addresses, internal URLs, bot inbox addresses. Short machine nicknames (for example `mbp14m4`) are OK.

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
- Keep changes small. Do not change unrelated config.
