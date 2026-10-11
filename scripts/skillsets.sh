#!/usr/bin/env bash
# Upstream skill sets: shallow sparse clone + prefixed symlinks + drift checks.
# Usage: skillsets.sh install | check | list
#   install  clone or update each set, link enabled sets into SKILLSETS_TARGET
#   check    read-only: REGISTRY rows vs upstream, installed links vs upstream
#   list     print upstream skills per set
# Exit: 0 ok, 1 drift, 2 error. Works with macOS bash 3.2.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="${SKILLSETS_MANIFEST:-$ROOT/stow/agents/skillsets.manifest}"
REGISTRY="${SKILLSETS_REGISTRY:-$ROOT/stow/agents/REGISTRY.md}"
CACHE="${SKILLSETS_CACHE:-$HOME/.cache/skillsets}"
TARGET="${SKILLSETS_TARGET:-$HOME/.agents/skills}"
cmd="${1:-check}"
drift=0

note() { printf '%-8s %s\n' "$1" "$2"; }

sets() { grep -vE '^[[:space:]]*(#|$)' "$MANIFEST"; }

# Fetch into $1 (dir) from $2 (repo) limited to $3 (subpath). check mode uses a temp dir.
fetch() {
  local dir="$1" repo="$2" sub="$3"
  if [[ -d "$dir/.git" ]]; then
    git -C "$dir" pull -q --ff-only || return 2
  else
    mkdir -p "$(dirname "$dir")"
    git clone -q --depth 1 --filter=blob:none --sparse "$repo" "$dir" || return 2
    git -C "$dir" sparse-checkout set "$sub" >/dev/null || return 2
  fi
}

# Print "<skill>\t<abs dir>" for every SKILL.md under subpath (depth 1 or 2).
skills_in() {
  local base="$1/$2"
  [[ -d "$base" ]] || return 0
  find "$base" -mindepth 2 -maxdepth 3 -name SKILL.md | while read -r f; do
    d="$(dirname "$f")"; printf '%s\t%s\n' "$(basename "$d")" "$d"
  done | sort
}

included() { # name include-list
  [[ -z "$2" ]] && return 0
  case " $2 " in *" $1 "*) return 0 ;; esac
  return 1
}

registry_rows() { # tag -> skill names listed in REGISTRY with that source tag
  local tag="$1"
  [[ -f "$REGISTRY" ]] || return 0
  awk -F'|' -v t="[$tag](" '
    index($3, t) { n=$2; gsub(/[ `\/]/, "", n); if (n != "") print n }' "$REGISTRY" | sort -u
}

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

while IFS=$'\t' read -r name repo sub prefix enabled tag include; do
  include="${include:-}"
  if [[ "$cmd" == install && "$enabled" != 1 ]]; then note SKIP "$name (enabled=0)"; continue; fi
  if [[ "$cmd" == install ]]; then dir="$CACHE/$name"; else dir="$tmp/$name"; fi
  if ! fetch "$dir" "$repo" "$sub"; then note ERROR "$name: fetch failed ($repo)"; exit 2; fi
  rev="$(git -C "$dir" log -1 --format=%h)"
  skills_in "$dir" "$sub" > "$tmp/$name.up"
  cut -f1 "$tmp/$name.up" > "$tmp/$name.names"
  note SET "$name @ $rev ($(wc -l < "$tmp/$name.names" | tr -d ' ') upstream skills, enabled=$enabled)"

  if [[ "$cmd" == list ]]; then sed 's/^/  /' "$tmp/$name.names"; continue; fi

  if [[ "$cmd" == install && "$enabled" == 1 ]]; then
    if [[ -L "$TARGET" ]]; then
      note ERROR "$TARGET is a folded Stow link; run make agents-restow first"; exit 2
    fi
    mkdir -p "$TARGET"
    # drop our own links that no longer resolve (renamed or removed upstream)
    for l in "$TARGET/$prefix"*; do
      [[ -L "$l" && ! -e "$l" ]] && { rm "$l"; note PRUNED "$(basename "$l")"; }
    done
    while IFS=$'\t' read -r s d; do
      included "$s" "$include" || continue
      link="$TARGET/$prefix$s"
      if [[ -e "$link" && ! -L "$link" ]]; then note CLASH "$link is a real dir; skipped"; drift=1; continue; fi
      ln -sfn "$d" "$link"
    done < "$tmp/$name.up"
    note LINKED "$name -> $TARGET/$prefix*"
  fi

  if [[ "$cmd" == check ]]; then
    # 1. REGISTRY rows that no longer exist upstream
    registry_rows "$tag" > "$tmp/$name.reg"
    gone="$(comm -13 "$tmp/$name.names" "$tmp/$name.reg")"
    for s in $gone; do note DRIFT "$name: REGISTRY lists $s, not upstream"; drift=1; done
    # 2. installed state for enabled sets
    if [[ "$enabled" == 1 ]]; then
      cached="$CACHE/$name"
      if [[ ! -d "$cached/.git" ]]; then
        note MISSING "$name not installed (make agents-skillsets)"; drift=1
      else
        crev="$(git -C "$cached" log -1 --format=%h)"
        [[ "$crev" != "$rev" ]] && { note STALE "$name cache @ $crev, upstream @ $rev"; drift=1; }
        while read -r s; do
          included "$s" "$include" || continue
          [[ -e "$TARGET/$prefix$s" ]] || { note MISSING "$TARGET/$prefix$s"; drift=1; }
        done < "$tmp/$name.names"
        for l in "$TARGET/$prefix"*; do
          [[ -L "$l" && ! -e "$l" ]] && { note BROKEN "$l"; drift=1; }
        done
      fi
    fi
  fi
done < <(sets)

if [[ "$cmd" == check ]]; then
  [[ "$drift" -eq 0 ]] && note OK "skill sets in sync" || note DRIFT "see lines above"
fi
exit "$drift"
