from __future__ import annotations

import ast
import re
from pathlib import Path

from lark import Lark, Token, Transformer, v_args

from eventforge.config.ast import PipelineSpec, PluginSpec, ProjectConfig
from eventforge.core.errors import ConfigError

GRAMMAR = r"""
start: section+
section: "input" block   -> input_section
       | "filter" block  -> filter_section
       | "output" block  -> output_section
block: "{" plugin* "}"
plugin: NAME "{" body? "}"
body: /[^{}]+/

%import common.CNAME -> NAME
%import common.WS
%ignore WS
%ignore COMMENT
COMMENT: /#[^\n]*/
"""

PAIR_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*=>\s*(\[[^\]]*\]|\{[^\}]*\}|\"[^\"]*\"|'[^']*'|[^\s]+)")


def _parse_value(raw: str):
    text = raw.strip()
    if text in {"true", "false"}:
        return text == "true"
    try:
        if text.startswith("{") and "=>" in text:
            # Supports hash values shaped as: { "k1" => "v1" "k2" => 2 }.
            # Nested hashes and nested arrays inside hash values are not supported
            # in this bootstrap parser implementation.
            inner = text.strip("{} ")
            result = {}
            if not inner:
                return result
            parts = re.findall(r"\"([^\"]+)\"\s*=>\s*(\"[^\"]*\"|'[^']*'|[^\s]+)", inner)
            for key, value in parts:
                result[key] = _parse_value(value)
            return result
        return ast.literal_eval(text)
    except Exception:
        return text


def _parse_body(body: str) -> dict:
    parsed: dict = {}
    for key, raw_value in PAIR_RE.findall(body):
        parsed[key] = _parse_value(raw_value)
    return parsed


@v_args(inline=True)
class DslTransformer(Transformer):
    def __init__(self) -> None:
        super().__init__()
        self.sections: dict[str, list[PluginSpec]] = {"input": [], "filter": [], "output": []}

    def plugin(self, name: Token, body: Token | None = None):
        config = _parse_body(str(body) if body else "")
        return str(name), config

    def input_section(self, plugins):
        for name, config in plugins.children:
            self.sections["input"].append(PluginSpec("input", name, config))

    def filter_section(self, plugins):
        for name, config in plugins.children:
            self.sections["filter"].append(PluginSpec("filter", name, config))

    def output_section(self, plugins):
        for name, config in plugins.children:
            self.sections["output"].append(PluginSpec("output", name, config))


_PARSER = Lark(GRAMMAR, parser="lalr")


def parse_dsl(text: str, pipeline_id: str = "main") -> ProjectConfig:
    tree = _PARSER.parse(text)
    transformer = DslTransformer()
    transformer.transform(tree)
    return ProjectConfig([
        PipelineSpec(pipeline_id=pipeline_id, plugins=transformer.sections),
    ])


def parse_dsl_file(path: str | Path, pipeline_id: str = "main") -> ProjectConfig:
    p = Path(path)
    try:
        return parse_dsl(p.read_text(encoding="utf-8"), pipeline_id=pipeline_id)
    except Exception as exc:
        raise ConfigError(f"DSL parse failed for {p}: {exc}") from exc
