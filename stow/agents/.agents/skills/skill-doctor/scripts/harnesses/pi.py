"""Pi agent harness."""

from __future__ import annotations

import hashlib
import json
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
    detect_skill_candidates,
    empty_stats,
    iter_jsonl_records,
    looks_injected,
    recent_files,
    truncate,
)

from .base import CollectContext, HarnessPlugin, SessionRef


def find_pi_session_files(pi_home: Path, cutoff: datetime):
    root = pi_home / "sessions"
    if not root.is_dir():
        return []
    return recent_files(root.glob("*/*.jsonl"), cutoff)


def parse_pi_session(path: Path, skill_names, include_subagents: bool):
    """Normalize one Pi agent JSONL session to the shared transcript shape.

    Pi has no subagent sessions; include_subagents is accepted for signature
    compatibility with the Claude parser and ignored.
    """
    try:
        records = iter_jsonl_records(path)
    except OSError:
        return None

    meta = {}
    stats = empty_stats()
    entries = TranscriptBuffer()
    seen_calls = {}
    used_tool_names = set()
    skills_used = set()
    has_code_edit_hint = False
    first_ts = last_ts = None

    for obj in records:
        record_type = obj.get("type")
        ts = obj.get("timestamp")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts

        if record_type == "session":
            if not meta:
                meta = {
                    "id": obj.get("id") or path.stem,
                    "cwd": obj.get("cwd"),
                    "started_at": ts,
                    "originator": "pi",
                    "thread_source": None,
                }
            else:
                meta["cwd"] = meta.get("cwd") or obj.get("cwd")
                meta["started_at"] = meta.get("started_at") or ts
            continue

        if record_type != "message":
            continue
        message = obj.get("message")
        if not isinstance(message, dict):
            continue
        role = message.get("role")
        content = message.get("content")
        blocks = content if isinstance(content, list) else [{"type": "text", "text": content}]

        if role == "toolResult":
            message_error = bool(message.get("isError"))
            for block in blocks:
                if not isinstance(block, dict):
                    continue
                result = block.get("text") or ""
                if not isinstance(result, str) or not result:
                    continue
                low = result[:2000].lower()
                if (
                    message_error
                    or block.get("isError")
                    or "error" in low
                    or "failed" in low
                    or "traceback" in low
                ):
                    stats["error_outputs"] += 1
                entries.append(("output", truncate(result, MAX_TOOL_CHARS)))
            continue

        has_user_text = False
        if role == "assistant":
            stats["assistant_turns"] += 1

        for block in blocks:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text":
                text = block.get("text")
                if not isinstance(text, str) or not text or looks_injected(text):
                    continue
                if role == "user":
                    has_user_text = True
                    entries.append(("user", truncate(text, MAX_MSG_CHARS)))
                elif role == "assistant":
                    entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))
            elif block_type == "toolCall":
                stats["tool_calls"] += 1
                name = str(block.get("name") or "unknown")
                args = block.get("arguments") or {}
                args_text = args if isinstance(args, str) else json.dumps(args, ensure_ascii=False)
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

        if role == "user" and has_user_text:
            stats["user_turns"] += 1

    if not meta:
        meta = {
            "id": path.stem,
            "cwd": None,
            "started_at": first_ts,
            "originator": "pi",
            "thread_source": None,
        }

    stats["first_ts"] = first_ts
    stats["last_ts"] = last_ts
    stats["has_code_edits"] = (
        bool(used_tool_names & GENERIC_EDIT_TOOLS)
        or has_code_edit_hint
    )
    return meta, stats, entries.finish(), sorted(skills_used & set(skill_names))


class PiHarness(HarnessPlugin):
    id = "pi"
    display_name = "Pi"

    def detect_runtime(self, environ=None) -> bool:
        env = environ if environ is not None else os.environ
        return bool(env.get("PI_HOME") or env.get("PI_AGENT_HOME"))

    def is_available(self, ctx: CollectContext) -> bool:
        home = ctx.homes.get(self.id)
        return bool(home and (home / "sessions").is_dir())

    def missing_source_error(self, ctx: CollectContext) -> str:
        home = ctx.homes.get(self.id, Path("~/.pi/agent").expanduser())
        return f"error: Pi session home not found at {home / 'sessions'}"

    def list_sessions(self, ctx: CollectContext) -> List[SessionRef]:
        home = ctx.homes[self.id]
        refs = []
        for mtime, path in find_pi_session_files(home, ctx.cutoff):
            refs.append(SessionRef(
                harness=self.id,
                path=path,
                mtime=mtime,
                file_label=str(path),
            ))
        return refs

    def parse_session(self, ref: SessionRef, skill_names, include_subagents: bool):
        return parse_pi_session(ref.path, skill_names, include_subagents)

    def discover_skills(self, ctx: CollectContext):
        if not ctx.include_global_skills:
            return []
        home = ctx.homes.get(self.id)
        return [home / "skills"] if home is not None else []
