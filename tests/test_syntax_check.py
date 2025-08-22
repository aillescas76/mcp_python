from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.syntax_check import syntax_check_tool

@pytest.fixture
def syntax_check_project(tmp_path: Path) -> Path:
    (tmp_path / "good_module.py").write_text("x = 1\n")
    (tmp_path / "bad_module.py").write_text("x = 1\ny = \n")
    return tmp_path

@pytest.mark.asyncio
async def test_syntax_check_good_file(syntax_check_project: Path):
    root = syntax_check_project
    indexer = ProjectIndex(root)
    indexer.build()

    module_uri = (root / "good_module.py").as_uri()
    diagnostics = await syntax_check_tool(indexer, module_uri)
    assert len(diagnostics) == 0

@pytest.mark.asyncio
async def test_syntax_check_bad_file(syntax_check_project: Path):
    root = syntax_check_project
    indexer = ProjectIndex(root)
    indexer.build()

    module_uri = (root / "bad_module.py").as_uri()
    diagnostics = await syntax_check_tool(indexer, module_uri)

    assert len(diagnostics) == 1
    diagnostic = diagnostics[0]
    assert diagnostic['severity'] == 'ERROR'
    assert "invalid syntax" in diagnostic['message']
