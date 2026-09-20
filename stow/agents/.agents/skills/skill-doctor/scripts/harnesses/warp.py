"""Warp conversation database plugin."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from warp_decoder import ProtobufDecodeError, decode_task

from .common import (
    MAX_MSG_CHARS,
    MAX_TOOL_CHARS,
    empty_stats,
    looks_injected,
    make_session,
    truncate,
)
from .protocol import BasePlugin

MAX_WARP_CONVERSATION_BYTES = 32 * 1024 * 1024


def parse_sqlite_timestamp(value):
    if not value:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def discover_warp_databases(explicit_paths=(), data_dir=None):
    """Find Warp channel databases, preferring explicit paths when provided."""
    candidates = []
    for value in explicit_paths:
        candidates.append(Path(value).expanduser())

    roots = []
    if data_dir:
        roots.append(Path(data_dir).expanduser())
    elif sys.platform == "darwin":
        roots.append(
            Path.home()
            / "Library"
            / "Group Containers"
            / "2BBY89MBSN.dev.warp"
            / "Library"
            / "Application Support"
        )
    elif sys.platform.startswith("linux"):
        xdg_data = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        roots.extend((xdg_data / "warp-terminal", xdg_data / "warp"))
    elif os.name == "nt" and os.environ.get("APPDATA"):
        roots.append(Path(os.environ["APPDATA"]) / "Warp")

    for root in roots:
        if root.is_file():
            candidates.append(root)
            continue
        candidates.append(root / "warp.sqlite")
        if root.is_dir():
            candidates.extend(root.glob("*/warp.sqlite"))

    databases = []
    seen = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved in seen or not resolved.is_file():
            continue
        seen.add(resolved)
        databases.append(resolved)
    return sorted(databases)


def open_warp_database(path):
    connection = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=2)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def warp_database_has_sessions(connection):
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'agent_conversations'"
    ).fetchone()
    return row is not None


def sqlite_table_columns(connection, table):
    return {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}


def find_warp_conversations(databases, cutoff):
    """Return newest copies of Warp conversations across installed channels."""
    newest_by_id = {}
    scanned = 0
    cutoff_text = cutoff.strftime("%Y-%m-%d %H:%M:%S")
    for database in databases:
        connection = None
        try:
            connection = open_warp_database(database)
            if not warp_database_has_sessions(connection):
                continue
            conversation_columns = sqlite_table_columns(connection, "agent_conversations")
            summary_expression = "summary" if "summary" in conversation_columns else "NULL"
            rows = connection.execute(
                f"""
                SELECT conversation_id, conversation_data, last_modified_at,
                       {summary_expression} AS summary
                FROM agent_conversations
                WHERE last_modified_at >= ?
                ORDER BY last_modified_at DESC
                """,
                (cutoff_text,),
            ).fetchall()
        except sqlite3.Error as exc:
            print(f"warning: could not read Warp database {database}: {exc}", file=sys.stderr)
            continue
        finally:
            if connection is not None:
                connection.close()
        scanned += len(rows)
        for row in rows:
            modified_at = parse_sqlite_timestamp(row["last_modified_at"])
            if modified_at is None or modified_at < cutoff:
                continue
            record = {
                "conversation_id": row["conversation_id"],
                "conversation_data": row["conversation_data"],
                "summary": row["summary"],
                "modified_at": modified_at,
                "database": database,
                "channel": database.parent.name,
            }
            existing = newest_by_id.get(record["conversation_id"])
            if existing is None or modified_at > existing["modified_at"]:
                newest_by_id[record["conversation_id"]] = record
    records = sorted(newest_by_id.values(), key=lambda row: row["modified_at"], reverse=True)
    return records, scanned


def load_warp_conversation_data(record):
    """Load task blobs and ai_query fallback metadata for one conversation."""
    connection = open_warp_database(record["database"])
    try:
        task_rows = connection.execute(
            """
            SELECT task
            FROM agent_tasks
            WHERE conversation_id = ?
            ORDER BY id
            """,
            (record["conversation_id"],),
        ).fetchall()
        query_rows = []
        query_columns = sqlite_table_columns(connection, "ai_queries")
        if {"conversation_id", "start_ts"}.issubset(query_columns):
            working_directory_expression = (
                "working_directory" if "working_directory" in query_columns else "NULL"
            )
            query_rows = connection.execute(
                f"""
                SELECT start_ts, {working_directory_expression} AS working_directory
                FROM ai_queries
                WHERE conversation_id = ?
                ORDER BY start_ts
                """,
                (record["conversation_id"],),
            ).fetchall()
    finally:
        connection.close()
    task_blobs = [bytes(row["task"]) for row in task_rows]
    total_bytes = sum(len(blob) for blob in task_blobs)
    if total_bytes > MAX_WARP_CONVERSATION_BYTES:
        raise ProtobufDecodeError(
            f"conversation task snapshot is {total_bytes} bytes "
            f"(limit {MAX_WARP_CONVERSATION_BYTES})"
        )

    first_query_at = None
    working_directory = None
    for row in query_rows:
        first_query_at = first_query_at or parse_sqlite_timestamp(row["start_ts"])
        working_directory = working_directory or row["working_directory"]
    return task_blobs, first_query_at, working_directory


def skill_name_from_reference(reference, skill_names):
    if not reference:
        return None
    candidates = [
        reference.get("name"),
        reference.get("bundled_skill_id"),
    ]
    path = reference.get("path")
    if path:
        skill_path = Path(path)
        candidates.extend((skill_path.parent.name, skill_path.stem))
    return next((name for name in candidates if name in skill_names), None)


def parse_warp_conversation(record, skill_names, include_subagents):
    """Normalize one persisted Warp conversation to the Codex transcript shape."""
    try:
        conversation_data = json.loads(record["conversation_data"] or "{}")
    except (json.JSONDecodeError, TypeError):
        conversation_data = {}
    is_child = bool(
        conversation_data.get("parent_agent_id")
        or conversation_data.get("parent_conversation_id")
    )
    if is_child and not include_subagents:
        return None

    try:
        summary = json.loads(record["summary"] or "{}")
    except (json.JSONDecodeError, TypeError):
        summary = {}

    try:
        task_blobs, first_query_at, query_cwd = load_warp_conversation_data(record)
        tasks = [decode_task(blob) for blob in task_blobs]
    except (OSError, sqlite3.Error, ProtobufDecodeError) as exc:
        print(
            f"warning: could not decode Warp conversation "
            f"{record['conversation_id']} from {record['channel']}: {exc}",
            file=sys.stderr,
        )
        return None

    messages = []
    sequence = 0
    for task in tasks:
        for message in task["messages"]:
            message["_sequence"] = sequence
            sequence += 1
            messages.append(message)
    messages.sort(
        key=lambda message: (
            message.get("order_key") is None,
            message.get("order_key") or (0, 0),
            message["_sequence"],
        )
    )

    stats = empty_stats()
    entries = []
    seen_calls = {}
    skills_used = set()
    first_ts = last_ts = None
    cwd = summary.get("initial_working_directory") or query_cwd
    has_code_edits = False

    for message in messages:
        timestamp = message.get("timestamp")
        if timestamp:
            first_ts = first_ts or timestamp
            last_ts = timestamp
        kind = message["kind"]
        if kind == "user_query":
            text = message.get("text", "")
            cwd = cwd or message.get("cwd")
            if text and not looks_injected(text):
                stats["user_turns"] += 1
                entries.append(("user", truncate(text, MAX_MSG_CHARS)))
        elif kind == "invoke_skill":
            skill_reference = message.get("skill")
            skill_name = skill_name_from_reference(skill_reference, skill_names)
            if skill_name:
                skills_used.add(skill_name)
            if skill_reference:
                entries.append((
                    "skill",
                    truncate(json.dumps(skill_reference, ensure_ascii=False), MAX_TOOL_CHARS),
                ))
            user_query = message.get("user_query") or {}
            text = user_query.get("text", "")
            cwd = cwd or user_query.get("cwd")
            if text and not looks_injected(text):
                stats["user_turns"] += 1
                entries.append(("user", truncate(text, MAX_MSG_CHARS)))
        elif kind == "agent_output":
            text = message.get("text", "")
            if text:
                stats["assistant_turns"] += 1
                entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))
        elif kind == "tool_call":
            stats["tool_calls"] += 1
            name = message.get("name", "unknown")
            payload = message.get("payload", "")
            key = hashlib.sha1((name + payload).encode()).hexdigest()
            seen_calls[key] = seen_calls.get(key, 0) + 1
            if seen_calls[key] > 1:
                stats["repeated_tool_calls"] += 1
            has_code_edits = has_code_edits or name == "apply_file_diffs"
            skill_reference = message.get("skill")
            skill_name = skill_name_from_reference(skill_reference, skill_names)
            if skill_name:
                skills_used.add(skill_name)
            entries.append((f"tool:{name}", truncate(payload, MAX_TOOL_CHARS)))
            if skill_reference:
                entries.append((
                    "skill",
                    truncate(json.dumps(skill_reference, ensure_ascii=False), MAX_TOOL_CHARS),
                ))
        elif kind == "tool_call_result":
            payload = message.get("payload", "")
            cwd = cwd or message.get("cwd")
            low = payload[:2000].lower()
            if "error" in low or "failed" in low or "traceback" in low:
                stats["error_outputs"] += 1
            entries.append(("output", truncate(payload, MAX_TOOL_CHARS)))

    started_at = first_ts or (first_query_at.isoformat() if first_query_at else None)
    meta = {
        "id": record["conversation_id"],
        "cwd": cwd,
        "started_at": started_at,
        "originator": "warp",
        "thread_source": "subagent" if is_child else None,
        "channel": record["channel"],
    }
    stats["first_ts"] = first_ts
    stats["last_ts"] = last_ts
    stats["has_code_edits"] = has_code_edits
    return meta, stats, entries, sorted(skills_used)


class WarpPlugin(BasePlugin):
    id = "warp"

    def add_cli_flags(self, parser) -> None:
        parser.add_argument(
            "--warp-db",
            action="append",
            default=[],
            help="explicit Warp warp.sqlite path (repeatable)",
        )
        parser.add_argument(
            "--warp-data-dir",
            default=os.environ.get("WARP_DATA_DIR"),
            help="directory containing Warp channel data directories",
        )

    def source_available(self, args) -> bool:
        return bool(discover_warp_databases(args.warp_db, args.warp_data_dir))

    def collect(self, args, cutoff, skill_names):
        databases = discover_warp_databases(args.warp_db, args.warp_data_dir)
        if not databases:
            return [], {}
        records, scanned = find_warp_conversations(databases, cutoff)
        sessions = []
        for record in records:
            parsed = parse_warp_conversation(
                record, skill_names, args.include_subagents
            )
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            sessions.append(make_session(
                self.id,
                meta,
                stats,
                skills_used,
                f"{record['database']}#agent_conversations/{record['conversation_id']}",
                record["modified_at"],
                entries,
            ))
        return sessions, {
            "databases": [str(path) for path in databases],
            "records_in_window": scanned,
            "records_after_channel_deduplication": len(records),
        }

    def missing_error(self, args) -> str:
        return "error: no Warp conversation databases found"
