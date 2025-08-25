import argparse
import threading
from inspect import Parameter, Signature
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools import tool_registry
from mcp_pytools.tools.registry import ToolRegistry
from mcp_pytools.tools.tool import Tool, ToolContext

mcp = FastMCP("Python Code Tools")

JSON_SCHEMA_TO_PYTHON_TYPE = {
    "string": str,
    "number": float,
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}


class ServerContext(ToolContext):
    def __init__(self, project_root: Path):
        self._project_root = project_root
        self._project_index = ProjectIndex(project_root)
        self._index_ready = threading.Event()
        self._tool_registry = tool_registry

    @property
    def project_index(self) -> ProjectIndex:
        return self._project_index

    @property
    def tool_registry(self) -> "ToolRegistry":
        return self._tool_registry

    def build_index(self):
        def build():
            print("Building project index...")
            self._project_index.build()
            print(
                f"Index built. {len(self._project_index.modules)} modules indexed."
            )
            self._index_ready.set()

        thread = threading.Thread(target=build, daemon=True)
        thread.start()

    def ensure_index_ready(self):
        """Blocks until the project index is ready."""
        self._index_ready.wait()


def create_tool_handler(tool: Tool, context: ServerContext):
    """Creates a handler function for a given tool that FastMCP can use."""

    async def handler(**kwargs):
        try:
            if tool.requires_index:
                context.ensure_index_ready()

            # Note: We assume the concrete tool's handle method accepts the context.
            return await tool.handle(context, **kwargs)
        except Exception as e:
            # Basic error handling, can be improved.
            return {
                "error": {
                    "code": -32000,  # Generic server error
                    "message": f"Tool '{tool.name}' execution failed: {type(e).__name__}",
                    "data": str(e),
                }
            }

    # Dynamically create the function signature for FastMCP's inspection
    params = []
    schema = tool.schema
    required_params = schema.get("required", [])
    if "properties" in schema:
        for name, prop_schema in schema["properties"].items():
            python_type = JSON_SCHEMA_TO_PYTHON_TYPE.get(
                prop_schema.get("type"), Any
            )

            default = Parameter.empty
            # If a parameter is not in the 'required' list, mark it as optional
            if name not in required_params:
                python_type = Optional[python_type]
                default = None

            params.append(
                Parameter(
                    name,
                    Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=python_type,
                    default=default,
                )
            )

    handler.__signature__ = Signature(params)
    handler.__name__ = tool.name
    handler.__doc__ = tool.description
    return handler


def main():
    """
    Main entry point for the MCP server.
    """
    parser = argparse.ArgumentParser(description="MCP Python Tools Server")
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="The root directory of the Python project.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    context = ServerContext(project_root)
    context.build_index()

    # Discover and register all tools with FastMCP
    for tool in tool_registry:
        handler = create_tool_handler(tool, context)
        mcp.tool()(handler)

    print(f"MCP Python Tools Server starting with {len(tool_registry._tools)} tools...")
    mcp.run()


if __name__ == "__main__":
    main()
