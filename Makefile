SHELL := /usr/bin/env bash

DOTFILES_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
STOW_DIR := $(DOTFILES_DIR)/stow
TARGET := $(HOME)

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

.PHONY: help install restow uninstall
.PHONY: install-core restow-core uninstall-core
.PHONY: install-editors restow-editors uninstall-editors
.PHONY: install-mac restow-mac uninstall-mac
.PHONY: install-secrets restow-secrets uninstall-secrets
.PHONY: install-linux restow-linux uninstall-linux
.PHONY: install-all restow-all uninstall-all
.PHONY: agents-install agents-restow agents-uninstall agents-verify

help:
	@printf '%s\n' \
	  'Groups (safe by default — no ssh/gnupg/linux):' \
	  '  make install            Install core + editors + mac' \
	  '  make restow             Restow those groups' \
	  '  make uninstall          Uninstall those groups' \
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
	  '  make agents-verify      Check agent entrypoints' \
	  '  make agents-install     Alias for install-agents'

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

# --- agents aliases + verify -----------------------------------------------

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
	if [[ "$$fail" -ne 0 ]]; then \
	  printf 'agents-verify failed\n' >&2; \
	  exit 1; \
	fi; \
	printf 'agents-verify OK\n'
