"""Codex session plugin."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

from .common import (
    CODE_EDIT_HINTS,
    MAX_MSG_CHARS,
    MAX_TOOL_CHARS,
    TranscriptBuffer,
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


def find_codex_session_files(codex_home: Path, cutoff: datetime):
    files = []
    for sub in ("sessions", "archived_sessions"):
        root = codex_home / sub
        if not root.is_dir():
            continue
        for f in root.rglob("rollout-*.jsonl"):
            try:
                mtime = mtime_utc(f)
            except OSError:
                continue
            if mtime >= cutoff:
                files.append((mtime, f))
    files.sort(key=lambda t: t[0], reverse=True)
    return files


def parse_codex_session(path: Path, skill_names, include_subagents: bool):
    """Returns (meta, stats, entries) or None if the session should be skipped."""
    try:
        records = iter_jsonl_records(path)
    except OSError:
        return None

    meta = {}
    stats = empty_stats()
    entries = TranscriptBuffer()
    seen_calls = {}
    skills_used = set()
    has_code_edits = False
    first_ts = last_ts = None

    for obj in records:
        ltype = obj.get("type")
        payload = obj.get("payload") or {}
        if not isinstance(payload, dict):
            continue
        ts = obj.get("timestamp")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts

        if ltype == "session_meta":
            meta = {
                "id": payload.get("id") or payload.get("session_id") or path.stem,
                "cwd": payload.get("cwd"),
                "started_at": payload.get("timestamp"),
                "originator": payload.get("originator"),
                "thread_source": payload.get("thread_source"),
                "cli_version": payload.get("cli_version"),
            }
            source = payload.get("source")
            is_subagent = payload.get("thread_source") == "subagent" or (
                isinstance(source, dict) and "subagent" in source
            )
            if is_subagent and not include_subagents:
                return None

        elif ltype == "event_msg":
            ptype = payload.get("type")
            if ptype == "user_message":
                stats["user_turns"] += 1
            elif ptype == "agent_message":
                stats["assistant_turns"] += 1

        elif ltype == "response_item":
            ptype = payload.get("type")
            if ptype == "message":
                role = payload.get("role")
                text = extract_text(payload.get("content"))
                if not text:
                    continue
                if role == "user":
                    if looks_injected(text):
                        continue
                    entries.append(("user", truncate(text, MAX_MSG_CHARS)))
                elif role == "assistant":
                    entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))
            elif ptype in ("function_call", "custom_tool_call", "local_shell_call"):
                stats["tool_calls"] += 1
                name = payload.get("name") or ptype
                args = payload.get("arguments") or payload.get("input") or ""
                if not isinstance(args, str):
                    args = json.dumps(args)
                key = hashlib.sha1((name + args).encode()).hexdigest()
                seen_calls[key] = seen_calls.get(key, 0) + 1
                if seen_calls[key] > 1:
                    stats["repeated_tool_calls"] += 1
                skills_used.update(detect_skill_candidates(args))
                has_code_edits = has_code_edits or any(
                    hint in args for hint in CODE_EDIT_HINTS
                )
                entries.append((f"tool:{name}", truncate(args, MAX_TOOL_CHARS)))
            elif ptype in ("function_call_output", "custom_tool_call_output"):
                out = payload.get("output") or ""
                if not isinstance(out, str):
                    out = json.dumps(out)
                low = out[:2000].lower()
                if "error" in low or "failed" in low or "traceback" in low:
                    stats["error_outputs"] += 1
                entries.append(("output", truncate(out, MAX_TOOL_CHARS)))

    if not meta:
        meta = {"id": path.stem, "cwd": None, "started_at": first_ts}

    stats["first_ts"] = first_ts
    stats["last_ts"] = last_ts
    stats["has_code_edits"] = has_code_edits
    return meta, stats, entries.finish(), sorted(skills_used)


class CodexPlugin(BasePlugin):
    id = "codex"

    def add_cli_flags(self, parser) -> None:
        parser.add_argument(
            "--codex-home",
            default=os.environ.get("CODEX_HOME", "~/.codex"),
        )

    def source_available(self, args) -> bool:
        return Path(args.codex_home).expanduser().is_dir()

    def collect(self, args, cutoff, skill_names):
        codex_home = Path(args.codex_home).expanduser()
        files = find_codex_session_files(codex_home, cutoff)
        sessions = []
        for mtime, path in files:
            parsed = parse_codex_session(path, skill_names, args.include_subagents)
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            sessions.append(make_session(
                self.id, meta, stats, skills_used, str(path), mtime, entries
            ))
        return sessions, {"home": str(codex_home), "records_in_window": len(files)}

    def global_skill_roots(self, args):
        return [Path(args.codex_home).expanduser() / "skills"]

    def missing_error(self, args) -> str:
        return f"error: Codex home not found at {Path(args.codex_home).expanduser()}"
