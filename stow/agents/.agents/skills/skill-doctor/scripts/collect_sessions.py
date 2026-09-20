#!/usr/bin/env python3
"""Collect local agent sessions and skills for scoring.

The orchestrator asks each harness plugin for sessions, discovers installed
skills, detects which sessions used which skills, and emits:

  <out>/inventory.json        - skills, per-session stats, sampling decisions
  <out>/transcripts/<id>.md   - condensed transcripts for sampled sessions

Everything runs locally; nothing is uploaded. Python 3.9+, stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from harnesses import CODING_HARNESSES, FLEET_HARNESSES, PLUGINS, plugin_ids, requested_plugins
from harnesses.claude import find_claude_session_files, parse_claude_session
from harnesses.codex import parse_codex_session
from harnesses.common import (
    detect_skills_from_entries,
    infer_session_repos,
    is_scoreable,
    render_transcript,
    session_matches_repos,
)
from harnesses.grok import find_grok_session_files, parse_grok_session
from harnesses.pi import find_pi_session_files, parse_pi_session
from harnesses.zcode import parse_zcode_session


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--harness",
        choices=("auto", "all") + plugin_ids(),
        default="auto",
        help="session source (default: auto; scans every locally available source)",
    )
    for plugin in PLUGINS.values():
        plugin.add_cli_flags(p)
    p.add_argument(
        "--repo",
        action="append",
        default=[],
        help="project to include (repeatable; default: git root of cwd, else cwd)",
    )
    p.add_argument(
        "--all-conversations",
        action="store_true",
        help="score conversations from every project represented in local history",
    )
    p.add_argument(
        "--include-global-skills",
        action="store_true",
        help="also discover global skills for the selected harness family",
    )
    p.add_argument("--days", type=int, default=45, help="only consider sessions modified in the last N days")
    p.add_argument("--max-sessions", type=int, default=12, help="max sessions to sample for scoring")
    p.add_argument("--per-skill", type=int, default=3, help="max sampled sessions per skill")
    p.add_argument("--no-skill", type=int, default=4, help="max sampled sessions that used no skill")
    p.add_argument("--skills-dir", action="append", default=[], help="extra skills directory to scan (repeatable)")
    p.add_argument("--include-subagents", action="store_true", help="include subagent/child sessions")
    p.add_argument("--out", default="./skill-doctor-report")
    return p.parse_args()


def resolve_repo(repo_arg) -> Path:
    if repo_arg:
        return Path(repo_arg).expanduser().resolve()
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10
        )
        if res.returncode == 0 and res.stdout.strip():
            return Path(res.stdout.strip()).resolve()
    except (subprocess.TimeoutExpired, OSError):
        pass
    return Path.cwd().resolve()


def resolve_repos(repo_args):
    if not repo_args:
        return [resolve_repo(None)]
    repos = []
    seen = set()
    for value in repo_args:
        repo = resolve_repo(value)
        if repo in seen:
            continue
        seen.add(repo)
        repos.append(repo)
    return repos


def project_skill_roots(repos):
    if isinstance(repos, Path):
        repos = [repos]
    roots = []
    for repo in repos:
        roots.extend((
            repo / ".agents" / "skills",
            repo / ".claude" / "skills",
            repo / ".codex" / "skills",
        ))
    return roots


def coding_hub_skill_roots():
    return [
        Path.home() / ".agents" / "skills",
        Path.home() / ".claude" / "skills",
        Path.home() / ".codex" / "skills",
    ]


def global_skill_roots_for_run(args):
    """Global skill dirs for the selected harness family.

    grok_bot-only runs use /home/box/agent-data/workflows and skip the coding hub.
    Auto and other coding harnesses keep the hub and skip fleet workflows.
    Mix both only with --skills-dir. pstack is never scanned.
    """
    if not args.include_global_skills:
        return []
    roots = []
    if args.harness == "grok_bot":
        roots.extend(PLUGINS["grok_bot"].global_skill_roots(args))
        return roots
    if args.harness in ("auto", "all") or args.harness in CODING_HARNESSES:
        roots.extend(coding_hub_skill_roots())
        for plugin_id, plugin in PLUGINS.items():
            if plugin_id in FLEET_HARNESSES:
                continue
            if plugin.is_requested(args.harness):
                roots.extend(plugin.global_skill_roots(args))
    return roots


def discover_skills(repos, codex_home: Path, extra_dirs, include_global: bool,
                    pi_home: Path = None, grok_home: Path = None, zcode_home: Path = None,
                    extra_roots=None):
    roots = project_skill_roots(repos)
    if include_global:
        if extra_roots is not None:
            roots += list(extra_roots)
        else:
            roots += [
                Path(codex_home) / "skills",
                Path.home() / ".agents" / "skills",
                Path.home() / ".claude" / "skills",
            ]
            for home in (pi_home, grok_home, zcode_home):
                if home is not None:
                    roots.append(Path(home) / "skills")
    roots += [Path(d).expanduser() for d in extra_dirs]
    return load_skills_from_roots(roots)


def load_skills_from_roots(roots):
    skills = {}
    for root in roots:
        if not root.is_dir():
            continue
        for skill_md in sorted(root.glob("*/SKILL.md")):
            name = skill_md.parent.name
            if name in skills:
                continue
            try:
                text = skill_md.read_text(errors="replace")
            except OSError:
                continue
            desc = ""
            m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
            if m:
                desc = m.group(1).strip().strip("\"'")[:300]
            skills[name] = {
                "name": name,
                "path": str(skill_md),
                "description": desc,
                "bytes": skill_md.stat().st_size,
                "modified_at": datetime.fromtimestamp(skill_md.stat().st_mtime, tz=timezone.utc).isoformat(),
            }
    return skills


def collect_from_plugins(args, cutoff, skill_names):
    sessions = []
    sources = {}
    scanned_count = 0
    in_scope_count = 0
    repos = [] if args.all_conversations else resolve_repos(args.repo)
    plugins = requested_plugins(args.harness)
    for plugin in plugins:
        available = plugin.source_available(args)
        if not available:
            if args.harness == plugin.id:
                print(plugin.missing_error(args), file=sys.stderr)
                sys.exit(1)
            continue
        collected, note = plugin.collect(args, cutoff, skill_names)
        if note:
            sources[plugin.id] = note
            scanned_count += int(note.get("records_in_window") or 0)
        for session in collected:
            if not args.all_conversations and not session_matches_repos(
                session["meta"].get("cwd"),
                repos,
            ):
                continue
            in_scope_count += 1
            if not is_scoreable(session["stats"]):
                continue
            sessions.append(session)
    return sessions, sources, scanned_count, in_scope_count, repos


def home_fields(args, sources):
    fields = {
        "claude_home": str(Path(args.claude_home).expanduser()) if "claude" in sources else None,
        "codex_home": str(Path(args.codex_home).expanduser()) if "codex" in sources else None,
        "pi_home": str(Path(args.pi_home).expanduser()) if "pi" in sources else None,
        "grok_home": str(Path(args.grok_home).expanduser()) if "grok" in sources else None,
        "zcode_home": str(Path(args.zcode_home).expanduser()) if "zcode" in sources else None,
        "cursor_home": str(Path(args.cursor_home).expanduser()) if "cursor" in sources else None,
        "grok_bot_home": str(Path(args.grok_bot_home).expanduser()) if "grok_bot" in sources else None,
        "warp_databases": sources.get("warp", {}).get("databases", []),
    }
    return fields


def main():
    args = parse_args()
    if args.all_conversations and args.repo:
        print(
            "error: --all-conversations cannot be combined with --repo",
            file=sys.stderr,
        )
        sys.exit(2)
    out_dir = Path(args.out).expanduser()
    transcripts_dir = out_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    repos = [] if args.all_conversations else resolve_repos(args.repo)
    extra_roots = global_skill_roots_for_run(args) if args.include_global_skills else []
    skills = discover_skills(
        repos,
        Path(args.codex_home).expanduser(),
        args.skills_dir,
        args.include_global_skills,
        pi_home=Path(args.pi_home).expanduser(),
        grok_home=Path(args.grok_home).expanduser(),
        zcode_home=Path(args.zcode_home).expanduser(),
        extra_roots=extra_roots,
    )
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    sessions, sources, scanned_count, in_scope_count, collected_repos = collect_from_plugins(
        args, cutoff, skills.keys()
    )
    if not args.all_conversations:
        repos = collected_repos

    if not sources:
        print(
            "error: no supported session source found "
            "(Claude Code, Codex, Warp, Pi, Grok Build, ZCode, Cursor, or Grok Bot)",
            file=sys.stderr,
        )
        sys.exit(1)
    if args.all_conversations:
        repos = infer_session_repos(sessions)
        extra_roots = global_skill_roots_for_run(args) if args.include_global_skills else []
        skills = discover_skills(
            repos,
            Path(args.codex_home).expanduser(),
            args.skills_dir,
            args.include_global_skills,
            pi_home=Path(args.pi_home).expanduser(),
            grok_home=Path(args.grok_home).expanduser(),
            zcode_home=Path(args.zcode_home).expanduser(),
            extra_roots=extra_roots,
        )
    installed_skill_names = set(skills)
    for session in sessions:
        detected = detect_skills_from_entries(
            session["_entries"],
            installed_skill_names,
        )
        session["skills_used"] = sorted(
            (set(session["skills_used"]) | detected) & installed_skill_names
        )

    sessions.sort(key=lambda session: session["modified_at"], reverse=True)
    for session in sessions:
        session["_key"] = f"{session['harness']}:{session['meta']['id']}"

    sampled_keys = set()
    per_skill_count = {name: 0 for name in skills}
    for s in sessions:
        if len(sampled_keys) >= args.max_sessions:
            break
        for name in s["skills_used"]:
            if per_skill_count.get(name, 0) < args.per_skill:
                per_skill_count[name] = per_skill_count.get(name, 0) + 1
                sampled_keys.add(s["_key"])
                break
    no_skill_taken = 0
    for s in sessions:
        if len(sampled_keys) >= args.max_sessions or no_skill_taken >= args.no_skill:
            break
        if not s["skills_used"] and s["_key"] not in sampled_keys:
            sampled_keys.add(s["_key"])
            no_skill_taken += 1

    for s in sessions:
        sid = s["meta"]["id"]
        s["sampled"] = s["_key"] in sampled_keys
        if s["sampled"]:
            tpath = transcripts_dir / f"{s['harness']}-{sid}.md"
            tpath.write_text(render_transcript(s["meta"], s["stats"], s["skills_used"], s["_entries"]))
            s["transcript_path"] = str(tpath)
        del s["_entries"]
        del s["_key"]

    skill_usage = {name: 0 for name in skills}
    for s in sessions:
        for name in s["skills_used"]:
            skill_usage[name] += 1

    if args.all_conversations:
        conversation_scope = "all"
        scope_name = "all-conversations"
    elif len(repos) == 1:
        conversation_scope = "projects"
        scope_name = repos[0].name
    else:
        conversation_scope = "projects"
        scope_name = "multiple-projects"

    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "harness": next(iter(sources)) if len(sources) == 1 else "mixed",
        "sources": sources,
        **home_fields(args, sources),
        "conversation_scope": conversation_scope,
        "repo": str(repos[0]) if len(repos) == 1 else None,
        "repos": [str(repo) for repo in repos],
        "repo_name": scope_name,
        "repo_names": [repo.name for repo in repos],
        "window_days": args.days,
        "skills": sorted(skills.values(), key=lambda x: x["name"]),
        "skill_usage": skill_usage,
        "stats": {
            "session_files_in_window": scanned_count,
            "session_records_in_window": scanned_count,
            "sessions_in_repo": in_scope_count,
            "sessions_in_scope": in_scope_count,
            "sessions_considered": len(sessions),
            "sessions_sampled": len(sampled_keys),
            "skills_found": len(skills),
            "skills_used": sum(1 for v in skill_usage.values() if v > 0),
        },
        "sessions": sessions,
    }
    (out_dir / "inventory.json").write_text(json.dumps(inventory, indent=2))

    st = inventory["stats"]
    print(
        "scope:             "
        + (
            "all conversations"
            if args.all_conversations
            else ", ".join(str(repo) for repo in repos)
        )
    )
    print(f"sources:           {', '.join(sources)}")
    print(f"skills found:      {st['skills_found']} ({st['skills_used']} used in window)")
    print(f"sessions in window: {st['session_records_in_window']} records, {st['sessions_in_scope']} in scope, {st['sessions_considered']} scoreable")
    print(f"sessions sampled:  {st['sessions_sampled']} -> {transcripts_dir}")
    print(f"inventory:         {out_dir / 'inventory.json'}")


if __name__ == "__main__":
    main()
