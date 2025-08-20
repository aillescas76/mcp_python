from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.find_references import find_references_tool
from .helpers import locations_from_data

@pytest.fixture
def find_refs_project(tmp_path: Path) -> Path:
    """Creates a temporary project for testing find references tool."""
    (tmp_path / "module_a.py").write_text(
        """
class MyClass:
    def my_method(self):
        pass

def top_level_func():
    x = 10
    return MyClass # another ref
"""
    )
    (tmp_path / "module_b.py").write_text(
        """
from module_a import MyClass

def another_func():
    instance = MyClass()
    instance.my_method()
    # Another reference to MyClass
    y = MyClass
"""
    )
    return tmp_path

@pytest.mark.asyncio
async def test_find_references_tool_class(find_refs_project: Path):
    root = find_refs_project
    indexer = ProjectIndex(root)
    indexer.build()

    module_a_uri = (root / "module_a.py").as_uri()
    module_b_uri = (root / "module_b.py").as_uri()

    references_data = await find_references_tool(indexer, "MyClass")
    references = locations_from_data(references_data)

    assert len(references) == 3

    # Check URIs
    assert len([r for r in references if r.uri == module_a_uri]) == 1
    assert len([r for r in references if r.uri == module_b_uri]) == 2

@pytest.mark.asyncio
async def test_find_references_tool_method(find_refs_project: Path):
    root = find_refs_project
    indexer = ProjectIndex(root)
    indexer.build()

    module_a_uri = (root / "module_a.py").as_uri()
    module_b_uri = (root / "module_b.py").as_uri()

    references_data = await find_references_tool(indexer, "my_method")
    references = locations_from_data(references_data)

    assert len(references) == 1

    # Check specific references
    assert any(r.uri == module_b_uri and r.range.start.line == 5 for r in references)

@pytest.mark.asyncio
async def test_find_references_tool_not_found(find_refs_project: Path):
    root = find_refs_project
    indexer = ProjectIndex(root)
    indexer.build()

    references = await find_references_tool(indexer, "non_existent_symbol")

    assert len(references) == 0