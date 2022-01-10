"""Macro expansion module."""

import ast
import inspect
import textwrap
from types import CodeType, FunctionType


class MacroExpander(ast.NodeTransformer):
    """Given a macro, expand it into a list of statements."""

    def __init__(self, macros: dict[str, str]):
        self.macros = macros

    def visit_Expr(self, node: ast.Expr) -> ast.Expr:
        """Expand a macro."""
        if isinstance(node.value, ast.Name) and node.value.id in self.macros:
            return ast.parse(self.macros[node.value.id]).body
        else:
            return node


def expand(macros: dict[str, str]) -> FunctionType:
    """Expand macros in a function."""

    def _expand(func: FunctionType) -> FunctionType:
        """Expand a function."""
        assert isinstance(func, FunctionType)

        # Get the source code of the function.
        lines, start_lineno = inspect.getsourcelines(func)
        source = textwrap.dedent("".join(lines))
        func_tree = ast.parse(source)
        ast.increment_lineno(func_tree, start_lineno - 1)

        # expand the macro definitions
        expander = MacroExpander(macros)
        func_tree = ast.fix_missing_locations(expander.visit(func_tree))

        # isolate the codeobj for the function
        tree_code_obj = compile(func_tree, func.__code__.co_filename, "exec",)
        code_objs = list(
            filter(
                lambda obj: isinstance(obj, CodeType)
                and obj.co_name == func.__code__.co_name,
                tree_code_obj.co_consts,
            )
        )
        assert len(code_objs) == 1
        func_code_obj = code_objs[0]

        # replace the current code object with the expanded code object
        func.__code__ = func_code_obj
        return func

    return _expand
