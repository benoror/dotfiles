"""Grok Bot fleet transcript plugin.

Root default: /home/box/agent-data/agent-transcripts
Layout: <uuid>/<uuid>.jsonl with the same stem as the directory.
sand-subagent-* directories are child runs. Exclude them unless
--include-subagents is set.

Line schema (verified 2026-09-20):
  {"role": "user"|"assistant"|"tool", "message": {"content": [{"type": ..., "text": ...}]}}

Global skills for this harness live under /home/box/agent-data/workflows.
Do not mix those with the coding hub unless the user passes --skills-dir.
"""

from __future__ import annotations

import json
import re
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

DEFAULT_HOME = "/home/box/agent-data/agent-transcripts"
DEFAULT_WORKFLOWS = "/home/box/agent-data/workflows"
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def is_uuid_name(name: str) -> bool:
    return bool(UUID_RE.match(name))


def is_subagent_dir(name: str) -> bool:
    return name.startswith("sand-subagent-")


def find_grok_bot_session_files(home: Path, cutoff: datetime, include_subagents: bool):
    if not home.is_dir():
        return []
    files = []
    for child in home.iterdir():
        if not child.is_dir():
            continue
        if is_subagent_dir(child.name) and not include_subagents:
            continue
        if not (is_uuid_name(child.name) or is_subagent_dir(child.name)):
            continue
        path = child / f"{child.name}.jsonl"
        if not path.is_file():
            continue
        try:
            mtime = mtime_utc(path)
        except OSError:
            continue
        if mtime >= cutoff:
            files.append((mtime, path))
    files.sort(key=lambda item: item[0], reverse=True)
    return files


def _cwd_from_text(text: str):
    match = re.search(r"(?:cwd|working.?directory|repo)\s*[:=]\s*(\S+)", text, re.I)
    if match:
        return match.group(1).strip("\"'")
    return None


def parse_grok_bot_session(path: Path, skill_names, include_subagents: bool):
    """Normalize one fleet jsonl to the shared transcript shape."""
    if is_subagent_dir(path.parent.name) and not include_subagents:
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
    cwd = None

    for obj in records:
        if not isinstance(obj, dict):
            continue
        ts = obj.get("timestamp")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts
        role = obj.get("role")
        if role not in ("user", "assistant", "tool"):
            continue
        message = obj.get("message") if isinstance(obj.get("message"), dict) else obj
        content = message.get("content")
        if role == "assistant":
            stats["assistant_turns"] += 1
        has_user_text = False
        for block in iter_content_blocks(content):
            block_type = block.get("type") or "text"
            text = block.get("text") or extract_text(block.get("content"))
            if block_type == "text":
                if not isinstance(text, str) or not text or looks_injected(text):
                    continue
                cwd = cwd or _cwd_from_text(text)
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
                name = str(block.get("name") or block.get("toolName") or "unknown")
                args = block.get("input") or block.get("arguments") or block.get("params") or {}
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
                if block.get("is_error") or block.get("isError") or "error" in low or "failed" in low:
                    stats["error_outputs"] += 1
                entries.append(("output", truncate(result, MAX_TOOL_CHARS)))
        if role == "tool" and content is None:
            result = extract_text(message)
            if result:
                low = result[:2000].lower()
                if "error" in low or "failed" in low or "traceback" in low:
                    stats["error_outputs"] += 1
                entries.append(("output", truncate(result, MAX_TOOL_CHARS)))
        if role == "user" and has_user_text:
            stats["user_turns"] += 1

    meta = {
        "id": path.stem,
        "cwd": cwd,
        "started_at": first_ts,
        "originator": "grok_bot",
        "thread_source": "subagent" if is_subagent_dir(path.parent.name) else None,
    }
    stats["first_ts"] = first_ts
    stats["last_ts"] = last_ts
    stats["has_code_edits"] = (
        bool(used_tool_names & GENERIC_EDIT_TOOLS) or has_code_edit_hint
    )
    return meta, stats, entries.finish(), sorted(set(skills_used) & set(skill_names))


class GrokBotPlugin(BasePlugin):
    id = "grok_bot"

    def add_cli_flags(self, parser) -> None:
        parser.add_argument(
            "--grok-bot-home",
            default=DEFAULT_HOME,
            help="Grok Bot transcript root (default: /home/box/agent-data/agent-transcripts)",
        )

    def source_available(self, args) -> bool:
        return Path(args.grok_bot_home).expanduser().is_dir()

    def collect(self, args, cutoff, skill_names):
        home = Path(args.grok_bot_home).expanduser()
        files = find_grok_bot_session_files(home, cutoff, args.include_subagents)
        sessions = []
        for mtime, path in files:
            parsed = parse_grok_bot_session(path, skill_names, args.include_subagents)
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            sessions.append(make_session(
                self.id, meta, stats, skills_used, str(path), mtime, entries
            ))
        return sessions, {"home": str(home), "records_in_window": len(files)}

    def global_skill_roots(self, args):
        return [Path(DEFAULT_WORKFLOWS)]

    def missing_error(self, args) -> str:
        home = Path(args.grok_bot_home).expanduser()
        return f"error: Grok Bot transcripts not found at {home}"
