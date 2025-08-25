"""
Tool to find all references to a symbol."""

import ast
from pathlib import Path
from typing import Any, Dict, List

from .find_definition import Location
from .tool import Tool, ToolContext


class ReferenceVisitor(ast.NodeVisitor):
    def __init__(self, name: str):
        self.name = name
        self.references: List[ast.AST] = []

    def visit_Name(self, node: ast.Name):
        if node.id == self.name:
            self.references.append(node)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if node.attr == self.name:
            self.references.append(node)
        self.generic_visit(node)

    def visit_alias(self, node: ast.alias):
        if node.name == self.name:
            self.references.append(node)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name == self.name:
            self.references.append(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        if node.name == self.name:
            self.references.append(node)
        self.generic_visit(node)


class FindReferencesTool(Tool):
    """A tool that finds all references to a symbol."""

    @property
    def name(self) -> str:
        return "find_references"

    @property
    def description(self) -> str:
        return "Finds all references to the symbol at a given position in a file. This is useful for understanding where a symbol is used throughout the project."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The file URI of the document containing the symbol.",
                },
                "line": {
                    "type": "integer",
                    "description": "The line number of the symbol's position.",
                },
                "character": {
                    "type": "integer",
                    "description": "The character offset of the symbol's position.",
                },
            },
            "required": ["uri", "line", "character"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> List[Dict[str, Any]]:
        """Handles a find references request for a given symbol."""
        # TODO: The implementation of this tool is incorrect. It should use the
        # line and character from kwargs to find the specific symbol at that
        # position, then find all references to it. The current implementation
        # is a placeholder.
        uri = kwargs["uri"]
        line = kwargs["line"]
        character = kwargs["character"]

        # Placeholder implementation returns no references.
        return []
