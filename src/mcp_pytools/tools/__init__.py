from .registry import ToolRegistry

tool_registry = ToolRegistry()
# Discover tools from the 'mcp_pytools.tools' package
tool_registry.discover_tools(__import__("mcp_pytools.tools", fromlist=[""]))
