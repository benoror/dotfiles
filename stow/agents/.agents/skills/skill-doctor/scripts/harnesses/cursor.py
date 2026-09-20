"""Cursor harness (best-effort).

Cursor does not publish a stable on-disk conversation schema. This plugin
scans documented locations and parses Claude-like or role/message JSONL.
Real Desktop/Cloud paths are often missing on CI VMs; use `--cursor-home`
or `--cursor-transcripts-dir` and synthetic fixtures in tests.

Documented discovery (first existing match wins per file; all are scanned):

1. `$CURSOR_HOME/projects/*/agent-transcripts/**/*.jsonl` (default `~/.cursor`)
2. `$CURSOR_TRANSCRIPTS_DIR/**/*.jsonl` when set
3. `/tmp/cursor/cloud-agent-transcripts/**/transcript.json` (cloud-agent dumps)
4. macOS `~/Library/Application Support/Cursor` stores composer data in
   sqlite (`state.vscdb`). This harness does not decode those databases.

`--cursor-home` overrides the Cursor config root.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

from common import recent_files

from .base import CollectContext, HarnessPlugin, SessionRef
from .claude import parse_claude_session
from .role_message import parse_role_message_session

DEFAULT_CLOUD_DUMP = Path("/tmp/cursor/cloud-agent-transcripts")


def default_cursor_home() -> Path:
    return Path(os.environ.get("CURSOR_HOME", Path.home() / ".cursor")).expanduser()


def cursor_transcript_roots(home: Path, extra_dir=None) -> List[Path]:
    roots = []
    if extra_dir:
        roots.append(Path(extra_dir).expanduser())
    env_dir = os.environ.get("CURSOR_TRANSCRIPTS_DIR")
    if env_dir:
        roots.append(Path(env_dir).expanduser())
    roots.append(home / "projects")
    roots.append(DEFAULT_CLOUD_DUMP)
    return roots


def _iter_candidate_files(root: Path, allow_loose_jsonl=False):
    if not root.exists():
        return
    if root.is_file():
        yield root
        return
    yield from root.glob("*/agent-transcripts/*.jsonl")
    yield from root.glob("*/agent-transcripts/*/*.jsonl")
    yield from root.glob("**/agent-transcripts/*.jsonl")
    # Cloud-agent dumps from cursor-cloud batch-fetch-details.
    yield from root.glob("**/transcript.json")
    if allow_loose_jsonl or root.name in {"agent-transcripts", "cloud-agent-transcripts"}:
        yield from root.glob("**/*.jsonl")


def find_cursor_session_files(home: Path, cutoff: datetime, extra_dir=None):
    seen = set()
    candidates = []
    for root in cursor_transcript_roots(home, extra_dir):
        loose = extra_dir is not None and Path(extra_dir).expanduser() == root
        for path in _iter_candidate_files(root, allow_loose_jsonl=loose):
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in seen:
                continue
            if path.suffix not in {".jsonl", ".json"}:
                continue
            seen.add(resolved)
            candidates.append(path)
    return recent_files(candidates, cutoff)


def _looks_like_claude(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    return False
                if not isinstance(obj, dict):
                    return False
                return obj.get("type") in ("user", "assistant") and "message" in obj
    except OSError:
        return False
    return False


def parse_cursor_session(path: Path, skill_names, include_subagents: bool):
    if path.suffix == ".json" or not _looks_like_claude(path):
        parsed = parse_role_message_session(path, skill_names, "cursor")
        if parsed is not None:
            return parsed
    parsed = parse_claude_session(path, skill_names, include_subagents)
    if parsed is not None:
        meta, stats, entries, skills = parsed
        meta["originator"] = "cursor"
        return meta, stats, entries, skills
    return parse_role_message_session(path, skill_names, "cursor")


class CursorHarness(HarnessPlugin):
    id = "cursor"
    display_name = "Cursor"
    cwd_optional = True

    def detect_runtime(self, environ=None) -> bool:
        env = environ if environ is not None else os.environ
        if env.get("CURSOR_AGENT") or env.get("CURSOR_TRACE_ID"):
            return True
        if env.get("CURSOR_HOME") or env.get("CURSOR"):
            return True
        return False

    def is_available(self, ctx: CollectContext) -> bool:
        home = ctx.homes.get(self.id) or default_cursor_home()
        extra = ctx.extra.get("cursor_transcripts_dir")
        for root in cursor_transcript_roots(home, extra):
            if root.exists():
                return True
        return False

    def missing_source_error(self, ctx: CollectContext) -> str:
        home = ctx.homes.get(self.id, default_cursor_home())
        extra = ctx.extra.get("cursor_transcripts_dir")
        hint = f"{home / 'projects'}/*/agent-transcripts"
        if extra:
            hint = f"{extra} or {hint}"
        return (
            "error: no Cursor transcripts found. "
            f"Looked under {hint} and {DEFAULT_CLOUD_DUMP}. "
            "Pass --cursor-home or --cursor-transcripts-dir."
        )

    def list_sessions(self, ctx: CollectContext) -> List[SessionRef]:
        home = ctx.homes.get(self.id) or default_cursor_home()
        extra = ctx.extra.get("cursor_transcripts_dir")
        refs = []
        for mtime, path in find_cursor_session_files(home, ctx.cutoff, extra):
            refs.append(SessionRef(
                harness=self.id,
                path=path,
                mtime=mtime,
                file_label=str(path),
            ))
        return refs

    def parse_session(self, ref: SessionRef, skill_names, include_subagents: bool):
        return parse_cursor_session(ref.path, skill_names, include_subagents)

    def discover_skills(self, ctx: CollectContext):
        if not ctx.include_global_skills:
            return []
        home = ctx.homes.get(self.id) or default_cursor_home()
        return [
            home / "skills",
            home / "skills-cursor",
        ]

    def source_info(self, ctx: CollectContext, refs):
        home = ctx.homes.get(self.id) or default_cursor_home()
        info = super().source_info(ctx, refs)
        info["discovery"] = [str(p) for p in cursor_transcript_roots(
            home, ctx.extra.get("cursor_transcripts_dir")
        )]
        return info
