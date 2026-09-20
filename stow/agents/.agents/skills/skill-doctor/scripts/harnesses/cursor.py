"""Cursor agent transcript plugin (best-effort, Mac-primary).

v1 reads JSONL under ~/.cursor/projects/*/agent-transcripts/.
It does not decode state.vscdb protobuf or ~/.cursor/chats store.db.

Published CLI shape (deja-vu, 2026-07-17):
  {"role":"user"|"assistant"|"tool","message":{"content":[{"type":"text","text":"..."}]}}

If files exist but the first records are not that shape, probe status is
format_unknown and collect returns no sessions.

Path unknowns on this cloud VM are documented in references/sot-surfaces.md.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from .common import (
    CODE_EDIT_HINTS,
    GENERIC_EDIT_TOOLS,
    MAX_MSG_CHARS,
    MAX_TOOL_CHARS,
    TranscriptBuffer,
    assistant_tool_calls,
    decode_encoded_project_path,
    detect_skill_candidates,
    empty_stats,
    extract_text,
    iter_content_blocks,
    iter_jsonl_records,
    looks_injected,
    make_session,
    mtime_utc,
    record_tool_call,
    truncate,
)
from .protocol import BasePlugin

KNOWN_ROLES = {"user", "assistant", "tool"}
KNOWN_BLOCK_TYPES = {
    "text",
    "tool_use",
    "toolCall",
    "function_call",
    "tool_result",
    "toolResult",
}


def default_cursor_home() -> str:
    return os.environ.get("CURSOR_CONFIG_DIR", "~/.cursor")


def cursor_ide_roots():
    """Typical IDE globalStorage roots. v1 probes them and does not parse."""
    roots = []
    if sys.platform == "darwin":
        roots.append(
            Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage"
        )
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    roots.append(xdg / "Cursor" / "User" / "globalStorage")
    return roots


def is_subagent_path(path: Path) -> bool:
    name = path.name.lower()
    parent = path.parent.name.lower()
    return "subagent" in name or "subagent" in parent


def find_cursor_session_files(cursor_home: Path, cutoff: datetime, include_subagents: bool):
    projects = cursor_home / "projects"
    if not projects.is_dir():
        return []
    files = []
    for path in projects.glob("*/agent-transcripts/*.jsonl"):
        _consider(path, cutoff, include_subagents, files)
    for path in projects.glob("*/agent-transcripts/*/*.jsonl"):
        _consider(path, cutoff, include_subagents, files)
    files.sort(key=lambda item: item[0], reverse=True)
    return files


def _consider(path, cutoff, include_subagents, files):
    if is_subagent_path(path) and not include_subagents:
        return
    try:
        mtime = mtime_utc(path)
    except OSError:
        return
    if mtime >= cutoff:
        files.append((mtime, path))


def probe_cursor_format(path: Path) -> str:
    """Return ok, empty, or format_unknown for one transcript."""
    try:
        records = list(iter_jsonl_records(path))
    except OSError:
        return "unavailable"
    if not records:
        return "empty"
    for obj in records[:8]:
        if not isinstance(obj, dict):
            continue
        role = obj.get("role") or obj.get("type")
        if role in KNOWN_ROLES or role in ("human", "ai"):
            message = obj.get("message")
            if isinstance(message, dict) or obj.get("content") is not None:
                return "ok"
            if isinstance(obj.get("text"), str):
                return "ok"
    return "format_unknown"


def cwd_from_cursor_path(path: Path) -> str:
    """Best-effort project path from ~/.cursor/projects/<encoded>/..."""
    try:
        parts = path.resolve().parts
        if "projects" in parts:
            idx = parts.index("projects")
            encoded = parts[idx + 1]
            return decode_encoded_project_path(encoded)
    except (OSError, ValueError, IndexError):
        pass
    return ""


def parse_cursor_session(path: Path, skill_names, include_subagents: bool):
    if is_subagent_path(path) and not include_subagents:
        return None
    status = probe_cursor_format(path)
    if status != "ok":
        return None
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
    first_ts = last_ts = None
    cwd = cwd_from_cursor_path(path) or None

    for obj in records:
        if not isinstance(obj, dict):
            continue
        ts = obj.get("timestamp") or obj.get("createdAt")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts
        role = obj.get("role") or obj.get("type")
        if role == "human":
            role = "user"
        if role == "ai":
            role = "assistant"
        if role not in KNOWN_ROLES:
            continue
        message = obj.get("message") if isinstance(obj.get("message"), dict) else obj
        content = message.get("content", obj.get("content", obj.get("text")))
        if role == "assistant":
            stats["assistant_turns"] += 1
        has_user_text = False
        for block in iter_content_blocks(content):
            block_type = block.get("type") or "text"
            text = block.get("text") or extract_text(block.get("content"))
            if block_type == "text":
                if not isinstance(text, str) or not text or looks_injected(text):
                    continue
                if role == "user":
                    has_user_text = True
                    entries.append(("user", truncate(text, MAX_MSG_CHARS)))
                elif role == "assistant":
                    entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))
                elif role == "tool":
                    low = text[:2000].lower()
                    if "error" in low or "failed" in low or "traceback" in low:
                        stats["error_outputs"] += 1
                    entries.append(("output", truncate(text, MAX_TOOL_CHARS)))
            elif block_type in ("tool_use", "toolCall", "function_call"):
                name = str(block.get("name") or "unknown")
                args = block.get("input") or block.get("arguments") or {}
                args_text = args if isinstance(args, str) else json.dumps(args, ensure_ascii=False)
                has_code_edit_hint = record_tool_call(stats, seen_calls, name, args_text) or has_code_edit_hint
                used_tool_names.add(name)
                skills_used.update(detect_skill_candidates(args_text))
                entries.append((f"tool:{name}", truncate(args_text, MAX_TOOL_CHARS)))
            elif block_type in ("tool_result", "toolResult"):
                result = text if isinstance(text, str) else extract_text(block.get("content"))
                if not result:
                    continue
                low = result[:2000].lower()
                if block.get("is_error") or "error" in low or "failed" in low:
                    stats["error_outputs"] += 1
                entries.append(("output", truncate(result, MAX_TOOL_CHARS)))
        for name, args_text in assistant_tool_calls(message if isinstance(message, dict) else {}):
            has_code_edit_hint = record_tool_call(stats, seen_calls, name, args_text) or has_code_edit_hint
            used_tool_names.add(name)
            skills_used.update(detect_skill_candidates(args_text))
            entries.append((f"tool:{name}", truncate(args_text, MAX_TOOL_CHARS)))
        if role == "user" and has_user_text:
            stats["user_turns"] += 1

    meta = {
        "id": path.stem,
        "cwd": cwd,
        "started_at": first_ts,
        "originator": "cursor",
        "thread_source": "subagent" if is_subagent_path(path) else None,
    }
    stats["first_ts"] = first_ts
    stats["last_ts"] = last_ts
    stats["has_code_edits"] = (
        bool(used_tool_names & GENERIC_EDIT_TOOLS) or has_code_edit_hint
    )
    return meta, stats, entries.finish(), sorted(set(skills_used) & set(skill_names))


class CursorPlugin(BasePlugin):
    id = "cursor"

    def add_cli_flags(self, parser) -> None:
        parser.add_argument(
            "--cursor-home",
            default=default_cursor_home(),
            help="Cursor config directory (default: CURSOR_CONFIG_DIR or ~/.cursor)",
        )

    def source_available(self, args) -> bool:
        return (Path(args.cursor_home).expanduser() / "projects").is_dir()

    def collect(self, args, cutoff, skill_names):
        home = Path(args.cursor_home).expanduser()
        files = find_cursor_session_files(home, cutoff, args.include_subagents)
        probe_paths = [str(home / "projects")]
        probe_paths.extend(str(p) for p in cursor_ide_roots())
        status = "unavailable"
        notes = (
            "Best-effort JSONL under projects/*/agent-transcripts. "
            "Does not decode state.vscdb or chats/*/store.db. "
            "Mac-primary; format unknown is accepted and yields no sessions."
        )
        if files:
            statuses = {probe_cursor_format(path) for _, path in files}
            if "ok" in statuses:
                status = "ok"
            elif statuses == {"empty"}:
                status = "unavailable"
            else:
                status = "format_unknown"
        sessions = []
        if status == "ok":
            for mtime, path in files:
                parsed = parse_cursor_session(path, skill_names, args.include_subagents)
                if parsed is None:
                    continue
                meta, stats, entries, skills_used = parsed
                sessions.append(make_session(
                    self.id, meta, stats, skills_used, str(path), mtime, entries
                ))
        note = {
            "home": str(home),
            "records_in_window": len(files),
            "probe_paths": probe_paths,
            "status": status,
            "notes": notes,
        }
        return sessions, note

    def global_skill_roots(self, args):
        return []

    def missing_error(self, args) -> str:
        home = Path(args.cursor_home).expanduser()
        return (
            f"error: Cursor transcripts not found under {home / 'projects'} "
            "(expected */agent-transcripts/*.jsonl)"
        )
