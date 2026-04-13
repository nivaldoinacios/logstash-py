from __future__ import annotations

import re
from collections.abc import Iterable
from functools import lru_cache
from typing import Any

from pydantic import Field

from eventforge.core.event import Event
from eventforge.plugins.base import FilterPlugin, PluginConfig, PluginMetadata

DEFAULT_PATTERNS = {
    "WORD": r"\\b\\w+\\b",
    "INT": r"[+-]?\\d+",
    "NUMBER": r"[+-]?(?:\\d+(?:\\.\\d+)?)",
    "GREEDYDATA": r".*",
    "DATA": r".*?",
    "IP": r"(?:\\d{1,3}\\.){3}\\d{1,3}",
    "TIMESTAMP_ISO8601": r"\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:?\\d{2})?",
}

TOKEN_RE = re.compile(r"%\{([A-Z0-9_]+)(?::([^}]+))?\}")


@lru_cache(maxsize=2048)
def compile_grok(pattern: str) -> re.Pattern[str]:
    def repl(match: re.Match[str]) -> str:
        base = match.group(1)
        field = match.group(2)
        expression = DEFAULT_PATTERNS.get(base, r".*")
        return f"(?P<{field}>{expression})" if field else f"(?:{expression})"

    return re.compile(TOKEN_RE.sub(repl, pattern))


class GrokFilterConfig(PluginConfig):
    source: str = "message"
    match: list[str] = Field(default_factory=list)
    tag_on_failure: str = "_grokparsefailure"


class GrokFilter(FilterPlugin):
    metadata = PluginMetadata(name="grok", description="Grok-like parser")
    config_model = GrokFilterConfig

    def process(self, event: Event) -> Iterable[Event]:
        source_value = event.get(self.config.source)
        if not isinstance(source_value, str):
            event.add_tag(self.config.tag_on_failure)
            return [event]

        for expr in self.config.match:
            regex = compile_grok(expr)
            matched = regex.search(source_value)
            if not matched:
                continue
            for key, value in matched.groupdict().items():
                if key and value is not None:
                    event.set(key, value)
            return [event]

        event.add_tag(self.config.tag_on_failure)
        return [event]
