import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

from mcp.server.fastmcp import FastMCP

from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.document_symbols import document_symbols_tool
from mcp_pytools.tools.find_definition import find_definition_tool
from mcp_pytools.tools.find_references import find_references_tool
from mcp_pytools.tools.import_graph import import_graph_tool
from mcp_pytools.tools.search_text import search_text_tool

mcp = FastMCP("Python Code Tools")

# This is a global index. For a real server, this would need better management.
# The server should be initialized with a project root.
PROJECT_ROOT = Path("/home/aic/code/mcp_python")
project_index = ProjectIndex(PROJECT_ROOT)


@mcp.tool()
async def document_symbols(uri: str) -> List[Dict[str, Any]]:
    """
    Provides a document symbol outline for a given file.
    """
    return await document_symbols_tool(project_index, uri)


@mcp.tool()
async def find_definition(symbol: str) -> List[Dict[str, Any]]:
    """
    Finds the definition of a symbol.
    """
    return await find_definition_tool(project_index, symbol)


@mcp.tool()
async def find_references(symbol: str) -> List[Dict[str, Any]]:
    """
    Finds all references to a symbol.
    """
    return await find_references_tool(project_index, symbol)


@mcp.tool()
async def import_graph(moduleUri: str) -> Dict[str, List[str]]:
    """
    Shows a module's direct imports and its dependents (reverse imports).
    """
    return await import_graph_tool(project_index, moduleUri)


@mcp.tool()
async def search_text(
    pattern: str,
    includeGlobs: Optional[List[str]] = None,
    excludeGlobs: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Performs a regular expression search over the files in the project.
    """
    return await search_text_tool(project_index, pattern, includeGlobs, excludeGlobs)


def main():
    """
    Main entry point for the MCP server.
    """
    print("Building project index...")
    project_index.build()
    print(f"Index built. {len(project_index.modules)} modules indexed.")
    print("MCP Python Tools Server starting...")
    mcp.run()


if __name__ == "__main__":
    main()