import ast
from typing import List, Dict, Any

from ..index.project import ProjectIndex
from .diagnostics import Diagnostic, DiagnosticSeverity

class MutabilityVisitor(ast.NodeVisitor):
    def __init__(self, uri: str):
        self.uri = uri
        self.diagnostics: List[Diagnostic] = []

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.check_defaults(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.check_defaults(node)
        self.generic_visit(node)

    def check_defaults(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        for default in node.args.defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set, ast.Call)):
                self.diagnostics.append(
                    Diagnostic(
                        range=default._range,
                        message="Mutable default argument",
                        severity=DiagnosticSeverity.WARNING,
                    )
                )
        for default in node.args.kw_defaults:
            if default and isinstance(default, (ast.List, ast.Dict, ast.Set, ast.Call)):
                self.diagnostics.append(
                    Diagnostic(
                        range=default._range,
                        message="Mutable default argument",
                        severity=DiagnosticSeverity.WARNING,
                    )
                )

async def mutability_check_tool(
    index: ProjectIndex, uri: str
) -> List[Dict[str, Any]]:
    """
    Checks for mutable default arguments in a Python module.
    """
    module = index.modules.get(uri)
    if not module:
        return []

    visitor = MutabilityVisitor(uri)
    visitor.visit(module.tree)
    return [d.to_dict() for d in visitor.diagnostics]
