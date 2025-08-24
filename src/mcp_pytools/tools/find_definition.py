"""Tool to find the definition of a symbol."""

import dataclasses
from typing import Any, Dict, List

from ..astutils.parser import Range
from .tool import Tool, ToolContext


@dataclasses.dataclass
class Location:
    uri: str
    range: Range

    def to_dict(self) -> Dict[str, Any]:
        return {"uri": self.uri, "range": self.range.to_dict()}


class FindDefinitionTool(Tool):
    """A tool that finds the definition of a symbol."""

    @property
    def name(self) -> str:
        return "find_definition"

    @property
    def description(self) -> str:
        return "Finds the definition of a symbol."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "The symbol to find."}
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
                        locations.append(Location(uri=uri, range=def_symbol.range))
                        # Assuming one symbol is in one doc
                        break
        return [loc.to_dict() for loc in locations]
