# tests/test_project_index.py

from pathlib import Path

import pytest

from mcp_pytools.index.project import ProjectIndex


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Creates a sample project for testing the indexer."""
    (tmp_path / "module1.py").write_text(
        """\nclass MyClass:
    pass
"""
    )
    (tmp_path / "module2.py").write_text(
        """\nfrom module1 import MyClass

def my_func():
    return MyClass()
"""
    )
    (tmp_path / "ignored_dir").mkdir()
    (tmp_path / "ignored_dir" / "ignored.py").write_text("print('ignored')")
    (tmp_path / ".gitignore").write_text("ignored_dir/")
    return tmp_path


def test_project_index_build(sample_project: Path):
    """Tests that the project index is built correctly."""
    indexer = ProjectIndex(sample_project)
    indexer.build()

    assert indexer.stats.files_indexed == 2
    assert indexer.stats.parse_errors == 0
    assert len(indexer.modules) == 2

    module1_uri = (sample_project / "module1.py").as_uri()
    module2_uri = (sample_project / "module2.py").as_uri()

    assert module1_uri in indexer.modules
    assert module2_uri in indexer.modules

    # Check symbols
    assert "MyClass" in indexer.defs_by_name
    assert len(indexer.defs_by_name["MyClass"]) == 1
    assert indexer.defs_by_name["MyClass"][0].name == "MyClass"

    # Check imports
    assert len(indexer.imports[module2_uri]) == 1
    assert indexer.imports[module2_uri][0].imported_name == "module1.MyClass"


def test_project_index_invalidation(sample_project: Path):
    """Tests that invalidating a module removes it from the index."""
    indexer = ProjectIndex(sample_project)
    indexer.build()

    assert indexer.stats.files_indexed == 2
    module1_uri = (sample_project / "module1.py").as_uri()

    indexer.invalidate(module1_uri)

    assert module1_uri not in indexer.modules
    assert "MyClass" not in indexer.defs_by_name


def test_project_index_rebuild(sample_project: Path):
    """Tests that rebuilding a module updates the index correctly."""
    indexer = ProjectIndex(sample_project)
    indexer.build()

    module1_path = sample_project / "module1.py"
    module1_uri = module1_path.as_uri()

    # Modify the file
    module1_path.write_text(
        """\nclass NewClass:
    pass
"""
    )

    indexer.rebuild(module1_uri)

    assert "MyClass" not in indexer.defs_by_name
    assert "NewClass" in indexer.defs_by_name
    assert len(indexer.defs_by_name["NewClass"]) == 1
