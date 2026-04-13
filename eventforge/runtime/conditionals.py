from __future__ import annotations

import ast
from functools import lru_cache
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

    tree = _compile_expression(expression)

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
    return bool(_eval_node(tree.body, context))


@lru_cache(maxsize=2048)
def _compile_expression(expression: str) -> ast.Expression:
    tree = ast.parse(expression, mode="eval")
    _safe(tree)
    return tree


def _eval_node(node: ast.AST, context: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id not in context:
            raise ValueError(f"unknown name in expression: {node.id}")
        return context[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not bool(_eval_node(node.operand, context))
    if isinstance(node, ast.BoolOp):
        values = [_eval_node(v, context) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(bool(v) for v in values)
        if isinstance(node.op, ast.Or):
            return any(bool(v) for v in values)
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, context)
        for op, comparator in zip(node.ops, node.comparators):
            right = _eval_node(comparator, context)
            if isinstance(op, ast.Eq):
                result = left == right
            elif isinstance(op, ast.NotEq):
                result = left != right
            elif isinstance(op, ast.Gt):
                result = left > right
            elif isinstance(op, ast.GtE):
                result = left >= right
            elif isinstance(op, ast.Lt):
                result = left < right
            elif isinstance(op, ast.LtE):
                result = left <= right
            elif isinstance(op, ast.In):
                result = left in right
            elif isinstance(op, ast.NotIn):
                result = left not in right
            else:
                raise ValueError(f"unsupported comparator: {type(op).__name__}")
            if not result:
                return False
            left = right
        return True
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("unsupported function call")
        name = node.func.id
        if name not in {"has", "field"}:
            raise ValueError(f"unsupported function: {name}")
        fn = context[name]
        args = [_eval_node(arg, context) for arg in node.args]
        return fn(*args)
    raise ValueError(f"unsupported expression node: {type(node).__name__}")
