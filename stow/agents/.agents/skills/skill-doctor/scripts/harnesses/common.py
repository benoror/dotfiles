"""Shared helpers for skill-doctor harness plugins.

Python 3.9+, stdlib only. Nothing here uploads transcripts.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

MAX_MSG_CHARS = 1500
MAX_TOOL_CHARS = 500
MAX_TRANSCRIPT_ENTRIES = 160
TRANSCRIPT_HEAD = 100
TRANSCRIPT_TAIL = 40

CODE_EDIT_HINTS = (
    "apply_patch",
    "*** Begin Patch",
    "edit_file",
    "create_file",
    "str_replace",
    "write_file",
)
CLAUDE_CODE_EDIT_TOOLS = {"Edit", "MultiEdit", "NotebookEdit", "Write"}
GENERIC_EDIT_TOOLS = {
    "edit",
    "write",
    "apply_patch",
    "edit_file",
    "write_file",
    "str_replace",
    "search_replace",
}


def truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f" …[truncated {len(text) - limit} chars]"


def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                t = block.get("text") or block.get("content") or ""
                if isinstance(t, str) and t:
                    parts.append(t)
            elif isinstance(block, str):
                parts.append(block)
    return "\n".join(parts)


def iter_jsonl_records(path: Path):
    """Yield every valid JSON object without loading the whole file."""
    stream = path.open("r", encoding="utf-8", errors="replace")

    def records():
        with stream:
            for line in stream:
                try:
                    yield json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue

    return records()


class TranscriptBuffer:
    """Keep complete short transcripts and a bounded head/tail for long ones."""

    def __init__(self):
        self._entries = []
        self._tail = None
        self._total = 0

    def append(self, entry):
        self._total += 1
        if self._tail is None:
            self._entries.append(entry)
            if len(self._entries) > MAX_TRANSCRIPT_ENTRIES:
                self._tail = deque(self._entries[-TRANSCRIPT_TAIL:], maxlen=TRANSCRIPT_TAIL)
                self._entries = self._entries[:TRANSCRIPT_HEAD]
        else:
            self._tail.append(entry)

    def finish(self):
        if self._tail is None:
            return self._entries
        omitted = self._total - TRANSCRIPT_HEAD - TRANSCRIPT_TAIL
        return self._entries + [
            ("note", f"[... {omitted} entries omitted ...]")
        ] + list(self._tail)


def detect_skill_candidates(text: str):
    """Extract possible installed-skill names from one tool argument payload."""
    normalized = text.replace("\\", "/")
    candidates = set(re.findall(r"(?:^|/)skills/+([^/]+)/+", normalized))
    candidates.update(re.findall(
        r'"(?:skill|name|bundled_skill_id)"\s*:\s*"([^"]+)"',
        normalized,
    ))
    return candidates


def looks_injected(text: str) -> bool:
    head = text.lstrip()[:80]
    return head.startswith("<") and any(
        tag in head
        for tag in (
            "environment_context", "user_instructions", "ENVIRONMENT", "system-reminder",
            "permissions", "collaboration_mode", "recommended_plugins", "turn_context",
            "user_info",
        )
    )


def assistant_tool_calls(message):
    """Extract (name, args_text) pairs from OpenAI-style tool_calls entries."""
    calls = []
    for call in message.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        fn = call.get("function") or {}
        name = call.get("name") or fn.get("name") or "unknown"
        args = call.get("arguments")
        if args is None:
            args = fn.get("arguments")
        if not isinstance(args, str):
            args = json.dumps(args, ensure_ascii=False)
        calls.append((str(name), args))
    return calls


def record_tool_call(stats, seen_calls, name, args_text):
    stats["tool_calls"] += 1
    key = hashlib.sha1((name + args_text).encode()).hexdigest()
    seen_calls[key] = seen_calls.get(key, 0) + 1
    if seen_calls[key] > 1:
        stats["repeated_tool_calls"] += 1
    return any(hint in args_text for hint in CODE_EDIT_HINTS)


def empty_stats():
    return {
        "user_turns": 0,
        "assistant_turns": 0,
        "tool_calls": 0,
        "repeated_tool_calls": 0,
        "error_outputs": 0,
    }


def mark_error_output(stats, text) -> bool:
    low = (text or "")[:2000].lower()
    if "error" in low or "failed" in low or "traceback" in low:
        stats["error_outputs"] += 1
        return True
    return False


def session_matches_repo(cwd, repo: Path) -> bool:
    """True when a session's recorded cwd belongs to this repo.

    Two ways to match:
    1. cwd is inside the repo root (same-machine sessions).
    2. cwd's trailing directory name equals the repo's name (git/Codex
       worktrees like ~/.codex/worktrees/<id>/<repo-name>, and sessions
       imported from another machine where the checkout path differs).
    Basename matching can over-match if two different projects share a
    directory name; acceptable for a report, and prefix matching alone
    misses every worktree session.
    """
    if not cwd:
        return False
    p = Path(cwd)
    try:
        if p.resolve().is_relative_to(repo):
            return True
    except OSError:
        pass  # cwd from another machine may not exist locally
    return p.name == repo.name or repo.name in p.parts


def session_matches_repos(cwd, repos) -> bool:
    return any(session_matches_repo(cwd, repo) for repo in repos)


def infer_session_repos(sessions):
    repos = []
    seen = set()
    for session in sessions:
        cwd = session["meta"].get("cwd")
        if not cwd:
            continue
        path = Path(cwd).expanduser()
        if not path.is_dir():
            continue
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (subprocess.TimeoutExpired, OSError):
            continue
        if result.returncode != 0 or not result.stdout.strip():
            continue
        repo = Path(result.stdout.strip()).resolve()
        if repo in seen:
            continue
        seen.add(repo)
        repos.append(repo)
    return repos


def detect_skills_from_entries(entries, skill_names):
    tool_text = "\n".join(
        text
        for role, text in entries
        if role == "skill" or role.startswith("tool:")
    ).replace("\\", "/")
    detected = set()
    for name in skill_names:
        markers = (
            f"skills/{name}/",
            f"{name}/SKILL.md",
            f'"skill": "{name}"',
            f'"name": "{name}"',
            f'"bundled_skill_id": "{name}"',
        )
        if any(marker in tool_text for marker in markers):
            detected.add(name)
    return detected


def render_transcript(meta, stats, skills_used, entries) -> str:
    lines = [
        f"# Session {meta.get('id')}",
        f"- cwd: {meta.get('cwd')}",
        f"- started: {meta.get('started_at') or stats.get('first_ts')}",
        f"- skills detected: {', '.join(skills_used) or '(none)'}",
        f"- stats: {stats['user_turns']} user turns, {stats['assistant_turns']} assistant turns, "
        f"{stats['tool_calls']} tool calls ({stats['repeated_tool_calls']} repeated), "
        f"{stats['error_outputs']} error-ish outputs, code edits: {stats['has_code_edits']}",
        "",
        "## Condensed transcript",
        "",
    ]
    shown = entries
    if len(entries) > MAX_TRANSCRIPT_ENTRIES:
        omitted = len(entries) - TRANSCRIPT_HEAD - TRANSCRIPT_TAIL
        shown = entries[:TRANSCRIPT_HEAD] + [("note", f"[... {omitted} entries omitted ...]")] + entries[-TRANSCRIPT_TAIL:]
    for role, text in shown:
        lines.append(f"[{role}] {text}")
        lines.append("")
    return "\n".join(lines)


def mtime_utc(path: Path):
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)


def expand_home(value) -> Path:
    return Path(value).expanduser()


def env_or(name: str, default: str) -> str:
    return os.environ.get(name, default)


def make_session(harness, meta, stats, skills_used, file, modified_at, entries):
    return {
        "harness": harness,
        "meta": meta,
        "stats": stats,
        "skills_used": skills_used,
        "file": file,
        "modified_at": modified_at if isinstance(modified_at, str) else modified_at.isoformat(),
        "_entries": entries,
    }


def is_scoreable(stats) -> bool:
    return stats.get("assistant_turns", 0) >= 1 and stats.get("tool_calls", 0) >= 1


def decode_encoded_project_path(encoded: str) -> str:
    """Best-effort decode of Cursor/Claude-style project folder names.

    Leading slash is often stripped and `/` becomes `-`. Hyphens that were
    already in the path cannot be recovered. Treat the result as a hint.
    """
    if not encoded:
        return ""
    text = encoded.strip()
    if text.startswith("-"):
        text = text[1:]
    guessed = "/" + text.replace("-", "/")
    return guessed


def iter_content_blocks(content) -> Iterable[dict]:
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                yield block
            elif isinstance(block, str) and block:
                yield {"type": "text", "text": block}
    elif isinstance(content, str) and content:
        yield {"type": "text", "text": content}
    elif isinstance(content, dict):
        yield content
