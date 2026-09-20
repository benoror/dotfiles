#!/usr/bin/env python3
"""Synthetic tests for the grok_bot harness plugin."""

import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from collect_sessions import global_skill_roots_for_run
from harnesses.grok_bot import (
    DEFAULT_HOME,
    DEFAULT_WORKFLOWS,
    GrokBotPlugin,
    find_grok_bot_session_files,
    parse_grok_bot_session,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "grok_bot"
PARENT_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
CHILD_ID = "sand-subagent-11111111-2222-3333-4444-555555555555"


def write_tree(root: Path):
    parent_dir = root / PARENT_ID
    child_dir = root / CHILD_ID
    parent_dir.mkdir(parents=True)
    child_dir.mkdir(parents=True)
    shutil.copy(FIXTURES / "parent.jsonl", parent_dir / f"{PARENT_ID}.jsonl")
    shutil.copy(FIXTURES / "sand-subagent-child.jsonl", child_dir / f"{CHILD_ID}.jsonl")
    return parent_dir / f"{PARENT_ID}.jsonl", child_dir / f"{CHILD_ID}.jsonl"


class GrokBotSessionTests(unittest.TestCase):
    def test_finds_parent_and_excludes_subagents_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            parent, child = write_tree(home)
            cutoff = datetime.now(timezone.utc) - timedelta(days=1)

            parents = find_grok_bot_session_files(home, cutoff, False)
            all_files = find_grok_bot_session_files(home, cutoff, True)

            self.assertEqual([path for _, path in parents], [parent])
            self.assertEqual({path for _, path in all_files}, {parent, child})

    def test_parses_roles_tools_and_skill_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            parent, _ = write_tree(home)
            parsed = parse_grok_bot_session(parent, {"skill-doctor"}, False)
            self.assertIsNotNone(parsed)
            meta, stats, entries, skills = parsed

            self.assertEqual(meta["id"], PARENT_ID)
            self.assertEqual(meta["originator"], "grok_bot")
            self.assertIsNone(meta["thread_source"])
            self.assertEqual(stats["user_turns"], 1)
            self.assertEqual(stats["assistant_turns"], 2)
            self.assertEqual(stats["tool_calls"], 2)
            self.assertTrue(stats["has_code_edits"])
            self.assertEqual(skills, ["skill-doctor"])
            self.assertIn(("user", "Grade the skill-doctor collector"), entries)
            self.assertTrue(any(role == "tool:read_file" for role, _ in entries))

    def test_excludes_subagent_parse_unless_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            _, child = write_tree(home)
            self.assertIsNone(parse_grok_bot_session(child, set(), False))
            parsed = parse_grok_bot_session(child, set(), True)
            self.assertEqual(parsed[0]["thread_source"], "subagent")
            self.assertEqual(parsed[0]["id"], CHILD_ID)

    def test_plugin_collects_and_names_workflow_roots(self):
        plugin = GrokBotPlugin()
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            write_tree(home)

            class Args:
                grok_bot_home = str(home)
                include_subagents = False

            args = Args()
            self.assertTrue(plugin.source_available(args))
            sessions, note = plugin.collect(
                args,
                datetime.now(timezone.utc) - timedelta(days=1),
                {"skill-doctor"},
            )
            self.assertEqual(note["records_in_window"], 1)
            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0]["harness"], "grok_bot")
            self.assertEqual(plugin.global_skill_roots(args), [Path(DEFAULT_WORKFLOWS)])
            self.assertEqual(DEFAULT_HOME, "/home/box/agent-data/agent-transcripts")

    def test_global_roots_do_not_mix_fleet_and_hub(self):
        class Args:
            include_global_skills = True
            harness = "grok_bot"
            pi_home = "~/.pi/agent"
            grok_home = "~/.grok"
            zcode_home = "~/.zcode"
            codex_home = "~/.codex"

        roots = global_skill_roots_for_run(Args())
        self.assertEqual(roots, [Path(DEFAULT_WORKFLOWS)])

        class AutoArgs(Args):
            harness = "auto"

        auto_roots = [str(p) for p in global_skill_roots_for_run(AutoArgs())]
        self.assertTrue(any(p.endswith("/.agents/skills") for p in auto_roots))
        self.assertNotIn(DEFAULT_WORKFLOWS, auto_roots)

    def test_collect_sessions_cli_samples_synthetic_parent(self):
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "transcripts"
            home.mkdir()
            write_tree(home)
            out = Path(tmp) / "report"
            script = Path(__file__).resolve().parent / "collect_sessions.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--harness",
                    "grok_bot",
                    "--grok-bot-home",
                    str(home),
                    "--all-conversations",
                    "--include-global-skills",
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            inventory = json.loads((out / "inventory.json").read_text())
            self.assertEqual(inventory["harness"], "grok_bot")
            self.assertEqual(inventory["stats"]["sessions_considered"], 1)
            self.assertEqual(inventory["sources"]["grok_bot"]["records_in_window"], 1)

    def test_fixture_has_no_real_user_content(self):
        raw = (FIXTURES / "parent.jsonl").read_text()
        for line in raw.splitlines():
            obj = json.loads(line)
            self.assertIn(obj["role"], ("user", "assistant", "tool"))


if __name__ == "__main__":
    unittest.main()
