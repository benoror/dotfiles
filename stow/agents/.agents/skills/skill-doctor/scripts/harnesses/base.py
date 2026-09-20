#!/usr/bin/env python3
"""Harness plugin API for skill-doctor.

Each collector implements:

- detect_runtime: is this harness the one executing now?
- list_sessions: find session files/records in the lookback window
- parse_session: normalize one session to the shared transcript shape
- discover_skills: extra skill roots for this harness

Keep inventory.json / transcript.md compatible with upstream scorers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ParsedSession = Tuple[dict, dict, list, list]


@dataclass
class CollectContext:
    cutoff: datetime
    include_subagents: bool
    include_global_skills: bool
    all_conversations: bool
    repos: Sequence[Path]
    extra_skill_dirs: Sequence[str]
    homes: Dict[str, Path] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionRef:
    harness: str
    mtime: datetime
    file_label: str
    path: Optional[Path] = None
    extra: Dict[str, Any] = field(default_factory=dict)


class HarnessPlugin:
    """One local conversation source."""

    id = ""
    display_name = ""
    # When True, sessions with no cwd still count for project-scoped runs.
    cwd_optional = False

    def detect_runtime(self, environ: Optional[dict] = None) -> bool:
        raise NotImplementedError

    def is_available(self, ctx: CollectContext) -> bool:
        raise NotImplementedError

    def missing_source_error(self, ctx: CollectContext) -> str:
        return f"error: {self.display_name} session source not found"

    def list_sessions(self, ctx: CollectContext) -> List[SessionRef]:
        raise NotImplementedError

    def parse_session(
        self,
        ref: SessionRef,
        skill_names,
        include_subagents: bool,
    ) -> Optional[ParsedSession]:
        raise NotImplementedError

    def discover_skills(self, ctx: CollectContext) -> List[Path]:
        """Extra skill directories (beyond project trees and the coding hub)."""
        return []

    def source_info(self, ctx: CollectContext, refs: Sequence[SessionRef]) -> dict:
        home = ctx.homes.get(self.id)
        info = {"records_in_window": len(refs)}
        if home is not None:
            info["home"] = str(home)
        return info
