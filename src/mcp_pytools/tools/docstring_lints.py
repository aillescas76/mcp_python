import ast
from typing import Any, Dict, List

from ..astutils.parser import Position, Range
from .diagnostics import Diagnostic, DiagnosticSeverity
from .tool import Tool, ToolContext


class DocstringVisitor(ast.NodeVisitor):
    def __init__(self, uri: str, ignore_private: bool = False):
        self.uri = uri
        self.diagnostics: List[Diagnostic] = []
        self.ignore_private = ignore_private

    def check_docstring(self, node: ast.AST, name: str):
        if self.ignore_private and name.startswith("_"):
            return

        if not (
            hasattr(node, "body")
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            self.diagnostics.append(
                Diagnostic(
                    range=node._range,
                    message=f"Missing docstring for '{name}'",
                    severity=DiagnosticSeverity.WARNING,
                )
            )

    def visit_Module(self, node: ast.Module):
        if not (
            hasattr(node, "body")
            and node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        ):
            default_range = Range(
                start=Position(line=0, column=0), end=Position(line=0, column=1)
            )
            self.diagnostics.append(
                Diagnostic(
                    range=default_range,
                    message=f"Missing docstring for '{self.uri}'",
                    severity=DiagnosticSeverity.WARNING,
                )
            )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.check_docstring(node, node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.check_docstring(node, node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.check_docstring(node, node.name)
        self.generic_visit(node)


class DocstringLintsTool(Tool):
    @property
    def name(self) -> str:
        return "docstring_lints"

    @property
    def description(self) -> str:
        return (
            "Lints a Python file to find missing docstrings in modules, classes, and "
            "functions, reporting them as diagnostics. This helps enforce "
            "documentation standards."
        )

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The file URI of the Python module to check.",
                },
                "ignore_private": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "If true, functions and classes starting with an underscore "
                        "will be ignored."
                    ),
                },
            },
            "required": ["uri"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> List[Dict[str, Any]]:
        uri = kwargs["uri"]
        ignore_private = kwargs.get("ignore_private", False)
        module = context.project_index.modules.get(uri)
        if not module:
            return []

        visitor = DocstringVisitor(uri, ignore_private)
        visitor.visit(module.tree)
        return [d.to_dict() for d in visitor.diagnostics]
