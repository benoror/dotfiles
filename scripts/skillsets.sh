#!/usr/bin/env bash
# Skill sets: upstream shallow sparse clones + local hub skills, linked into
# agent skill dirs, with a read-only drift check.
# Usage: skillsets.sh install | check | list | fetch
#   install  clone or update upstream sets, link enabled sets into every target
#   check    read-only: REGISTRY rows vs upstream, installed links vs upstream
#   list     print skills per set
#   fetch    clone or update upstream caches only (no links)
# Safety: only creates, replaces or prunes symlinks it owns (pointing into the
# skill set cache or this repo). Never touches real dirs or other links.
# Exit: 0 ok, 1 drift or clash (check), 2 error. install warns on clashes, exits 0. Works with macOS bash 3.2.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="${SKILLSETS_MANIFEST:-$ROOT/stow/agents/skillsets.manifest}"
REGISTRY="${SKILLSETS_REGISTRY:-$ROOT/stow/agents/REGISTRY.md}"
CACHE="${SKILLSETS_CACHE:-$HOME/.cache/skillsets}"
AGENTS_DIR="$HOME/.agents/skills"
TARGETS="${SKILLSETS_TARGETS:-$AGENTS_DIR $HOME/.claude/skills}"
cmd="${1:-check}"
drift=0

note() { printf '%-8s %s\n' "$1" "$2"; }
sets() { grep -vE '^[[:space:]]*(#|$)' "$MANIFEST"; }

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

skills_in() { # base -> "<skill>\t<abs dir>"
  [[ -d "$1" ]] || return 0
  find "$1" -mindepth 2 -maxdepth 3 -name SKILL.md | while read -r f; do
    d="$(dirname "$f")"; printf '%s\t%s\n' "$(basename "$d")" "$d"
  done | sort
}

included() { [[ -z "$2" ]] && return 0; case " $2 " in *" $1 "*) return 0 ;; esac; return 1; }

registry_rows() {
  [[ "$1" == - || ! -f "$REGISTRY" ]] && return 0
  awk -F'|' -v t="[$1](" 'index($3, t) { n=$2; gsub(/[ `\/]/, "", n); if (n != "") print n }' "$REGISTRY" | sort -u
}

