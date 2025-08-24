# tests/test_symbols.py

from mcp_pytools.analysis.symbols import SymbolKind, document_symbols
from mcp_pytools.astutils.parser import parse_module

SAMPLE_CODE = """
import os

class MyClass:
    class_var = 1

    def my_method(self, a: int):
        pass

def top_level_func():
    pass

x = 10
"""

def test_document_symbols():
    parsed = parse_module(SAMPLE_CODE, "file:///test.py")
    symbols = document_symbols(parsed)

    assert len(symbols) == 5 # MyClass, class_var, my_method, top_level_func, x

    symbol_map = {s.name: s for s in symbols}

    assert "MyClass" in symbol_map
    assert symbol_map["MyClass"].kind == SymbolKind.CLASS
    assert symbol_map["MyClass"].container is None

    assert "class_var" in symbol_map
    assert symbol_map["class_var"].kind == SymbolKind.VARIABLE
    assert symbol_map["class_var"].container == "MyClass"

    assert "my_method" in symbol_map
    assert symbol_map["my_method"].kind == SymbolKind.METHOD
    assert symbol_map["my_method"].container == "MyClass"

    assert "top_level_func" in symbol_map
    assert symbol_map["top_level_func"].kind == SymbolKind.FUNCTION
    assert symbol_map["top_level_func"].container is None

    assert "x" in symbol_map
    assert symbol_map["x"].kind == SymbolKind.VARIABLE
    assert symbol_map["x"].container is None
