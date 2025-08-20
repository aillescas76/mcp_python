# src/mcp_pytools/fs/cache.py

import dataclasses
import hashlib
import threading
from pathlib import Path
from typing import Dict, Optional


@dataclasses.dataclass
class FileRecord:
    path: Path
    mtime_ns: int
    size: int
    sha256: Optional[str] = None
    _content_bytes: Optional[bytes] = None
    _content_text: Optional[str] = None


class FileCache:
    """
    A cache for file content and metadata.
    This cache is thread-safe.
    """

    def __init__(self):
        self._cache: Dict[Path, FileRecord] = {}
        self._lock = threading.RLock()

    def get_text(self, path: Path) -> str:
        """Gets the text content of a file, using the cache if possible."""
        record = self._get_or_read_record(path)
        if record._content_text is None:
            with self._lock:
                # Check again in case another thread just populated it
                if record._content_text is None:
                    try:
                        record._content_text = record._content_bytes.decode("utf-8")
                    except (UnicodeDecodeError, AttributeError):
                        # Fallback for binary files or if bytes are not there
                        if record._content_bytes is None:
                            record._content_bytes = path.read_bytes()
                        record._content_text = record._content_bytes.decode(
                            "utf-8", errors="replace"
                        )
        return record._content_text

    def get_bytes(self, path: Path) -> bytes:
        """Gets the byte content of a file, using the cache if possible."""
        record = self._get_or_read_record(path)
        if record._content_bytes is None:
            with self._lock:
                if record._content_bytes is None:
                    record._content_bytes = path.read_bytes()
        return record._content_bytes

    def stat(self, path: Path) -> FileRecord:
        """Gets the metadata record for a file."""
        return self._get_or_read_record(path)

    def invalidate(self, path: Path):
        """Removes a file from the cache."""
        with self._lock:
            if path in self._cache:
                del self._cache[path]

    def _get_or_read_record(self, path: Path) -> FileRecord:
        with self._lock:
            stat_res = path.stat()
            if path in self._cache and self._cache[path].mtime_ns == stat_res.st_mtime_ns:
                return self._cache[path]

            # Read file and create record
            record = FileRecord(
                path=path,
                mtime_ns=stat_res.st_mtime_ns,
                size=stat_res.st_size,
            )
            self._cache[path] = record
            return record

    def get_sha256(self, path: Path) -> str:
        """Gets the SHA256 hash of a file, using the cache if possible.

        The hash is computed lazily and cached.

        Args:
            path: The path to the file.

        Returns:
            The SHA256 hash of the file content.
        """
        record = self._get_or_read_record(path)
        if record.sha256 is None:
            with self._lock:
                if record.sha256 is None:
                    content_bytes = self.get_bytes(path)
                    record.sha256 = hashlib.sha256(content_bytes).hexdigest()
        return record.sha256
