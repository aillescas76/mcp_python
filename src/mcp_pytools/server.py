from pathlib import Path
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
from functools import partial

from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools import tool_registry
from mcp_pytools.tools.tool import ToolContext

mcp = FastMCP("Python Code Tools")

PROJECT_ROOT = Path("/home/aic/code/mcp_python")

class ServerContext(ToolContext):
    def __init__(self, project_root: Path):
        self._project_root = project_root
        self._project_index = ProjectIndex(project_root)

    @property
    def project_index(self) -> ProjectIndex:
        return self._project_index

    def build_index(self):
        print("Building project index...")
        self._project_index.build()
        print(f"Index built. {len(self._project_index.modules)} modules indexed.")

def create_tool_handler(tool, context: ServerContext):
    async def handler(**kwargs):
        try:
            return await tool.handle(context, **kwargs)
        except Exception as e:
            return {
                "error": {
                    "code": -32000,
                    "message": f"Tool execution failed: {e}",
                    "data": str(e),
                }
            }
    return handler

def main():
    """
    Main entry point for the MCP server.
    """
    context = ServerContext(PROJECT_ROOT)
    context.build_index()

    for tool in tool_registry:
        handler = create_tool_handler(tool, context)
        # Manually create a signature for the tool
        # This is a bit of a hack, but it's the easiest way to make it work with FastMCP
        # which relies on function signatures to generate the tool schema.
        from inspect import Parameter, Signature
        params = [
            Parameter(name, Parameter.POSITIONAL_OR_KEYWORD, annotation=p.get("type", Any))
            for name, p in tool.schema.get("properties", {}).items()
        ]
        sig = Signature(params)

        handler.__signature__ = sig
        handler.__name__ = tool.name
        handler.__doc__ = tool.description

        mcp.tool()(handler)

    print("MCP Python Tools Server starting...")
    mcp.run()

if __name__ == "__main__":
    main()