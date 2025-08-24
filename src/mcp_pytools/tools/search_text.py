# src/mcp_pytools/tools/search_text.py

import dataclasses
import fnmatch
import re
from typing import Any, Dict, List, Optional

from ..astutils.parser import Position, Range
from ..fs.ignore import walk_text_files
from .tool import Tool, ToolContext


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


class SearchTextTool(Tool):
    @property
    def name(self) -> str:
        return "search_text"

    @property
    def description(self) -> str:
        return "Performs a regular expression search over the files in the project."

    async def handle(
        self,
        context: ToolContext,
        pattern: str,
        includeGlobs: Optional[List[str]] = None,
        excludeGlobs: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        matches: List[Match] = []
        try:
            regex = re.compile(pattern)
        except re.error:
            return []

        for path in walk_text_files(context.project_index.root):
            if excludeGlobs:
                if any(fnmatch.fnmatch(path.name, glob) for glob in excludeGlobs):
                    continue

            uri = path.as_uri()
            try:
                content = context.project_index.file_cache.get_text(path)
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
                continue

        return [m.to_dict() for m in matches]
