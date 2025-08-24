# tests/test_ignore.py

from pathlib import Path

import pytest

from mcp_pytools.fs.ignore import IgnoreFilter, walk_python_files


@pytest.fixture
def ignore_test_project(tmp_path: Path) -> Path:
    """Creates a temporary project for testing ignore logic."""
    gitignore_content = """
ignored_dir/
*.log

# A comment
!important.log
build
"""
    (tmp_path / ".gitignore").write_text(gitignore_content)

    (tmp_path / ".mcpignore").write_text("*.pyc\n.venv/")

    (tmp_path / "file1.py").touch()
    (tmp_path / "important.log").touch()
    (tmp_path / "another.log").touch()

    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "ignored_dir" / "file2.py").touch()

    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "output.txt").touch()

    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file3.py").touch()

    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "pyvenv.cfg").touch()

    return tmp_path

def test_ignore_filter(ignore_test_project: Path):
    root = ignore_test_project
    ignore_filter = IgnoreFilter.from_root(root)

    assert ignore_filter.is_ignored(root / "ignored_dir")
    assert ignore_filter.is_ignored(root / "ignored_dir" / "file2.py")
    assert not ignore_filter.is_ignored(root / "file1.py")
    assert not ignore_filter.is_ignored(root / "dir1" / "file3.py")

    # Test negation
    assert not ignore_filter.is_ignored(root / "important.log")
    assert ignore_filter.is_ignored(root / "another.log")

    # Test .mcpignore
    assert ignore_filter.is_ignored(root / ".venv")

    # Test directory pattern without trailing slash
    assert ignore_filter.is_ignored(root / "build")
    assert ignore_filter.is_ignored(root / "build" / "output.txt")


def test_walk_python_files(ignore_test_project: Path):
    root = ignore_test_project
    files = list(walk_python_files(root))

    relative_files = {str(f.relative_to(root)) for f in files}

    assert "file1.py" in relative_files
    assert "dir1/file3.py" in relative_files
    assert "ignored_dir/file2.py" not in relative_files
