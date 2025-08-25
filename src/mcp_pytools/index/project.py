# src/mcp_pytools/index/project.py

import dataclasses
import threading
from pathlib import Path
from typing import Dict, List

from mcp_pytools.analysis.imports import ImportEdge, import_edges
from mcp_pytools.analysis.symbols import Symbol, document_symbols
from mcp_pytools.astutils.parser import ParsedModule, StructuredSyntaxError, parse_module
from mcp_pytools.fs.cache import FileCache
from mcp_pytools.fs.ignore import walk_text_files


@dataclasses.dataclass
class IndexStats:
    """Statistics about the indexing process."""

    files_indexed: int = 0
    parse_errors: int = 0


class ProjectIndex:
    """An in-memory index of a Python project.

    This class is responsible for scanning a project directory, parsing the
    Python files within it, and building an index of modules, symbols, and
    imports. It is designed to be thread-safe.
    """

    def __init__(self, root: Path):
        """Initializes the ProjectIndex.

        Args:
            root: The root directory of the project to index.
        """
        self.root = root
        self.file_cache = FileCache()
        self.lock = threading.RLock()

        self.modules: Dict[str, ParsedModule] = {}
        self.symbols: Dict[str, List[Symbol]] = {}
        self.imports: Dict[str, List[ImportEdge]] = {}
        self.defs_by_name: Dict[str, List[Symbol]] = {}
        self.stats = IndexStats()

    def build(self):
        """Builds the project index by scanning and parsing all Python files."""
        with self.lock:
            self.modules.clear()
            self.symbols.clear()
            self.imports.clear()
            self.stats = IndexStats()

            for file_path in walk_text_files(self.root):
                self._index_file(file_path)

            self._build_cross_module_maps()

    def get_all_uris(self) -> List[str]:
        """Returns a list of all indexed URIs."""
        with self.lock:
            return list(self.modules.keys())

    def invalidate(self, uri: str):
        """Invalidates the index for a given URI and rebuilds cross-module maps."""
        with self.lock:
            self._invalidate_uri(uri)
            self._build_cross_module_maps()

    def rebuild(self, uri: str):
        """Re-indexes a single file and updates the index."""
        with self.lock:
            self._invalidate_uri(uri)
            try:
                # A URI might not be a file URI, so handle this gracefully
                if uri.startswith("file://"):
                    file_path = Path(uri[7:])
                    if file_path.is_file():
                        self._index_file(file_path)
            except Exception:
                # Ignore errors for non-existent files etc.
                pass

            self._build_cross_module_maps()

    def _index_file(self, file_path: Path):
        """Internal helper to index a single file."""
        uri = file_path.as_uri()
        try:
            text = self.file_cache.get_text(file_path)
            module = parse_module(text, uri)

            self.modules[uri] = module
            self.symbols[uri] = document_symbols(module)
            self.imports[uri] = import_edges(module)

            self.stats.files_indexed += 1
        except (StructuredSyntaxError, ValueError):
            self.stats.parse_errors += 1
        except Exception:
            self.stats.parse_errors += 1

    def _invalidate_uri(self, uri: str):
        """Internal helper to remove all data for a URI."""
        if uri in self.modules:
            del self.modules[uri]
        if uri in self.symbols:
            del self.symbols[uri]
        if uri in self.imports:
            del self.imports[uri]

        try:
            if uri.startswith("file://"):
                file_path = Path(uri[7:])
                self.file_cache.invalidate(file_path)
        except Exception:
            pass

    def _build_cross_module_maps(self):
        """Builds maps that require information from all modules."""
        self.defs_by_name.clear()
        for uri, symbols in self.symbols.items():
            for symbol in symbols:
                # Unqualified name
                if symbol.name not in self.defs_by_name:
                    self.defs_by_name[symbol.name] = []
                self.defs_by_name[symbol.name].append(symbol)

                # Qualified name
                if symbol.container:
                    q_name = f"{symbol.container}.{symbol.name}"
                    if q_name not in self.defs_by_name:
                        self.defs_by_name[q_name] = []
                    self.defs_by_name[q_name].append(symbol)
