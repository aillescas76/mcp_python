"""Tool to find all references to a symbol."""

import ast
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


class FindReferencesTool(Tool):
    """A tool that finds all references to a symbol."""

    @property
    def name(self) -> str:
        return "find_references"

    @property
    def description(self) -> str:
        return "Finds all references to a symbol."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The symbol to find references for.",
                }
            },
            "required": ["symbol"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> List[Dict[str, Any]]:
        """Handles a find references request for a given symbol."""
        symbol = kwargs["symbol"]
        locations: List[Location] = []
        all_uris = context.project_index.get_all_uris()
        for file_uri in all_uris:
            file_module = context.project_index.modules.get(file_uri)
            if not file_module:
                continue

            visitor = ReferenceVisitor(symbol)
            visitor.visit(file_module.tree)
            for ref_node in visitor.references:
                if hasattr(ref_node, "_range"):
                    locations.append(Location(uri=file_uri, range=ref_node._range))

        return [loc.to_dict() for loc in locations]
