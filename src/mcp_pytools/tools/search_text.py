# src/mcp_pytools/tools/search_text.py

import dataclasses
import fnmatch
import re
from typing import Any, Dict, List

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
        return (
            "Performs a case-sensitive regular expression search across all text files "
            "in the project, respecting .gitignore rules. Returns a list of all "
            "matching lines. Example: {\"pattern\":\"foo\",\"includeGlobs\":[\"**/*.py\"]}"
        )

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": (
                        "The Python-style regular expression to search for. "
                        "Example: \"migrate_kpi_pipeline\""
                    ),
                },
                "includeGlobs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional list of glob patterns to include in the search. "
                        "Example: [\"**/*.py\"]"
                    ),
                },
                "excludeGlobs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional list of glob patterns to exclude from the search. "
                        "Example: [\"**/tests/**\",\"**/.venv/**\"]"
                    ),
                },
            },
            "required": ["pattern"],
        }

    async def handle(self, context: ToolContext, **kwargs: Any) -> List[Dict[str, Any]]:
        pattern = kwargs["pattern"]
        includeGlobs = kwargs.get("includeGlobs")
        excludeGlobs = kwargs.get("excludeGlobs")

        matches: List[Match] = []
        try:
            regex = re.compile(pattern)
        except re.error as exc:
            raise ValueError(f"Invalid regex pattern: {pattern}") from exc

        for path in walk_text_files(context.project_index.root):
            # Filtering based on includeGlobs and excludeGlobs
            if includeGlobs and not any(
                fnmatch.fnmatch(str(path), glob) for glob in includeGlobs
            ):
                continue
            if excludeGlobs and any(
                fnmatch.fnmatch(str(path), glob) for glob in excludeGlobs
            ):
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
                # Ignore files that can't be read
                continue

        return [m.to_dict() for m in matches]
