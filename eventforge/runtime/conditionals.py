from __future__ import annotations

import ast
from typing import Any

from eventforge.core.event import Event

ALLOWED = (
    ast.Expression,
    ast.BoolOp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Gt,
    ast.GtE,
    ast.Lt,
    ast.LtE,
    ast.In,
    ast.NotIn,
    ast.Call,
)


def _safe(node: ast.AST) -> None:
    for subnode in ast.walk(node):
        if not isinstance(subnode, ALLOWED):
            raise ValueError(f"unsupported expression syntax: {type(subnode).__name__}")
        if isinstance(subnode, ast.Call) and not isinstance(subnode.func, ast.Name):
            raise ValueError("only builtin helper calls are allowed")


def evaluate(expression: str | None, event: Event) -> bool:
    if not expression:
        return True

    tree = ast.parse(expression, mode="eval")
    _safe(tree)

    def has(path: str) -> bool:
        return event.get(path) is not None

    def field(path: str, default: Any = None) -> Any:
        return event.get(path, default)

    context = {
        "has": has,
        "field": field,
        "tags": event.get("tags", []),
        "metadata": event.get("[@metadata]", {}),
    }
    return bool(eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, context))