ours() { # link path -> 0 if it is a symlink we own (points into cache or this repo)
  [[ -L "$1" ]] || return 1
  local t; t="$(readlink "$1")"
  case "$t" in "$CACHE"/*|"$ROOT"/*|*/stow/agents/.agents/skills/*) return 0 ;; esac
  return 1
}

leftover() { # real dir holding only empty dirs or our broken links (Stow --no-folding remains)
  local f
  [[ -d "$1" && ! -L "$1" ]] || return 1
  while IFS= read -r f; do
    [[ -L "$f" && ! -e "$f" ]] && ours "$f" && continue
    return 1
  done < <(find "$1" ! -type d)
  return 0
}

clear_leftover() { # remove only our broken links and empty dirs
  find "$1" -type l ! -exec test -e {} \; -delete
  find "$1" -depth -type d -empty -delete
}

link_one() { # target-dir name src
  local link="$1/$2"
  if [[ -L "$link" ]]; then
    if ours "$link"; then ln -sfn "$3" "$link"; return 0; fi
    note CLASH "$link links elsewhere ($(readlink "$link")); skipped"; drift=1; return 0
  fi
  if leftover "$link"; then clear_leftover "$link"; note CLEANED "$link (Stow leftover)"; fi
  if [[ -e "$link" ]]; then note CLASH "$link is a real dir; skipped"; drift=1; return 0; fi
  ln -s "$3" "$link"
}

prune() { # target-dir: drop our links that no longer resolve
  local l
  for l in "$1"/* "$1"/.[!.]*; do
    [[ -L "$l" && ! -e "$l" ]] && ours "$l" && { rm "$l"; note PRUNED "$l"; }
  done
  return 0
}

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

if [[ "$cmd" == install ]]; then
  for t in $TARGETS; do
    if [[ -L "$t" ]]; then note ERROR "$t is a folded link; run make agents-restow first"; exit 2; fi
    mkdir -p "$t"
  done
fi

while IFS=$'\t' read -r name type src sub prefix enabled tag include; do
  include="${include:-}"; [[ "$prefix" == - ]] && prefix=""
  if [[ "$type" == local ]]; then
    base="$ROOT/$sub"; rev=local
  else
    if [[ "$cmd" == install || "$cmd" == fetch ]]; then
      [[ "$enabled" != 1 && "$cmd" == install ]] && { note SKIP "$name (enabled=0)"; continue; }
      dir="$CACHE/$name"
    else
      dir="$tmp/$name"
    fi
    fetch "$dir" "$src" "$sub" || { note ERROR "$name: fetch failed ($src)"; exit 2; }
    base="$dir/$sub"; rev="$(git -C "$dir" log -1 --format=%h)"
  fi
  skills_in "$base" > "$tmp/all"
  : > "$tmp/$name.up"
  while IFS=$'\t' read -r s d; do included "$s" "$include" && printf '%s\t%s\n' "$s" "$d" >> "$tmp/$name.up"; done < "$tmp/all"
  cut -f1 "$tmp/all" > "$tmp/$name.names"
  note SET "$name ($type @ $rev, $(wc -l < "$tmp/$name.up" | tr -d ' ') linked of $(wc -l < "$tmp/$name.names" | tr -d ' '), enabled=$enabled)"

  # included skills missing from the source are drift for upstream, an error for local
  for s in $include; do
    grep -qxF "$s" "$tmp/$name.names" || { note DRIFT "$name: include lists $s, not in source"; drift=1; }
  done

  case "$cmd" in
    list) cut -f1 "$tmp/$name.up" | sed 's/^/  /' ;;
    fetch) : ;;
    install)
      [[ "$enabled" == 1 ]] || continue
      for t in $TARGETS; do
        # Stow owns local skills in ~/.agents/skills
        [[ "$type" == local && "$t" == "$AGENTS_DIR" ]] && continue
        while IFS=$'\t' read -r s d; do link_one "$t" "$prefix$s" "$d"; done < "$tmp/$name.up"
      done ;;
    check)
      if [[ "$type" == upstream ]]; then
        registry_rows "$tag" > "$tmp/$name.reg"
        for s in $(comm -13 "$tmp/$name.names" "$tmp/$name.reg"); do note DRIFT "$name: REGISTRY lists $s, not upstream"; drift=1; done
        if [[ "$enabled" == 1 ]]; then
          if [[ ! -d "$CACHE/$name/.git" ]]; then note MISSING "$name not installed (make agents-skillsets)"; drift=1
          else
            crev="$(git -C "$CACHE/$name" log -1 --format=%h)"
            [[ "$crev" != "$rev" ]] && { note STALE "$name cache @ $crev, upstream @ $rev"; drift=1; }
          fi
        fi
      fi
      if [[ "$enabled" == 1 ]]; then
        for t in $TARGETS; do
          [[ -d "$t" ]] || continue
          [[ "$type" == local && "$t" == "$AGENTS_DIR" ]] && continue
          while IFS=$'\t' read -r s d; do
            l="$t/$prefix$s"; want="$d"
            [[ "$type" == upstream ]] && want="$CACHE/$name${d#"$tmp/$name"}"
            if [[ ! -e "$l" && ! -L "$l" ]]; then note MISSING "$l"; drift=1
            elif ! ours "$l"; then note CLASH "$l is not ours (real dir or other link)"; drift=1
            elif [[ "$(readlink "$l")" != "$want" ]]; then note STALE "$l -> $(readlink "$l")"; drift=1; fi
          done < "$tmp/$name.up"
        done
      fi ;;
  esac
done < <(sets)

if [[ "$cmd" == install ]]; then
  for t in $TARGETS; do prune "$t"; done
  note LINKED "$TARGETS"
  [[ "$drift" -ne 0 ]] && note WARN "clashes left alone (see CLASH lines); install still OK"
  exit 0
fi
if [[ "$cmd" == check ]]; then
  for t in $TARGETS; do
    [[ -d "$t" ]] || continue
    for l in "$t"/*; do [[ -L "$l" && ! -e "$l" ]] && ours "$l" && { note BROKEN "$l"; drift=1; }; done
  done
  [[ "$drift" -eq 0 ]] && note OK "skill sets in sync" || note DRIFT "see lines above"
fi
exit "$drift"
