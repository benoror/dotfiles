#!/usr/bin/env python3
"""Synthetic tests for the Cursor harness plugin."""

import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from harnesses.cursor import (
    CursorPlugin,
    find_cursor_session_files,
    parse_cursor_session,
    probe_cursor_format,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "cursor"


def write_cursor_tree(root: Path, filename="session.jsonl", fixture="minimal.jsonl"):
    encoded = "Users-ben-app"
    dest = root / "projects" / encoded / "agent-transcripts" / filename
    dest.parent.mkdir(parents=True)
    shutil.copy(FIXTURES / fixture, dest)
    return dest


class CursorSessionTests(unittest.TestCase):
    def test_probes_known_and_unknown_shapes(self):
        self.assertEqual(probe_cursor_format(FIXTURES / "minimal.jsonl"), "ok")
        self.assertEqual(probe_cursor_format(FIXTURES / "unknown.jsonl"), "format_unknown")

    def test_finds_flat_and_nested_transcripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            flat = write_cursor_tree(home, "flat.jsonl")
            nested = (
                home / "projects" / "Users-ben-app" / "agent-transcripts"
                / "nested-id" / "nested-id.jsonl"
            )
            nested.parent.mkdir()
            shutil.copy(FIXTURES / "minimal.jsonl", nested)
            cutoff = datetime.now(timezone.utc) - timedelta(days=1)

            files = find_cursor_session_files(home, cutoff, False)
            found = {path for _, path in files}
            self.assertIn(flat, found)
            self.assertIn(nested, found)

    def test_parses_fixture_and_decodes_encoded_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            path = write_cursor_tree(home)
            parsed = parse_cursor_session(path, {"update-skill"}, False)
            self.assertIsNotNone(parsed)
            meta, stats, entries, skills = parsed

            self.assertEqual(meta["originator"], "cursor")
            self.assertEqual(meta["cwd"], "/Users/ben/app")
            self.assertEqual(stats["user_turns"], 1)
            self.assertEqual(stats["assistant_turns"], 2)
            self.assertEqual(stats["tool_calls"], 2)
            self.assertTrue(stats["has_code_edits"])
            self.assertEqual(skills, ["update-skill"])
            self.assertIn(("user", "Inspect the Cursor adapter"), entries)

    def test_unknown_format_yields_no_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            path = write_cursor_tree(home, fixture="unknown.jsonl")
            self.assertIsNone(parse_cursor_session(path, set(), False))

            class Args:
                cursor_home = str(home)
                include_subagents = False

            plugin = CursorPlugin()
            sessions, note = plugin.collect(
                Args(),
                datetime.now(timezone.utc) - timedelta(days=1),
                set(),
            )
            self.assertEqual(sessions, [])
            self.assertEqual(note["status"], "format_unknown")

    def test_excludes_subagent_paths_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            path = write_cursor_tree(home, filename="sand-subagent-1.jsonl")
            cutoff = datetime.now(timezone.utc) - timedelta(days=1)
            self.assertEqual(find_cursor_session_files(home, cutoff, False), [])
            self.assertEqual(len(find_cursor_session_files(home, cutoff, True)), 1)
            self.assertIsNone(parse_cursor_session(path, set(), False))

    def test_plugin_reports_empty_global_skill_roots(self):
        plugin = CursorPlugin()
        self.assertEqual(plugin.global_skill_roots(None), [])


if __name__ == "__main__":
    unittest.main()
