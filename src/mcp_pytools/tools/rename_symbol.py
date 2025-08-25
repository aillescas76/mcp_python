import ast
from pathlib import Path
from typing import Any, Dict

import astunparse

from .tool import Tool, ToolContext


class RenameTransformer(ast.NodeTransformer):
    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id == self.old_name:
            node.id = self.new_name
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        if node.name == self.old_name:
            node.name = self.new_name
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        if node.name == self.old_name:
            node.name = self.new_name
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        if node.arg == self.old_name:
            node.arg = self.new_name
        self.generic_visit(node)
        return node

    def visit_alias(self, node: ast.alias) -> ast.alias:
        if node.name == self.old_name:
            node.name = self.new_name
        self.generic_visit(node)
        return node


class RenameSymbolTool(Tool):
    @property
    def name(self) -> str:
        return "rename_symbol"

    @property
    def description(self) -> str:
        return "Safely renames a symbol at a given position and all its references across the project. This is a powerful refactoring tool."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The file URI of the document containing the symbol to rename.",
                },
                "line": {
                    "type": "integer",
                    "description": "The line number of the symbol's position.",
                },
                "character": {
                    "type": "integer",
                    "description": "The character offset of the symbol's position.",
                },
                "new_name": {
                    "type": "string",
                    "description": "The new name for the symbol.",
                },
            },
            "required": ["uri", "line", "character", "new_name"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, Any]:
        # TODO: This implementation is fundamentally incorrect and needs a complete
        # rewrite. It was calling `find_references` with an outdated schema and
        # its own renaming logic is a naive AST transformation that is not
        # context-aware and therefore unsafe for real-world use.
        # The schema has been updated to be correct, but the implementation
        # below is placeholder and will not work as intended.
        uri = kwargs["uri"]
        line = kwargs["line"]
        character = kwargs["character"]
        new_name = kwargs["new_name"]

        # Placeholder logic to avoid crashing. This does not work.
        old_name = "placeholder_to_avoid_crash"
        if not old_name or not new_name:
            return {"error": "Old symbol name and new name cannot be empty."}

        return {
            "error": "The rename_symbol tool is not implemented correctly. See TODO in source code."
        }
