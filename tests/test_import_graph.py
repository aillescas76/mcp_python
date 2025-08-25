from pathlib import Path

import pytest

from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.import_graph import ImportGraphResult, ImportGraphTool

from .helpers import MockToolContext


@pytest.fixture
def import_graph_project(tmp_path: Path) -> Path:
    """Creates a temporary project for testing import graph tool."""
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").touch()
    (tmp_path / "pkg" / "module_a.py").write_text(
        """
import os
from . import module_b
from .. import top_level_module
"""
    )
    (tmp_path / "pkg" / "module_b.py").write_text(
        """
from pkg import module_a
"""
    )
    (tmp_path / "top_level_module.py").write_text(
        """
import pkg.module_a
"""
    )
    return tmp_path

@pytest.mark.anyio
async def test_import_graph_tool(import_graph_project: Path):
    root = import_graph_project
    indexer = ProjectIndex(root)
    indexer.build()
    context = MockToolContext(indexer)
    tool = ImportGraphTool()

    module_a_uri = (root / "pkg" / "module_a.py").as_uri()

    result_data = await tool.handle(context, moduleUri=module_a_uri)
    result = ImportGraphResult(**result_data)


    # Test direct imports
    expected_imports = sorted(["os", "pkg.module_b", "top_level_module"])
    assert result.imports == expected_imports

    # Test dependents (simplified check based on module name)
    # module_b imports module_a
    # top_level_module imports pkg.module_a
    expected_dependents = sorted([
        (root / "pkg" / "module_b.py").as_uri(),
        (root / "top_level_module.py").as_uri(),
    ])
    assert result.dependents == expected_dependents

@pytest.mark.anyio
async def test_import_graph_tool_no_imports(import_graph_project: Path):
    root = import_graph_project
    indexer = ProjectIndex(root)
    indexer.build()
    context = MockToolContext(indexer)
    tool = ImportGraphTool()

    # Create a module with no imports
    (root / "no_imports.py").write_text("x = 1")
    indexer.rebuild((root / "no_imports.py").as_uri())

    result_data = await tool.handle(context, moduleUri=(root / "no_imports.py").as_uri())
    result = ImportGraphResult(**result_data)
    assert result.imports == []
    assert result.dependents == []
