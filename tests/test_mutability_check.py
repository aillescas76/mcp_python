from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.mutability_check import mutability_check_tool

@pytest.fixture
def mutability_check_project(tmp_path: Path) -> Path:
    (tmp_path / "module_with_mutables.py").write_text(
        """

def good_func(arg1, arg2=None):
    pass

def bad_func(arg1, arg2=[]):
    pass

def another_bad_func(arg1, arg2={}):
    pass

def yet_another_bad_func(arg1, arg2=set()):
    pass

class MyClass:
    def __init__(self, items=list()):
        self.items = items
"""
    )
    return tmp_path

@pytest.mark.asyncio
async def test_mutability_check(mutability_check_project: Path):
    root = mutability_check_project
    indexer = ProjectIndex(root)
    indexer.build()

    module_uri = (root / "module_with_mutables.py").as_uri()
    diagnostics = await mutability_check_tool(indexer, module_uri)

    assert len(diagnostics) == 4
    messages = {d['message'] for d in diagnostics}
    assert "Mutable default argument" in messages
