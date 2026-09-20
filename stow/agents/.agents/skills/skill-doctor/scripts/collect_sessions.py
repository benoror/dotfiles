#!/usr/bin/env python3
"""Collect local agent sessions and skills for scoring.

Harness plugins implement detect_runtime / list_sessions / parse_session /
discover_skills. This module orchestrates them and emits:

  <out>/inventory.json        - skills, per-session stats, sampling decisions
  <out>/transcripts/<id>.md   - condensed transcripts for sampled sessions

Everything runs locally; nothing is uploaded. Python 3.9+, stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common import (  # noqa: E402
    detect_skills_from_entries,
    hub_skill_roots,
    infer_session_repos,
    project_skill_roots,
    render_transcript,
    resolve_repo,
    resolve_repos,
    scan_skill_roots,
    session_matches_repos,
)
from harnesses import HARNESS_IDS, CollectContext, detect_runtime, select_plugins  # noqa: E402
from harnesses.claude import find_claude_session_files, parse_claude_session  # noqa: E402
from harnesses.codex import find_codex_session_files, parse_codex_session  # noqa: E402
from harnesses.cursor import find_cursor_session_files, parse_cursor_session  # noqa: E402
from harnesses.grok import find_grok_session_files, parse_grok_session  # noqa: E402
from harnesses.grok_bot import (  # noqa: E402
    DEFAULT_GROK_BOT_HOME,
    DEFAULT_GROK_BOT_WORKFLOWS,
    find_grok_bot_session_files,
    parse_grok_bot_session,
    workflows_dir_for,
)
from harnesses.pi import find_pi_session_files, parse_pi_session  # noqa: E402
from harnesses.warp import (  # noqa: E402
    discover_warp_databases,
    find_warp_conversations,
    parse_warp_conversation,
)
from harnesses.zcode import find_zcode_session_files, parse_zcode_session  # noqa: E402

__all__ = [
    "detect_runtime",
    "detect_skills_from_entries",
    "discover_skills",
    "discover_warp_databases",
    "find_claude_session_files",
    "find_codex_session_files",
    "find_cursor_session_files",
    "find_grok_bot_session_files",
    "find_grok_session_files",
    "find_pi_session_files",
    "find_warp_conversations",
    "find_zcode_session_files",
    "parse_claude_session",
    "parse_codex_session",
    "parse_cursor_session",
    "parse_grok_bot_session",
    "parse_grok_session",
    "parse_pi_session",
    "parse_warp_conversation",
    "parse_zcode_session",
    "session_matches_repos",
]


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--harness",
        choices=("auto", "all") + HARNESS_IDS,
        default="auto",
        help="session source (default: auto; scans every locally available source)",
    )
    p.add_argument(
        "--detect-runtime",
        action="store_true",
        help="print the executing harness collector ID and exit",
    )
    p.add_argument(
        "--claude-home",
        default=os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"),
        help="Claude Code config directory (default: CLAUDE_CONFIG_DIR or ~/.claude)",
    )
    p.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"))
    p.add_argument(
        "--pi-home",
        default="~/.pi/agent",
        help="Pi agent home (default: ~/.pi/agent)",
    )
    p.add_argument(
        "--grok-home",
        default="~/.grok",
        help="Grok Build home (default: ~/.grok)",
    )
    p.add_argument(
        "--zcode-home",
        default="~/.zcode",
        help="ZCode home (default: ~/.zcode)",
    )
    p.add_argument(
        "--cursor-home",
        default=os.environ.get("CURSOR_HOME", "~/.cursor"),
        help="Cursor config directory (default: CURSOR_HOME or ~/.cursor)",
    )
    p.add_argument(
        "--cursor-transcripts-dir",
        default=os.environ.get("CURSOR_TRANSCRIPTS_DIR"),
        help="explicit Cursor transcript directory (repeatable discovery root)",
    )
    p.add_argument(
        "--grok-bot-home",
        default=os.environ.get("GROK_BOT_HOME", str(DEFAULT_GROK_BOT_HOME)),
        help="Grok Bot transcript root (default: /home/box/agent-data/agent-transcripts)",
    )
    p.add_argument(
        "--grok-bot-workflows",
        default=os.environ.get("GROK_BOT_WORKFLOWS", str(DEFAULT_GROK_BOT_WORKFLOWS)),
        help="Grok Stow workflows root used with --include-global-skills",
    )
    p.add_argument(
        "--warp-db",
        action="append",
        default=[],
        help="explicit Warp warp.sqlite path (repeatable)",
    )
    p.add_argument(
        "--warp-data-dir",
        default=os.environ.get("WARP_DATA_DIR"),
        help="directory containing Warp channel data directories",
    )
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
        help=(
            "also discover skills outside the repo (coding hub ~/.agents/skills, "
            "harness homes, and Grok Stow workflows for grok_bot)"
        ),
    )
    p.add_argument("--days", type=int, default=45, help="only consider sessions modified in the last N days")
    p.add_argument("--max-sessions", type=int, default=12, help="max sessions to sample for scoring")
    p.add_argument("--per-skill", type=int, default=3, help="max sampled sessions per skill")
    p.add_argument("--no-skill", type=int, default=4, help="max sampled sessions that used no skill")
    p.add_argument("--skills-dir", action="append", default=[], help="extra skills directory to scan (repeatable)")
    p.add_argument("--include-subagents", action="store_true", help="include subagent/child sessions")
    p.add_argument("--out", default="./skill-doctor-report")
    return p.parse_args(argv)


def discover_skills(repos, codex_home: Path, extra_dirs, include_global: bool,
                    pi_home: Path = None, grok_home: Path = None, zcode_home: Path = None,
                    extra_roots=None):
    """Discover installed skills. Signature stays compatible with upstream tests."""
    if isinstance(repos, Path):
        repos = [repos]
    roots = list(project_skill_roots(repos))
    if include_global:
        roots += hub_skill_roots()
        roots.append(Path.home() / ".claude" / "skills")
        if codex_home is not None:
            roots.append(Path(codex_home) / "skills")
        for home in (pi_home, grok_home, zcode_home):
            if home is not None:
                roots.append(Path(home) / "skills")
    if extra_roots:
        roots.extend(Path(r).expanduser() for r in extra_roots)
    roots += [Path(d).expanduser() for d in extra_dirs]
    return scan_skill_roots(roots)


def _homes_from_args(args):
    return {
        "claude": Path(args.claude_home).expanduser(),
        "codex": Path(args.codex_home).expanduser(),
        "pi": Path(args.pi_home).expanduser(),
        "grok": Path(args.grok_home).expanduser(),
        "zcode": Path(args.zcode_home).expanduser(),
        "cursor": Path(args.cursor_home).expanduser(),
        "grok_bot": Path(args.grok_bot_home).expanduser(),
    }


def _plugin_skill_roots(plugins, ctx):
    roots = []
    for plugin in plugins:
        roots.extend(plugin.discover_skills(ctx))
    return roots


def collect_sessions(args):
    """Run collection and write inventory + sampled transcripts. Returns inventory."""
    if args.all_conversations and args.repo:
        print(
            "error: --all-conversations cannot be combined with --repo",
            file=sys.stderr,
        )
        sys.exit(2)

    homes = _homes_from_args(args)
    out_dir = Path(args.out).expanduser()
    transcripts_dir = out_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    repos = [] if args.all_conversations else resolve_repos(args.repo)
    plugins = select_plugins(args.harness)
    ctx = CollectContext(
        cutoff=datetime.now(timezone.utc) - timedelta(days=args.days),
        include_subagents=args.include_subagents,
        include_global_skills=args.include_global_skills,
        all_conversations=args.all_conversations,
        repos=repos,
        extra_skill_dirs=args.skills_dir,
        homes=homes,
        extra={
            "warp_db": args.warp_db,
            "warp_data_dir": args.warp_data_dir,
            "cursor_transcripts_dir": args.cursor_transcripts_dir,
            "grok_bot_workflows": Path(args.grok_bot_workflows).expanduser(),
        },
    )

    extra_roots = _plugin_skill_roots(plugins, ctx)
    skills = discover_skills(
        repos,
        homes["codex"],
        args.skills_dir,
        args.include_global_skills,
        pi_home=homes["pi"],
        grok_home=homes["grok"],
        zcode_home=homes["zcode"],
        extra_roots=extra_roots,
    )

    sessions = []
    in_scope_count = 0
    scanned_count = 0
    sources = {}
    warp_databases = []

    for plugin in plugins:
        available = plugin.is_available(ctx)
        if not available:
            if args.harness == plugin.id:
                print(plugin.missing_source_error(ctx), file=sys.stderr)
                sys.exit(1)
            continue

        refs = plugin.list_sessions(ctx)
        info = plugin.source_info(ctx, refs)
        sources[plugin.id] = info
        scanned_count += int(info.get("records_in_window") or len(refs))
        if plugin.id == "warp":
            warp_databases = [Path(p) for p in info.get("databases") or []]

        for ref in refs:
            parsed = plugin.parse_session(ref, skills.keys(), args.include_subagents)
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            cwd = meta.get("cwd")
            if not args.all_conversations:
                if cwd:
                    if not session_matches_repos(cwd, repos):
                        continue
                elif not plugin.cwd_optional:
                    continue
            in_scope_count += 1
            if stats["assistant_turns"] < 1 or stats["tool_calls"] < 1:
                continue
            sessions.append({
                "harness": plugin.id,
                "meta": meta,
                "stats": stats,
                "skills_used": skills_used,
                "file": ref.file_label,
                "modified_at": ref.mtime.isoformat(),
                "_entries": entries,
            })

    if not sources:
        print(
            "error: no supported session source found "
            "(Claude Code, Codex, Warp, Pi, Grok Build, ZCode, Cursor, or Grok Bot)",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.all_conversations:
        repos = infer_session_repos(sessions)
        extra_roots = _plugin_skill_roots(plugins, ctx)
        skills = discover_skills(
            repos,
            homes["codex"],
            args.skills_dir,
            args.include_global_skills,
            pi_home=homes["pi"],
            grok_home=homes["grok"],
            zcode_home=homes["zcode"],
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
        "claude_home": str(homes["claude"]) if "claude" in sources else None,
        "codex_home": str(homes["codex"]) if "codex" in sources else None,
        "pi_home": str(homes["pi"]) if "pi" in sources else None,
        "grok_home": str(homes["grok"]) if "grok" in sources else None,
        "zcode_home": str(homes["zcode"]) if "zcode" in sources else None,
        "cursor_home": str(homes["cursor"]) if "cursor" in sources else None,
        "grok_bot_home": str(homes["grok_bot"]) if "grok_bot" in sources else None,
        "warp_databases": [str(path) for path in warp_databases],
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
    print(
        f"sessions in window: {st['session_records_in_window']} records, "
        f"{st['sessions_in_scope']} in scope, {st['sessions_considered']} scoreable"
    )
    print(f"sessions sampled:  {st['sessions_sampled']} -> {transcripts_dir}")
    print(f"inventory:         {out_dir / 'inventory.json'}")
    return inventory


def main(argv=None):
    args = parse_args(argv)
    if args.detect_runtime:
        identified = detect_runtime()
        if identified:
            print(identified)
            return
        print("unknown", file=sys.stderr)
        sys.exit(2)
    collect_sessions(args)


if __name__ == "__main__":
    main()
