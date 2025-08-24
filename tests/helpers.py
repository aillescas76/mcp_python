from typing import List, Dict, Any
from mcp_pytools.tools.find_definition import Location
from mcp_pytools.astutils.parser import Range, Position
from mcp_pytools.tools.tool import ToolContext
from mcp_pytools.index.project import ProjectIndex

class MockToolContext(ToolContext):
    def __init__(self, index: ProjectIndex):
        self._project_index = index

    @property
    def project_index(self) -> ProjectIndex:
        return self._project_index

def locations_from_data(locations_data: List[Dict[str, Any]]) -> List[Location]:
    locations = []
    for loc_data in locations_data:
        range_data = loc_data['range']
        start_pos = Position(line=range_data['start']['line'], column=range_data['start']['character'])
        end_pos = Position(line=range_data['end']['line'], column=range_data['end']['character'])
        loc_range = Range(start=start_pos, end=end_pos)
        locations.append(Location(uri=loc_data['uri'], range=loc_range))
    return locations