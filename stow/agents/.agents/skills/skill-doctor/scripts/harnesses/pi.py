"""Pi agent session plugin."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from .common import (
    CODE_EDIT_HINTS,
    GENERIC_EDIT_TOOLS,
    MAX_MSG_CHARS,
    MAX_TOOL_CHARS,
    TranscriptBuffer,
    detect_skill_candidates,
    empty_stats,
    iter_jsonl_records,
    looks_injected,
    make_session,
    mtime_utc,
    truncate,
)
from .protocol import BasePlugin


def find_pi_session_files(pi_home: Path, cutoff: datetime):
    root = pi_home / "sessions"
    if not root.is_dir():
        return []
    files = []
    for path in root.glob("*/*.jsonl"):
        try:
            mtime = mtime_utc(path)
        except OSError:
            continue
        if mtime >= cutoff:
            files.append((mtime, path))
    files.sort(key=lambda item: item[0], reverse=True)
    return files


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


class PiPlugin(BasePlugin):
    id = "pi"

    def add_cli_flags(self, parser) -> None:
        parser.add_argument(
            "--pi-home",
            default="~/.pi/agent",
            help="Pi agent home (default: ~/.pi/agent)",
        )

    def source_available(self, args) -> bool:
        return (Path(args.pi_home).expanduser() / "sessions").is_dir()

    def collect(self, args, cutoff, skill_names):
        pi_home = Path(args.pi_home).expanduser()
        files = find_pi_session_files(pi_home, cutoff)
        sessions = []
        for mtime, path in files:
            parsed = parse_pi_session(path, skill_names, args.include_subagents)
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            sessions.append(make_session(
                self.id, meta, stats, skills_used, str(path), mtime, entries
            ))
        return sessions, {"home": str(pi_home), "records_in_window": len(files)}

    def global_skill_roots(self, args):
        return [Path(args.pi_home).expanduser() / "skills"]

    def missing_error(self, args) -> str:
        home = Path(args.pi_home).expanduser() / "sessions"
        return f"error: Pi session home not found at {home}"
