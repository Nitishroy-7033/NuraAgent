"""
math_tool.py — Safe math expression evaluator

Uses Python's ast module to safely evaluate math expressions
without allowing arbitrary code execution (no eval() with full globals).

Supports: +, -, *, /, //, %, **, sqrt, sin, cos, log, abs, round, etc.
"""
import ast
import math
import operator
from typing import Any

from utils.logger import get_logger

logger = get_logger("math_tool")

# Allowed operators
OPERATORS = {
    ast.Add:      operator.add,
    ast.Sub:      operator.sub,
    ast.Mult:     operator.mul,
    ast.Div:      operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod:      operator.mod,
    ast.Pow:      operator.pow,
    ast.USub:     operator.neg,
    ast.UAdd:     operator.pos,
}

# Allowed math functions
SAFE_FUNCTIONS = {
    "sqrt":  math.sqrt,
    "sin":   math.sin,
    "cos":   math.cos,
    "tan":   math.tan,
    "log":   math.log,
    "log2":  math.log2,
    "log10": math.log10,
    "abs":   abs,
    "round": round,
    "floor": math.floor,
    "ceil":  math.ceil,
    "pi":    math.pi,
    "e":     math.e,
    "inf":   math.inf,
    "factorial": math.factorial,
    "gcd":   math.gcd,
    "pow":   pow,
    "min":   min,
    "max":   max,
    "sum":   sum,
}


def evaluate_math(expression: str) -> dict:
    """
    Safely evaluate a math expression string.

    Returns:
      {
        "success":    bool,
        "result":     Any,
        "result_str": str,
        "error":      str,
        "expression": str,
      }
    """
    expression = expression.strip()
    logger.debug(f"Evaluating math: {expression}")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)

        # Format result nicely
        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                result_str = str(int(result))
            else:
                result_str = f"{result:.10g}"   # up to 10 significant figures
        else:
            result_str = str(result)

        logger.info(f"Math evaluated: {expression} = {result_str}")
        return {
            "success":    True,
            "result":     result,
            "result_str": result_str,
            "error":      "",
            "expression": expression,
        }

    except ZeroDivisionError:
        return _err(expression, "Division by zero")
    except ValueError as e:
        return _err(expression, f"Math error: {e}")
    except (TypeError, KeyError) as e:
        return _err(expression, f"Invalid expression: {e}")
    except Exception as e:
        return _err(expression, f"Could not evaluate: {e}")


def _eval_node(node: ast.AST) -> Any:
    """Recursively evaluate an AST node."""

    # Numbers
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise TypeError(f"Unsupported constant type: {type(node.value)}")

    # Unary ops: -x, +x
    if isinstance(node, ast.UnaryOp):
        op_fn = OPERATORS.get(type(node.op))
        if op_fn is None:
            raise TypeError(f"Unsupported unary operator: {type(node.op)}")
        return op_fn(_eval_node(node.operand))

    # Binary ops: x + y, x ** y, etc.
    if isinstance(node, ast.BinOp):
        op_fn = OPERATORS.get(type(node.op))
        if op_fn is None:
            raise TypeError(f"Unsupported operator: {type(node.op)}")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return op_fn(left, right)

    # Function calls: sqrt(x), log(x, 10), etc.
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise TypeError("Only simple function calls allowed")
        fn_name = node.func.id
        fn = SAFE_FUNCTIONS.get(fn_name)
        if fn is None:
            raise KeyError(f"Function not allowed: {fn_name}")
        args = [_eval_node(a) for a in node.args]
        return fn(*args)

    # Named constants: pi, e, inf
    if isinstance(node, ast.Name):
        val = SAFE_FUNCTIONS.get(node.id)
        if val is None:
            raise KeyError(f"Unknown name: {node.id}")
        return val

    # Lists (for sum([1,2,3]) etc.)
    if isinstance(node, ast.List):
        return [_eval_node(el) for el in node.elts]

    raise TypeError(f"Unsupported node type: {type(node).__name__}")


def _err(expression: str, message: str) -> dict:
    logger.warning(f"Math eval failed: {expression} - {message}")
    return {
        "success":    False,
        "result":     None,
        "result_str": "",
        "error":      message,
        "expression": expression,
    }


def format_result(result: dict) -> str:
    """Format math result for display in chat."""
    if result["success"]:
        return f"`{result['expression']}` = **{result['result_str']}**"
    else:
        return f"Math error: {result['error']}\nExpression: `{result['expression']}`"