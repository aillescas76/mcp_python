# src/mcp_pytools/fs/ignore.py

import fnmatch
from pathlib import Path
from typing import Iterator, List, Tuple


class IgnoreFilter:
    """
    A filter for files and directories based on .gitignore style patterns
    read from the root of a project.
    """

    def __init__(self, patterns: List[Tuple[str, bool]], root: Path):
        self.patterns = patterns
        self.root = root

    @classmethod
    def from_root(cls, root: Path) -> "IgnoreFilter":
        """Creates an IgnoreFilter by finding ignore files in the root."""
        patterns = []
        for filename in [".gitignore", ".mcpignore"]:
            ignore_file = root / filename
            if ignore_file.is_file():
                patterns.extend(cls._parse_ignore_file(ignore_file))
        return cls(patterns, root)

    def is_ignored(self, path: Path) -> bool:
        """
        Checks if a path is ignored by the loaded patterns.
        The last matching pattern determines the outcome.
        """
        if self.root not in path.parents and self.root != path:
            return False

        try:
            relative_path_str = str(path.relative_to(self.root))
        except ValueError:
            return False

        ignored = False
        for pattern, is_negation in self.patterns:
            match = False
            if pattern.endswith("/"):
                p = pattern.rstrip("/")
                if relative_path_str == p or relative_path_str.startswith(p + "/"):
                    match = True
            else:
                if fnmatch.fnmatch(relative_path_str, pattern) or fnmatch.fnmatch(
                    relative_path_str, pattern + "/*"
                ):
                    match = True

            if match:
                ignored = not is_negation
        return ignored

    @staticmethod
    def _parse_ignore_file(file_path: Path) -> List[Tuple[str, bool]]:
        """Parses a .gitignore style file."""
        patterns = []
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                is_negation = line.startswith("!")
                if is_negation:
                    line = line[1:]

                patterns.append((line, is_negation))
        return patterns


def walk_python_files(root: Path) -> Iterator[Path]:
    """Walks a directory and yields Python files that are not ignored.

    This function respects .gitignore and .mcpignore files in the root
    directory and will not descend into ignored directories.

    Args:
        root: The root directory to start walking from.

    Yields:
        Paths to Python files that are not ignored.
    """
    yield from _walk_files(root, lambda p: p.suffix == ".py")


def walk_text_files(root: Path) -> Iterator[Path]:
    """Walks a directory and yields all non-ignored text files.

    This function respects .gitignore and .mcpignore files in the root
    directory and will not descend into ignored directories.

    Args:
        root: The root directory to start walking from.

    Yields:
        Paths to text files that are not ignored.
    """
    # A simple heuristic for text files. Can be expanded.
    TEXT_FILE_EXTENSIONS = {
        ".py", ".txt", ".md", ".json", ".yaml", ".yml", ".xml", ".html",
        ".css", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h",
        ".hpp", ".go", ".rs", ".toml", ".ini", ".cfg"
    }
    yield from _walk_files(root, lambda p: p.suffix in TEXT_FILE_EXTENSIONS)


def _walk_files(root: Path, file_filter) -> Iterator[Path]:
    """Internal helper to walk files with a given filter."""
    ignore_filter = IgnoreFilter.from_root(root)
    dirs_to_visit = [root]

    while dirs_to_visit:
        current_dir = dirs_to_visit.pop(0)

        if current_dir != root and ignore_filter.is_ignored(current_dir):
            continue

        try:
            for item in current_dir.iterdir():
                if ignore_filter.is_ignored(item):
                    continue

                if item.is_dir():
                    dirs_to_visit.append(item)
                elif item.is_file() and file_filter(item):
                    yield item
        except OSError:
            # Ignore permission errors etc.
            pass
