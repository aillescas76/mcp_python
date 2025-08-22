import ast
from typing import List, Dict, Any

from ..index.project import ProjectIndex
from .diagnostics import Diagnostic, DiagnosticSeverity
from ..astutils.parser import Range, Position

class DocstringVisitor(ast.NodeVisitor):
    def __init__(self, uri: str, ignore_private: bool = False):
        self.uri = uri
        self.diagnostics: List[Diagnostic] = []
        self.ignore_private = ignore_private

    def check_docstring(self, node: ast.AST, name: str):
        if self.ignore_private and name.startswith("_"):
            return

        if not (hasattr(node, "body") and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)):
            self.diagnostics.append(
                Diagnostic(
                    range=node._range,
                    message=f"Missing docstring for '{name}'",
                    severity=DiagnosticSeverity.WARNING,
                )
            )

    def visit_Module(self, node: ast.Module):
        if not (hasattr(node, "body") and node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)):
            default_range = Range(start=Position(line=0, column=0), end=Position(line=0, column=1))
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

async def docstring_lints_tool(
    index: ProjectIndex, uri: str, ignore_private: bool = False
) -> List[Dict[str, Any]]:
    """
    Checks for missing docstrings in a Python module.
    """
    module = index.modules.get(uri)
    if not module:
        return []

    visitor = DocstringVisitor(uri, ignore_private)
    visitor.visit(module.tree)
    return [d.to_dict() for d in visitor.diagnostics]