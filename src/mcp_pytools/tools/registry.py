import importlib
import inspect
import pkgutil
from typing import Dict, Iterator

from .tool import Tool


class ToolRegistry:
    """A registry for discovering and holding tool instances."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def discover_tools(self, package) -> None:
        """Discovers tools in the given package."""
        for module_info in pkgutil.iter_modules(package.__path__):
            module_name = f"{package.__name__}.{module_info.name}"
            module = importlib.import_module(module_name)
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Tool)
                    and not inspect.isabstract(obj)
                ):
                    # Assuming tools have a no-argument constructor
                    tool_instance = obj()
                    self.register(tool_instance)

    def register(self, tool: Tool) -> None:
        """Registers a tool."""
        if tool.name in self._tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        """Gets a tool by name."""
        if name not in self._tools:
            raise ValueError(f"No tool with name '{name}' is registered.")
        return self._tools[name]

    def __iter__(self) -> Iterator[Tool]:
        """Iterates over the registered tools."""
        return iter(self._tools.values())
