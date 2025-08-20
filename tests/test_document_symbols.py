# tests/test_document_symbols.py

from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.document_symbols import document_symbols_tool
from mcp_pytools.analysis.symbols import Symbol, SymbolKind

@pytest.fixture
def doc_symbols_project(tmp_path: Path) -> Path:
    """Creates a temporary project for testing document symbols tool."""
    (tmp_path / "test_module.py").write_text(
        """
class MyClass:
    def my_method(self):
        pass

def my_function():
    x = 1
"""
    )
    return tmp_path

@pytest.mark.asyncio
async def test_document_symbols_tool(doc_symbols_project: Path):
    root = doc_symbols_project
    indexer = ProjectIndex(root)
    indexer.build()

    module_uri = (root / "test_module.py").as_uri()
    symbols_data = await document_symbols_tool(indexer, module_uri)
    symbols = [Symbol(kind=SymbolKind[s["kind"]], **{k: v for k, v in s.items() if k != "kind"}) for s in symbols_data]


    assert len(symbols) == 4 # MyClass, my_method, my_function, x

    symbol_names = {s.name for s in symbols}
    assert "MyClass" in symbol_names
    assert "my_method" in symbol_names
    assert "my_function" in symbol_names
    assert "x" in symbol_names

    my_class_symbol = next(s for s in symbols if s.name == "MyClass")
    assert my_class_symbol.kind == SymbolKind.CLASS
    assert my_class_symbol.container is None

    my_method_symbol = next(s for s in symbols if s.name == "my_method")
    assert my_method_symbol.kind == SymbolKind.METHOD
    assert my_method_symbol.container == "MyClass"

    my_function_symbol = next(s for s in symbols if s.name == "my_function")
    assert my_function_symbol.kind == SymbolKind.FUNCTION
    assert my_function_symbol.container is None

    x_symbol = next(s for s in symbols if s.name == "x")
    assert x_symbol.kind == SymbolKind.VARIABLE
    assert x_symbol.container == "my_function"