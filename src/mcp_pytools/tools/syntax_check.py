from typing import Any, Dict, List

from ..astutils.parser import Position, Range, StructuredSyntaxError, parse_module
from .diagnostics import Diagnostic, DiagnosticSeverity
from .tool import Tool, ToolContext


class SyntaxCheckTool(Tool):
    @property
    def name(self) -> str:
        return "syntax_check"

    @property
    def description(self) -> str:
        return (
            "Analyzes a single Python file for syntax errors and reports them as "
            "diagnostics. This tool is useful for quickly validating the basic "
            "structure of a file without performing a full analysis."
        )

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "uri": {
                    "type": "string",
                    "description": "The file URI of the Python module to check.",
                }
            },
            "required": ["uri"],
        }

    @property
    def requires_index(self) -> bool:
        return False

    async def handle(self, context: ToolContext, **kwargs: Any) -> List[Dict[str, Any]]:
        uri = kwargs["uri"]
        diagnostics: List[Diagnostic] = []
        try:
            path = context.project_index.root / uri.replace("file://", "")
            content = context.project_index.file_cache.get_text(path)
            parse_module(content, uri)
        except StructuredSyntaxError as e:
            pos = Position(line=e.lineno - 1, column=e.offset - 1 if e.offset else 0)
            error_range = Range(start=pos, end=pos)
            diagnostics.append(
                Diagnostic(
                    range=error_range,
                    message=e.msg,
                    severity=DiagnosticSeverity.ERROR,
                    source="syntax-check",
                )
            )
        except Exception:
            pass

        return [d.to_dict() for d in diagnostics]
