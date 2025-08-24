# tests/test_parser.py

import pytest

from mcp_pytools.astutils.parser import StructuredSyntaxError, parse_module

SAMPLE_CODE = """
import os

class MyClass:
    def my_method(self, a: int) -> int:
        return a + 1

x = 10
"""

def test_parse_module_success():
    parsed = parse_module(SAMPLE_CODE, "file:///test.py")
    assert parsed is not None
    assert parsed.uri == "file:///test.py"
    assert len(parsed.lines) == 8

    # Check that tree has been populated with ranges and parents
    # A few spot checks
    class_node = parsed.tree.body[1]
    assert hasattr(class_node, "_range")
    assert class_node.name == "MyClass"

    func_node = class_node.body[0]
    assert hasattr(func_node, "_parent")
    assert func_node._parent is class_node
    assert hasattr(func_node, "_range")
    assert func_node.name == "my_method"

def test_parse_module_syntax_error():
    with pytest.raises(StructuredSyntaxError) as excinfo:
        parse_module("x = .", "file:///bad.py")

    err = excinfo.value
    assert err.filename == "file:///bad.py"
    assert err.lineno == 1
    assert err.offset == 5
    assert "invalid syntax" in err.msg.lower()
