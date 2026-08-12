SHELL := /usr/bin/env bash

DOTFILES_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
STOW_DIR := $(DOTFILES_DIR)/stow
TARGET := $(HOME)
AGENTS_PKG := $(STOW_DIR)/agents
AGENTS_LINKS_REGISTRY := $(AGENTS_PKG)/links.registry

# Safe defaults (no secrets, no Linux leftovers)
CORE := zsh git asdf agents ghostty
EDITORS := nvim vscode cursor
MAC := iterm2

# Explicit only — keys / secrets
SECRETS := ssh gnupg

# Optional — Linux desktop leftovers
LINUX := kde konsole

SAFE := $(CORE) $(EDITORS) $(MAC)
ALL := $(SAFE) $(SECRETS) $(LINUX)

.PHONY: help install restow uninstall verify
.PHONY: install-core restow-core uninstall-core
.PHONY: install-editors restow-editors uninstall-editors
.PHONY: install-mac restow-mac uninstall-mac
.PHONY: install-secrets restow-secrets uninstall-secrets
.PHONY: install-linux restow-linux uninstall-linux
.PHONY: install-all restow-all uninstall-all
.PHONY: agents-install agents-restow agents-uninstall agents-verify
.PHONY: agents-link-vault agents-link-code agents-link-sync

# Default skill sets when a registry/CLI row omits SKILLS=
AGENTS_VAULT_SKILLS ?= find-skills skill-creator pr-description
AGENTS_CODE_SKILLS ?= grill-me tdd ask-matt pr-description gh-stack

help:
	@printf '%s\n' \
	  'Groups (safe by default — no ssh/gnupg/linux):' \
	  '  make install            Install core + editors + mac' \
	  '  make restow             Restow those groups' \
	  '  make uninstall          Uninstall those groups' \
	  '  make verify             Smoke: SAFE package dirs exist under stow/' \
	  '  make install-core       $(CORE)' \
	  '  make install-editors    $(EDITORS)' \
	  '  make install-mac        $(MAC)' \
	  '  make install-secrets    $(SECRETS)  (explicit)' \
	  '  make install-linux      $(LINUX)  (optional)' \
	  '  make install-all        Safe + secrets + linux' \
	  '' \
	  'Per package: make install-<pkg> | restow-<pkg> | uninstall-<pkg>' \
	  '  packages: $(ALL)' \
	  '' \
	  'Agents extras:' \
	  '  make agents-verify      Check agent entrypoints + skill count' \
	  '  make agents-install     Alias for install-agents' \
	  '  make agents-link-vault VAULT=~/vaults/personal [SKILLS="…"]' \
	  '  make agents-link-code CODE=~/code/foo [SKILLS="…"]' \
	  '  make agents-link-sync   Re-link all rows in stow/agents/links.registry' \
	  '  APPEND=1                With link-vault/code: append target to registry'

# Explicit per-package rules (Make 3.81: pattern rules lose to empty prereq nodes)
define PACKAGE_RULES
.PHONY: install-$(1) restow-$(1) uninstall-$(1)
install-$(1):
	stow --dir="$(STOW_DIR)" --target="$(TARGET)" --stow $(1)
restow-$(1):
	stow --dir="$(STOW_DIR)" --target="$(TARGET)" --restow $(1)
uninstall-$(1):
	stow --dir="$(STOW_DIR)" --target="$(TARGET)" --delete $(1)
endef

$(foreach pkg,$(ALL),$(eval $(call PACKAGE_RULES,$(pkg))))

# --- default = safe groups -------------------------------------------------

install: install-core install-editors install-mac
restow: restow-core restow-editors restow-mac
uninstall: uninstall-core uninstall-editors uninstall-mac

install-core: $(addprefix install-,$(CORE))
restow-core: $(addprefix restow-,$(CORE))
uninstall-core: $(addprefix uninstall-,$(CORE))

install-editors: $(addprefix install-,$(EDITORS))
restow-editors: $(addprefix restow-,$(EDITORS))
uninstall-editors: $(addprefix uninstall-,$(EDITORS))

install-mac: $(addprefix install-,$(MAC))
restow-mac: $(addprefix restow-,$(MAC))
uninstall-mac: $(addprefix uninstall-,$(MAC))

