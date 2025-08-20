"""Tool to provide a document symbol outline for a given file."""

from typing import Any, Dict, List

from ..analysis.symbols import Symbol
from ..index.project import ProjectIndex


async def document_symbols_tool(index: ProjectIndex, uri: str) -> List[Dict[str, Any]]:
    """Handles a document symbols request.

    This tool retrieves the hierarchical symbol outline for a given document URI.
    It relies on the project index to get the symbols for the file.

    Args:
        index: The project index.
        uri: The URI of the document to analyze.

    Returns:
        A list of Symbol objects, serialized as dictionaries.
    """
    symbols: List[Symbol] = index.symbols.get(uri, [])
    return [symbol.to_dict() for symbol in symbols]
