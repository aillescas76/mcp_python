# tests/test_imports.py

from mcp_pytools.analysis.imports import import_edges
from mcp_pytools.astutils.parser import parse_module

SAMPLE_CODE = """
import os
import sys as system
from pathlib import Path
from . import relative_import
from .. import outer_relative_import
from .sibling import another
from wildcard_module import *
"""

def test_import_edges():
    parsed = parse_module(SAMPLE_CODE, "file:///project/module/test.py")
    edges = import_edges(parsed)

    assert len(edges) == 7

    # A bit hard to test with a map due to multiple imports from same module

    os_import = next(e for e in edges if e.imported_name == "os")
    assert os_import.alias is None

    sys_import = next(e for e in edges if e.imported_name == "sys")
    assert sys_import.alias == "system"

    path_import = next(e for e in edges if e.imported_name == "pathlib.Path")
    assert path_import.alias is None

    relative_import = next(e for e in edges if e.imported_name == ".relative_import")
    assert relative_import.alias is None

    outer_relative_import = next(e for e in edges if e.imported_name == "..outer_relative_import")
    assert outer_relative_import.alias is None

    sibling_import = next(e for e in edges if e.imported_name == ".sibling.another")
    assert sibling_import.alias is None

    wildcard_import = next(e for e in edges if e.is_wildcard)
    assert wildcard_import.imported_name == "wildcard_module"
