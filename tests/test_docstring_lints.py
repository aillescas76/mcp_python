from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.docstring_lints import DocstringLintsTool
from mcp_pytools.tools.tool import ToolContext

class MockToolContext(ToolContext):
    def __init__(self, index: ProjectIndex):
        self._project_index = index

    @property
    def project_index(self) -> ProjectIndex:
        return self._project_index

@pytest.fixture
def docstring_lint_project(tmp_path: Path) -> Path:
    (tmp_path / "module_with_lints.py").write_text(
        '''
# No module docstring

class MyClass:
    def method_with_docstring(self):
        """This is a method docstring."""
        pass

    def method_without_docstring(self):
        pass

def func_without_docstring():
    pass

class _PrivateClass:
    def _private_method_with_docstring(self):
        """Docstring."""
        pass
    
    def _private_method_without_docstring(self):
        pass
'''
    )
    return tmp_path

@pytest.mark.anyio
async def test_docstring_lints(docstring_lint_project: Path):
    root = docstring_lint_project
    indexer = ProjectIndex(root)
    indexer.build()
    context = MockToolContext(indexer)
    tool = DocstringLintsTool()

    module_uri = (root / "module_with_lints.py").as_uri()
    diagnostics = await tool.handle(context, uri=module_uri)

    assert len(diagnostics) == 6
    messages = {d['message'] for d in diagnostics}
    assert f"Missing docstring for '{module_uri}'" in messages
    assert "Missing docstring for 'MyClass'" in messages
    assert "Missing docstring for 'method_without_docstring'" in messages
    assert "Missing docstring for 'func_without_docstring'" in messages
    assert "Missing docstring for '_PrivateClass'" in messages
    assert "Missing docstring for '_private_method_without_docstring'" in messages

@pytest.mark.anyio
async def test_docstring_lints_ignore_private(docstring_lint_project: Path):
    root = docstring_lint_project
    indexer = ProjectIndex(root)
    indexer.build()
    context = MockToolContext(indexer)
    tool = DocstringLintsTool()

    module_uri = (root / "module_with_lints.py").as_uri()
    diagnostics = await tool.handle(context, uri=module_uri, ignore_private=True)

    assert len(diagnostics) == 4
    messages = {d['message'] for d in diagnostics}
    assert f"Missing docstring for '{module_uri}'" in messages
    assert "Missing docstring for 'MyClass'" in messages
    assert "Missing docstring for 'method_without_docstring'" in messages
    assert "Missing docstring for 'func_without_docstring'" in messages