install-secrets: $(addprefix install-,$(SECRETS))
restow-secrets: $(addprefix restow-,$(SECRETS))
uninstall-secrets: $(addprefix uninstall-,$(SECRETS))

install-linux: $(addprefix install-,$(LINUX))
restow-linux: $(addprefix restow-,$(LINUX))
uninstall-linux: $(addprefix uninstall-,$(LINUX))

install-all: install install-secrets install-linux
restow-all: restow restow-secrets restow-linux
uninstall-all: uninstall uninstall-secrets uninstall-linux

# Lightweight package presence check (not per-file content verify)
verify:
	@set -euo pipefail; \
	fail=0; \
	for pkg in $(SAFE); do \
	  if [[ -d "$(STOW_DIR)/$$pkg" ]]; then \
	    printf 'OK       stow/%s\n' "$$pkg"; \
	  else \
	    printf 'MISSING  stow/%s\n' "$$pkg"; \
	    fail=1; \
	  fi; \
	done; \
	if [[ "$$fail" -ne 0 ]]; then \
	  printf 'verify failed\n' >&2; \
	  exit 1; \
	fi; \
	printf 'verify OK (use agents-verify for hub entrypoints)\n'

# --- agents aliases + verify + link ----------------------------------------

agents-install: install-agents
agents-restow: restow-agents
agents-uninstall: uninstall-agents

agents-verify:
	@set -euo pipefail; \
	fail=0; \
	check_link() { \
	  local path="$$1" expect="$$2"; \
	  if [[ -L "$$path" ]]; then \
	    local got; got="$$(readlink "$$path")"; \
	    printf 'OK       %s -> %s\n' "$$path" "$$got"; \
	  elif [[ -f "$$path" ]]; then \
	    printf 'FILE     %s\n' "$$path"; \
	  else \
	    printf 'MISSING  %s\n' "$$path"; \
	    fail=1; \
	    return; \
	  fi; \
	  if [[ -n "$$expect" ]]; then \
	    if grep -qxF "$$expect" "$$path"; then \
	      printf '         content OK (%s)\n' "$$expect"; \
	    else \
	      printf 'BAD      expected content: %s\n' "$$expect"; \
	      fail=1; \
	    fi; \
	  fi; \
	}; \
	check_link "$(HOME)/.agents/AGENTS.md" ""; \
	check_link "$(HOME)/.agents/RESOLVER.md" ""; \
	check_link "$(HOME)/.claude/CLAUDE.md" "@~/.agents/AGENTS.md"; \
	check_link "$(HOME)/.codex/AGENTS.md" ""; \
	check_link "$(HOME)/.config/opencode/AGENTS.md" ""; \
	check_link "$(HOME)/.config/agents/AGENTS.md" ""; \
	skills="$(HOME)/.agents/skills"; \
	if [[ -d "$$skills" || -L "$$skills" ]]; then \
	  count="$$(find -L "$$skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"; \
	  printf 'OK       %s (%s skill dirs)\n' "$$skills" "$$count"; \
	  if [[ "$$count" -eq 0 ]]; then \
	    printf 'WARN     no skill directories under %s\n' "$$skills"; \
	  fi; \
	else \
	  printf 'MISSING  %s\n' "$$skills"; \
	  fail=1; \
	fi; \
	if [[ "$$fail" -ne 0 ]]; then \
	  printf 'agents-verify failed\n' >&2; \
	  exit 1; \
	fi; \
	printf 'agents-verify OK\n'

# Shared: link hub skills into ROOT/.agents/skills (skills list via $$1)
# Skips missing roots (personal-only paths on other machines).
define AGENTS_LINK_INTO
	src="$(HOME)/.agents/skills"; \
	root_raw="$$(python3 -c 'import os,sys; print(os.path.expanduser(sys.argv[1]))' "$(1)")"; \
	if [[ ! -d "$$root_raw" ]]; then \
	  printf 'SKIP     missing target: %s\n' "$$root_raw"; \
	else \
	root="$$(cd "$$root_raw" && pwd)"; \
	dest="$$root/.agents/skills"; \
	mkdir -p "$$dest"; \
	skills="$(2)"; \
	if [[ -z "$$skills" ]]; then skills="$(3)"; fi; \
	for name in $$skills; do \
	  if [[ ! -d "$$src/$$name" ]]; then \
	    printf 'SKIP     missing hub skill: %s\n' "$$name"; \
	    continue; \
	  fi; \
	  target="$$dest/$$name"; \
	  if [[ -L "$$target" ]]; then \
	    ln -sfn "$$src/$$name" "$$target"; \
	    printf 'RELINK   %s -> %s\n' "$$target" "$$src/$$name"; \
	  elif [[ -e "$$target" ]]; then \
	    printf 'CONFLICT %s exists (not a symlink); leave alone\n' "$$target"; \
	  else \
	    ln -s "$$src/$$name" "$$target"; \
	    printf 'LINK     %s -> %s\n' "$$target" "$$src/$$name"; \
	  fi; \
	done; \
	fi
