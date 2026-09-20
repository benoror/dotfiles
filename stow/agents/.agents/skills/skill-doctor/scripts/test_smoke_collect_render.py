#!/usr/bin/env python3
"""Smoke collect+render without uploading transcripts."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from smoke_collect_render import (
    build_fixture_tree,
    parse_smoke_args,
    run_smoke,
    write_jsonl,
    fixture_records,
)


class SmokeCollectRenderTests(unittest.TestCase):
    def test_skill_documents_slash_trigger_and_entrypoints(self):
        skill_root = Path(__file__).resolve().parent.parent
        skill_text = (skill_root / "SKILL.md").read_text()
        self.assertIn("Use when the user asks for /skill-doctor", skill_text)
        self.assertIn("## First run (`/skill-doctor`)", skill_text)
        self.assertIn("scripts/collect_sessions.py", skill_text)
        self.assertIn("scripts/render_report.py", skill_text)
        self.assertIn("scripts/smoke_collect_render.py", skill_text)
        self.assertIn("--harness grok_bot", skill_text)
        self.assertIn("--grok-bot-home", skill_text)
        self.assertNotIn("Warp Factories", skill_text)

    def test_fixture_smoke_collects_and_renders_locally(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report"
            result = run_smoke(parse_smoke_args(["--out", str(out)]))
            inventory = result["inventory"]
            html = result["html_path"].read_text()

            self.assertEqual(inventory["harness"], "grok_bot")
            self.assertGreaterEqual(inventory["stats"]["sessions_sampled"], 1)
            self.assertTrue((out / "inventory.json").is_file())
            self.assertTrue((out / "report.json").is_file())
            self.assertTrue((out / "report.html").is_file())
            transcript = Path(inventory["sessions"][0]["transcript_path"])
            self.assertTrue(transcript.is_file())
            self.assertIn("Grade my skill usage", transcript.read_text())
            self.assertIn("Based on Warp&#x27;s skill-doctor", html)
            self.assertIn("forked from warpdotdev/common-skills", html)
            self.assertNotIn("Warp Factories", html)
            self.assertNotIn("request-access", html)
            report = json.loads((out / "report.json").read_text())
            self.assertIn("No transcript was uploaded.", report["top_findings"])

    def test_explicit_home_smoke_uses_provided_transcripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            transcripts, repo = build_fixture_tree(root / "box")
            extra = transcripts / "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
            extra_file = extra / "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa.jsonl"
            write_jsonl(extra_file, fixture_records(str(repo)))
            out = root / "report"

            result = run_smoke(
                parse_smoke_args(
                    [
                        "--grok-bot-home",
                        str(transcripts),
                        "--out",
                        str(out),
                    ]
                )
            )
            inventory = result["inventory"]
            report = json.loads((out / "report.json").read_text())
            self.assertEqual(inventory["harness"], "grok_bot")
            self.assertGreaterEqual(inventory["stats"]["sessions_sampled"], 1)
            self.assertTrue((out / "report.html").is_file())
            self.assertIn("No transcript was uploaded.", report["top_findings"])
            self.assertNotIn("Warp Factories", result["html_path"].read_text())


if __name__ == "__main__":
    unittest.main()
