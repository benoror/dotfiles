#!/usr/bin/env python3
"""Synthetic Cursor harness tests. No real transcripts."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from collect_sessions import collect_sessions, parse_args
from harnesses.cursor import parse_cursor_session


def write_jsonl(path: Path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n")


class CursorHarnessTests(unittest.TestCase):
    def test_parses_role_message_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent-transcripts" / "session-1.jsonl"
            write_jsonl(path, [
                {
                    "role": "user",
                    "cwd": "/tmp/repo",
                    "message": {"content": [{"type": "text", "text": "Fix the test"}]},
                },
                {
                    "role": "assistant",
                    "message": {
                        "content": [
                            {"type": "text", "text": "Editing."},
                            {
                                "type": "tool_use",
                                "name": "StrReplace",
                                "input": {
                                    "path": "/tmp/repo/.agents/skills/tdd/SKILL.md",
                                    "old_string": "a",
                                    "new_string": "b",
                                },
                            },
                        ]
                    },
                },
            ])

            meta, stats, entries, skills = parse_cursor_session(path, {"tdd"}, False)
            self.assertEqual(meta["originator"], "cursor")
            self.assertEqual(stats["user_turns"], 1)
            self.assertEqual(stats["tool_calls"], 1)
            self.assertTrue(stats["has_code_edits"])
            self.assertEqual(skills, ["tdd"])
            self.assertIn(("user", "Fix the test"), entries)

    def test_collect_from_explicit_transcripts_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            skill = repo / ".cursor" / "skills" / "tdd" / "SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("---\ndescription: TDD\n---\n")
            transcripts = root / "cursor-transcripts"
            path = transcripts / "session-2.jsonl"
            write_jsonl(path, [
                {
                    "role": "user",
                    "cwd": str(repo),
                    "message": {"content": [{"type": "text", "text": "Run tdd"}]},
                },
                {
                    "role": "assistant",
                    "message": {
                        "content": [
                            {"type": "text", "text": "Reading skill."},
                            {
                                "type": "tool_use",
                                "name": "read",
                                "input": {"path": str(skill)},
                            },
                        ]
                    },
                },
            ])
            out = root / "report"
            args = parse_args([
                "--harness", "cursor",
                "--cursor-home", str(root / "missing-cursor-home"),
                "--cursor-transcripts-dir", str(transcripts),
                "--repo", str(repo),
                "--days", "7",
                "--out", str(out),
            ])
            inventory = collect_sessions(args)
            self.assertEqual(inventory["harness"], "cursor")
            self.assertEqual(inventory["stats"]["sessions_considered"], 1)
            self.assertEqual(inventory["sessions"][0]["skills_used"], ["tdd"])


if __name__ == "__main__":
    unittest.main()
