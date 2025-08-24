from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol


class Tool(ABC):
    """Abstract base class for a tool."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A short description of the tool."""
        pass

    @property
    def schema(self) -> Dict[str, Any]:
        """The schema of the tool's input."""
        return {}

    @abstractmethod
    async def handle(self, **kwargs: Any) -> Any:
        """Executes the tool with the given arguments."""
        pass


class ToolContext(Protocol):
    """A protocol for the context that is passed to tools."""

    @property
    def project_index(self) -> Any:
        ...
