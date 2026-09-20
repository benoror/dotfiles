"""Grok Bot (grok_bot) harness.

Verified v1 layout (treat path notes as hypotheses until listed):

- Transcripts: `/home/box/agent-data/agent-transcripts/<uuid>/<uuid>.jsonl`
  Directory name equals the JSONL stem.
- Override the transcript root with `--grok-bot-home` or `GROK_BOT_HOME`.
- Skip `sand-subagent-*` unless `--include-subagents`.
- JSONL: `{role: user|assistant|tool, message: {content: [{type, text}, ...]}}`.
- Global Grok Stow skills (`--include-global-skills`): `/home/box/agent-data/workflows`.
  The coding hub remains `~/.agents/skills` (collector, not this plugin).
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from common import recent_files

from .base import CollectContext, HarnessPlugin, SessionRef
from .role_message import parse_role_message_session

DEFAULT_GROK_BOT_HOME = Path("/home/box/agent-data/agent-transcripts")
DEFAULT_GROK_BOT_WORKFLOWS = Path("/home/box/agent-data/workflows")
SUBAGENT_PREFIX = "sand-subagent-"


def default_grok_bot_home() -> Path:
    return Path(os.environ.get("GROK_BOT_HOME", DEFAULT_GROK_BOT_HOME)).expanduser()


def workflows_dir_for(transcripts_home: Path, explicit: Optional[Path] = None) -> Path:
    if explicit is not None:
        return Path(explicit).expanduser()
    if transcripts_home.name == "agent-transcripts":
        return transcripts_home.parent / "workflows"
    sibling = transcripts_home.parent / "workflows"
    nested = transcripts_home / "workflows"
    if sibling.is_dir():
        return sibling
    return nested


def is_subagent_session(path: Path) -> bool:
    return path.parent.name.startswith(SUBAGENT_PREFIX) or path.stem.startswith(SUBAGENT_PREFIX)


def is_canonical_grok_bot_file(path: Path) -> bool:
    """`<uuid>/<uuid>.jsonl` — directory name equals file stem."""
    return path.suffix == ".jsonl" and path.parent.name == path.stem


def find_grok_bot_session_files(home: Path, cutoff: datetime, include_subagents: bool):
    if not home.is_dir():
        return []
    candidates = []
    for path in home.glob("*/*.jsonl"):
        if not is_canonical_grok_bot_file(path):
            continue
        if is_subagent_session(path) and not include_subagents:
            continue
        candidates.append(path)
    return recent_files(candidates, cutoff)


def parse_grok_bot_session(path: Path, skill_names, include_subagents: bool):
    if is_subagent_session(path) and not include_subagents:
        return None
    thread_source = "subagent" if is_subagent_session(path) else None
    parsed = parse_role_message_session(path, skill_names, "grok_bot", thread_source)
    if parsed is None:
        return None
    meta, stats, entries, skills_used = parsed
    meta["id"] = path.stem
    return meta, stats, entries, skills_used


class GrokBotHarness(HarnessPlugin):
    id = "grok_bot"
    display_name = "Grok Bot"
    cwd_optional = True

    def detect_runtime(self, environ=None) -> bool:
        env = environ if environ is not None else os.environ
        if env.get("GROK_BOT") or env.get("GROK_BOT_HOME"):
            return True
        if env.get("XAI_GROK_BOT"):
            return True
        transcripts = Path(env.get("GROK_BOT_HOME", DEFAULT_GROK_BOT_HOME)).expanduser()
        # Only treat the default box layout as a runtime hint when we are
        # clearly inside that environment (path exists and GROK-ish vars).
        if env.get("GROK") and transcripts.is_dir():
            return True
        return False

    def is_available(self, ctx: CollectContext) -> bool:
        home = ctx.homes.get(self.id)
        return bool(home and home.is_dir())

    def missing_source_error(self, ctx: CollectContext) -> str:
        home = ctx.homes.get(self.id, default_grok_bot_home())
        return f"error: Grok Bot transcripts not found at {home}"

    def list_sessions(self, ctx: CollectContext) -> List[SessionRef]:
        home = ctx.homes[self.id]
        refs = []
        for mtime, path in find_grok_bot_session_files(home, ctx.cutoff, ctx.include_subagents):
            refs.append(SessionRef(
                harness=self.id,
                path=path,
                mtime=mtime,
                file_label=str(path),
            ))
        return refs

    def parse_session(self, ref: SessionRef, skill_names, include_subagents: bool):
        return parse_grok_bot_session(ref.path, skill_names, include_subagents)

    def discover_skills(self, ctx: CollectContext):
        if not ctx.include_global_skills:
            return []
        explicit = ctx.extra.get("grok_bot_workflows")
        home = ctx.homes.get(self.id, default_grok_bot_home())
        workflows = workflows_dir_for(home, explicit)
        return [workflows]
