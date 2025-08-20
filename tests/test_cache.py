# tests/test_cache.py


from pathlib import Path

import pytest

from mcp_pytools.fs.cache import FileCache


@pytest.fixture
def cache_test_project(tmp_path: Path) -> Path:
    """Creates a temporary project for testing cache logic."""
    (tmp_path / "file1.txt").write_text("hello")
    (tmp_path / "file2.bin").write_bytes(b"\x01\x02\x03")
    return tmp_path

def test_file_cache_get_text(cache_test_project: Path):
    cache = FileCache()
    path = cache_test_project / "file1.txt"

    content1 = cache.get_text(path)
    assert content1 == "hello"

    # Second access should be cached
    record1 = cache.stat(path)
    content2 = cache.get_text(path)
    record2 = cache.stat(path)
    assert content2 == "hello"
    assert record1 is record2

def test_file_cache_get_bytes(cache_test_project: Path):
    cache = FileCache()
    path = cache_test_project / "file2.bin"

    content1 = cache.get_bytes(path)
    assert content1 == b"\x01\x02\x03"

    # Second access should be cached
    record1 = cache.stat(path)
    content2 = cache.get_bytes(path)
    record2 = cache.stat(path)
    assert content2 == b"\x01\x02\x03"
    assert record1 is record2

def test_file_cache_invalidation(cache_test_project: Path):
    cache = FileCache()
    path = cache_test_project / "file1.txt"

    content1 = cache.get_text(path)
    assert content1 == "hello"

    # Modify the file
    path.write_text("world")

    # Manually invalidate to ensure the test is robust
    cache.invalidate(path)

    # Now, the cache should fetch the new content
    content2 = cache.get_text(path)
    assert content2 == "world"

    # Also check that a new record was created
    record1 = cache.stat(path) # old record is gone
    path.write_text("hello again")
    cache.invalidate(path)
    record2 = cache.stat(path)

    assert record1 is not record2

def test_file_cache_manual_invalidation(cache_test_project: Path):
    cache = FileCache()
    path = cache_test_project / "file1.txt"

    cache.get_text(path)
    assert path in cache._cache

    cache.invalidate(path)
    assert path not in cache._cache

def test_file_cache_sha256(cache_test_project: Path):
    cache = FileCache()
    path = cache_test_project / "file1.txt"

    sha1 = cache.get_sha256(path)
    # sha256 of "hello"
    assert sha1 == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

    record = cache.stat(path)
    assert record.sha256 == sha1

    # Second access should be cached
    sha2 = cache.get_sha256(path)
    assert sha1 == sha2