endef

agents-link-vault:
	@set -euo pipefail; \
	if [[ -z "$(VAULT)" ]]; then \
	  printf 'Usage: make agents-link-vault VAULT=~/vaults/personal [SKILLS="…"] [APPEND=1]\n' >&2; \
	  exit 1; \
	fi; \
	$(call AGENTS_LINK_INTO,$(VAULT),$(SKILLS),$(AGENTS_VAULT_SKILLS)); \
	if [[ "$(APPEND)" == "1" ]]; then \
	  skills="$(SKILLS)"; \
	  if [[ -z "$$skills" ]]; then skills="$(AGENTS_VAULT_SKILLS)"; fi; \
	  printf 'vault\t%s\t%s\n' "$(VAULT)" "$$skills" >> "$(AGENTS_LINKS_REGISTRY)"; \
	  printf 'APPEND   %s\n' "$(AGENTS_LINKS_REGISTRY)"; \
	fi

agents-link-code:
	@set -euo pipefail; \
	if [[ -z "$(CODE)" ]]; then \
	  printf 'Usage: make agents-link-code CODE=~/code/foo [SKILLS="…"] [APPEND=1]\n' >&2; \
	  exit 1; \
	fi; \
	$(call AGENTS_LINK_INTO,$(CODE),$(SKILLS),$(AGENTS_CODE_SKILLS)); \
	if [[ "$(APPEND)" == "1" ]]; then \
	  skills="$(SKILLS)"; \
	  if [[ -z "$$skills" ]]; then skills="$(AGENTS_CODE_SKILLS)"; fi; \
	  printf 'code\t%s\t%s\n' "$(CODE)" "$$skills" >> "$(AGENTS_LINKS_REGISTRY)"; \
	  printf 'APPEND   %s\n' "$(AGENTS_LINKS_REGISTRY)"; \
	fi

# Re-link every registry row (portable across machines after clone + agents-restow)
# Optional 4th field: hosts=personal|work (comma-separated). Omit = all machines.
agents-link-sync:
	@set -euo pipefail; \
	reg="$(AGENTS_LINKS_REGISTRY)"; \
	if [[ ! -f "$$reg" ]]; then \
	  printf 'MISSING  %s\n' "$$reg" >&2; \
	  exit 1; \
	fi; \
	host="$$(scutil --get LocalHostName 2>/dev/null || hostname -s)"; \
	role=personal; \
	case "$$host" in \
	  mbp14m4*|*-work*|work*) role=work ;; \
	esac; \
	printf 'HOST     %s (role=%s)\n' "$$host" "$$role"; \
	while IFS=$$'\t' read -r kind path skills hosts || [[ -n "$$kind" ]]; do \
	  [[ -z "$$kind" || "$$kind" =~ ^# ]] && continue; \
	  if [[ -n "$${hosts:-}" && "$$hosts" == hosts=* ]]; then \
	    tags="$${hosts#hosts=}"; \
	    if [[ ",$$tags," != *",$$role,"* ]]; then \
	      printf 'SKIP     hosts=%s (this machine role=%s): %s %s\n' "$$tags" "$$role" "$$kind" "$$path"; \
	      continue; \
	    fi; \
	  fi; \
	  case "$$kind" in \
	    vault) \
	      $(MAKE) agents-link-vault VAULT="$$path" SKILLS="$$skills" ;; \
	    code) \
	      $(MAKE) agents-link-code CODE="$$path" SKILLS="$$skills" ;; \
	    *) \
	      printf 'SKIP     unknown kind: %s\n' "$$kind" ;; \
	  esac; \
	done < "$$reg"; \
	printf 'agents-link-sync OK\n'
