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
                    file_path = Path(file_uri.replace("file://", ""))
                    file_content = context.project_index.file_cache.get_text(file_path)
                    lines = file_content.splitlines()
                    start_line = ref_node._range.start.line
                    end_line = ref_node._range.end.line
                    start_col = ref_node._range.start.column
                    end_col = ref_node._range.end.column

                    if start_line == end_line:
                        text = lines[start_line][start_col:end_col]
                    else:
                        text_lines = [lines[start_line][start_col:]]
                        text_lines.extend(lines[start_line + 1:end_line])
                        text_lines.append(lines[end_line][:end_col])
                        text = "\n".join(text_lines)

                    locations.append(Location(uri=file_uri, range=ref_node._range, text=text))

        return [loc.to_dict() for loc in locations]
