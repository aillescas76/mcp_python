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

    @property
    def requires_index(self) -> bool:
        return False

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, Any]:
        """Gets the status of the project index."""
        stats = context.project_index.stats
        return {
            "indexed_files": stats.files_indexed,
            "parse_errors": stats.parse_errors,
        }
