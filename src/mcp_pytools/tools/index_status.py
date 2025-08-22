from typing import Any, Dict

from .tool import Tool, ToolContext


class IndexStatusTool(Tool):
    """A tool to get the status of the project index."""

    @property
    def name(self) -> str:
        return "index.status"

    @property
    def description(self) -> str:
        return "Gets the status of the project index."

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, Any]:
        """Gets the status of the project index."""
        return {
            "indexed_files": len(context.project_index.modules),
            "parse_errors": len(context.project_index.parse_errors),
        }
