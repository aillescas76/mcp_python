from typing import Any, Dict, List

from mcp_pytools.astutils.parser import Position, Range
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.find_definition import Location
from mcp_pytools.tools.registry import ToolRegistry
from mcp_pytools.tools.tool import ToolContext


class MockToolContext(ToolContext):
    def __init__(self, index: ProjectIndex):
        self._project_index = index
        self._tool_registry = ToolRegistry()
        self._tool_registry.discover_tools(__import__("mcp_pytools.tools", fromlist=[""]))


    @property
    def project_index(self) -> ProjectIndex:
        return self._project_index

    @property
    def tool_registry(self) -> "ToolRegistry":
        return self._tool_registry

def locations_from_data(locations_data: List[Dict[str, Any]]) -> List[Location]:
    locations = []
    for loc_data in locations_data:
        range_data = loc_data['range']
        start_pos = Position(line=range_data['start']['line'], column=range_data['start']['column'])
        end_pos = Position(line=range_data['end']['line'], column=range_data['end']['column'])
        loc_range = Range(start=start_pos, end=end_pos)
        locations.append(Location(uri=loc_data['uri'], range=loc_range, text=loc_data['text']))
    return locations
