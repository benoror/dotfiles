SHELL := /usr/bin/env bash

DOTFILES_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
STOW_DIR := $(DOTFILES_DIR)/stow
TARGET := $(HOME)

.PHONY: help agents-install agents-restow agents-uninstall agents-verify

help:
	@printf '%s\n' \
	  'make agents-install    Install agents Stow package into $$HOME' \
	  'make agents-restow     Restow agents package (reconcile links)' \
	  'make agents-verify     Check expected agent entrypoints' \
	  'make agents-uninstall  Remove agents Stow package links'

agents-install:
	stow --dir="$(STOW_DIR)" --target="$(TARGET)" --stow agents

agents-restow:
	stow --dir="$(STOW_DIR)" --target="$(TARGET)" --restow agents

agents-uninstall:
	stow --dir="$(STOW_DIR)" --target="$(TARGET)" --delete agents

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
