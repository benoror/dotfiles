#!/usr/bin/env bash
# Read-only health check: is this machine on the latest dotfiles, and do the
# agent skills resolve in every agent skill dir?
# Usage: agents-doctor.sh [--fix]
#   --fix  git pull --ff-only, then make agents-restow agents-skillsets
# Output: counts and names only. Exit: 0 ok, 1 problems found.
# NO_FETCH=1 skips git fetch (no repo writes). Over SSH, see stow/agents/README.md.
set -uo pipefail

ROOT="${DOTFILES:-}"
if [[ -z "$ROOT" ]]; then
  src="${BASH_SOURCE[0]:-}"
  if [[ -n "$src" && -f "$src" ]]; then ROOT="$(cd "$(dirname "$src")/.." && pwd)"; else ROOT="$HOME/dotfiles"; fi
fi
SKILLS="$ROOT/stow/agents/.agents/skills"
host="$(hostname -s 2>/dev/null || hostname)"
bad=0; missing_all=""; dangling_all=""
note() { printf '%-9s %s\n' "$1" "$2"; }

[[ -d "$ROOT/.git" ]] || { note ERROR "no dotfiles repo at $ROOT"; exit 2; }

if [[ "${1:-}" == --fix ]]; then
  git -C "$ROOT" pull --ff-only && make -C "$ROOT" --no-print-directory agents-restow agents-skillsets || exit 2
fi

# 1. Repo state
if [[ -n "${NO_FETCH:-}" ]]; then note INFO "NO_FETCH set; behind is vs last fetch"
else git -C "$ROOT" fetch -q origin 2>/dev/null || note WARN "fetch failed; behind count may be old"; fi
commit="$(git -C "$ROOT" rev-parse --short HEAD)"
behind="$(git -C "$ROOT" rev-list --count HEAD..origin/master 2>/dev/null || echo '?')"
dirty="$(git -C "$ROOT" status --porcelain | wc -l | tr -d ' ')"
note REPO "$commit, behind origin/master: $behind, dirty files: $dirty"
[[ "$behind" == 0 ]] || bad=1

# 2. Skill dirs
repo_skills="$(cd "$SKILLS" && for d in */; do [[ -f "$d/SKILL.md" ]] && printf '%s\n' "${d%/}"; done)"
for t in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.cursor/skills"; do
  if [[ ! -d "$t" ]]; then note ABSENT "$t (not installed)"; bad=1; continue; fi
  miss=""; dang=""; extra=""
  for s in $repo_skills; do [[ -e "$t/$s" ]] || miss="$miss $s"; done
  for l in "$t"/*; do
    n="$(basename "$l")"
    [[ -L "$l" && ! -e "$l" ]] && { dang="$dang $n"; continue; }
    [[ -L "$l" ]] && case "$(readlink "$l")" in */stow/agents/*|*/.cache/skillsets/*) continue ;; esac
    printf '%s\n' "$repo_skills" | grep -qxF "$n" || extra="$extra $n"
  done
  note TARGET "$t: $(ls -1 "$t" | wc -l | tr -d ' ') entries, missing:${miss:- none}, dangling:${dang:- none}"
  [[ -n "$extra" ]] && note EXTRA "$t not in repo:$extra"
  [[ -n "$miss$dang" ]] && bad=1
  missing_all="$missing_all$miss"; dangling_all="$dangling_all$dang"
done
for e in .codex/AGENTS.md .config/opencode/AGENTS.md .claude/CLAUDE.md .agents/AGENTS.md; do
  [[ -e "$HOME/$e" ]] && note ENTRY "~/$e OK" || { note ENTRY "~/$e missing"; bad=1; }
done

# 3. Upstream skill sets (read-only)
if "$ROOT/scripts/skillsets.sh" check > /tmp/agents-doctor.$$ 2>&1; then sets=OK; else sets=DRIFT; bad=1; fi
grep -vE '^SET ' /tmp/agents-doctor.$$ | sed 's/^/  /'; rm -f /tmp/agents-doctor.$$
note SETS "$sets"

# 4. Summary
m="$(printf '%s\n' $missing_all | sort -u | tr '\n' ' ')"; d="$(printf '%s\n' $dangling_all | sort -u | tr '\n' ' ')"
note SUMMARY "$host $commit behind=$behind dirty=$dirty sets=$sets missing=[${m% }] dangling=[${d% }]"
exit "$bad"
