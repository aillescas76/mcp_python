# tests/test_search_text.py

import re
from pathlib import Path
import pytest
from mcp_pytools.index.project import ProjectIndex
from mcp_pytools.tools.search_text import search_text_tool, Match

@pytest.fixture
def search_text_project(tmp_path: Path) -> Path:
    """Creates a temporary project for testing search text tool."""
    (tmp_path / "file1.py").write_text(
        """
def my_function():
    x = 10 # variable x
    print("hello")
"""
    )
    (tmp_path / "file2.txt").write_text(
        """
This is a test file.
It contains the word function.
"""
    )
    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "ignored_dir" / "ignored_file.py").write_text("def ignored_func(): pass")
    (tmp_path / ".gitignore").write_text("ignored_dir/")
    return tmp_path

@pytest.mark.asyncio
async def test_search_text_tool_basic(search_text_project: Path):
    root = search_text_project
    indexer = ProjectIndex(root)
    indexer.build()

    matches_data = await search_text_tool(indexer, r"function")
    matches = [Match(**m) for m in matches_data]


    assert len(matches) == 2 # One in file1.py, one in file2.txt

    # Check content of matches
    match_texts = {m.line for m in matches}
    assert "def my_function():" in match_texts
    assert "It contains the word function." in match_texts

@pytest.mark.asyncio
async def test_search_text_tool_with_include(search_text_project: Path):
    root = search_text_project
    indexer = ProjectIndex(root)
    indexer.build()

    matches_data = await search_text_tool(indexer, r"x = 10", includeGlobs=["*.py"])
    matches = [Match(**m) for m in matches_data]


    assert len(matches) == 1
    assert matches[0].uri == (root / "file1.py").as_uri()
    assert matches[0].line == "    x = 10 # variable x"

@pytest.mark.asyncio
async def test_search_text_tool_with_exclude(search_text_project: Path):
    root = search_text_project
    indexer = ProjectIndex(root)
    indexer.build()

    matches_data = await search_text_tool(indexer, r"function", excludeGlobs=["*.txt"])
    matches = [Match(**m) for m in matches_data]

    assert len(matches) == 1
    assert matches[0].uri == (root / "file1.py").as_uri()
    assert matches[0].line == "def my_function():"

@pytest.mark.asyncio
async def test_search_text_tool_respects_gitignore(search_text_project: Path):
    root = search_text_project
    indexer = ProjectIndex(root)
    indexer.build()

    matches = await search_text_tool(indexer, r"ignored_func")

    assert len(matches) == 0 # Should not find in ignored_dir

@pytest.mark.asyncio
async def test_search_text_tool_no_match(search_text_project: Path):
    root = search_text_project
    indexer = ProjectIndex(root)
    indexer.build()

    matches = await search_text_tool(indexer, r"non_existent_pattern")

    assert len(matches) == 0