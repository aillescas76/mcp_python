# src/mcp_pytools/tools/search_text.py

from pathlib import Path
import re
import dataclasses
import fnmatch
from typing import Any, Dict, List, Optional

from ..astutils.parser import Position, Range
from ..index.project import ProjectIndex
from ..fs.ignore import walk_text_files


@dataclasses.dataclass
class Match:
    uri: str
    range: Range
    line: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "range": self.range.to_dict(),
            "line": self.line,
        }


async def search_text_tool(
    index: ProjectIndex,
    pattern: str,
    includeGlobs: Optional[List[str]] = None,
    excludeGlobs: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Handles a text search request using regular expressions.

    This tool searches for a regex pattern across all text files known to the
    project index.

    Note: `includeGlobs` is not yet implemented.

    Args:
        index: The project index, used for file access.
        pattern: The regular expression pattern to search for.
        includeGlobs: Glob patterns for files to include (not yet implemented).
        excludeGlobs: Glob patterns for files to exclude.

    Returns:
        A list of Match objects, serialized as dictionaries.
    """
    # TODO: Implement includeGlobs filtering.
    matches: List[Match] = []
    try:
        regex = re.compile(pattern)
    except re.error:
        # Invalid regex, return no matches. Could also return an error.
        return []

    for path in walk_text_files(index.root):
        if excludeGlobs:
            if any(fnmatch.fnmatch(path.name, glob) for glob in excludeGlobs):
                continue

        uri = path.as_uri()
        try:
            content = index.file_cache.get_text(path)
            lines = content.splitlines()
            for i, line_text in enumerate(lines):
                for match in regex.finditer(line_text):
                    start_pos = Position(line=i, column=match.start())
                    end_pos = Position(line=i, column=match.end())
                    match_range = Range(start=start_pos, end=end_pos)
                    matches.append(
                        Match(uri=uri, range=match_range, line=line_text)
                    )
        except Exception:
            # Skip binary files or files that can't be read.
            continue

    return [m.to_dict() for m in matches]
