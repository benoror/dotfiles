"""Shared parser for role/message/content JSONL transcripts.

Used by grok_bot (verified v1) and the best-effort Cursor harness.
Lines look like:

    {role: user|assistant|tool, message: {content: [{type, text}, ...]}}
"""

from __future__ import annotations

import json
from pathlib import Path

from common import (
    CODE_EDIT_HINTS,
    CURSOR_EDIT_TOOLS,
    MAX_MSG_CHARS,
    MAX_TOOL_CHARS,
    TranscriptBuffer,
    detect_skill_candidates,
    empty_stats,
    extract_text,
    iter_jsonl_records,
    looks_injected,
    note_error_output,
    note_tool_call,
    truncate,
)


def _blocks(content):
    if content is None:
        return []
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict) or isinstance(block, str)]
    if isinstance(content, dict):
        return [content]
    return [{"type": "text", "text": content}]


def _block_text(block):
    if isinstance(block, str):
        return block
    return block.get("text") or extract_text(block.get("content"))


def _tool_payload(block):
    args = block.get("input") or block.get("arguments") or block.get("params") or {}
    if isinstance(args, str):
        return args
    return json.dumps(args, ensure_ascii=False)


def parse_role_message_session(path: Path, skill_names, originator, thread_source=None):
    """Normalize a role/message JSONL (or JSON array) file."""
    records = list(_iter_records(path))
    if not records:
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
        ts = obj.get("timestamp") or obj.get("createdAt") or obj.get("created_at")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts
        cwd = cwd or obj.get("cwd") or obj.get("working_directory")

        role = obj.get("role") or obj.get("type")
        message = obj.get("message") if isinstance(obj.get("message"), dict) else {}
        cwd = cwd or message.get("cwd")
        content = message.get("content") if message else obj.get("content")
        role = message.get("role") or role
        if role in ("system", "reasoning"):
            continue

        if role in ("tool", "toolResult", "tool_result"):
            result = extract_text(content)
            if not result:
                continue
            note_error_output(stats, result, is_error=bool(obj.get("is_error") or message.get("is_error")))
            entries.append(("output", truncate(result, MAX_TOOL_CHARS)))
            continue

        blocks = _blocks(content)
        has_user_text = False
        saw_assistant_text = False

        for block in blocks:
            if isinstance(block, str):
                text = block
                block_type = "text"
                block = {"type": "text", "text": text}
            else:
                block_type = block.get("type") or "text"
                text = _block_text(block)

            if block_type in ("tool_use", "toolCall", "tool_call", "function_call"):
                name = str(block.get("name") or block.get("toolName") or "unknown")
                args_text = _tool_payload(block)
                note_tool_call(stats, seen_calls, name, args_text)
                used_tool_names.add(name)
                skills_used.update(detect_skill_candidates(args_text))
                has_code_edit_hint = has_code_edit_hint or any(
                    hint in args_text for hint in CODE_EDIT_HINTS
                )
                if name in ("Skill", "skill") and isinstance(block.get("input"), dict):
                    skill_name = block["input"].get("skill")
                    if skill_name:
                        skills_used.add(skill_name)
                entries.append((f"tool:{name}", truncate(args_text, MAX_TOOL_CHARS)))
            elif block_type in ("tool_result", "toolResult"):
                result = text or extract_text(block.get("content"))
                if not result:
                    continue
                note_error_output(stats, result, is_error=bool(block.get("is_error") or block.get("isError")))
                entries.append(("output", truncate(result, MAX_TOOL_CHARS)))
            elif block_type in ("text", "output_text"):
                if not isinstance(text, str) or not text or looks_injected(text):
                    continue
                if role == "user":
                    has_user_text = True
                    entries.append(("user", truncate(text, MAX_MSG_CHARS)))
                elif role == "assistant":
                    saw_assistant_text = True
                    entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))

        if role == "user" and has_user_text:
            stats["user_turns"] += 1
        if role == "assistant" and (saw_assistant_text or any(
            (b.get("type") if isinstance(b, dict) else None) in ("tool_use", "toolCall", "tool_call")
            for b in blocks
            if isinstance(b, dict)
        )):
            # Count one assistant turn per assistant record, not per block.
            stats["assistant_turns"] += 1

    meta = {
        "id": path.stem,
        "cwd": cwd,
        "started_at": first_ts,
        "originator": originator,
        "thread_source": thread_source,
    }
    stats["first_ts"] = first_ts
    stats["last_ts"] = last_ts
    stats["has_code_edits"] = (
        bool(used_tool_names & CURSOR_EDIT_TOOLS)
        or has_code_edit_hint
    )
    installed = set(skill_names)
    detected = set(skills_used)
    return meta, stats, entries.finish(), sorted(detected & installed if installed else detected)


def _iter_records(path: Path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace").lstrip()
    except OSError:
        return
    if text.startswith("["):
        try:
            payload = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            payload = None
        if isinstance(payload, list):
            for obj in payload:
                yield obj
            return
    try:
        yield from iter_jsonl_records(path)
    except OSError:
        return


def parse_role_message_session_filtered(path: Path, skill_names, originator, thread_source=None):
    """Like parse_role_message_session, but skill hits are intersected with inventory."""
    parsed = parse_role_message_session(path, skill_names, originator, thread_source)
    if parsed is None:
        return None
    meta, stats, entries, skills_used = parsed
    installed = set(skill_names)
    if installed:
        skills_used = sorted(set(skills_used) & installed)
    else:
        skills_used = sorted(set(skills_used))
    return meta, stats, entries, skills_used
