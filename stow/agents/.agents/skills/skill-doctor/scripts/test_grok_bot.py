#!/usr/bin/env python3
"""Synthetic grok_bot parse + collect tests. No real transcripts."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from collect_sessions import collect_sessions, parse_args
from harnesses.grok_bot import (
    find_grok_bot_session_files,
    is_canonical_grok_bot_file,
    parse_grok_bot_session,
    workflows_dir_for,
)


def write_jsonl(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")


def grok_bot_records(cwd="/tmp/repo"):
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
                            "path": "/tmp/repo/.agents/skills/update-skill/SKILL.md"
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
                        "input": {"path": "/tmp/repo/out.txt", "content": "ok"},
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


def session_path(home: Path, name=None) -> Path:
    stem = name or str(uuid4())
    return home / stem / f"{stem}.jsonl"


class GrokBotParseTests(unittest.TestCase):
    def test_parses_role_message_tools_and_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = session_path(Path(tmp), "11111111-1111-1111-1111-111111111111")
            write_jsonl(path, grok_bot_records())

            meta, stats, entries, skills = parse_grok_bot_session(
                path, {"update-skill"}, False
            )

            self.assertEqual(meta["id"], "11111111-1111-1111-1111-111111111111")
            self.assertEqual(meta["cwd"], "/tmp/repo")
            self.assertEqual(meta["originator"], "grok_bot")
            self.assertIsNone(meta["thread_source"])
            self.assertEqual(stats["user_turns"], 1)
            self.assertEqual(stats["assistant_turns"], 2)
            self.assertEqual(stats["tool_calls"], 2)
            self.assertEqual(stats["error_outputs"], 1)
            self.assertTrue(stats["has_code_edits"])
            self.assertEqual(skills, ["update-skill"])
            self.assertIn(("user", "Grade my skill usage"), entries)
            self.assertIn(("assistant", "I will read the skill."), entries)
            self.assertTrue(any(role == "tool:read" for role, _ in entries))
            self.assertTrue(any(role == "output" for role, _ in entries))

    def test_skips_sand_subagent_unless_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = session_path(Path(tmp), "sand-subagent-abc")
            write_jsonl(path, grok_bot_records())

            self.assertIsNone(parse_grok_bot_session(path, {"update-skill"}, False))
            parsed = parse_grok_bot_session(path, {"update-skill"}, True)
            self.assertEqual(parsed[0]["thread_source"], "subagent")
            self.assertEqual(parsed[0]["id"], "sand-subagent-abc")


class GrokBotCollectTests(unittest.TestCase):
    def test_lists_canonical_files_and_skips_subagents(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            parent = session_path(home, "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
            child = session_path(home, "sand-subagent-bbbb")
            mismatch = home / "cccccccc-cccc-cccc-cccc-cccccccccccc" / "other.jsonl"
            old = session_path(home, "dddddddd-dddd-dddd-dddd-dddddddddddd")
            write_jsonl(parent, grok_bot_records())
            write_jsonl(child, grok_bot_records())
            write_jsonl(mismatch, grok_bot_records())
            write_jsonl(old, grok_bot_records())
            old_time = (datetime.now(timezone.utc) - timedelta(days=10)).timestamp()
            os.utime(old, (old_time, old_time))
            cutoff = datetime.now(timezone.utc) - timedelta(days=1)

            self.assertTrue(is_canonical_grok_bot_file(parent))
            self.assertFalse(is_canonical_grok_bot_file(mismatch))

            parents = find_grok_bot_session_files(home, cutoff, False)
            with_subs = find_grok_bot_session_files(home, cutoff, True)

            self.assertEqual([path for _, path in parents], [parent])
            self.assertEqual({path for _, path in with_subs}, {parent, child})

    def test_collect_writes_inventory_from_synthetic_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcripts = root / "agent-transcripts"
            workflows = root / "workflows"
            repo = root / "repo"
            skill = repo / ".agents" / "skills" / "update-skill" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\ndescription: Update a skill\n---\n")
            workflow_skill = workflows / "fleet-pack" / "SKILL.md"
            workflow_skill.parent.mkdir(parents=True)
            workflow_skill.write_text("---\ndescription: Fleet pack\n---\n")

            session = session_path(transcripts, "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
            write_jsonl(session, grok_bot_records(cwd=str(repo)))
            out = root / "report"

            args = parse_args([
                "--harness", "grok_bot",
                "--grok-bot-home", str(transcripts),
                "--grok-bot-workflows", str(workflows),
                "--repo", str(repo),
                "--include-global-skills",
                "--days", "7",
                "--out", str(out),
            ])
            inventory = collect_sessions(args)

            self.assertEqual(inventory["harness"], "grok_bot")
            self.assertEqual(inventory["stats"]["sessions_considered"], 1)
            self.assertEqual(inventory["stats"]["sessions_sampled"], 1)
            self.assertIn("update-skill", {s["name"] for s in inventory["skills"]})
            self.assertIn("fleet-pack", {s["name"] for s in inventory["skills"]})
            self.assertEqual(inventory["sessions"][0]["skills_used"], ["update-skill"])
            transcript = Path(inventory["sessions"][0]["transcript_path"])
            self.assertTrue(transcript.is_file())
            self.assertIn("Grade my skill usage", transcript.read_text())
            self.assertTrue((out / "inventory.json").is_file())

    def test_workflows_dir_follows_transcript_sibling(self):
        home = Path("/home/box/agent-data/agent-transcripts")
        self.assertEqual(
            workflows_dir_for(home),
            Path("/home/box/agent-data/workflows"),
        )
        explicit = Path("/tmp/custom-workflows")
        self.assertEqual(workflows_dir_for(home, explicit), explicit)


if __name__ == "__main__":
    unittest.main()
