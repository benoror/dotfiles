"""Harness plugin registry for skill-doctor."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from .claude import ClaudePlugin
from .codex import CodexPlugin
from .cursor import CursorPlugin
from .grok import GrokBuildPlugin
from .grok_bot import GrokBotPlugin
from .pi import PiPlugin
from .warp import WarpPlugin
from .zcode import ZcodePlugin

# grok is Grok Build. grok_bot is the /home/box fleet. They do not alias.
PLUGINS = {
    "claude": ClaudePlugin(),
    "codex": CodexPlugin(),
    "warp": WarpPlugin(),
    "pi": PiPlugin(),
    "grok": GrokBuildPlugin(),
    "zcode": ZcodePlugin(),
    "cursor": CursorPlugin(),
    "grok_bot": GrokBotPlugin(),
}

CODING_HARNESSES = frozenset(
    {"claude", "codex", "warp", "pi", "grok", "zcode", "cursor"}
)
FLEET_HARNESSES = frozenset({"grok_bot"})


def plugin_ids():
    return tuple(PLUGINS.keys())


def requested_plugins(harness: str):
    return [plugin for plugin in PLUGINS.values() if plugin.is_requested(harness)]
