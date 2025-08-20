"""Tool to find the definition of a symbol."""

import dataclasses
from typing import Any, Dict, List

from ..astutils.parser import Range
from ..index.project import ProjectIndex


@dataclasses.dataclass
class Location:
    uri: str
    range: Range

    def to_dict(self) -> Dict[str, Any]:
        return {"uri": self.uri, "range": self.range.to_dict()}


async def find_definition_tool(
    index: ProjectIndex, symbol: str
) -> List[Dict[str, Any]]:
    """Handles a find definition request for a given symbol.

    Args:
        index: The project index.
        symbol: The symbol name to find.

    Returns:
        A list of Locations of the definition, serialized as dictionaries.
    """
    locations: List[Location] = []
    if symbol in index.defs_by_name:
        for def_symbol in index.defs_by_name[symbol]:
            for uri, symbols_in_doc in index.symbols.items():
                if def_symbol in symbols_in_doc:
                    locations.append(Location(uri=uri, range=def_symbol.range))
                    # Assuming one symbol is in one doc
                    break
    return [loc.to_dict() for loc in locations]
