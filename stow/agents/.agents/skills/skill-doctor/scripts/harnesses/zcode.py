"""ZCode harness."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import List

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


def find_zcode_session_files(zcode_home: Path, cutoff: datetime):
    root = zcode_home / "cli" / "rollout"
    if not root.is_dir():
        return []
    return recent_files(root.glob("model-io-*.jsonl"), cutoff)


def parse_zcode_session(path: Path, skill_names, include_subagents: bool):
    """Normalize one ZCode model-io rollout to the shared transcript shape.

    Model-io logs are request dumps: only the last request's message list is
    reconstructed, so stats describe the final context window rather than the
    full session.
    """
    try:
        records = iter_jsonl_records(path)
    except OSError:
        return None

    messages = None
    for obj in records:
        if not isinstance(obj, dict):
            continue
        body = (obj.get("request") or {}).get("body") or {}
        candidate = body.get("messages")
        if isinstance(candidate, list) and candidate:
            messages = candidate
    if not messages:
        return None

    stats = empty_stats()
    entries = TranscriptBuffer()
    seen_calls = {}
    used_tool_names = set()
    skills_used = set()
    has_code_edit_hint = False

    for message in messages:
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        if role == "user":
            text = extract_text(message.get("content"))
            if not text or looks_injected(text):
                continue
            stats["user_turns"] += 1
            entries.append(("user", truncate(text, MAX_MSG_CHARS)))
        elif role == "assistant":
            text = extract_text(message.get("content"))
            if text:
                stats["assistant_turns"] += 1
                entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))
            for name, args_text in assistant_tool_calls(message):
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
        elif role == "tool":
            result = extract_text(message.get("content"))
            if not result:
                continue
            low = result[:2000].lower()
            if "error" in low or "failed" in low or "traceback" in low:
                stats["error_outputs"] += 1
            entries.append(("output", truncate(result, MAX_TOOL_CHARS)))

    entries = entries.finish()
    if not entries:
        return None

    meta = {
        "id": path.stem.removeprefix("model-io-"),
        "cwd": None,
        "started_at": None,
        "originator": "zcode",
        "thread_source": None,
    }
    stats["first_ts"] = None
    stats["last_ts"] = None
    stats["has_code_edits"] = (
        bool(used_tool_names & GENERIC_EDIT_TOOLS)
        or has_code_edit_hint
    )
    return meta, stats, entries, sorted(skills_used & set(skill_names))


class ZcodeHarness(HarnessPlugin):
    id = "zcode"
    display_name = "ZCode"
    cwd_optional = True

    def detect_runtime(self, environ=None) -> bool:
        env = environ if environ is not None else os.environ
        return bool(env.get("ZCODE_HOME") or env.get("ZCODE"))

    def is_available(self, ctx: CollectContext) -> bool:
        home = ctx.homes.get(self.id)
        return bool(home and (home / "cli" / "rollout").is_dir())

    def missing_source_error(self, ctx: CollectContext) -> str:
        home = ctx.homes.get(self.id, Path("~/.zcode").expanduser())
        return f"error: ZCode model-io rollouts not found at {home / 'cli' / 'rollout'}"

    def list_sessions(self, ctx: CollectContext) -> List[SessionRef]:
        home = ctx.homes[self.id]
        refs = []
        for mtime, path in find_zcode_session_files(home, ctx.cutoff):
            refs.append(SessionRef(
                harness=self.id,
                path=path,
                mtime=mtime,
                file_label=str(path),
            ))
        return refs

    def parse_session(self, ref: SessionRef, skill_names, include_subagents: bool):
        return parse_zcode_session(ref.path, skill_names, include_subagents)

    def discover_skills(self, ctx: CollectContext):
        if not ctx.include_global_skills:
            return []
        home = ctx.homes.get(self.id)
        return [home / "skills"] if home is not None else []
