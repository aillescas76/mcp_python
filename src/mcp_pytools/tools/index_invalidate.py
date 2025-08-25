from typing import Any, Dict

from .tool import Tool, ToolContext


class IndexInvalidateTool(Tool):
    """A tool to invalidate and rebuild a file in the project index."""

    @property
    def name(self) -> str:
        return "index_invalidate"

    @property
    def description(self) -> str:
        return "Invalidates and rebuilds a file in the project index."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The URI of the file to invalidate and rebuild.",
                }
            },
            "required": ["uri"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, Any]:
        """Handles an invalidate request."""
        uri = kwargs["uri"]
        context.project_index.rebuild(uri)
        return {
            "status": "ok",
            "message": f"URI '{uri}' invalidated and rebuilt.",
        }
