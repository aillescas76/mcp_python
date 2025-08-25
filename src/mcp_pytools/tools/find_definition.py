import ast
import dataclasses
from pathlib import Path
from typing import Any, Dict, List

from ..astutils.parser import Range, parse_module
from .tool import Tool, ToolContext


@dataclasses.dataclass
class Location:
    uri: str
    range: Range
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return {"uri": self.uri, "range": self.range.to_dict(), "text": self.text}


class FindDefinitionTool(Tool):
    """A tool that finds the definition of a symbol."""

    @property
    def name(self) -> str:
        return "find_definition"

    @property
    def description(self) -> str:
        return (
            "Finds the definition of a symbol by its name, searching across the "
            "entire project. This is a custom implementation that performs a "
            "project-wide search."
        )

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The name of the symbol to find the definition for.",
                }
            },
            "required": ["symbol"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> List[Dict[str, Any]]:
        """Handles a find definition request for a given symbol."""
        symbol = kwargs["symbol"]
        locations: List[Location] = []
        if symbol in context.project_index.defs_by_name:
            for def_symbol in context.project_index.defs_by_name[symbol]:
                for uri, symbols_in_doc in context.project_index.symbols.items():
                    if def_symbol in symbols_in_doc:
                        file_path = Path(uri.replace("file://", ""))
                        file_content = context.project_index.file_cache.get_text(file_path)
                        if file_content:
                            module = parse_module(file_content, uri)
                            for node in ast.walk(module.tree):
                                if hasattr(node, "name") and node.name == symbol:
                                    text = ast.get_source_segment(file_content, node)
                                    if text:
                                        locations.append(
                                            Location(
                                                uri=uri,
                                                range=def_symbol.range,
                                                text=text,
                                            )
                                        )
                                        break
                        # Assuming one symbol is in one doc
                        break
        return [loc.to_dict() for loc in locations]
