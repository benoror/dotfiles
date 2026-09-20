"""Built-in skill-doctor harness plugins."""

from __future__ import annotations

import os
from typing import Dict, List, Optional

from .base import CollectContext, HarnessPlugin, SessionRef
from .claude import ClaudeHarness
from .codex import CodexHarness
from .cursor import CursorHarness
from .grok import GrokHarness
from .grok_bot import GrokBotHarness
from .pi import PiHarness
from .warp import WarpHarness
from .zcode import ZcodeHarness

_PLUGINS: List[HarnessPlugin] = [
    WarpHarness(),
    ClaudeHarness(),
    CodexHarness(),
    PiHarness(),
    GrokHarness(),
    ZcodeHarness(),
    CursorHarness(),
    GrokBotHarness(),
]

REGISTRY: Dict[str, HarnessPlugin] = {plugin.id: plugin for plugin in _PLUGINS}
HARNESS_IDS = tuple(REGISTRY)


def all_plugins() -> List[HarnessPlugin]:
    return list(_PLUGINS)


def get_plugin(harness_id: str) -> HarnessPlugin:
    return REGISTRY[harness_id]


def select_plugins(harness: str) -> List[HarnessPlugin]:
    if harness in ("auto", "all"):
        return all_plugins()
    return [get_plugin(harness)]


def detect_runtime(environ: Optional[dict] = None) -> Optional[str]:
    """Return the collector ID of the executing harness, if identified."""
    env = environ if environ is not None else os.environ
    matches = [plugin.id for plugin in _PLUGINS if plugin.detect_runtime(env)]
    if len(matches) == 1:
        return matches[0]
    # Prefer more specific Grok Bot over Grok Build when both match.
    if matches == ["grok", "grok_bot"] or set(matches) == {"grok", "grok_bot"}:
        return "grok_bot"
    if "cursor" in matches and len(matches) > 1:
        return "cursor"
    if len(matches) > 1:
        return matches[0]
    return None


__all__ = [
    "CollectContext",
    "HARNESS_IDS",
    "HarnessPlugin",
    "REGISTRY",
    "SessionRef",
    "all_plugins",
    "detect_runtime",
    "get_plugin",
    "select_plugins",
]
