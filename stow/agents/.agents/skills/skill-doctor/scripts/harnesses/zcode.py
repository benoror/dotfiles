"""ZCode model-io rollout plugin."""

from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from .common import (
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
    make_session,
    mtime_utc,
    truncate,
)
from .protocol import BasePlugin


def find_zcode_session_files(zcode_home: Path, cutoff: datetime):
    root = zcode_home / "cli" / "rollout"
    if not root.is_dir():
        return []
    files = []
    for path in root.glob("model-io-*.jsonl"):
        try:
            mtime = mtime_utc(path)
        except OSError:
            continue
        if mtime >= cutoff:
            files.append((mtime, path))
    files.sort(key=lambda item: item[0], reverse=True)
    return files


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


class ZcodePlugin(BasePlugin):
    id = "zcode"

    def add_cli_flags(self, parser) -> None:
        parser.add_argument(
            "--zcode-home",
            default="~/.zcode",
            help="ZCode home (default: ~/.zcode)",
        )

    def source_available(self, args) -> bool:
        return (Path(args.zcode_home).expanduser() / "cli" / "rollout").is_dir()

    def collect(self, args, cutoff, skill_names):
        zcode_home = Path(args.zcode_home).expanduser()
        files = find_zcode_session_files(zcode_home, cutoff)
        sessions = []
        for mtime, path in files:
            parsed = parse_zcode_session(path, skill_names, args.include_subagents)
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            sessions.append(make_session(
                self.id, meta, stats, skills_used, str(path), mtime, entries
            ))
        return sessions, {"home": str(zcode_home), "records_in_window": len(files)}

    def global_skill_roots(self, args):
        return [Path(args.zcode_home).expanduser() / "skills"]

    def missing_error(self, args) -> str:
        home = Path(args.zcode_home).expanduser() / "cli" / "rollout"
        return f"error: ZCode model-io rollouts not found at {home}"
