from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.find_definition import FindDefinitionTool
from .helpers import locations_from_data, MockToolContext

@pytest.fixture
def find_def_project(tmp_path: Path) -> Path:
    """Creates a temporary project for testing find definition tool."""
    (tmp_path / "module_a.py").write_text(
        """
class MyClass:
    def my_method(self):
        pass

def top_level_func():
    x = 10
"""
    )
    (tmp_path / "module_b.py").write_text(
        """
from module_a import MyClass

def another_func():
    instance = MyClass()
    instance.my_method()
"""
    )
    return tmp_path

@pytest.mark.anyio
async def test_find_definition_tool_local_func(find_def_project: Path):
    root = find_def_project
    indexer = ProjectIndex(root)
    indexer.build()
    context = MockToolContext(indexer)
    tool = FindDefinitionTool()

    module_a_uri = (root / "module_a.py").as_uri()

    locations_data = await tool.handle(context, symbol="top_level_func")
    assert locations_data
    locations = locations_from_data(locations_data)

    assert len(locations) == 1
    location = locations[0]
    assert location.uri == module_a_uri
    assert location.range.start.line == 5
    assert location.range.start.column == 4 # def top_level_func

@pytest.mark.anyio
async def test_find_definition_tool_class(find_def_project: Path):
    root = find_def_project
    indexer = ProjectIndex(root)
    indexer.build()
    context = MockToolContext(indexer)
    tool = FindDefinitionTool()

    locations_data = await tool.handle(context, symbol="MyClass")
    assert locations_data
    locations = locations_from_data(locations_data)

    assert len(locations) == 1
    location = locations[0]
    assert location.uri == (root / "module_a.py").as_uri()
    assert location.range.start.line == 1
    assert location.range.start.column == 6 # class MyClass

@pytest.mark.anyio
async def test_find_definition_tool_method(find_def_project: Path):
    root = find_def_project
    indexer = ProjectIndex(root)
    indexer.build()
    context = MockToolContext(indexer)
    tool = FindDefinitionTool()

    locations_data = await tool.handle(context, symbol="my_method")
    assert locations_data
    locations = locations_from_data(locations_data)

    assert len(locations) == 1
    location = locations[0]
    assert location.uri == (root / "module_a.py").as_uri()
    assert location.range.start.line == 2
    assert location.range.start.column == 8 # def my_method

@pytest.mark.anyio
async def test_find_definition_tool_not_found(find_def_project: Path):
    root = find_def_project
    indexer = ProjectIndex(root)
    indexer.build()
    context = MockToolContext(indexer)
    tool = FindDefinitionTool()

    locations = await tool.handle(context, symbol="non_existent_symbol")

    assert not locations
