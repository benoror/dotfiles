#!/usr/bin/env bash
# Wire tool-specific AGENTS/CLAUDE entrypoints to the ~/.agents hub.
# Run after: stow -d ~/dotfiles/stow -t ~ agents
set -euo pipefail

HUB="${HUB:-$HOME/.agents}"
DRY_RUN=0
VERIFY_ONLY=0
SKIP_ABSENT=0
CONFLICTS=0

usage() {
  cat <<'EOF'
Usage: symlink-agents.sh [options]

  Provision and verify symlinks from coding tools into ~/.agents.

Options:
  --dry-run       Show actions; do not write.
  --verify        Report status only; do not write.
  --skip-absent   Only wire tools whose base dir already exists.
                  Default: create missing base dirs (covers future installs).
  -h, --help      Show this help.

Conflict prompt choices:
  s  skip this path
  b  backup existing path (*.bak-YYYYMMDDHHMMSS) then replace
  a  abort
EOF
}

log() { printf '%s\n' "$*"; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
err() { printf 'ERROR: %s\n' "$*" >&2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --verify) VERIFY_ONLY=1; shift ;;
    --skip-absent) SKIP_ABSENT=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) err "Unknown option: $1"; usage; exit 1 ;;
  esac
done

if [[ ! -d "$HUB" ]]; then
  err "Hub not found: $HUB"
  err "Run first: stow -d \"\$HOME/dotfiles/stow\" -t \"\$HOME\" agents"
  exit 1
fi

if [[ ! -f "$HUB/AGENTS.md" ]]; then
  err "Missing hub file: $HUB/AGENTS.md"
  exit 1
fi

timestamp() { date +%Y%m%d%H%M%S; }

resolve_path() {
  local p="$1"
  if command -v realpath >/dev/null 2>&1; then
    realpath "$p" 2>/dev/null || readlink "$p" || printf '%s' "$p"
  else
    readlink "$p" 2>/dev/null || printf '%s' "$p"
  fi
}

same_target() {
  local dest="$1"
  local src="$2"
  [[ -L "$dest" ]] || return 1
  local cur
  cur="$(readlink "$dest")"
  [[ "$cur" == "$src" ]] && return 0
  # Also accept if both resolve to the same path
  local a b
  a="$(resolve_path "$dest")"
  b="$(resolve_path "$src")"
  [[ -n "$a" && -n "$b" && "$a" == "$b" ]]
}

backup_path() {
  local dest="$1"
  local bak="${dest}.bak-$(timestamp)"
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "DRY-RUN: mv \"$dest\" \"$bak\""
    return 0
  fi
  mv "$dest" "$bak"
  log "Backed up: $dest -> $bak"
}

prompt_conflict() {
  local dest="$1"
  local kind="$2"
  CONFLICTS=$((CONFLICTS + 1))
  warn "Conflict at $dest ($kind)"
  ls -ld "$dest" 2>/dev/null || true
  if [[ -t 0 ]]; then
    local choice
    while true; do
      printf 'Resolve [s]kip / [b]ackup+replace / [a]bort: ' >&2
      read -r choice
      case "$choice" in
        s|S) return 1 ;;
        b|B) return 0 ;;
        a|A) err "Aborted by user."; exit 2 ;;
        *) warn "Enter s, b, or a." ;;
      esac
    done
  else
    err "Non-interactive shell; skip conflict: $dest"
    return 1
  fi
}

ensure_dir() {
  local dir="$1"
  if [[ -d "$dir" ]]; then
    return 0
  fi
  if [[ "$SKIP_ABSENT" -eq 1 ]]; then
    log "Skip absent dir: $dir (--skip-absent)"
    return 1
  fi
  if [[ "$VERIFY_ONLY" -eq 1 ]]; then
    warn "Missing dir: $dir"
    return 1
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "DRY-RUN: mkdir -p \"$dir\""
    return 0
  fi
  mkdir -p "$dir"
  log "Created dir: $dir"
}

write_shim() {
  local dest="$1"
  local content="$2"
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ -f "$dest" && ! -L "$dest" ]]; then
      local existing
      existing="$(<"$dest")"
      if [[ "$existing" == "$content" ]]; then
        log "OK shim: $dest"
        return 0
      fi
    fi
    if [[ "$VERIFY_ONLY" -eq 1 ]]; then
      warn "Shim differs or is not plain file: $dest"
      CONFLICTS=$((CONFLICTS + 1))
      return 0
    fi
    if ! prompt_conflict "$dest" "existing shim/file"; then
      log "Skipped: $dest"
      return 0
    fi
    backup_path "$dest"
  fi
  if [[ "$VERIFY_ONLY" -eq 1 ]]; then
    warn "Missing shim: $dest"
    CONFLICTS=$((CONFLICTS + 1))
    return 0
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "DRY-RUN: write shim $dest <= @AGENTS.md"
    return 0
  fi
  printf '%s\n' "$content" >"$dest"
  log "Wrote shim: $dest"
}

link_file() {
  local src="$1"
  local dest="$2"
  if same_target "$dest" "$src"; then
    log "OK link: $dest -> $src"
    return 0
  fi
  if [[ -e "$dest" || -L "$dest" ]]; then
    if [[ "$VERIFY_ONLY" -eq 1 ]]; then
      warn "Wrong or non-link target: $dest (want -> $src)"
      CONFLICTS=$((CONFLICTS + 1))
      return 0
    fi
    if ! prompt_conflict "$dest" "existing path"; then
      log "Skipped: $dest"
      return 0
    fi
    backup_path "$dest"
  elif [[ "$VERIFY_ONLY" -eq 1 ]]; then
    warn "Missing link: $dest (want -> $src)"
    CONFLICTS=$((CONFLICTS + 1))
    return 0
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "DRY-RUN: ln -s \"$src\" \"$dest\""
    return 0
  fi
  ln -s "$src" "$dest"
  log "Linked: $dest -> $src"
}

wire_agents_link() {
  local base="$1"
  ensure_dir "$base" || return 0
  link_file "$HUB/AGENTS.md" "$base/AGENTS.md"
}

# --- tools ---
# Default: create base dirs so future tool installs find the links ready.
# Use --skip-absent to only touch tools that already exist.

wire_agents_link "$HOME/.claude"
if [[ -d "$HOME/.claude" ]] || [[ "$SKIP_ABSENT" -eq 0 ]]; then
  # Claude expects CLAUDE.md locally; point it at AGENTS.md in the same dir.
  if ensure_dir "$HOME/.claude"; then
    write_shim "$HOME/.claude/CLAUDE.md" "@AGENTS.md"
  fi
fi

wire_agents_link "$HOME/.cursor"
wire_agents_link "$HOME/.codex"
wire_agents_link "$HOME/.config/opencode"
wire_agents_link "$HOME/.config/agents"

if [[ "$CONFLICTS" -gt 0 && ( "$VERIFY_ONLY" -eq 1 || "$DRY_RUN" -eq 1 ) ]]; then
  warn "Issues reported: $CONFLICTS"
  exit 1
fi

if [[ "$CONFLICTS" -gt 0 ]]; then
  warn "Skipped conflicts remain: $CONFLICTS"
  exit 1
fi

log "Done. Hub: $HUB"
