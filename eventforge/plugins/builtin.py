from __future__ import annotations

from eventforge.plugins.codecs import JsonCodec, JsonLinesCodec, PlainCodec
from eventforge.plugins.filters import DateFilter, DropFilter, GrokFilter, JsonFilter, MutateFilter
from eventforge.plugins.inputs import FileInput, HttpInput, StdinInput
from eventforge.plugins.outputs import ElasticsearchOutput, FileOutput, HttpOutput, StdoutOutput
from eventforge.plugins.registry import PluginRegistry


def register_builtin_plugins(registry: PluginRegistry) -> None:
    registry.register("input", "stdin", StdinInput)
    registry.register("input", "file", FileInput)
    registry.register("input", "http", HttpInput)

    registry.register("filter", "mutate", MutateFilter)
    registry.register("filter", "json", JsonFilter)
    registry.register("filter", "grok", GrokFilter)
    registry.register("filter", "date", DateFilter)
    registry.register("filter", "drop", DropFilter)

    registry.register("output", "stdout", StdoutOutput)
    registry.register("output", "file", FileOutput)
    registry.register("output", "http", HttpOutput)
    registry.register("output", "elasticsearch", ElasticsearchOutput)

    registry.register("codec", "plain", PlainCodec)
    registry.register("codec", "json", JsonCodec)
    registry.register("codec", "json_lines", JsonLinesCodec)
