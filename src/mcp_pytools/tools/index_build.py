from typing import Any, Dict

from .tool import Tool, ToolContext


class IndexBuildTool(Tool):
    """A tool to trigger a full rebuild of the project index."""

    @property
    def name(self) -> str:
        return "index.build"

    @property
    def description(self) -> str:
        return "Builds or rebuilds the entire project index."

    async def handle(self, context: ToolContext, **kwargs: Any) -> Dict[str, Any]:
        """Triggers a full rebuild of the project index."""
        context.project_index.build()
        return {
            "status": "ok",
            "message": f"Index built with {len(context.project_index.modules)} modules.",
        }
