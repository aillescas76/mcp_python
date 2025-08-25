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
        return "Lists all symbols (classes, functions, methods, etc.) in a given Python file. This is useful for getting a high-level overview of a file's structure and contents."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The file URI of the Python module to analyze.",
                }
            },
            "required": ["uri"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> List[Dict[str, Any]]:
        """Handles a document symbols request."""
        uri = kwargs["uri"]
        symbols: List[Symbol] = context.project_index.symbols.get(uri, [])
        return [symbol.to_dict() for symbol in symbols]
