"""Tool to provide a document symbol outline for a given file."""

from typing import Any, Dict, List

from ..analysis.symbols import Symbol
from .tool import Tool, ToolContext


class DocumentSymbolsTool(Tool):
    """A tool that provides a document symbol outline for a given file."""

    @property
    def name(self) -> str:
        return "document_symbols"

    @property
    def description(self) -> str:
        return "Provides a document symbol outline for a given file."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "uri": {"type": "string", "description": "The URI of the document to analyze."}
            },
            "required": ["uri"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> List[Dict[str, Any]]:
        """Handles a document symbols request."""
        uri = kwargs["uri"]
        symbols: List[Symbol] = context.project_index.symbols.get(uri, [])
        return [symbol.to_dict() for symbol in symbols]
