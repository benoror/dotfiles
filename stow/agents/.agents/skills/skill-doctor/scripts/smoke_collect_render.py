#!/usr/bin/env python3
"""Fixture or box smoke: collect sessions, then render a local report.

/skill-doctor smoke entrypoint. Never uploads transcripts.

  python3 scripts/smoke_collect_render.py
  python3 scripts/smoke_collect_render.py --out "$REPORT_DIR"
  python3 scripts/smoke_collect_render.py --grok-bot-home PATH --out "$REPORT_DIR"

Without --grok-bot-home, write a synthetic grok_bot session and collect that.
With --grok-bot-home, collect from that transcript root (still no upload).
Scoring is a local smoke scorecard from inventory.json, not a model pass.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from collect_sessions import collect_sessions, parse_args as parse_collect_args
from render_report import render_page


def write_jsonl(path: Path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")


def fixture_records(cwd: str):
    return [
        {
            "role": "user",
            "cwd": cwd,
            "timestamp": "2026-09-20T10:00:00Z",
            "message": {
                "content": [{"type": "text", "text": "Grade my skill usage"}],
            },
        },
        {
            "role": "assistant",
            "timestamp": "2026-09-20T10:00:01Z",
            "message": {
                "content": [
                    {"type": "text", "text": "I will read the skill."},
                    {
                        "type": "tool_use",
                        "name": "read",
                        "input": {
                            "path": f"{cwd}/.agents/skills/update-skill/SKILL.md"
                        },
                    },
                ],
            },
        },
        {
            "role": "tool",
            "timestamp": "2026-09-20T10:00:02Z",
            "message": {
                "content": [{"type": "text", "text": "---\ndescription: update\n"}],
            },
        },
        {
            "role": "assistant",
            "timestamp": "2026-09-20T10:00:03Z",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "write",
                        "input": {"path": f"{cwd}/out.txt", "content": "ok"},
                    }
                ],
            },
        },
        {
            "role": "tool",
            "timestamp": "2026-09-20T10:00:04Z",
            "message": {
                "content": [{"type": "text", "text": "write failed: disk full"}],
            },
        },
    ]


def build_fixture_tree(root: Path):
    transcripts = root / "agent-transcripts"
    repo = root / "repo"
    skill = repo / ".agents" / "skills" / "update-skill" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: update-skill\ndescription: Update a skill\n---\n")
    stem = str(uuid4())
    session = transcripts / stem / f"{stem}.jsonl"
    write_jsonl(session, fixture_records(str(repo)))
    return transcripts, repo


def smoke_report_from_inventory(inventory: dict) -> dict:
    stats = inventory.get("stats") or {}
    sampled = int(stats.get("sessions_sampled") or 0)
    used = sum(
        1
        for session in inventory.get("sessions") or []
        if session.get("sampled") and session.get("skills_used")
    )
    coverage = (used / sampled) if sampled else 0.0
    return {
        "title": "Agent Skill Report",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "harness": inventory.get("harness") or "unknown",
        "handle": inventory.get("repo_name") or "smoke",
        "stats": {
            "sessions_analyzed": sampled,
            "sessions_scanned": stats.get("session_records_in_window", 0),
            "skills_found": stats.get("skills_found", 0),
            "skills_used": stats.get("skills_used", 0),
            "window_days": inventory.get("window_days", 45),
        },
        "scores": {
            "efficiency": 0.5,
            "code_quality": 0.5,
            "procedure_compliance": 0.5,
            "verbosity": 0.5,
            "skill_coverage": coverage,
            "overall": 0.5,
        },
        "top_findings": [
            "Smoke path only: collect and render ran locally.",
            "No transcript was uploaded.",
            "Full scoring still needs a /skill-doctor run.",
        ],
        "suggestions": [],
    }


def write_smoke_artifacts(inventory: dict, out_dir: Path) -> Path:
    report = smoke_report_from_inventory(inventory)
    report_json = out_dir / "report.json"
    report_json.write_text(json.dumps(report, indent=2) + "\n")
    html_path = out_dir / "report.html"
    html_path.write_text(render_page(report))
    return html_path


def parse_smoke_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--grok-bot-home",
        help="real grok_bot transcript root; omit to use synthetic fixtures",
    )
    parser.add_argument(
        "--grok-bot-workflows",
        help="optional grok_bot workflows root used with --include-global-skills",
    )
    parser.add_argument(
        "--out",
        help="report directory (default: a fresh temp directory that is kept)",
    )
    return parser.parse_args(argv)


def run_smoke(args) -> dict:
    if args.out:
        out = Path(args.out).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        work = out.parent
    else:
        work = Path(tempfile.mkdtemp(prefix="skill-doctor-smoke-"))
        out = work / "report"
        out.mkdir(parents=True, exist_ok=True)

    collect_argv = [
        "--harness",
        "grok_bot",
        "--out",
        str(out),
        "--days",
        "45",
    ]
    if args.grok_bot_home:
        collect_argv += [
            "--grok-bot-home",
            args.grok_bot_home,
            "--all-conversations",
            "--include-global-skills",
        ]
        if args.grok_bot_workflows:
            collect_argv += ["--grok-bot-workflows", args.grok_bot_workflows]
    else:
        transcripts, repo = build_fixture_tree(work / "fixtures")
        collect_argv += [
            "--grok-bot-home",
            str(transcripts),
            "--repo",
            str(repo),
        ]

    inventory = collect_sessions(parse_collect_args(collect_argv))
    html_path = write_smoke_artifacts(inventory, out)
    print(f"smoke inventory: {out / 'inventory.json'}")
    print(f"smoke report:    {html_path}")
    print("no transcripts uploaded")
    return {
        "out": out,
        "inventory": inventory,
        "html_path": html_path,
    }


def main(argv=None):
    run_smoke(parse_smoke_args(argv))


if __name__ == "__main__":
    main()
