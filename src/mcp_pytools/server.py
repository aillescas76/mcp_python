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
from mcp_pytools.tools.docstring_lints import docstring_lints_tool
from mcp_pytools.tools.mutability_check import mutability_check_tool
from mcp_pytools.tools.syntax_check import syntax_check_tool
from mcp_pytools.tools.organize_imports import organize_imports_tool

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


@mcp.tool()
async def docstring_lints(uri: str, ignore_private: bool = False) -> List[Dict[str, Any]]:
    """
    Checks for missing docstrings in a Python module.
    """
    return await docstring_lints_tool(project_index, uri, ignore_private)


@mcp.tool()
async def mutability_check(uri: str) -> List[Dict[str, Any]]:
    """
    Checks for mutable default arguments in a Python module.
    """
    return await mutability_check_tool(project_index, uri)


@mcp.tool()
async def syntax_check(uri: str) -> List[Dict[str, Any]]:
    """
    Checks for syntax errors in a Python module.
    """
    return await syntax_check_tool(project_index, uri)


@mcp.tool()
async def organize_imports(uri: str, apply: bool = False) -> Dict[str, Any]:
    """
    Organizes imports in a Python module using ruff.
    """
    return await organize_imports_tool(project_index, uri, apply)


@mcp.tool()
async def rename_symbol(symbol: str, new_name: str, apply: bool = False) -> Dict[str, Any]:
    """
    Renames a symbol and all its references across the project.
    """
    return await rename_symbol_tool(project_index, symbol, new_name, apply)


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