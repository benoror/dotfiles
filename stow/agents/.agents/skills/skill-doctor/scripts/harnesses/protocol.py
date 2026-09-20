"""Harness plugin contract for skill-doctor collection.

A plugin owns one session source. It finds files, parses them into the
shared session dict, and reports its own missing-source error. The
orchestrator samples, writes inventory, and never reads raw transcripts
except through these records.
"""

from __future__ import annotations

from typing import Protocol


class HarnessPlugin(Protocol):
    id: str

    def add_cli_flags(self, parser) -> None:
        """Register --<id>-home and any extra source flags."""

    def is_requested(self, harness: str) -> bool:
        """True when --harness is auto, all, or this plugin id."""

    def source_available(self, args) -> bool:
        """True when the local source directory or database exists."""

    def collect(self, args, cutoff, skill_names):
        """Return (sessions, source_note).

        sessions are dicts with harness, meta, stats, skills_used, file,
        modified_at, and _entries. Do not apply repo or scoreable filters.
        """

    def global_skill_roots(self, args):
        """Extra global skill directories owned by this harness."""

    def missing_error(self, args) -> str:
        """stderr line when --harness is this id and the source is absent."""


class BasePlugin:
    id = ""

    def add_cli_flags(self, parser) -> None:
        return None

    def is_requested(self, harness: str) -> bool:
        return harness in ("auto", "all", self.id)

    def source_available(self, args) -> bool:
        return False

    def collect(self, args, cutoff, skill_names):
        return [], {}

    def global_skill_roots(self, args):
        return []

    def missing_error(self, args) -> str:
        return f"error: {self.id} session source not found"
