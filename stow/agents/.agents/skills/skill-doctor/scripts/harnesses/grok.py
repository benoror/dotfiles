"""Grok Build harness (distinct from Grok Bot / grok_bot)."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import List
from urllib.parse import unquote

from common import (
    CODE_EDIT_HINTS,
    GENERIC_EDIT_TOOLS,
    MAX_MSG_CHARS,
    MAX_TOOL_CHARS,
    TranscriptBuffer,
    assistant_tool_calls,
    detect_skill_candidates,
    empty_stats,
    extract_text,
    iter_jsonl_records,
    looks_injected,
    recent_files,
    truncate,
)

from .base import CollectContext, HarnessPlugin, SessionRef


def find_grok_session_files(grok_home: Path, cutoff: datetime):
    root = grok_home / "sessions"
    if not root.is_dir():
        return []
    return recent_files(root.glob("*/*/chat_history.jsonl"), cutoff)


def parse_grok_session(path: Path, skill_names, include_subagents: bool):
    """Normalize one Grok Build chat_history.jsonl to the shared transcript shape.

    Grok stores a session as one flat file; subagent activity appears as
    synthetic_reason injections which are skipped, so include_subagents is
    accepted for signature compatibility and ignored.
    """
    try:
        records = iter_jsonl_records(path)
    except OSError:
        return None

    stats = empty_stats()
    entries = TranscriptBuffer()
    seen_calls = {}
    used_tool_names = set()
    skills_used = set()
    has_code_edit_hint = False

    for obj in records:
        record_type = obj.get("type")
        if record_type in ("system", "reasoning", "backend_tool_call"):
            continue
        if obj.get("synthetic_reason"):
            continue

        if record_type == "user":
            text = extract_text(obj.get("content"))
            if not text or looks_injected(text):
                continue
            stats["user_turns"] += 1
            entries.append(("user", truncate(text, MAX_MSG_CHARS)))
        elif record_type == "assistant":
            text = extract_text(obj.get("content"))
            if text:
                stats["assistant_turns"] += 1
                entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))
            for name, args_text in assistant_tool_calls(obj):
                stats["tool_calls"] += 1
                key = hashlib.sha1((name + args_text).encode()).hexdigest()
                seen_calls[key] = seen_calls.get(key, 0) + 1
                if seen_calls[key] > 1:
                    stats["repeated_tool_calls"] += 1
                used_tool_names.add(name)
                skills_used.update(detect_skill_candidates(args_text))
                has_code_edit_hint = has_code_edit_hint or any(
                    hint in args_text for hint in CODE_EDIT_HINTS
                )
                entries.append((f"tool:{name}", truncate(args_text, MAX_TOOL_CHARS)))
        elif record_type == "tool_result":
            result = extract_text(obj.get("content"))
            if not result:
                continue
            low = result[:2000].lower()
            if "error" in low or "failed" in low or "traceback" in low:
                stats["error_outputs"] += 1
            entries.append(("output", truncate(result, MAX_TOOL_CHARS)))

    meta = {
        "id": path.parent.name,
        "cwd": unquote(path.parent.parent.name),
        "started_at": None,
        "originator": "grok",
        "thread_source": None,
    }
    stats["first_ts"] = None
    stats["last_ts"] = None
    stats["has_code_edits"] = (
        bool(used_tool_names & GENERIC_EDIT_TOOLS)
        or has_code_edit_hint
    )
    return meta, stats, entries.finish(), sorted(skills_used & set(skill_names))


class GrokHarness(HarnessPlugin):
    id = "grok"
    display_name = "Grok Build"

    def detect_runtime(self, environ=None) -> bool:
        env = environ if environ is not None else os.environ
        if env.get("GROK_BOT_HOME") or env.get("GROK_BOT"):
            return False
        return bool(env.get("GROK_HOME") or env.get("GROK_BUILD"))

    def is_available(self, ctx: CollectContext) -> bool:
        home = ctx.homes.get(self.id)
        return bool(home and (home / "sessions").is_dir())

    def missing_source_error(self, ctx: CollectContext) -> str:
        home = ctx.homes.get(self.id, Path("~/.grok").expanduser())
        return f"error: Grok Build session home not found at {home / 'sessions'}"

    def list_sessions(self, ctx: CollectContext) -> List[SessionRef]:
        home = ctx.homes[self.id]
        refs = []
        for mtime, path in find_grok_session_files(home, ctx.cutoff):
            refs.append(SessionRef(
                harness=self.id,
                path=path,
                mtime=mtime,
                file_label=str(path),
            ))
        return refs

    def parse_session(self, ref: SessionRef, skill_names, include_subagents: bool):
        return parse_grok_session(ref.path, skill_names, include_subagents)

    def discover_skills(self, ctx: CollectContext):
        if not ctx.include_global_skills:
            return []
        home = ctx.homes.get(self.id)
        return [home / "skills"] if home is not None else []
