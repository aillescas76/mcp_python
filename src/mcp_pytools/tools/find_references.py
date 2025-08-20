"""Tool to find all references to a symbol."""

import ast
from typing import Any, Dict, List

from ..index.project import ProjectIndex
from .find_definition import Location


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


async def find_references_tool(
    index: ProjectIndex, symbol: str
) -> List[Dict[str, Any]]:
    """Handles a find references request for a given symbol.

    This version performs a simple AST traversal to find all references by name.

    Args:
        index: The project index.
        symbol: The symbol name to find references for.

    Returns:
        A list of Locations where the symbol name appears.
    """
    locations: List[Location] = []
    all_uris = index.get_all_uris()
    for file_uri in all_uris:
        file_module = index.modules.get(file_uri)
        if not file_module:
            continue

        visitor = ReferenceVisitor(symbol)
        visitor.visit(file_module.tree)
        for ref_node in visitor.references:
            if hasattr(ref_node, "_range"):
                locations.append(Location(uri=file_uri, range=ref_node._range))

    return [loc.to_dict() for loc in locations]
